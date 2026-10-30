"""Small persistent SQLite vector index and FastEmbed adapter for Static RAG."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
from collections import Counter
import math

import numpy as np

from systems.static_corpus import CorpusChunk


DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
INDEX_SCHEMA_VERSION = "1"


class FastEmbedEncoder:
    """CPU ONNX text embeddings; model files are downloaded on first build/use."""

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL, threads: int = 2):
        try:
            from fastembed import TextEmbedding
        except ImportError as exc:
            raise RuntimeError("FastEmbed is required for System B; install requirements.txt") from exc
        self.model_name = model_name
        self.model = TextEmbedding(model_name=model_name, threads=threads, cuda=False)

    def embed_documents(self, texts: list[str]) -> list[np.ndarray]:
        return [np.asarray(vector, dtype=np.float32) for vector in self.model.passage_embed(texts)]

    def embed_query(self, text: str) -> np.ndarray:
        return np.asarray(next(iter(self.model.query_embed(text))), dtype=np.float32)


@dataclass(frozen=True)
class SearchHit:
    metadata: dict
    score: float
    dense_score: float = 0.0
    dense_rank: int = 0
    lexical_rank: int | None = None
    article_match: bool = False
    hybrid_score: float = 0.0


def _unit_vector(vector) -> np.ndarray:
    result = np.asarray(vector, dtype=np.float32).reshape(-1)
    if result.size == 0 or not np.isfinite(result).all():
        raise ValueError("Embedding must contain finite values")
    norm = float(np.linalg.norm(result))
    if norm == 0.0:
        raise ValueError("Embedding must not be a zero vector")
    return result / norm


def build_index(
    index_path: Path,
    chunks: list[CorpusChunk],
    embedder,
    embedding_model: str,
    corpus_snapshot: str,
    source_manifest: list[dict],
    excluded_sources: list[dict],
    batch_size: int = 32,
) -> dict:
    """Create/rebuild an index file, replacing it only after a successful build."""
    if not chunks:
        raise ValueError("Cannot build a vector index with no text chunks")
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")
    index_path = Path(index_path)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = index_path.with_name(index_path.name + ".building")
    if temp_path.exists():
        temp_path.unlink()
    conn = sqlite3.connect(temp_path)
    try:
        conn.execute("PRAGMA journal_mode=DELETE")
        conn.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        conn.execute("""CREATE TABLE chunks (
            chunk_id TEXT PRIMARY KEY,
            chunk_text TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            embedding BLOB NOT NULL,
            embedding_dimensions INTEGER NOT NULL
        )""")
        with conn:
            for offset in range(0, len(chunks), batch_size):
                batch = chunks[offset:offset + batch_size]
                vectors = embedder.embed_documents([chunk.chunk_text for chunk in batch])
                if len(vectors) != len(batch):
                    raise ValueError("Embedder returned a different number of vectors than input chunks")
                for chunk, vector in zip(batch, vectors):
                    normalized = _unit_vector(vector).astype("<f4", copy=False)
                    conn.execute(
                        "INSERT INTO chunks VALUES (?, ?, ?, ?, ?)",
                        (chunk.chunk_id, chunk.chunk_text,
                         json.dumps(chunk.metadata(), ensure_ascii=False),
                         normalized.tobytes(), int(normalized.size)),
                    )
            metadata = {
                "index_schema_version": INDEX_SCHEMA_VERSION,
                "embedding_model": embedding_model,
                "corpus_snapshot": corpus_snapshot,
                "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
                "chunk_count": str(len(chunks)),
                "source_manifest": json.dumps(source_manifest, ensure_ascii=False),
                "excluded_sources": json.dumps(excluded_sources, ensure_ascii=False),
            }
            conn.executemany("INSERT INTO metadata(key, value) VALUES (?, ?)", metadata.items())
        conn.close()
        temp_path.replace(index_path)
    except Exception:
        conn.close()
        if temp_path.exists():
            temp_path.unlink()
        raise
    return {"chunk_count": len(chunks), "corpus_snapshot": corpus_snapshot, "embedding_model": embedding_model}


class SQLiteVectorIndex:
    """Hybrid dense and lexical search over the fixed corpus.

    System B's retrieval API deliberately accepts no reference date and applies no
    metadata filters. It searches the complete fixed snapshot for every question.
    Dense and BM25-style lexical rankings are combined with Reciprocal Rank Fusion.
    """

    RRF_K = 60
    LEXICAL_RRF_WEIGHT = 4

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return re.findall(r"[a-z0-9]+", text.casefold())

    @staticmethod
    def _explicit_article_numbers(question: str) -> list[str]:
        """Return explicit Article IDs without conflating a number and its suffix."""
        identifiers = []
        pattern = re.compile(r"\b(?:article|art\.?)\s*(\d{1,3})\s*([a-z]?)\b", re.IGNORECASE)
        for match in pattern.finditer(question):
            identifier = f"{match.group(1)}{match.group(2)}".upper()
            if identifier not in identifiers:
                identifiers.append(identifier)
        return identifiers

    @classmethod
    def _lexical_scores(cls, question: str, documents: list[str]) -> list[float]:
        """Compute dependency-free BM25 scores, retaining alphanumeric Article IDs."""
        query_terms = set(cls._tokens(question))
        tokenized = [cls._tokens(document) for document in documents]
        if not query_terms or not tokenized:
            return [0.0] * len(documents)
        lengths = [len(tokens) for tokens in tokenized]
        average_length = sum(lengths) / len(lengths) or 1.0
        frequencies = [Counter(tokens) for tokens in tokenized]
        document_frequency = Counter(
            term for term in query_terms
            for frequency in frequencies if frequency.get(term, 0)
        )
        scores = []
        for length, frequency in zip(lengths, frequencies):
            score = 0.0
            for term in query_terms:
                tf = frequency.get(term, 0)
                if not tf:
                    continue
                df = document_frequency[term]
                idf = math.log(1 + (len(documents) - df + 0.5) / (df + 0.5))
                denominator = tf + 1.5 * (1 - 0.75 + 0.75 * length / average_length)
                score += idf * tf * 2.5 / denominator
            scores.append(score)
        return scores

    def __init__(self, index_path: Path, embedder):
        self.index_path = Path(index_path)
        if not self.index_path.is_file():
            raise FileNotFoundError(f"Static RAG index not found: {self.index_path}; run build-index first")
        self.embedder = embedder
        with sqlite3.connect(self.index_path) as conn:
            rows = dict(conn.execute("SELECT key, value FROM metadata"))
            self.metadata = {
                **rows,
                "source_manifest": json.loads(rows["source_manifest"]),
                "excluded_sources": json.loads(rows["excluded_sources"]),
                "chunk_count": int(rows["chunk_count"]),
            }

    def search(self, question: str, top_k: int = 5) -> list[SearchHit]:
        if not question.strip():
            raise ValueError("Search question must not be empty")
        if top_k < 1:
            raise ValueError("top_k must be at least 1")
        query = _unit_vector(self.embedder.embed_query(question))
        with sqlite3.connect(self.index_path) as conn:
            rows = conn.execute(
                "SELECT chunk_id, chunk_text, metadata_json, embedding, embedding_dimensions FROM chunks"
            ).fetchall()
        if not rows:
            return []
        ids, chunk_texts, metadata_json, blobs, dimensions = zip(*rows)
        if any(dimension != query.size for dimension in dimensions):
            raise ValueError("Query embedding dimension does not match indexed vectors")
        matrix = np.vstack([np.frombuffer(blob, dtype="<f4") for blob in blobs])
        dense_scores = matrix @ query
        dense_order = sorted(range(len(rows)), key=lambda idx: (-float(dense_scores[idx]), ids[idx]))
        lexical_documents = []
        for text, metadata in zip(chunk_texts, metadata_json):
            item = json.loads(metadata)
            lexical_documents.append(" ".join(filter(None, (
                item.get("article_number"), item.get("section_or_heading"), text,
            ))))
        lexical_scores = self._lexical_scores(question, lexical_documents)
        lexical_order = sorted(
            (idx for idx, score in enumerate(lexical_scores) if score > 0),
            key=lambda idx: (-lexical_scores[idx], ids[idx]),
        )
        dense_ranks = {idx: rank for rank, idx in enumerate(dense_order, start=1)}
        lexical_ranks = {idx: rank for rank, idx in enumerate(lexical_order, start=1)}
        fused_scores = {
            idx: 1 / (self.RRF_K + dense_ranks[idx])
            + (self.LEXICAL_RRF_WEIGHT / (self.RRF_K + lexical_ranks[idx])
               if idx in lexical_ranks else 0)
            for idx in range(len(rows))
        }
        hybrid_order = sorted(range(len(rows)), key=lambda idx: (-fused_scores[idx], ids[idx]))
        requested_articles = self._explicit_article_numbers(question)
        article_order = {article: position for position, article in enumerate(requested_articles)}
        article_matches = [
            idx for idx, raw_metadata in enumerate(metadata_json)
            if str(json.loads(raw_metadata).get("article_number") or "").upper() in article_order
        ]
        article_matches.sort(key=lambda idx: (
            article_order[str(json.loads(metadata_json[idx]).get("article_number")).upper()],
            json.loads(metadata_json[idx]).get("source_document", ""),
            int(json.loads(metadata_json[idx]).get("page_number", 0)),
            self._source_offset(json.loads(metadata_json[idx]).get("source_locator", "")),
            ids[idx],
        ))
        if article_matches:
            matched = set(article_matches)
            ranked = article_matches + [idx for idx in hybrid_order if idx not in matched]
            count = min(len(ranked), max(top_k, len(article_matches)))
            ranked = ranked[:count]
        else:
            ranked = hybrid_order[:min(top_k, len(rows))]
        return [
            SearchHit(
                json.loads(metadata_json[idx]),
                float(fused_scores[idx] + (1.0 if idx in article_matches else 0.0)),
                float(dense_scores[idx]), dense_ranks[idx], lexical_ranks.get(idx),
                idx in article_matches, float(fused_scores[idx]),
            )
            for idx in ranked
        ]

    @staticmethod
    def _source_offset(locator: str) -> int:
        match = re.search(r"character offsets (\d+):", locator)
        return int(match.group(1)) if match else 0
