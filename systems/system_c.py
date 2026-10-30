"""System C: verified historical Article selection and evidence-grounded QA."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Callable
from uuid import uuid4

from systems.generation_settings import GenerationSettings
from systems.static_index import DEFAULT_EMBEDDING_MODEL, FastEmbedEncoder
from systems.system_a import (
    ApiRequestError,
    MissingApiKeyError,
    RateLimitError,
    _append_jsonl,
    _effective_temperature,
    _log_generation_failure,
    _log_generation_success,
    _utc_timestamp,
    _validate_question,
    classify_api_error,
    generate_with_gemini,
    load_dotenv_file,
)
from systems.temporal_corpus import (
    DEFAULT_DATASET_PATH,
    TemporalCorpus,
    load_temporal_corpus,
)
from systems.temporal_index import TemporalArticleIndex


SYSTEM_NAME = "System C — Temporal RAG"
ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = ROOT / "results" / "system_c" / "runs.jsonl"
DEFAULT_TOP_K = 5
ARTICLE_IDENTIFIER = re.compile(r"\b(?:article|art\.?)\s*(\d{1,3})\s*([a-z]?)\b", re.I)


def identify_article_numbers(question: str) -> list[str]:
    """Extract explicit Article numbers, retaining alphabetic insertion suffixes."""
    identifiers = []
    for match in ARTICLE_IDENTIFIER.finditer(question):
        number = f"{match.group(1)}{match.group(2)}".upper()
        if number not in identifiers:
            identifiers.append(number)
    return identifiers


def build_temporal_prompt(question: str, reference_date: str, evidence: list) -> str:
    blocks = []
    for item in evidence:
        metadata = item.metadata
        interval_end = metadata["effective_to"] or "no recorded end date"
        amendment = metadata.get("source_amendment")
        source_reference = metadata["source_reference"]
        boundary_evidence = []
        for evidence_name in ("commencement_evidence", "end_boundary_evidence"):
            evidence = source_reference.get(evidence_name)
            if evidence:
                boundary_evidence.append(
                    f"{evidence_name}={evidence['source_document']} at {evidence['page_or_locator']} "
                    f"(date={evidence['effective_date']})"
                )
        boundary_note = "; ".join(boundary_evidence)
        act_note = ""
        if amendment:
            act_note = (
                f"; source Act assent date={amendment.get('act_date')} "
                "(provenance only, not the effective date)"
            )
        blocks.append(
            f"[{metadata['chunk_id']}] [Evidence | Article {metadata['article_number']} | "
            f"version={metadata['version_id']} | interval=[{metadata['effective_from']}, {interval_end}) | "
            f"evidence verified through={metadata['evidence_coverage']['verified_through']} inclusive | "
            f"verification={metadata['verification_status']} | source={metadata['source_document']} | "
            f"locator={metadata['source_locator']} | section={metadata.get('source_section')}"
            f" | interval evidence={boundary_note}{act_note}]\n{metadata['chunk_text']}"
        )
    context = "\n\n".join(blocks)
    return (
        "Answer the Indian constitutional law question using only the verified, date-eligible "
        "Article-version evidence below. The reference date determines which version applies. "
        "Do not use current Constitution wording, outside knowledge, web search, or any version "
        "not shown here. Cite each supporting passage with its exact evidence ID in square "
        "brackets. If the evidence does not support an answer, say that the available verified "
        "temporal evidence is insufficient. Act assent dates shown in provenance are not effective dates.\n\n"
        f"Reference date: {reference_date}\nQuestion: {question}\n\n"
        f"Verified temporal evidence:\n{context}"
    )


def _eligible_log_fields(versions: list[dict]) -> tuple[list[str], list[dict], list[dict]]:
    return (
        [record["version_id"] for record in versions],
        [
            {"version_id": row["version_id"], "effective_from": row["effective_from"],
             "effective_to": row["effective_to"],
             "evidence_verified_through": row["evidence_coverage"]["verified_through"]}
            for row in versions
        ],
        [
            {"version_id": row["version_id"], "status": row["verification_status"]}
            for row in versions
        ],
    )


def _temporal_abstention_reason(excluded: list[dict]) -> str:
    """Classify why no requested candidate was eligible for this date."""
    verified = [row for row in excluded if row.get("verification_status") == "verified"]
    if not verified:
        return "no_verified_legal_version"
    legal_candidates = [row for row in verified if row.get("exclusion_reason") != "legal_interval_mismatch"]
    if not legal_candidates:
        return "legal_interval_mismatch"
    reasons = {row.get("exclusion_reason") for row in legal_candidates}
    if "missing_evidence_coverage" in reasons:
        return "missing_evidence_coverage"
    if "beyond_evidence_coverage" in reasons:
        return "beyond_evidence_coverage"
    return "no_verified_legal_version"


def run_experiment(
    question_id: str,
    question: str,
    reference_date: str,
    settings: GenerationSettings,
    api_key: str | None,
    corpus: TemporalCorpus,
    embedder=None,
    generate: Callable[[str, GenerationSettings, str], str] = generate_with_gemini,
    output_path: Path = RESULTS_PATH,
    top_k: int = DEFAULT_TOP_K,
    timestamp: str | None = None,
) -> dict:
    """Run one temporal QA experiment; date/status filtering precedes retrieval."""
    _validate_question(question_id, question, reference_date)
    requested = identify_article_numbers(question)
    run_timestamp = timestamp or _utc_timestamp()
    retrieval_started_at = _utc_timestamp()
    retrieval_started = time.perf_counter()
    eligible, excluded = corpus.select_with_exclusions(reference_date, requested or None)
    selected_ids, intervals, statuses = _eligible_log_fields(eligible)
    evidence = []
    index = TemporalArticleIndex(eligible, reference_date, embedder=embedder)
    if eligible:
        evidence = index.search(question, top_k=top_k, article_numbers=requested or None)
    retrieval_elapsed = round(time.perf_counter() - retrieval_started, 6)
    retrieval_completed_at = _utc_timestamp()

    if requested and not eligible:
        reason = _temporal_abstention_reason(excluded)
    elif not eligible:
        reason = _temporal_abstention_reason(excluded)
    elif any(row["provision_status"] != "in_force" for row in eligible) and not evidence:
        reason = "selected_version_is_not_in_force_or_has_no_text"
    elif not evidence:
        reason = "insufficient_verified_evidence"
    else:
        reason = None

    prompt = build_temporal_prompt(question, reference_date, evidence) if evidence else None
    record = {
        "question_id": question_id,
        "question": question,
        "reference_date": reference_date,
        "system_name": SYSTEM_NAME,
        "dataset_id": corpus.dataset_id,
        "requested_article_identifier": requested[0] if requested else None,
        "requested_article_identifiers": requested,
        "selected_version_ids": selected_ids,
        "effective_intervals": intervals,
        "verification_statuses": statuses,
        "excluded_candidate_versions": excluded,
        "retrieval_method": (
            "explicit Article metadata selection within verified date-eligible versions"
            if requested and evidence else (
                "BM25 and exact cosine RRF over verified date-eligible versions"
                if embedder is not None else "BM25 lexical retrieval over verified date-eligible versions"
            )
        ),
        "retrieved_chunk_ids": [item.metadata["chunk_id"] for item in evidence],
        "retrieved_chunks": [
            {**item.metadata, "retrieval_score": item.score, "article_match": item.article_match,
             "dense_score": item.dense_score, "dense_rank": item.dense_rank,
             "lexical_rank": item.lexical_rank, "hybrid_score": item.hybrid_score}
            for item in evidence
        ],
        "source_provenance": [
            {key: item.metadata.get(key) for key in (
                "chunk_id", "version_id", "article_number", "effective_from", "effective_to",
                "verification_status", "evidence_coverage", "source_document", "source_locator", "source_section",
                "source_amendment", "source_reference",
            )}
            for item in evidence
        ],
        "prompt": prompt,
        "raw_answer": None,
        "model_name": settings.model_name,
        "generation_model": settings.model_name,
        "generation_settings": {
            "temperature": _effective_temperature(settings),
            "max_output_tokens": settings.max_output_tokens,
            "request_timeout_seconds": settings.request_timeout_seconds,
            "max_retries": settings.max_retries,
            "retry_backoff_seconds": settings.retry_backoff_seconds,
        },
        "retrieval_used": bool(evidence),
        "temporal_filtering_used": True,
        "web_access_used": False,
        "retrieval_started_at": retrieval_started_at,
        "retrieval_completed_at": retrieval_completed_at,
        "retrieval_elapsed_seconds": retrieval_elapsed,
        "generation_started_at": None,
        "generation_elapsed_seconds": None,
        "abstention_status": reason is not None,
        "abstention_reason": reason,
        "attempt_count": 0,
        "final_status": "not_attempted",
        "final_api_status": None,
        "error_details": [],
        "run_timestamp": run_timestamp,
        "run_status": "abstained" if reason else "failed",
        "error_message": None,
    }

    if reason:
        record["raw_answer"] = (
            "I cannot answer from a verified Article version effective on "
            f"{reference_date}. The available verified temporal evidence is insufficient."
        )
        record["run_status"] = "abstained"
        _append_jsonl(Path(output_path), record)
        return record

    if not api_key or not api_key.strip():
        failure = MissingApiKeyError("GEMINI_API_KEY is missing or empty")
        failure.attempt_count = 0
        failure.error_details = []
        failure.final_status = "failed"
        failure.final_api_status = "missing_api_key"
        classified = failure
    else:
        classified = None

    if classified is None:
        record["generation_started_at"] = _utc_timestamp()
        generation_started = time.perf_counter()
        try:
            answer = generate(prompt, settings, api_key)
            if not isinstance(answer, str) or not answer.strip():
                raise ApiRequestError("Gemini returned an empty text response")
            record["generation_elapsed_seconds"] = round(time.perf_counter() - generation_started, 6)
            _log_generation_success(record, answer)
            record["run_status"] = "succeeded"
        except Exception as exc:
            record["generation_elapsed_seconds"] = round(time.perf_counter() - generation_started, 6)
            classified = exc if isinstance(exc, (MissingApiKeyError, ApiRequestError)) else classify_api_error(exc)
    if classified is not None:
        _log_generation_failure(record, classified)
        record["error_message"] = str(classified)
        record["run_status"] = "failed"
        record["abstention_status"] = False
    _append_jsonl(Path(output_path), record)
    return record


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run verified temporal Article RAG (System C).")
    commands = parser.add_subparsers(dest="command", required=True)
    ask = commands.add_parser("ask", help="Answer using only verified Article versions effective on the reference date")
    ask.add_argument("--question-id", help="Benchmark question ID; generated if omitted")
    ask.add_argument("--question", required=True)
    ask.add_argument("--reference-date", required=True, help="YYYY-MM-DD date used for half-open interval selection")
    ask.add_argument("--top-k", type=_positive_int, default=DEFAULT_TOP_K)
    ask.add_argument("--dataset-path", type=Path, default=DEFAULT_DATASET_PATH)
    ask.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL)
    args = parser.parse_args(argv)
    try:
        question_id = args.question_id or f"adhoc-{uuid4().hex}"
        _validate_question(question_id, args.question, args.reference_date)
        load_dotenv_file()
        settings = GenerationSettings.from_environment()
        corpus = load_temporal_corpus(args.dataset_path)
        requested = identify_article_numbers(args.question)
        date_eligible = corpus.select(args.reference_date, requested or None)
        has_text = any(
            row["provision_status"] == "in_force" and isinstance(row.get("text"), str)
            and row["text"].strip() for row in date_eligible
        )
        # Load the same small CPU embedding model as System B only when there is
        # verified, in-force, date-eligible text to retrieve.
        encoder = FastEmbedEncoder(args.embedding_model) if has_text else None
        result = run_experiment(
            question_id=question_id,
            question=args.question,
            reference_date=args.reference_date,
            settings=settings,
            api_key=os.getenv("GEMINI_API_KEY"),
            corpus=corpus,
            embedder=encoder,
            top_k=args.top_k,
        )
    except (ValueError, MissingApiKeyError, RateLimitError, ApiRequestError, RuntimeError, OSError) as exc:
        print(f"System C error: {exc}", file=sys.stderr)
        return 2
    print(result["raw_answer"])
    print(f"Run status: {result['run_status']}", file=sys.stderr)
    print(f"Saved run: {RESULTS_PATH}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
