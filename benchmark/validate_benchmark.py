"""Validate the benchmark's JSON Schema and gold-evidence semantics (stdlib only)."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCHEMA_PATH = HERE / "schema.json"
DATA_PATH = HERE / "questions.json"
QUESTION_CATEGORIES = {
    "direct_article_lookup", "constitutional_interpretation", "amendment_related",
    "historical_version", "effective_date", "multi_article",
}


def _type_ok(value, expected):
    checks = {
        "object": lambda v: isinstance(v, dict), "array": lambda v: isinstance(v, list),
        "string": lambda v: isinstance(v, str), "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "null": lambda v: v is None,
    }
    return checks[expected](value)


def _resolve_ref(ref, schema_path):
    file_part, _, fragment = ref.partition("#")
    path = (schema_path.parent / file_part).resolve() if file_part else schema_path.resolve()
    target = json.loads(path.read_text(encoding="utf-8"))
    if fragment:
        for token in fragment.lstrip("/").split("/"):
            target = target[token.replace("~1", "/").replace("~0", "~")]
    return target, path


def validate_schema(instance, schema, schema_path, at="$", errors=None):
    """Small local validator for the JSON Schema keywords used here."""
    errors = [] if errors is None else errors
    if "$ref" in schema:
        try:
            target, target_path = _resolve_ref(schema["$ref"], schema_path)
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
            errors.append(f"{at}: cannot resolve $ref: {exc}")
            return errors
        return validate_schema(instance, target, target_path, at, errors)
    expected = schema.get("type")
    if expected is not None:
        types = expected if isinstance(expected, list) else [expected]
        if not any(_type_ok(instance, kind) for kind in types):
            errors.append(f"{at}: expected type {' or '.join(types)}")
            return errors
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{at}: value is outside allowed enum")
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{at}: value does not match const")
    if isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{at}: string shorter than minLength")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{at}: string does not match pattern")
        if schema.get("format") == "date":
            try:
                parsed = date.fromisoformat(instance)
                if parsed.isoformat() != instance:
                    raise ValueError("date is not canonical YYYY-MM-DD")
            except ValueError:
                errors.append(f"{at}: invalid calendar date {instance!r}")
    if isinstance(instance, int) and not isinstance(instance, bool) and instance < schema.get("minimum", instance):
        errors.append(f"{at}: integer is below minimum")
    if isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{at}: array shorter than minItems")
        for i, item in enumerate(instance):
            if "items" in schema:
                validate_schema(item, schema["items"], schema_path, f"{at}[{i}]", errors)
    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{at}: missing required property {key!r}")
        properties = schema.get("properties", {})
        for key, child in properties.items():
            if key in instance:
                validate_schema(instance[key], child, schema_path, f"{at}.{key}", errors)
        if schema.get("additionalProperties") is False:
            for key in instance.keys() - properties.keys():
                errors.append(f"{at}: unexpected property {key!r}")
    return errors


def validate_benchmark(dataset, schema_path=SCHEMA_PATH):
    """Return schema and cross-field errors. A claim of gold requires verified sources."""
    try:
        schema_path = Path(schema_path)
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot load schema: {exc}"]
    errors = validate_schema(dataset, schema, schema_path)
    if not isinstance(dataset, dict) or not isinstance(dataset.get("questions"), list):
        return errors

    if not isinstance(dataset.get("corpus_provenance"), dict):
        return errors

    seen = set()
    for index, question in enumerate(dataset["questions"]):
        at = f"questions[{index}]"
        if not isinstance(question, dict):
            continue
        qid = question.get("question_id")
        if isinstance(qid, str):
            if qid in seen:
                errors.append(f"{at}: duplicate question_id {qid}")
            seen.add(qid)
        refs = question.get("source_references", [])
        ref_map = {}
        if isinstance(refs, list):
            for ref in refs:
                if not isinstance(ref, dict) or not isinstance(ref.get("reference_id"), str):
                    continue
                ref_id = ref["reference_id"]
                if ref_id in ref_map:
                    errors.append(f"{at}: duplicate source reference_id {ref_id}")
                ref_map[ref_id] = ref
        evidence = question.get("gold_evidence", [])
        verified_claim = question.get("verification_status") == "verified"
        expected_evaluation_status = (
            "suitable_for_evaluation" if verified_claim else "pending_source_verification"
        )
        if question.get("evaluation_status") != expected_evaluation_status:
            errors.append(f"{at}: evaluation_status conflicts with verification_status")
        if verified_claim:
            if not isinstance(question.get("expected_answer"), str) or not question["expected_answer"].strip():
                errors.append(f"{at}: verified question requires a non-empty expected_answer")
            if not evidence:
                errors.append(f"{at}: verified question requires gold_evidence")
            for ev_index, item in enumerate(evidence if isinstance(evidence, list) else []):
                ev_at = f"{at}.gold_evidence[{ev_index}]"
                if not isinstance(item, dict):
                    continue
                source = ref_map.get(item.get("source_reference_id"))
                if source is None:
                    errors.append(f"{ev_at}: source_reference_id does not resolve")
                elif source.get("verification_status") != "verified":
                    errors.append(f"{ev_at}: gold evidence points to a non-verified source")
                elif source.get("source_type") == "canonical_pilot":
                    errors.append(f"{ev_at}: canonical pilot records cannot be gold evidence")
                if item.get("verification_status") != "verified":
                    errors.append(f"{ev_at}: gold evidence itself is not verified")
                evidence_text = item.get("evidence_text")
                if not isinstance(evidence_text, str) or not evidence_text.strip():
                    errors.append(f"{ev_at}: gold evidence text is empty")
        else:
            if question.get("expected_answer") is not None:
                errors.append(f"{at}: pending question must not contain expected_answer")
            if evidence:
                errors.append(f"{at}: pending question must not contain gold_evidence")
            if question.get("expected_version_id") is not None:
                errors.append(f"{at}: pending question must not claim expected_version_id")
        if question.get("expected_version_id") is not None:
            version_id = question["expected_version_id"]
            if not any(isinstance(ev, dict) and ev.get("version_id") == version_id and ev.get("verification_status") == "verified" for ev in evidence):
                errors.append(f"{at}: expected_version_id is not backed by verified gold evidence")
        if question.get("question_category") == "historical_version" and not verified_claim:
            if question.get("expected_temporal_status") != "historical_version_pending_verification":
                errors.append(f"{at}: unverified historical question must be marked pending")
    return errors


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read benchmark JSON {path}: {exc}", file=sys.stderr)
        return 2
    errors = validate_benchmark(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    counts = {}
    for question in data["questions"]:
        category = question["question_category"]
        counts[category] = counts.get(category, 0) + 1
    ready = sum(question["verification_status"] == "verified" for question in data["questions"])
    pending = len(data["questions"]) - ready
    historical_blocked = sum(
        question["question_category"] == "historical_version"
        and question["verification_status"] != "verified"
        for question in data["questions"]
    )
    print(f"OK: {len(data['questions'])} questions; {ready} suitable for evaluation; {pending} pending source verification")
    print(f"Historical questions blocked by version evidence gaps: {historical_blocked}")
    for category in sorted(QUESTION_CATEGORIES):
        print(f"{category}: {counts.get(category, 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
