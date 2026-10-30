"""Load and gate historical Article records for System C.

Only a record explicitly marked ``verified`` may enter temporal answer retrieval.
An Act's assent date is retained as provenance and is never substituted for the
record's effective interval.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_PATH = ROOT / "processed" / "canonical" / "article_versions_pilot.json"
DEFAULT_SCHEMA_PATH = ROOT / "processed" / "canonical" / "article_versions_dataset.schema.json"
VERIFIED_STATUS_THRESHOLD = "verified"


class TemporalCorpusError(ValueError):
    """Raised when the canonical version dataset fails validation."""


@dataclass(frozen=True)
class TemporalCorpus:
    dataset_id: str
    records: tuple[dict, ...]

    def select(self, reference_date: str, article_numbers: list[str] | None = None) -> list[dict]:
        """Select verified records covered by both legal time and evidence time."""
        selected, _ = self.select_with_exclusions(reference_date, article_numbers)
        return selected

    def select_with_exclusions(
        self, reference_date: str, article_numbers: list[str] | None = None
    ) -> tuple[list[dict], list[dict]]:
        """Return eligible records and explicit reasons for every excluded candidate.

        Legal intervals remain half-open. ``verified_through`` is an inclusive
        evidence cutoff; a missing or malformed cutoff fails closed.
        """
        day = _parse_date(reference_date)
        if day is None:
            raise ValueError("reference_date must be a valid YYYY-MM-DD date")
        targets = {value.upper() for value in article_numbers} if article_numbers else None
        selected = []
        excluded = []
        for record in self.records:
            if targets is not None and record.get("article_number", "").upper() not in targets:
                continue
            reason = _record_exclusion_reason(record, day)
            if reason is None:
                selected.append(record)
            else:
                excluded.append(_exclusion_record(record, reason))
        return selected, excluded

    def candidates_for(self, article_numbers: list[str] | None = None) -> list[dict]:
        """Return records for audit logging only; callers must not retrieve from these."""
        if not article_numbers:
            return list(self.records)
        targets = {value.upper() for value in article_numbers}
        return [record for record in self.records if record["article_number"].upper() in targets]


def _parse_date(value: str | None) -> date | None:
    if value is None or not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == value else None


def load_temporal_corpus(
    dataset_path: Path = DEFAULT_DATASET_PATH,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
) -> TemporalCorpus:
    """Read the canonical dataset and run its schema and cross-record validator."""
    dataset_path = Path(dataset_path)
    try:
        dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TemporalCorpusError(f"Cannot read temporal dataset {dataset_path}: {exc}") from exc
    try:
        from processed.canonical.validate_article_versions import validate_dataset
    except ImportError:
        # Also support invocation with the canonical directory as the import root.
        from validate_article_versions import validate_dataset
    errors = validate_dataset(dataset, Path(schema_path))
    if errors:
        preview = "; ".join(errors[:5])
        suffix = f" (and {len(errors) - 5} more)" if len(errors) > 5 else ""
        raise TemporalCorpusError(f"Temporal dataset failed validation: {preview}{suffix}")
    records = tuple(dataset["records"])
    skipped = sum(record["verification_status"] != VERIFIED_STATUS_THRESHOLD for record in records)
    if skipped:
        print(
            f"System C excluded {skipped} non-verified Article version record(s); "
            f"eligibility threshold is {VERIFIED_STATUS_THRESHOLD!r}.",
            file=sys.stderr,
        )
    return TemporalCorpus(dataset["dataset_id"], records)


def excluded_candidates(
    corpus: TemporalCorpus,
    reference_date: str,
    article_numbers: list[str] | None = None,
) -> list[dict]:
    """Describe candidate rejections for run transparency without selecting them."""
    day = _parse_date(reference_date)
    if day is None:
        raise ValueError("reference_date must be a valid YYYY-MM-DD date")
    result = []
    targets = {value.upper() for value in article_numbers} if article_numbers else None
    for record in corpus.records:
        if targets is not None and record.get("article_number", "").upper() not in targets:
            continue
        reason = _record_exclusion_reason(record, day)
        if reason is not None:
            result.append(_exclusion_record(record, reason))
    return result


def _record_exclusion_reason(record: dict, day: date) -> str | None:
    if record.get("verification_status") != VERIFIED_STATUS_THRESHOLD:
        return "verification_status_below_threshold"
    start = _parse_date(record.get("effective_from"))
    raw_end = record.get("effective_to")
    end = _parse_date(raw_end) if raw_end is not None else None
    if start is None or (raw_end is not None and end is None) or day < start or (end is not None and day >= end):
        return "legal_interval_mismatch"
    coverage = record.get("evidence_coverage")
    if not isinstance(coverage, dict):
        return "missing_evidence_coverage"
    verified_through = _parse_date(coverage.get("verified_through"))
    if verified_through is None:
        return "missing_evidence_coverage"
    if day > verified_through:
        return "beyond_evidence_coverage"
    return None


def _exclusion_record(record: dict, reason: str) -> dict:
    coverage = record.get("evidence_coverage")
    return {
        "version_id": record.get("version_id"),
        "article_number": record.get("article_number"),
        "verification_status": record.get("verification_status"),
        "effective_from": record.get("effective_from"),
        "effective_to": record.get("effective_to"),
        "evidence_verified_through": coverage.get("verified_through") if isinstance(coverage, dict) else None,
        "exclusion_reason": reason,
    }
