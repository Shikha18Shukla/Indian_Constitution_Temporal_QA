"""Lightweight hybrid index over already date-eligible Article versions.

The constructor accepts only records selected by ``TemporalCorpus.select``.
It performs no disk writes. It can use System B's existing CPU embedding model plus
BM25/RRF; tests and inspection can use its lexical-only mode without model weights.
Each passage carries its version interval and source provenance into citations.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
import hashlib
import math
import re

import numpy as np


DEFAULT_CHUNK_SIZE = 1800
DEFAULT_CHUNK_OVERLAP = 200
COMPREHENSIVE_QUERY = re.compile(r"\b(all|complete|full|every|each|list|freedoms|clauses)\b", re.I)


@dataclass(frozen=True)
class TemporalEvidence:
    metadata: dict
    score: float
    article_match: bool = False
    dense_score: float | None = None
    dense_rank: int | None = None
    lexical_rank: int | None = None
    hybrid_score: float | None = None


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.casefold())


def _split_text(text: str, chunk_size: int, overlap: int) -> list[tuple[int, int]]:
    if chunk_size < 1 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size >= 1 and 0 <= overlap < chunk_size")
    spans = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            floor = start + chunk_size // 2
            boundary = max(text.rfind(". ", floor, end), text.rfind("; ", floor, end), text.rfind(" ", floor, end))
            if boundary > start:
                end = boundary + (1 if text[boundary] in ".;" else 0)
        spans.append((start, end))
        if end == len(text):
            break
        next_start = max(start + 1, end - overlap)
        next_space = text.find(" ", next_start, min(next_start + 80, end))
        start = next_space + 1 if next_space >= 0 else next_start
    return spans


class TemporalArticleIndex:
    """In-memory BM25 index whose contents are already filtered by date/status."""

    def __init__(
        self,
        eligible_versions: list[dict],
        reference_date: str,
        embedder=None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_CHUNK_OVERLAP,
    ):
        try:
            reference_day = date.fromisoformat(reference_date)
        except (TypeError, ValueError) as exc:
            raise ValueError("reference_date must be a valid YYYY-MM-DD date") from exc
        if reference_day.isoformat() != reference_date:
            raise ValueError("reference_date must use YYYY-MM-DD format")
        for record in eligible_versions:
            if record["verification_status"] != "verified":
                raise ValueError(f"Temporal index refuses non-verified version {record['version_id']}")
            start = date.fromisoformat(record["effective_from"])
            end = date.fromisoformat(record["effective_to"]) if record["effective_to"] is not None else None
            if not (start <= reference_day and (end is None or reference_day < end)):
                raise ValueError(f"Temporal index refuses version outside reference date: {record['version_id']}")
            coverage = record.get("evidence_coverage")
            if not isinstance(coverage, dict) or not isinstance(coverage.get("verified_through"), str):
                raise ValueError(f"Temporal index refuses version without evidence coverage: {record['version_id']}")
            try:
                verified_through = date.fromisoformat(coverage["verified_through"])
            except ValueError as exc:
                raise ValueError(f"Temporal index refuses invalid evidence coverage: {record['version_id']}") from exc
            if verified_through.isoformat() != coverage["verified_through"]:
                raise ValueError(f"Temporal index refuses invalid evidence coverage: {record['version_id']}")
            if verified_through < start or (end is not None and verified_through >= end):
                raise ValueError(f"Temporal index refuses inconsistent evidence coverage: {record['version_id']}")
            references = coverage.get("source_references")
            if not isinstance(references, list) or not references or any(
                not isinstance(ref, dict)
                or any(not isinstance(ref.get(key), str) or not ref[key].strip()
                       for key in ("source_document", "page_or_locator", "claim"))
                for ref in references
            ):
                raise ValueError(f"Temporal index refuses evidence coverage without provenance: {record['version_id']}")
            if reference_day > verified_through:
                raise ValueError(f"Temporal index refuses version beyond evidence coverage: {record['version_id']}")
        self.reference_date = reference_date
        self.eligible_version_ids = tuple(record["version_id"] for record in eligible_versions)
        self.chunks = []
        for record in eligible_versions:
            text = record.get("text")
            if record.get("provision_status") != "in_force" or not isinstance(text, str) or not text.strip():
                continue
            for start, end in _split_text(text, chunk_size, overlap):
                chunk_text = text[start:end]
                identity = f"{record['version_id']}\0{start}\0{end}\0{chunk_text}"
                chunk_id = "temporal-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]
                self.chunks.append({
                    "chunk_id": chunk_id,
                    "article_number": record["article_number"],
                    "version_id": record["version_id"],
                    "effective_from": record["effective_from"],
                    "effective_to": record["effective_to"],
                    "verification_status": record["verification_status"],
                    "evidence_coverage": record["evidence_coverage"],
                    "provision_status": record["provision_status"],
                    "operation_type": record["operation_type"],
                    "source_amendment": record["source_amendment"],
                    "source_section": record["source_section"],
                    "source_document": record["source_reference"]["source_document"],
                    "source_locator": record["source_reference"]["page_or_locator"],
                    "source_reference": record["source_reference"],
                    "text_offsets": [start, end],
                    "chunk_text": chunk_text,
                })
        self._tokens = [_tokenize(chunk["chunk_text"]) for chunk in self.chunks]
        self._frequencies = [Counter(tokens) for tokens in self._tokens]
        lengths = [len(tokens) for tokens in self._tokens]
        self._average_length = sum(lengths) / len(lengths) if lengths else 0.0
        self._lengths = lengths
        self.embedder = embedder
        self._vectors = None
        if self.chunks and embedder is not None:
            vectors = embedder.embed_documents([chunk["chunk_text"] for chunk in self.chunks])
            if len(vectors) != len(self.chunks):
                raise ValueError("Embedder returned a different number of vectors than temporal chunks")
            normalized = []
            for vector in vectors:
                value = np.asarray(vector, dtype=np.float32).reshape(-1)
                norm = float(np.linalg.norm(value))
                if not value.size or not np.isfinite(value).all() or norm == 0.0:
                    raise ValueError("Temporal embedding must contain finite, non-zero values")
                normalized.append(value / norm)
            self._vectors = np.vstack(normalized)

    @staticmethod
    def _unit_vector(vector):
        value = np.asarray(vector, dtype=np.float32).reshape(-1)
        norm = float(np.linalg.norm(value))
        if not value.size or not np.isfinite(value).all() or norm == 0.0:
            raise ValueError("Temporal query embedding must contain finite, non-zero values")
        return value / norm

    def _bm25_scores(self, question: str) -> list[float]:
        terms = set(_tokenize(question))
        if not terms or not self.chunks:
            return [0.0] * len(self.chunks)
        document_frequency = {
            term: sum(frequency.get(term, 0) > 0 for frequency in self._frequencies)
            for term in terms
        }
        average = self._average_length or 1.0
        scores = []
        for length, frequency in zip(self._lengths, self._frequencies):
            score = 0.0
            for term in terms:
                tf = frequency.get(term, 0)
                if not tf:
                    continue
                df = document_frequency[term]
                idf = math.log(1 + (len(self.chunks) - df + 0.5) / (df + 0.5))
                score += idf * tf * 2.5 / (tf + 1.5 * (0.25 + 0.75 * length / average))
            scores.append(score)
        return scores

    def search(
        self,
        question: str,
        top_k: int = 5,
        article_numbers: list[str] | None = None,
    ) -> list[TemporalEvidence]:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("Search question must not be empty")
        if top_k < 1:
            raise ValueError("top_k must be at least 1")
        if not self.chunks:
            return []

        targets = {number.upper() for number in article_numbers} if article_numbers else None
        if targets:
            matches = [
                index for index, chunk in enumerate(self.chunks)
                if chunk["article_number"].upper() in targets
            ]
            matches.sort(key=lambda index: (
                self.chunks[index]["article_number"].upper(),
                self.chunks[index]["effective_from"],
                self.chunks[index]["text_offsets"][0],
                self.chunks[index]["chunk_id"],
            ))
            if matches:
                return [TemporalEvidence(self.chunks[index], 1.0, True) for index in matches]

        scores = self._bm25_scores(question)
        lexical_order = sorted(
            (index for index, score in enumerate(scores) if score > 0),
            key=lambda index: (-scores[index], self.chunks[index]["chunk_id"]),
        )
        lexical_ranks = {index: rank for rank, index in enumerate(lexical_order, start=1)}
        if self._vectors is not None:
            query_vector = self._unit_vector(self.embedder.embed_query(question))
            if query_vector.size != self._vectors.shape[1]:
                raise ValueError("Temporal query embedding dimension does not match indexed vectors")
            dense_scores = self._vectors @ query_vector
            dense_order = sorted(
                range(len(self.chunks)),
                key=lambda index: (-float(dense_scores[index]), self.chunks[index]["chunk_id"]),
            )
            dense_ranks = {index: rank for rank, index in enumerate(dense_order, start=1)}
            hybrid_scores = {
                index: 1 / (60 + dense_ranks[index])
                + (4 / (60 + lexical_ranks[index]) if index in lexical_ranks else 0)
                for index in range(len(self.chunks))
            }
            ranked = sorted(range(len(self.chunks)), key=lambda index: (-hybrid_scores[index], self.chunks[index]["chunk_id"]))
        else:
            dense_scores = None
            dense_ranks = {}
            hybrid_scores = {index: scores[index] for index in range(len(self.chunks))}
            ranked = lexical_order
        selected = ranked[:top_k]
        if selected and COMPREHENSIVE_QUERY.search(question):
            selected_versions = {self.chunks[index]["version_id"] for index in selected}
            selected = [
                index for index, chunk in enumerate(self.chunks)
                if chunk["version_id"] in selected_versions
            ]
            selected.sort(key=lambda index: (
                self.chunks[index]["version_id"], self.chunks[index]["text_offsets"][0],
            ))
        return [
            TemporalEvidence(
                self.chunks[index], float(hybrid_scores[index]), False,
                float(dense_scores[index]) if dense_scores is not None else None,
                dense_ranks.get(index), lexical_ranks.get(index), float(hybrid_scores[index]),
            )
            for index in selected
        ]
