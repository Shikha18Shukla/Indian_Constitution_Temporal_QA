"""System B: static-corpus semantic retrieval with shared Gemini generation."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import sys
import time
from uuid import uuid4

from systems.generation_settings import GenerationSettings
from systems.static_corpus import (
    DEFAULT_AMENDMENTS_DIR,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CONSTITUTION,
    chunk_pages,
    load_pdf_pages,
    source_manifest,
)
from systems.static_index import (
    DEFAULT_EMBEDDING_MODEL,
    FastEmbedEncoder,
    SQLiteVectorIndex,
    build_index,
)
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


SYSTEM_NAME = "System B — Static RAG"
ARTICLE_DIAGNOSTIC_QUESTIONS = (
    ("Q002", "What does Article 14 guarantee?"),
    ("Q003", "What freedoms are protected under Article 19?"),
    ("Q004", "What does Article 21 provide?"),
    ("Q001", "What does Article 21A provide?"),
    ("Q005", "What is the purpose of Article 45?"),
)
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX_PATH = ROOT / "processed" / "static_rag" / "index.sqlite3"
RESULTS_PATH = ROOT / "results" / "system_b" / "runs.jsonl"
DEFAULT_MAX_CONTEXT_TOKENS = 4000


def build_static_index(
    root: Path = ROOT,
    index_path: Path = DEFAULT_INDEX_PATH,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
    batch_size: int = 32,
    encoder=None,
) -> dict:
    constitution = root / DEFAULT_CONSTITUTION
    amendments_dir = root / DEFAULT_AMENDMENTS_DIR
    print("Loading page text from the fixed PDF corpus...", file=sys.stderr, flush=True)
    pages, excluded, snapshot = load_pdf_pages(root, constitution, amendments_dir)
    chunks = chunk_pages(pages, snapshot, chunk_size=chunk_size, overlap=overlap)
    manifest = source_manifest(root, constitution, amendments_dir)
    if encoder is None:
        print(f"Loading CPU embedding model {embedding_model}...", file=sys.stderr, flush=True)
        encoder = FastEmbedEncoder(embedding_model)
    result = build_index(
        index_path=index_path,
        chunks=chunks,
        embedder=encoder,
        embedding_model=embedding_model,
        corpus_snapshot=snapshot,
        source_manifest=manifest,
        excluded_sources=excluded,
        batch_size=batch_size,
    )
    result.update({
        "pages_with_text": len(pages),
        "excluded_sources": excluded,
        "index_path": str(index_path),
    })
    return result


def _approx_token_count(text: str) -> int:
    """Tokenizer-independent estimate for diagnostics and the context budget."""
    return math.ceil(len(text) / 4)


def _format_evidence(position: int, hit) -> str:
    metadata = hit.metadata
    labels = [
        f"chunk_id={metadata['chunk_id']}",
        f"source={metadata['source_document']}",
        f"page={metadata['page_number']}",
    ]
    if metadata.get("article_number") is not None:
        labels.append(f"article={metadata['article_number']}")
    if metadata.get("section_or_heading"):
        labels.append(f"heading={metadata['section_or_heading']}")
    return f"[Evidence {position} | {' | '.join(labels)}]\n{metadata['chunk_text']}"


def prepare_static_prompt(
    question: str,
    reference_date: str,
    hits: list,
    max_context_tokens: int = DEFAULT_MAX_CONTEXT_TOKENS,
) -> tuple[str, list, dict]:
    """Budget whole evidence blocks; never truncate passage text or citation labels."""
    if max_context_tokens < 1:
        raise ValueError("max_context_tokens must be at least 1")
    selected, evidence, omitted_ids = [], [], []
    included_tokens = 0
    chunk_lengths = []
    retrieved_text_characters = sum(len(hit.metadata["chunk_text"]) for hit in hits)
    for position, hit in enumerate(hits, start=1):
        text = hit.metadata["chunk_text"]
        block = _format_evidence(position, hit)
        block_tokens = _approx_token_count(block)
        chunk_lengths.append({
            "chunk_id": hit.metadata["chunk_id"],
            "text_characters": len(text),
            "text_approx_tokens": _approx_token_count(text),
            "evidence_block_characters": len(block),
            "evidence_block_approx_tokens": block_tokens,
        })
        if included_tokens + block_tokens <= max_context_tokens:
            selected.append(hit)
            evidence.append(block)
            included_tokens += block_tokens
        else:
            omitted_ids.append(hit.metadata["chunk_id"])

    context = "\n\n".join(evidence)
    if not context and hits:
        context = "[No retrieved passages fit within the configured context budget.]"
    elif not context:
        context = "[No passages were retrieved.]"
    prompt = (
        "Answer the Indian constitutional law question using the retrieved context below. "
        "Treat the retrieved passages as the only documentary evidence available. Cite each "
        "supporting passage with its exact chunk_id in square brackets, for example [chunk-abc]. "
        "Do not invent constitutional wording, sources, or citations. If the retrieved context "
        "does not support an answer, say that the available context is insufficient. The reference "
        "date is question context only: this is a fixed static corpus and passages have not been "
        "selected or filtered by effective date. Do not claim that a passage was legally in force "
        "on that date unless the provided passage itself establishes that fact.\n\n"
        f"Reference date: {reference_date}\n"
        f"Question: {question}\n\n"
        f"Retrieved context:\n{context}"
    )
    diagnostics = {
        "max_context_tokens": max_context_tokens,
        "token_estimation": "ceil(characters / 4); approximate, not model-tokenizer counts",
        "retrieved_chunk_count": len(hits),
        "retrieved_chunk_text_characters": retrieved_text_characters,
        "retrieved_context_approx_tokens": _approx_token_count("".join(
            hit.metadata["chunk_text"] for hit in hits
        )),
        "chunk_lengths": chunk_lengths,
        "included_chunk_count": len(selected),
        "included_chunk_ids": [hit.metadata["chunk_id"] for hit in selected],
        "omitted_chunk_ids": omitted_ids,
        "included_evidence_characters": sum(len(block) for block in evidence),
        "included_context_approx_tokens": included_tokens,
        "prompt_length_characters": len(prompt),
        "prompt_approx_tokens": _approx_token_count(prompt),
    }
    return prompt, selected, diagnostics


def article_retrieval_diagnostics(index, top_k: int = 5) -> list[dict]:
    """Run local retrieval only and return auditable hits for the core Article cases."""
    report = []
    for question_id, question in ARTICLE_DIAGNOSTIC_QUESTIONS:
        hits = index.search(question, top_k=top_k)
        report.append({
            "question_id": question_id,
            "question": question,
            "retrieved_chunks": [
                {
                    **hit.metadata,
                    "article_match": hit.article_match,
                    "retrieval_score": hit.score,
                    "hybrid_score": hit.hybrid_score,
                    "dense_score": hit.dense_score,
                    "dense_rank": hit.dense_rank,
                    "lexical_rank": hit.lexical_rank,
                }
                for hit in hits
            ],
        })
    return report


def build_static_prompt(
    question: str,
    reference_date: str,
    hits: list,
    max_context_tokens: int = DEFAULT_MAX_CONTEXT_TOKENS,
) -> str:
    """Return the single assembled Static RAG prompt."""
    return prepare_static_prompt(question, reference_date, hits, max_context_tokens)[0]


def _emit_diagnostic(event: str, **fields) -> None:
    """Emit structured operational diagnostics without prompt text or credentials."""
    print(json.dumps({"event": event, **fields}, ensure_ascii=False), file=sys.stderr, flush=True)


def run_experiment(
    question_id: str,
    question: str,
    reference_date: str,
    settings: GenerationSettings,
    api_key: str | None,
    index: SQLiteVectorIndex,
    top_k: int = 5,
    max_context_tokens: int = DEFAULT_MAX_CONTEXT_TOKENS,
    generate=generate_with_gemini,
    output_path: Path = RESULTS_PATH,
    timestamp: str | None = None,
) -> dict:
    """Retrieve from the full fixed snapshot, generate once, and log the attempt."""
    _validate_question(question_id, question, reference_date)
    if top_k < 1:
        raise ValueError("top_k must be at least 1")
    if max_context_tokens < 1:
        raise ValueError("max_context_tokens must be at least 1")
    record = {
        "question_id": question_id,
        "question": question,
        "reference_date": reference_date,
        "system_name": SYSTEM_NAME,
        "model_name": settings.model_name,
        "prompt": None,
        "raw_answer": None,
        "retrieved_chunks": [],
        "retrieval_scores": [],
        "source_metadata": [],
        "context_chunks": [],
        "context_diagnostics": None,
        "run_timestamp": timestamp or _utc_timestamp(),
        "generation_settings": {
            "temperature": _effective_temperature(settings),
            "max_output_tokens": settings.max_output_tokens,
            "request_timeout_seconds": settings.request_timeout_seconds,
            "max_retries": settings.max_retries,
            "retry_backoff_seconds": settings.retry_backoff_seconds,
        },
        "embedding_model": index.metadata["embedding_model"],
        "corpus_snapshot": index.metadata["corpus_snapshot"],
        "top_k": top_k,
        "attempt_count": 0,
        "final_status": "not_attempted",
        "final_api_status": None,
        "error_details": [],
        "retrieval_used": True,
        "temporal_filtering_used": False,
        "web_access_used": False,
        "run_status": "failed",
        "error_message": None,
    }
    generation_started = False
    retrieval_timer = time.perf_counter()
    try:
        # The retrieval API intentionally receives no reference_date.
        hits = index.search(question, top_k=top_k)
        retrieval_elapsed = time.perf_counter() - retrieval_timer
        retrieval_completed_at = _utc_timestamp()
        record["retrieved_chunks"] = [
            {**hit.metadata, "retrieval_score": hit.score,
             "hybrid_score": hit.hybrid_score,
             "dense_score": hit.dense_score, "dense_rank": hit.dense_rank,
             "lexical_rank": hit.lexical_rank, "article_match": hit.article_match}
            for hit in hits
        ]
        record["retrieval_scores"] = [hit.score for hit in hits]
        record["source_metadata"] = [
            {key: hit.metadata.get(key) for key in (
                "document_id", "chunk_id", "source_document", "source_type", "page_number",
                "article_number", "section_or_heading", "source_locator", "corpus_snapshot",
            )}
            for hit in hits
        ]
        record["prompt"], selected_hits, context_diagnostics = prepare_static_prompt(
            question, reference_date, hits, max_context_tokens,
        )
        context_diagnostics["retrieval_completed_at"] = retrieval_completed_at
        context_diagnostics["retrieval_elapsed_seconds"] = round(retrieval_elapsed, 6)
        record["context_diagnostics"] = context_diagnostics
        record["context_chunks"] = [
            {**hit.metadata, "retrieval_score": hit.score,
             "hybrid_score": hit.hybrid_score,
             "dense_score": hit.dense_score, "dense_rank": hit.dense_rank,
             "lexical_rank": hit.lexical_rank, "article_match": hit.article_match}
            for hit in selected_hits
        ]
        if not api_key or not api_key.strip():
            failure = MissingApiKeyError("GEMINI_API_KEY is missing or empty")
            failure.attempt_count = 0
            failure.error_details = []
            failure.final_status = "failed"
            failure.final_api_status = "missing_api_key"
            raise failure
        generation_started = True
        generation_started_at = _utc_timestamp()
        generation_timer = time.perf_counter()
        context_diagnostics["generation_started_at"] = generation_started_at
        _emit_diagnostic(
            "system_b_generation_request_start",
            question_id=question_id,
            retrieval_completed_at=retrieval_completed_at,
            retrieval_elapsed_seconds=round(retrieval_elapsed, 6),
            generation_started_at=generation_started_at,
            retrieved_chunk_count=context_diagnostics["retrieved_chunk_count"],
            retrieved_context_characters=context_diagnostics["retrieved_chunk_text_characters"],
            retrieved_context_approx_tokens=context_diagnostics["retrieved_context_approx_tokens"],
            individual_chunk_lengths=context_diagnostics["chunk_lengths"],
            included_context_chunk_count=context_diagnostics["included_chunk_count"],
            omitted_context_chunk_ids=context_diagnostics["omitted_chunk_ids"],
            included_evidence_characters=context_diagnostics["included_evidence_characters"],
            included_context_approx_tokens=context_diagnostics["included_context_approx_tokens"],
            prompt_length_characters=context_diagnostics["prompt_length_characters"],
            prompt_approx_tokens=context_diagnostics["prompt_approx_tokens"],
            max_context_tokens=max_context_tokens,
            top_k=top_k,
            request_timeout_seconds=settings.request_timeout_seconds,
            max_retries=settings.max_retries,
        )
        try:
            answer = generate(record["prompt"], settings, api_key)
        except Exception as exc:
            generation_elapsed = time.perf_counter() - generation_timer
            context_diagnostics["generation_elapsed_seconds"] = round(generation_elapsed, 6)
            _emit_diagnostic(
                "system_b_generation_request_complete",
                question_id=question_id,
                generation_elapsed_seconds=round(generation_elapsed, 6),
                final_status="failed",
                attempt_count=getattr(exc, "attempt_count", 1),
                final_api_status=getattr(exc, "final_api_status", None),
            )
            raise
        generation_elapsed = time.perf_counter() - generation_timer
        context_diagnostics["generation_elapsed_seconds"] = round(generation_elapsed, 6)
        if not isinstance(answer, str) or not answer.strip():
            raise ApiRequestError("Gemini returned an empty text response")
        _log_generation_success(record, answer)
        record["run_status"] = "succeeded"
        _emit_diagnostic(
            "system_b_generation_request_complete",
            question_id=question_id,
            generation_elapsed_seconds=round(generation_elapsed, 6),
            final_status="succeeded",
            attempt_count=record["attempt_count"],
            final_api_status=record["final_api_status"],
        )
    except Exception as exc:
        classified = exc if isinstance(exc, (MissingApiKeyError, ApiRequestError)) else classify_api_error(exc)
        _log_generation_failure(record, classified, default_attempt_count=1 if generation_started else 0)
        record["error_message"] = str(classified)
        _append_jsonl(Path(output_path), record)
        raise classified from exc
    _append_jsonl(Path(output_path), record)
    return record


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build or run System B Static RAG.")
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build-index", help="Build the fixed PDF corpus embedding index")
    build.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL)
    build.add_argument("--chunk-size", type=_positive_int, default=DEFAULT_CHUNK_SIZE)
    build.add_argument("--overlap", type=int, default=DEFAULT_CHUNK_OVERLAP)
    build.add_argument("--batch-size", type=_positive_int, default=32)
    build.add_argument("--index-path", type=Path, default=DEFAULT_INDEX_PATH)

    ask = commands.add_parser("ask", help="Ask one question using the built static index")
    ask.add_argument("--question-id", help="Benchmark question ID; generated if omitted")
    ask.add_argument("--question", required=True)
    ask.add_argument("--reference-date", required=True, help="Question context, not a retrieval filter")
    ask.add_argument("--top-k", type=_positive_int)
    ask.add_argument("--max-context-tokens", type=_positive_int)
    ask.add_argument("--index-path", type=Path, default=DEFAULT_INDEX_PATH)
    diagnose = commands.add_parser(
        "diagnose-retrieval", help="Print local top chunks for Articles 14, 19, 21, 21A and 45 (no generation)"
    )
    diagnose.add_argument("--top-k", type=_positive_int, default=5)
    diagnose.add_argument("--index-path", type=Path, default=DEFAULT_INDEX_PATH)
    args = parser.parse_args(argv)
    try:
        if args.command == "build-index":
            result = build_static_index(
                index_path=args.index_path,
                embedding_model=args.embedding_model,
                chunk_size=args.chunk_size,
                overlap=args.overlap,
                batch_size=args.batch_size,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command == "diagnose-retrieval":
            index_metadata = SQLiteVectorIndex(args.index_path, embedder=None).metadata
            encoder = FastEmbedEncoder(index_metadata["embedding_model"])
            index = SQLiteVectorIndex(args.index_path, encoder)
            print(json.dumps(
                article_retrieval_diagnostics(index, args.top_k), ensure_ascii=False, indent=2,
            ))
            return 0
        load_dotenv_file()
        settings = GenerationSettings.from_environment()
        if args.top_k is None:
            try:
                top_k = int(os.getenv("SYSTEM_B_TOP_K", "5"))
            except ValueError as exc:
                raise ValueError("SYSTEM_B_TOP_K must be an integer") from exc
            if top_k < 1:
                raise ValueError("SYSTEM_B_TOP_K must be at least 1")
        else:
            top_k = args.top_k
        if args.max_context_tokens is None:
            try:
                max_context_tokens = int(os.getenv(
                    "SYSTEM_B_MAX_CONTEXT_TOKENS", str(DEFAULT_MAX_CONTEXT_TOKENS),
                ))
            except ValueError as exc:
                raise ValueError("SYSTEM_B_MAX_CONTEXT_TOKENS must be an integer") from exc
            if max_context_tokens < 1:
                raise ValueError("SYSTEM_B_MAX_CONTEXT_TOKENS must be at least 1")
        else:
            max_context_tokens = args.max_context_tokens
        index_metadata = SQLiteVectorIndex(args.index_path, embedder=None).metadata
        encoder = FastEmbedEncoder(index_metadata["embedding_model"])
        index = SQLiteVectorIndex(args.index_path, encoder)
        result = run_experiment(
            question_id=args.question_id or f"adhoc-{uuid4().hex}",
            question=args.question,
            reference_date=args.reference_date,
            settings=settings,
            api_key=os.getenv("GEMINI_API_KEY"),
            index=index,
            top_k=top_k,
            max_context_tokens=max_context_tokens,
        )
    except (ValueError, MissingApiKeyError, RateLimitError, ApiRequestError, RuntimeError, OSError) as exc:
        print(f"System B error: {exc}", file=sys.stderr)
        return 2
    print(result["raw_answer"])
    print(f"Saved run: {RESULTS_PATH}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
