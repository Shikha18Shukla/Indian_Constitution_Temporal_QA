"""Run one benchmark snapshot against Systems A/B/C with auditable run records.

Dry-run is the default. ``--mocked`` exercises orchestration without API calls;
``--live`` is the only mode that launches the Gemini-backed system CLIs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import time
from typing import Callable
from uuid import uuid4

try:
    from benchmark.validate_benchmark import DATA_PATH, validate_benchmark
except ModuleNotFoundError:  # Also support direct execution as `python benchmark/run_benchmark.py`.
    from validate_benchmark import DATA_PATH, validate_benchmark


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
DEFAULT_OUTPUT_ROOT = ROOT / "results" / "benchmark_runs"
RUNNER_VERSION = "1.0"
SYSTEMS = ("system_a", "system_b", "system_c")
SYSTEM_LOGS = {
    "system_a": ROOT / "results" / "system_a" / "runs.jsonl",
    "system_b": ROOT / "results" / "system_b" / "runs.jsonl",
    "system_c": ROOT / "results" / "system_c" / "runs.jsonl",
}
SUITABLE_STATUS = "suitable_for_evaluation"


class BenchmarkRunError(ValueError):
    """Raised for invalid benchmark input or an unsafe output destination."""


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _canonical_json(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _read_validated_benchmark(path: Path):
    try:
        raw = path.read_bytes()
        data = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BenchmarkRunError(f"Cannot read benchmark JSON {path}: {exc}") from exc
    errors = validate_benchmark(data)
    if errors:
        preview = "; ".join(errors[:8])
        suffix = f" (and {len(errors) - 8} more)" if len(errors) > 8 else ""
        raise BenchmarkRunError(f"Benchmark validation failed: {preview}{suffix}")
    return data, raw


def _eligibility(question: dict) -> tuple[bool, str | None]:
    status = question.get("evaluation_status")
    if status == SUITABLE_STATUS:
        return True, None
    return False, (
        f"evaluation_status={status}; verification_status="
        f"{question.get('verification_status')}"
    )


def build_manifest(data: dict, benchmark_bytes: bytes, mode: str) -> dict:
    """Build a deterministic plan manifest (execution timestamps are separate)."""
    eligible = [q for q in data["questions"] if _eligibility(q)[0]]
    skipped = [
        {"question_id": q["question_id"], "reason": _eligibility(q)[1]}
        for q in data["questions"] if not _eligibility(q)[0]
    ]
    plan = {
        "manifest_schema_version": "1",
        "runner_version": RUNNER_VERSION,
        "benchmark_id": data["benchmark_id"],
        "benchmark_sha256": hashlib.sha256(benchmark_bytes).hexdigest(),
        "mode": mode,
        "selection_rule": f"evaluation_status == {SUITABLE_STATUS!r}",
        "systems": list(SYSTEMS),
        "corpus_provenance": data.get("corpus_provenance"),
        "eligible_questions": [
            {"question_id": q["question_id"], "question": q["question"], "reference_date": q["reference_date"]}
            for q in eligible
        ],
        "skipped_questions": skipped,
    }
    plan["manifest_id"] = hashlib.sha256(_canonical_json(plan)).hexdigest()
    return plan


def build_system_argv(system: str, question: dict) -> list[str]:
    """Map a benchmark record to a system CLI without editing its text or date."""
    if system not in SYSTEMS:
        raise ValueError(f"Unknown system: {system}")
    prefix = [sys.executable, "-m"]
    if system == "system_a":
        command = ["systems.system_a"]
    elif system == "system_b":
        command = ["systems.system_b", "ask"]
    else:
        command = ["systems.system_c", "ask"]
    return prefix + command + [
        "--question-id", question["question_id"],
        "--reference-date", question["reference_date"],
        "--question", question["question"],
    ]


def _records_added_since(path: Path, offset: int) -> list[dict]:
    if not path.is_file():
        return []
    try:
        with path.open("rb") as stream:
            size = path.stat().st_size
            stream.seek(offset if offset <= size else 0)
            added = stream.read().decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    records = []
    for line in added.splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            records.append(record)
    return records


def execute_live(system: str, question: dict, timeout_seconds: int = 300) -> dict:
    """Invoke an existing system CLI, then inspect only its newly appended log row."""
    log_path = SYSTEM_LOGS[system]
    try:
        offset = log_path.stat().st_size if log_path.is_file() else 0
    except OSError:
        offset = 0
    argv = build_system_argv(system, question)
    try:
        completed = subprocess.run(
            argv, cwd=ROOT, capture_output=True, text=True, check=False,
            timeout=timeout_seconds, env=os.environ.copy(),
        )
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        returncode = None
        stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        timed_out = True

    new_records = [
        row for row in _records_added_since(log_path, offset)
        if row.get("question_id") == question["question_id"]
    ]
    system_record = new_records[-1] if new_records else None
    if timed_out:
        return {"status": "failed", "error_reason": f"System process timed out after {timeout_seconds}s", "stdout": stdout}
    if returncode != 0:
        reason = (system_record or {}).get("error_message") or stderr.strip() or f"System exited with status {returncode}"
        return {"status": "failed", "error_reason": reason, "stdout": stdout, "system_run_status": (system_record or {}).get("run_status")}
    if system_record is None:
        return {"status": "failed", "error_reason": "System exited successfully but appended no matching run record", "stdout": stdout}

    run_status = system_record.get("run_status")
    if run_status == "abstained":
        return {
            "status": "abstained",
            "abstention_reason": system_record.get("abstention_reason") or system_record.get("error_message") or "System C abstained without a recorded reason",
            "raw_answer": system_record.get("raw_answer"),
            "system_run_status": run_status,
        }
    if run_status != "succeeded":
        return {"status": "failed", "error_reason": system_record.get("error_message") or f"Unexpected system run_status: {run_status!r}", "system_run_status": run_status}
    return {"status": "completed", "raw_answer": system_record.get("raw_answer"), "system_run_status": run_status}


def _mock_executor(system: str, question: dict, temporal_corpus=None) -> dict:
    """No-API mock: A/B are simulated; C checks verified date eligibility only."""
    if system != "system_c":
        return {"status": "mocked", "raw_answer": None, "mock_note": "No generation call was made."}
    if temporal_corpus is None:
        from systems.temporal_corpus import load_temporal_corpus
        temporal_corpus = load_temporal_corpus()
    from systems.system_c import identify_article_numbers
    requested = identify_article_numbers(question["question"])
    eligible, excluded = temporal_corpus.select_with_exclusions(question["reference_date"], requested or None)
    if not eligible:
        verified = [row for row in excluded if row.get("verification_status") == "verified"]
        if not verified:
            reason = "no_verified_legal_version"
        else:
            legal_candidates = [row for row in verified if row.get("exclusion_reason") != "legal_interval_mismatch"]
            if not legal_candidates:
                reason = "legal_interval_mismatch"
            else:
                exclusion_reasons = {row.get("exclusion_reason") for row in legal_candidates}
                if "missing_evidence_coverage" in exclusion_reasons:
                    reason = "missing_evidence_coverage"
                elif "beyond_evidence_coverage" in exclusion_reasons:
                    reason = "beyond_evidence_coverage"
                else:
                    reason = "no_verified_legal_version"
        return {"status": "abstained", "abstention_reason": reason, "raw_answer": None, "mock_note": "Actual verified-version eligibility checked; no generation call was made."}
    return {"status": "mocked", "raw_answer": None, "mock_note": "Eligible version exists; retrieval/generation were not run."}


def _append_jsonl(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_benchmark(
    benchmark_path: Path = DATA_PATH,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    mode: str = "dry-run",
    executor: Callable[[str, dict], dict] | None = None,
    timeout_seconds: int = 300,
) -> dict:
    """Run or plan each eligible question against each system and persist every outcome."""
    if mode not in {"dry-run", "mocked", "live"}:
        raise ValueError("mode must be dry-run, mocked, or live")
    if timeout_seconds < 1:
        raise ValueError("timeout_seconds must be positive")
    benchmark_path = Path(benchmark_path)
    data, raw_bytes = _read_validated_benchmark(benchmark_path)
    manifest = build_manifest(data, raw_bytes, mode)
    started = _utc_timestamp()
    execution_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid4().hex[:8]
    run_dir = Path(output_root) / manifest["manifest_id"] / execution_id
    run_dir.mkdir(parents=True, exist_ok=False)
    _write_json(run_dir / "manifest.json", manifest)
    question_by_id = {q["question_id"]: q for q in data["questions"]}
    skipped_by_id = {item["question_id"]: item["reason"] for item in manifest["skipped_questions"]}
    counts = {key: 0 for key in ("completed", "failed", "skipped", "abstained", "mocked", "planned")}
    by_system = {}
    effective_executor = executor
    temporal_corpus = None
    if mode == "live" and effective_executor is None:
        effective_executor = lambda system, question: execute_live(system, question, timeout_seconds)
    elif mode == "mocked" and effective_executor is None:
        # Load the small canonical JSON once; no embedding model or network access is used.
        from systems.temporal_corpus import load_temporal_corpus
        temporal_corpus = load_temporal_corpus()
        effective_executor = lambda system, question: _mock_executor(system, question, temporal_corpus)

    for system in SYSTEMS:
        system_path = run_dir / f"{system}.jsonl"
        by_system[system] = {key: 0 for key in counts}
        for question in data["questions"]:
            qid = question["question_id"]
            eligible, reason = _eligibility(question)
            now = _utc_timestamp()
            base = {
                "question_id": qid,
                "system": system,
                "status": None,
                "timestamp": now,
                "execution_time_seconds": 0.0,
                "question": question["question"],
                "reference_date": question["reference_date"],
                "execution_mode": mode,
                "raw_answer": None,
                "error_reason": None,
                "abstention_reason": None,
            }
            if not eligible:
                base.update(status="skipped", error_reason=reason)
                status = "skipped"
            elif mode == "dry-run":
                base["status"] = "planned"
                status = "planned"
            else:
                t0 = time.perf_counter()
                try:
                    result = effective_executor(system, question)
                    if not isinstance(result, dict):
                        raise TypeError("executor must return a result dictionary")
                except Exception as exc:  # Continue and persist all other question/system outcomes.
                    result = {"status": "failed", "error_reason": f"{type(exc).__name__}: {exc}"}
                base["execution_time_seconds"] = round(time.perf_counter() - t0, 6)
                status = result.get("status")
                if status not in {"completed", "failed", "abstained", "mocked"}:
                    status = "failed"
                    result["error_reason"] = result.get("error_reason") or f"Invalid executor status: {result.get('status')!r}"
                if system == "system_c" and status == "completed" and result.get("system_run_status") == "abstained":
                    status = "abstained"
                    result["abstention_reason"] = result.get("abstention_reason") or "System C abstained"
                base.update(
                    status=status,
                    raw_answer=result.get("raw_answer"),
                    error_reason=result.get("error_reason"),
                    abstention_reason=result.get("abstention_reason"),
                )
                if "system_run_status" in result:
                    base["system_run_status"] = result["system_run_status"]
                if "mock_note" in result:
                    base["mock_note"] = result["mock_note"]
            _append_jsonl(system_path, base)
            counts[status] += 1
            by_system[system][status] += 1

    skipped_questions = [
        {"question_id": qid, "reason": skipped_by_id[qid]}
        for qid in question_by_id if qid in skipped_by_id
    ]
    _write_json(run_dir / "skipped_questions.json", {"count": len(skipped_questions), "questions": skipped_questions})
    summary = {
        "manifest_id": manifest["manifest_id"],
        "execution_id": execution_id,
        "execution_mode": mode,
        "started_at": started,
        "finished_at": _utc_timestamp(),
        "run_directory": str(run_dir.resolve()),
        "counts": counts,
        "skipped_question_count": len(skipped_questions),
        "skipped_question_ids_and_reasons": skipped_questions,
        "per_system_counts": by_system,
    }
    _write_json(run_dir / "summary.json", summary)
    summary["summary_path"] = str((run_dir / "summary.json").resolve())
    return summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run the shared benchmark against Systems A, B and C.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", dest="mode", action="store_const", const="dry-run", help="Plan outputs without launching systems (default)")
    mode.add_argument("--mocked", dest="mode", action="store_const", const="mocked", help="Exercise orchestration without Gemini calls")
    mode.add_argument("--live", dest="mode", action="store_const", const="live", help="Explicitly run Gemini-backed systems")
    parser.set_defaults(mode="dry-run")
    parser.add_argument("--benchmark", type=Path, default=DATA_PATH)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--timeout-seconds", type=int, default=300, help="Per-system process timeout in live mode")
    args = parser.parse_args(argv)
    try:
        summary = run_benchmark(args.benchmark, args.output_root, args.mode, timeout_seconds=args.timeout_seconds)
    except (BenchmarkRunError, OSError, ValueError) as exc:
        print(f"Benchmark runner error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["counts"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
