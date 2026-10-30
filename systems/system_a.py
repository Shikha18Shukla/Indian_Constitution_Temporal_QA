"""System A: Gemini Base LLM with no retrieval or external context."""

import argparse
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import random
import re
import sys
import time
from typing import Callable
from uuid import uuid4

from systems.generation_settings import GenerationSettings


SYSTEM_NAME = "System A — Base LLM"
RESULTS_PATH = Path(__file__).resolve().parents[1] / "results" / "system_a" / "runs.jsonl"


class MissingApiKeyError(RuntimeError):
    """Raised when GEMINI_API_KEY is not configured."""


class ApiRequestError(RuntimeError):
    """Raised for other Gemini API or response failures."""


class TransientApiError(ApiRequestError):
    """Raised for retryable 503/504 Gemini service responses."""


class ConnectionTimeoutError(ApiRequestError):
    """Raised when the configured Gemini request timeout is reached."""


class NetworkRequestError(ApiRequestError):
    """Raised when a Gemini request fails at the network layer."""


class InvalidApiKeyError(ApiRequestError):
    """Raised when Gemini rejects the configured API key."""


class RateLimitError(ApiRequestError):
    """Raised when Gemini reports a rate limit or quota response."""


class GeminiResponse(str):
    """String answer carrying the request attempt telemetry for the run logger."""

    def __new__(cls, answer: str, attempt_count: int, error_details: list[dict]):
        result = super().__new__(cls, answer)
        result.attempt_count = attempt_count
        result.error_details = error_details
        result.final_status = "succeeded"
        result.final_api_status = "OK"
        return result


def load_dotenv_file():
    """Load the repository .env file without overriding process variables."""
    try:
        from dotenv import load_dotenv
    except ImportError as exc:
        raise RuntimeError("python-dotenv is required; install requirements.txt") from exc
    repository_root = Path(__file__).resolve().parents[1]
    load_dotenv(repository_root / ".env", override=False)


def build_prompt(question: str, reference_date: str) -> str:
    """Build the fixed, neutral prompt used by the Base LLM condition."""
    return (
        "Answer the following question about Indian constitutional law. "
        "Use the reference date to interpret the question.\n\n"
        f"Reference date: {reference_date}\n"
        f"Question: {question}\n\n"
        "Provide a direct answer. If you are uncertain, state that clearly."
    )


def _validate_question(question_id: str, question: str, reference_date: str) -> None:
    if not isinstance(question_id, str) or not question_id.strip():
        raise ValueError("question_id must be a non-empty string")
    if not isinstance(question, str) or not question.strip():
        raise ValueError("question must be a non-empty string")
    try:
        parsed = date.fromisoformat(reference_date)
    except (TypeError, ValueError) as exc:
        raise ValueError("reference_date must be a valid YYYY-MM-DD date") from exc
    if parsed.isoformat() != reference_date:
        raise ValueError("reference_date must use YYYY-MM-DD format")


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as output:
        output.write(json.dumps(record, ensure_ascii=False) + "\n")


def _api_status_code(exc: Exception):
    status = getattr(exc, "status_code", None)
    if status is None:
        status = getattr(exc, "code", None)
    response = getattr(exc, "response", None)
    if status is None and response is not None:
        status = getattr(response, "status_code", None)
    if status is not None and str(status).isdigit():
        return int(status)
    match = re.search(r"\b(503|504)\b", str(exc))
    return int(match.group(1)) if match else None


def classify_api_error(exc: Exception) -> Exception:
    status = _api_status_code(exc)
    message = str(exc)
    exception_names = {cls.__name__.lower() for cls in type(exc).__mro__}
    message_upper = message.upper()
    if any("timeout" in name for name in exception_names) or isinstance(exc, TimeoutError):
        return ConnectionTimeoutError(
            f"Gemini request timed out after the configured timeout: {message}"
        )
    if any(
        name in exception_names
        for name in ("connecterror", "networkerror", "transporterror", "connectionerror", "readerror", "writeerror", "proxyerror")
    ):
        return NetworkRequestError(f"Gemini network request failed: {message}")
    if str(status) in {"401", "403"} or any(
        marker in message_upper
        for marker in ("API_KEY_INVALID", "INVALID API KEY", "API KEY NOT VALID", "UNAUTHENTICATED")
    ):
        return InvalidApiKeyError(f"Gemini rejected the API key: {message}")
    if str(status) == "429" or "RESOURCE_EXHAUSTED" in message.upper():
        return RateLimitError(f"Gemini rate limit or quota error: {message}")
    if status in {503, 504} or "503 UNAVAILABLE" in message_upper or "504 DEADLINE_EXCEEDED" in message_upper:
        return TransientApiError(f"Gemini transient service error: {message}")
    return ApiRequestError(f"Gemini API request failed: {message}")


def _error_details(exc: Exception, attempt: int) -> dict:
    message = str(exc)
    status_code = _api_status_code(exc)
    label_match = re.search(r"\b(?:503|504)\s+([A-Z][A-Z_]+)\b", message.upper())
    code = getattr(exc, "code", None)
    return {
        "attempt": attempt,
        "error_type": type(exc).__name__,
        "status_code": status_code,
        "status_label": label_match.group(1) if label_match else (str(code) if code and not str(code).isdigit() else None),
        "message": message,
    }


def _final_api_status(exc: Exception) -> str:
    status = _api_status_code(exc)
    if status in {503, 504}:
        label = _error_details(exc, 1)["status_label"]
        return f"{status} {label}" if label else str(status)
    if isinstance(exc, ConnectionTimeoutError):
        return "connection_timeout"
    if isinstance(exc, NetworkRequestError):
        return "network_error"
    if isinstance(exc, InvalidApiKeyError):
        return "invalid_api_key"
    if isinstance(exc, RateLimitError):
        return "rate_limited"
    return "api_error"


def _is_retryable_api_error(exc: Exception) -> bool:
    return isinstance(exc, (TransientApiError, NetworkRequestError, ConnectionTimeoutError))


def _attach_failure_telemetry(exc: Exception, attempts: int, errors: list[dict]) -> Exception:
    exc.attempt_count = attempts
    exc.error_details = errors
    exc.final_status = "failed"
    exc.final_api_status = _final_api_status(exc)
    return exc


def _log_generation_success(record: dict, answer) -> None:
    record["raw_answer"] = str(answer)
    record["attempt_count"] = getattr(answer, "attempt_count", 1)
    record["error_details"] = getattr(answer, "error_details", [])
    record["final_status"] = "succeeded"
    record["final_api_status"] = getattr(answer, "final_api_status", "OK")


def _log_generation_failure(record: dict, exc: Exception, default_attempt_count: int = 1) -> None:
    record["attempt_count"] = getattr(exc, "attempt_count", default_attempt_count)
    record["error_details"] = getattr(exc, "error_details", [_error_details(exc, 1)])
    record["final_status"] = getattr(exc, "final_status", "failed")
    record["final_api_status"] = getattr(exc, "final_api_status", _final_api_status(exc))


def _is_gemini_3_model(model_name: str) -> bool:
    return model_name.lower().startswith("gemini-3.")


def _effective_temperature(settings: GenerationSettings):
    """Return None when Gemini 3.x uses its model-defined sampling defaults."""
    return None if _is_gemini_3_model(settings.model_name) else settings.temperature


def generate_with_gemini(prompt: str, settings: GenerationSettings, api_key: str) -> str:
    """Call Gemini with bounded retries for transient service/network failures only."""
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        failure = ApiRequestError("google-genai is required; install requirements.txt")
        raise _attach_failure_telemetry(failure, 0, []) from exc
    try:
        http_options = types.HttpOptions(
            timeout=settings.request_timeout_seconds * 1000,
            retry_options=types.HttpRetryOptions(attempts=1),
        )
        client = genai.Client(api_key=api_key, http_options=http_options)
        config_kwargs = {"max_output_tokens": settings.max_output_tokens}
        if not _is_gemini_3_model(settings.model_name):
            config_kwargs["temperature"] = settings.temperature
        print(
            f"Waiting for Gemini ({settings.model_name}; timeout {settings.request_timeout_seconds}s per attempt; up to {settings.max_retries} transient retries)...",
            file=sys.stderr,
            flush=True,
        )
        config = types.GenerateContentConfig(**config_kwargs)
    except Exception as exc:
        failure = classify_api_error(exc)
        raise _attach_failure_telemetry(failure, 0, []) from exc

    error_details = []
    total_attempts = settings.max_retries + 1
    for attempt in range(1, total_attempts + 1):
        try:
            response = client.models.generate_content(
                model=settings.model_name,
                contents=prompt,
                config=config,
            )
        except Exception as exc:
            classified = classify_api_error(exc)
            error_details.append(_error_details(exc, attempt))
            if _is_retryable_api_error(classified) and attempt < total_attempts:
                backoff_cap = settings.retry_backoff_seconds * (2 ** (attempt - 1))
                delay = random.uniform(0.0, backoff_cap)
                print(
                    f"Gemini transient failure ({_final_api_status(classified)}); retrying "
                    f"attempt {attempt + 1}/{total_attempts} after {delay:.2f}s.",
                    file=sys.stderr,
                    flush=True,
                )
                time.sleep(delay)
                continue
            failure = _attach_failure_telemetry(classified, attempt, error_details)
            raise failure from exc

        answer = getattr(response, "text", None)
        if not isinstance(answer, str) or not answer.strip():
            failure = ApiRequestError("Gemini returned an empty text response")
            raise _attach_failure_telemetry(failure, attempt, error_details)
        return GeminiResponse(answer, attempt, error_details)


def run_experiment(
    question_id: str,
    question: str,
    reference_date: str,
    settings: GenerationSettings,
    api_key: str | None,
    generate: Callable[[str, GenerationSettings, str], str] = generate_with_gemini,
    output_path: Path = RESULTS_PATH,
    timestamp: str | None = None,
) -> dict:
    """Run and persist one experiment attempt, including failed API attempts."""
    _validate_question(question_id, question, reference_date)
    prompt = build_prompt(question, reference_date)
    record = {
        "question_id": question_id,
        "question": question,
        "reference_date": reference_date,
        "system_name": SYSTEM_NAME,
        "model_name": settings.model_name,
        "prompt": prompt,
        "raw_answer": None,
        "run_timestamp": timestamp or _utc_timestamp(),
        "temperature": _effective_temperature(settings),
        "max_output_tokens": settings.max_output_tokens,
        "request_timeout_seconds": settings.request_timeout_seconds,
        "max_retries": settings.max_retries,
        "retry_backoff_seconds": settings.retry_backoff_seconds,
        "attempt_count": 0,
        "final_status": "not_attempted",
        "final_api_status": None,
        "error_details": [],
        "retrieval_used": False,
        "web_access_used": False,
        "run_status": "failed",
        "error_message": None,
    }
    if not api_key or not api_key.strip():
        record["error_message"] = "GEMINI_API_KEY is missing or empty"
        record["final_status"] = "failed"
        record["final_api_status"] = "missing_api_key"
        _append_jsonl(Path(output_path), record)
        raise MissingApiKeyError(record["error_message"])
    try:
        answer = generate(prompt, settings, api_key)
        if not isinstance(answer, str) or not answer.strip():
            failure = ApiRequestError("Gemini returned an empty text response")
            _attach_failure_telemetry(
                failure,
                getattr(answer, "attempt_count", 1),
                getattr(answer, "error_details", []),
            )
            raise failure
        _log_generation_success(record, answer)
        record["run_status"] = "succeeded"
    except Exception as exc:
        classified = exc if isinstance(exc, (RateLimitError, ApiRequestError)) else classify_api_error(exc)
        _log_generation_failure(record, classified)
        record["error_message"] = str(classified)
        _append_jsonl(Path(output_path), record)
        raise classified from exc
    _append_jsonl(Path(output_path), record)
    return record


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run one System A Base LLM experiment.")
    parser.add_argument("--question-id", help="Benchmark question ID; generated if omitted")
    parser.add_argument("--question", required=True, help="Indian constitutional law question")
    parser.add_argument("--reference-date", required=True, help="Reference date in YYYY-MM-DD format")
    args = parser.parse_args(argv)

    try:
        load_dotenv_file()
        settings = GenerationSettings.from_environment()
        question_id = args.question_id or f"adhoc-{uuid4().hex}"
        result = run_experiment(
            question_id=question_id,
            question=args.question,
            reference_date=args.reference_date,
            settings=settings,
            api_key=os.getenv("GEMINI_API_KEY"),
        )
    except (ValueError, MissingApiKeyError, RateLimitError, ApiRequestError, RuntimeError) as exc:
        print(f"System A error: {exc}", file=sys.stderr)
        return 2
    print(result["raw_answer"])
    print(f"Saved run: {RESULTS_PATH}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
