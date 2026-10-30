"""Validate the pilot JSON Schema and its cross-record temporal rules (stdlib only)."""

import json
import sys
from datetime import date
from pathlib import Path


HERE = Path(__file__).resolve().parent
DATASET_SCHEMA = HERE / "article_versions_dataset.schema.json"
RECORD_SCHEMA = HERE / "article_version.schema.json"
PILOT_DATA = HERE / "article_versions_pilot.json"

REQUIRED_RECORD = {
    "article_number", "version_id", "text", "effective_from", "effective_to",
    "source_amendment", "source_section", "source_reference", "operation_type",
    "verification_status", "verification_notes", "provision_status",
}
VALID_OPERATIONS = {"baseline", "not_in_force", "inserted", "substituted", "amended", "omitted"}
VALID_STATUSES = {"verified", "partially_verified", "unverified"}
VALID_PROVISION_STATES = {"in_force", "not_in_force", "omitted"}


def _is_type(value, expected):
    """JSON types, taking care that bool is not an integer in JSON Schema."""
    checks = {
        "object": lambda v: isinstance(v, dict),
        "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str),
        "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "boolean": lambda v: isinstance(v, bool),
        "null": lambda v: v is None,
    }
    return checks.get(expected, lambda _v: True)(value)


def _resolve_ref(ref, schema_path):
    file_part, _, fragment = ref.partition("#")
    target_path = (schema_path.parent / file_part).resolve() if file_part else schema_path
    target = json.loads(target_path.read_text(encoding="utf-8"))
    if fragment:
        for token in fragment.lstrip("/").split("/"):
            target = target[token.replace("~1", "/").replace("~0", "~")]
    return target, target_path


def validate_json_schema(instance, schema, schema_path, instance_path="$", errors=None):
    """Validate the JSON Schema keywords used by the two local schema files."""
    if errors is None:
        errors = []
    if "$ref" in schema:
        try:
            target_schema, target_path = _resolve_ref(schema["$ref"], schema_path)
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            errors.append(f"{instance_path}: cannot resolve schema ref {schema['$ref']!r}: {exc}")
            return errors
        return validate_json_schema(instance, target_schema, target_path, instance_path, errors)

    expected = schema.get("type")
    if expected is not None:
        allowed_types = expected if isinstance(expected, list) else [expected]
        if not any(_is_type(instance, item) for item in allowed_types):
            errors.append(f"{instance_path}: expected type {' or '.join(allowed_types)}")
            return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{instance_path}: must equal {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{instance_path}: value is outside the allowed enum")
    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{instance_path}: string is shorter than minLength")
        if schema.get("format") == "date":
            try:
                parsed = date.fromisoformat(instance)
                if parsed.isoformat() != instance:
                    raise ValueError("not canonical YYYY-MM-DD")
            except ValueError:
                errors.append(f"{instance_path}: invalid date format/value {instance!r}")

    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{instance_path}: array is shorter than minItems")
        if "items" in schema:
            for index, item in enumerate(instance):
                validate_json_schema(item, schema["items"], schema_path, f"{instance_path}[{index}]", errors)

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{instance_path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        for key, child in properties.items():
            if key in instance:
                validate_json_schema(instance[key], child, schema_path, f"{instance_path}.{key}", errors)
        if schema.get("additionalProperties") is False:
            for key in instance.keys() - properties.keys():
                errors.append(f"{instance_path}: unexpected property {key!r}")
    return errors


def _parse_date(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.isoformat() == value else None


def validate_dataset(dataset, dataset_schema_path=DATASET_SCHEMA):
    """Return all schema and semantic validation errors for one dataset."""
    try:
        schema = json.loads(Path(dataset_schema_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot load dataset schema: {exc}"]

    errors = validate_json_schema(dataset, schema, Path(dataset_schema_path))
    if not isinstance(dataset, dict) or not isinstance(dataset.get("records"), list):
        return errors

    seen_ids = set()
    grouped = {}
    for index, record in enumerate(dataset["records"]):
        if not isinstance(record, dict) or REQUIRED_RECORD - record.keys():
            continue  # The JSON Schema errors above describe malformed records.
        rid = record["version_id"]
        if rid in seen_ids:
            errors.append(f"{rid}: duplicate version_id")
        seen_ids.add(rid)

        start = _parse_date(record["effective_from"])
        end_value = record["effective_to"]
        end = _parse_date(end_value) if end_value is not None else None
        if end_value is not None and end is None:
            # Already reported by schema validation; avoid misleading interval checks.
            continue
        if start and end and end <= start:
            errors.append(f"{rid}: effective_to must be later than effective_from")

        coverage = record.get("evidence_coverage")
        if coverage is not None:
            if not isinstance(coverage, dict):
                # The schema reports the malformed object; avoid secondary errors.
                coverage = None
            else:
                verified_through = _parse_date(coverage.get("verified_through"))
                if verified_through is not None and start is not None and verified_through < start:
                    errors.append(f"{rid}: evidence_coverage.verified_through is before effective_from")
                if verified_through is not None and end is not None and verified_through >= end:
                    errors.append(f"{rid}: evidence_coverage.verified_through must be before exclusive effective_to")
                references = coverage.get("source_references")
                if isinstance(references, list):
                    for ref_index, reference in enumerate(references):
                        if isinstance(reference, dict):
                            for field in ("source_document", "page_or_locator", "claim"):
                                value = reference.get(field)
                                if isinstance(value, str) and not value.strip():
                                    errors.append(
                                        f"{rid}: evidence_coverage.source_references[{ref_index}].{field} must be non-empty"
                                    )

        operation = record["operation_type"]
        state = record["provision_status"]
        text = record["text"]
        if state == "not_in_force":
            if text is not None or operation != "not_in_force":
                errors.append(f"{rid}: not_in_force requires null text and operation_type not_in_force")
        elif state == "omitted":
            if text is not None or operation != "omitted":
                errors.append(f"{rid}: omitted requires null text and operation_type omitted")
        elif state == "in_force":
            if not isinstance(text, str) or not text.strip():
                errors.append(f"{rid}: in_force requires non-empty text")
            if operation in {"not_in_force", "omitted"}:
                errors.append(f"{rid}: operation_type {operation} conflicts with in_force state")

        source = record["source_reference"]
        if not isinstance(source, dict):
            continue
        _check_evidence(source.get("commencement_evidence"), start, "commencement_evidence", rid, errors)
        if end_value is not None:
            _check_evidence(source.get("end_boundary_evidence"), end, "end_boundary_evidence", rid, errors)
        if operation in {"inserted", "substituted", "amended", "omitted"}:
            if not isinstance(record["source_amendment"], dict):
                errors.append(f"{rid}: amendment operation requires source_amendment object")
            if not isinstance(record["source_section"], str) or not record["source_section"].strip():
                errors.append(f"{rid}: amendment operation requires source_section")
        grouped.setdefault(record["article_number"], []).append((start, end, rid))

    for article, rows in grouped.items():
        rows.sort(key=lambda row: row[0] or date.min)
        for previous, current in zip(rows, rows[1:]):
            _, previous_end, previous_id = previous
            current_start, _, current_id = current
            if previous_end is None:
                errors.append(f"{article}: {previous_id} is open-ended but followed by {current_id}")
            elif current_start and previous_end > current_start:
                errors.append(f"{article}: overlapping intervals {previous_id} and {current_id}")
            elif current_start and previous_end < current_start:
                errors.append(f"{article}: gap between {previous_id} and {current_id}")
    return errors


def _check_evidence(evidence, expected_date, field, record_id, errors):
    if not isinstance(evidence, dict):
        errors.append(f"{record_id}: {field} must be an object")
        return
    for key in ("source_document", "page_or_locator"):
        if not isinstance(evidence.get(key), str) or not evidence[key].strip():
            errors.append(f"{record_id}: {field}.{key} must be non-empty")
    evidence_date = _parse_date(evidence.get("effective_date"))
    if evidence_date is None:
        errors.append(f"{record_id}: {field}.effective_date must be a valid YYYY-MM-DD date")
    elif expected_date and evidence_date != expected_date:
        errors.append(f"{record_id}: {field}.effective_date does not match interval boundary")


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else PILOT_DATA
    try:
        dataset = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read valid JSON from {path}: {exc}", file=sys.stderr)
        return 2
    errors = validate_dataset(dataset)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"OK: {len(dataset['records'])} records validated in {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
