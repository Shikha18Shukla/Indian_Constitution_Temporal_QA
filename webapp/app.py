"""FastAPI adapter around the existing Systems A, B, and C implementations."""

from __future__ import annotations

from datetime import date, datetime, timezone
from functools import lru_cache
import importlib.util
import json
import os
from pathlib import Path
import re
import tempfile
import threading
import time
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator, model_validator

from systems.generation_settings import GenerationSettings
from systems.static_index import DEFAULT_EMBEDDING_MODEL, FastEmbedEncoder, SQLiteVectorIndex
from systems.system_a import (
    RESULTS_PATH as SYSTEM_A_RESULTS,
    _validate_question,
    load_dotenv_file,
    run_experiment as run_system_a,
)
from systems.system_b import (
    DEFAULT_INDEX_PATH,
    RESULTS_PATH as SYSTEM_B_RESULTS,
    run_experiment as run_system_b,
)
from systems.system_c import (
    DEFAULT_TOP_K,
    RESULTS_PATH as SYSTEM_C_RESULTS,
    identify_article_numbers,
    run_experiment as run_system_c,
)
from systems.temporal_corpus import DEFAULT_DATASET_PATH, load_temporal_corpus


ROOT = Path(__file__).resolve().parents[1]
HISTORY_PATH = ROOT / "results" / "web_interface" / "comparison_history.jsonl"
SYSTEM_RESULT_PATHS = {
    "A": SYSTEM_A_RESULTS,
    "B": SYSTEM_B_RESULTS,
    "C": SYSTEM_C_RESULTS,
}
_HISTORY_LOCK = threading.Lock()
_CITATION_RE = re.compile(r"\[((?:chunk|temporal)-[^\]\s]+)\]")


class CompareRequest(BaseModel):
    question: str = Field(min_length=1, max_length=10000)
    reference_date: str
    systems: list[Literal["A", "B", "C"]] = Field(min_length=1)

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("question must not be blank")
        return value

    @field_validator("reference_date")
    @classmethod
    def date_must_be_iso_calendar_date(cls, value: str) -> str:
        try:
            parsed = date.fromisoformat(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("reference_date must be a valid YYYY-MM-DD date") from exc
        if parsed.isoformat() != value:
            raise ValueError("reference_date must use YYYY-MM-DD format")
        return value

    @model_validator(mode="after")
    def systems_must_be_unique(self):
        if len(self.systems) != len(set(self.systems)):
            raise ValueError("systems must not contain duplicates")
        return self


app = FastAPI(
    title="Indian Constitution Temporal QA API",
    version="1.0.0",
    description="Local interface for the existing Base LLM, Static RAG, and Temporal RAG systems.",
)


def _api_key_is_configured() -> bool:
    # Reuse the project's existing .env loader while never displaying or
    # returning the secret itself.
    try:
        load_dotenv_file()
    except RuntimeError:
        return False
    return bool(os.getenv("GEMINI_API_KEY", "").strip())


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


def _embedding_model_cached(model_name: str = DEFAULT_EMBEDDING_MODEL) -> bool:
    """Inspect FastEmbed's cache without creating directories or downloading files."""
    try:
        from fastembed import TextEmbedding
        from huggingface_hub.file_download import repo_folder_name

        description = next(
            item for item in TextEmbedding.list_supported_models()
            if item.get("model", "").casefold() == model_name.casefold()
        )
        repo_id = description.get("sources", {}).get("hf")
        if not repo_id:
            return False
        cache_dir = Path(os.getenv(
            "FASTEMBED_CACHE_PATH", str(Path(tempfile.gettempdir()) / "fastembed_cache"),
        ))
        repo_cache = cache_dir / repo_folder_name(repo_id=repo_id, repo_type="model")
        snapshots = repo_cache / "snapshots"
        if snapshots.is_dir():
            expected_model_file = Path(description.get("model_file", "")).name
            for snapshot in snapshots.iterdir():
                if not snapshot.is_dir():
                    continue
                found = {path.name for path in snapshot.rglob("*") if path.is_file()}
                if expected_model_file in found and "tokenizer.json" in found:
                    return True
        legacy = cache_dir / f"fast-{model_name.split('/')[-1]}"
        if legacy.is_dir():
            found = {path.name for path in legacy.rglob("*") if path.is_file()}
            return Path(description.get("model_file", "")).name in found and "tokenizer.json" in found
        return False
    except (ImportError, KeyError, StopIteration, OSError, ValueError):
        return False


def _health_systems() -> dict[str, bool]:
    """Check local prerequisites without calling Gemini or downloading models."""
    key_present = _api_key_is_configured()
    genai_present = _module_available("google.genai")
    fastembed_present = _module_available("fastembed")
    embedding_cached = fastembed_present and _embedding_model_cached()
    try:
        static_index_available = DEFAULT_INDEX_PATH.is_file() and bool(
            SQLiteVectorIndex(DEFAULT_INDEX_PATH, embedder=None).metadata
        )
    except Exception:
        static_index_available = False
    try:
        load_temporal_corpus(DEFAULT_DATASET_PATH)
        temporal_data_available = True
    except Exception:
        temporal_data_available = False
    return {
        "A": key_present and genai_present,
        "B": key_present and genai_present and embedding_cached and static_index_available,
        "C": key_present and genai_present and embedding_cached and temporal_data_available,
    }


@app.get("/api/health")
def health():
    systems = _health_systems()
    all_available = all(systems.values())
    return {
        "status": "ok" if all_available else "degraded",
        "all_systems_available": all_available,
        "systems_available": systems,
        "gemini_api_key_configured": _api_key_is_configured(),
        "availability_note": "Checks local prerequisites and cached embedding files only; no API call or model download is attempted.",
    }


@lru_cache(maxsize=1)
def _get_static_index() -> SQLiteVectorIndex:
    metadata = SQLiteVectorIndex(DEFAULT_INDEX_PATH, embedder=None).metadata
    encoder = FastEmbedEncoder(metadata.get("embedding_model", DEFAULT_EMBEDDING_MODEL))
    return SQLiteVectorIndex(DEFAULT_INDEX_PATH, encoder)


@lru_cache(maxsize=1)
def _get_temporal_corpus():
    return load_temporal_corpus(DEFAULT_DATASET_PATH)


@lru_cache(maxsize=1)
def _get_encoder(model_name: str = DEFAULT_EMBEDDING_MODEL):
    return FastEmbedEncoder(model_name)


def _read_latest_system_record(system: str, question_id: str) -> dict | None:
    path = SYSTEM_RESULT_PATHS[system]
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("question_id") == question_id:
            return row
    return None


def _run_selected_system(system: str, question: str, reference_date: str, question_id: str) -> dict:
    """Call one existing experiment function and return its persisted record."""
    _validate_question(question_id, question, reference_date)
    load_dotenv_file()
    settings = GenerationSettings.from_environment()
    api_key = os.getenv("GEMINI_API_KEY")
    if system == "A":
        return run_system_a(question_id, question, reference_date, settings, api_key)
    if system == "B":
        return run_system_b(
            question_id, question, reference_date, settings, api_key,
            index=_get_static_index(),
        )
    if system == "C":
        corpus = _get_temporal_corpus()
        requested = identify_article_numbers(question)
        eligible = corpus.select(reference_date, requested or None)
        has_in_force_text = any(
            row.get("provision_status") == "in_force"
            and isinstance(row.get("text"), str)
            and row["text"].strip()
            for row in eligible
        )
        encoder = _get_encoder(DEFAULT_EMBEDDING_MODEL) if has_in_force_text else None
        return run_system_c(
            question_id, question, reference_date, settings, api_key,
            corpus=corpus, embedder=encoder, top_k=DEFAULT_TOP_K,
        )
    raise ValueError(f"Unsupported system: {system}")


def _sanitize_error(message: str | None, api_key: str | None) -> str | None:
    if not message:
        return message
    return message.replace(api_key, "[REDACTED]") if api_key else message


def _format_system_result(system: str, record: dict | None, error: str | None, elapsed: float, api_key: str | None) -> dict:
    record = record or {}
    run_status = record.get("run_status")
    if error:
        status = "failed"
    elif run_status == "abstained":
        status = "abstained"
    elif run_status == "succeeded":
        status = "completed"
    else:
        status = "failed"
        error = error or record.get("error_message") or "System returned no successful or abstention status."

    retrieved_evidence = record.get("retrieved_chunks") or record.get("context_chunks") or []
    prompt_evidence = record.get("context_chunks") or record.get("retrieved_chunks") or []
    evidence_by_id = {
        item.get("chunk_id"): item for item in prompt_evidence if item.get("chunk_id")
    }
    answer = record.get("raw_answer")
    citation_ids = list(dict.fromkeys(_CITATION_RE.findall(answer or "")))
    citations = [
        {"citation_id": citation_id, "evidence": evidence_by_id.get(citation_id),
         "found_in_retrieved_evidence": citation_id in evidence_by_id}
        for citation_id in citation_ids
    ]
    selected_ids = record.get("selected_version_ids") or []
    intervals = record.get("effective_intervals") or []
    versions = record.get("verification_statuses") or []
    return {
        "system": system,
        "status": status,
        "answer": answer,
        "citations": citations,
        "retrieved_evidence": retrieved_evidence,
        "prompt_evidence": prompt_evidence,
        "elapsed_seconds": round(elapsed, 6),
        "error": _sanitize_error(error or record.get("error_message"), api_key),
        "abstention_reason": record.get("abstention_reason"),
        "model_name": record.get("model_name"),
        "generation_settings": record.get("generation_settings"),
        "retrieval_used": record.get("retrieval_used"),
        "temporal_filtering_used": record.get("temporal_filtering_used"),
        "requested_article_identifier": record.get("requested_article_identifier"),
        "selected_version_id": selected_ids[0] if len(selected_ids) == 1 else None,
        "selected_version_ids": selected_ids,
        "effective_dates": intervals,
        "verification_statuses": versions,
        "evidence_coverage": [
            {"version_id": item.get("version_id"), "verified_through": item.get("evidence_verified_through")}
            for item in intervals
        ],
        "retrieval_elapsed_seconds": record.get("retrieval_elapsed_seconds")
        or (record.get("context_diagnostics") or {}).get("retrieval_elapsed_seconds"),
        "generation_elapsed_seconds": record.get("generation_elapsed_seconds")
        or (record.get("context_diagnostics") or {}).get("generation_elapsed_seconds"),
    }


def _append_history(record: dict) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
    with _HISTORY_LOCK:
        with HISTORY_PATH.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(line + "\n")


@app.post("/api/compare")
def compare(request: CompareRequest):
    comparison_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    try:
        load_dotenv_file()
    except RuntimeError:
        # Each selected system will surface the existing dependency error in
        # its own explicit result status below.
        pass
    api_key = os.getenv("GEMINI_API_KEY")
    results = {}
    for system in request.systems:
        question_id = f"web-{comparison_id}-{system}"
        started = time.perf_counter()
        record = None
        error = None
        try:
            record = _run_selected_system(system, request.question, request.reference_date, question_id)
        except Exception as exc:
            record = _read_latest_system_record(system, question_id)
            error = str(exc)
        results[system] = _format_system_result(
            system, record, error, time.perf_counter() - started, api_key,
        )

    response = {
        "comparison_id": comparison_id,
        "created_at": created_at,
        "question": request.question,
        "reference_date": request.reference_date,
        "systems": results,
    }
    try:
        _append_history(response)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Comparison completed but local history could not be saved: {exc}") from exc
    return response


@app.get("/api/history")
def history(limit: int = Query(default=20, ge=1, le=100)):
    if not HISTORY_PATH.is_file():
        return {"count": 0, "runs": []}
    runs = []
    try:
        for line in HISTORY_PATH.read_text(encoding="utf-8").splitlines():
            try:
                runs.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Cannot read comparison history: {exc}") from exc
    return {"count": min(len(runs), limit), "runs": list(reversed(runs[-limit:]))}
