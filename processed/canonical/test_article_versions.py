"""Semantic, provenance, and dataset-schema tests for the pilot."""

import copy
import json
import unittest
from pathlib import Path

from validate_article_versions import DATASET_SCHEMA, PILOT_DATA, validate_dataset


DATASET = json.loads(PILOT_DATA.read_text(encoding="utf-8"))


def record(dataset, version_id):
    return next(row for row in dataset["records"] if row["version_id"] == version_id)


class ArticleVersionTests(unittest.TestCase):
    def setUp(self):
        self.data = copy.deepcopy(DATASET)

    def assert_error(self, data, fragment):
        errors = validate_dataset(data)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_pilot_validates_against_dataset_schema_and_semantics(self):
        self.assertEqual(validate_dataset(self.data), [])

    def test_inserted_article_has_null_pre_insertion_state(self):
        before = record(self.data, "21A_pre_86th")
        after = record(self.data, "21A_v1")
        self.assertEqual(before["provision_status"], "not_in_force")
        self.assertIsNone(before["text"])
        self.assertEqual(before["effective_to"], after["effective_from"])
        self.assertEqual(after["operation_type"], "inserted")
        self.assertTrue(after["text"])

    def test_article_45_substitution_has_adjacent_text_versions(self):
        before = record(self.data, "45_pre_86th")
        after = record(self.data, "45_v2")
        self.assertEqual(before["operation_type"], "baseline")
        self.assertTrue(before["text"])
        self.assertEqual(after["operation_type"], "substituted")
        self.assertTrue(after["text"])
        self.assertEqual(before["effective_to"], after["effective_from"])

    def test_article_174_has_exact_adjacent_provisional_intervals(self):
        original = record(self.data, "174_original_1949")
        replacement = record(self.data, "174_first_amendment_s8")
        self.assertEqual(original["effective_from"], "1950-01-26")
        self.assertEqual(original["effective_to"], "1951-06-18")
        self.assertEqual(original["operation_type"], "baseline")
        self.assertEqual(original["text"], (
            "174. (1) The House or Houses of the Legislature of the State shall be summoned "
            "to meet twice at least in every year, and six months shall not intervene between "
            "their last sitting in one session and the date appointed for their first sitting "
            "in the next session. (2) Subject to the provisions of clause (1), the Governor "
            "may from time to time— (a) summon the House or either House to meet at such time "
            "and place as he thinks fit; (b) prorogue the House or Houses; (c) dissolve the "
            "Legislative Assembly."
        ))
        self.assertEqual(replacement["effective_from"], "1951-06-18")
        self.assertIsNone(replacement["effective_to"])
        self.assertEqual(replacement["operation_type"], "substituted")
        self.assertEqual(replacement["text"], (
            "174. Sessions of the State Legislature, prorogation and dissolution.-(1) The "
            "Governor shall from time to time summon the House or each House of the Legislature "
            "of the State to meet at such time and place as he thinks fit, but six months shall "
            "not intervene between its last sitting in one session and the date appointed for "
            "its first sitting in the next session. (2) The Governor may from time to time- "
            "(a) prorogue the House or either House; (b) dissolve the Legislative Assembly."
        ))
        self.assertEqual(original["effective_to"], replacement["effective_from"])
        self.assertEqual(original["verification_status"], "verified")
        self.assertEqual(replacement["verification_status"], "verified")
        self.assertEqual(original["evidence_coverage"]["verified_through"], "1951-06-17")
        self.assertEqual(replacement["evidence_coverage"]["verified_through"], "2026-05-01")
        self.assertTrue(original["evidence_coverage"]["source_references"])
        self.assertTrue(replacement["evidence_coverage"]["source_references"])

    def test_article_174_exact_boundary_and_primary_source_provenance(self):
        original = record(self.data, "174_original_1949")
        replacement = record(self.data, "174_first_amendment_s8")
        # Half-open intervals: the old text ends exclusively when the substitute begins.
        boundary = "1951-06-18"
        self.assertFalse(original["effective_from"] <= boundary < original["effective_to"])
        self.assertTrue(replacement["effective_from"] <= boundary)
        self.assertEqual(
            original["source_reference"]["commencement_evidence"]["effective_date"],
            "1950-01-26",
        )
        self.assertEqual(
            original["source_reference"]["end_boundary_evidence"]["effective_date"],
            boundary,
        )
        self.assertIn("PDF p. 106", original["source_reference"]["page_or_locator"])
        self.assertIn("printed p. 89", original["source_reference"]["page_or_locator"])
        self.assertIn("316dae4a42e11ccab825e47b495a8bf2ff0bebbb8877cfe61ba0756c19d1e9c9",
                      replacement["source_reference"]["source_document"])
        self.assertIn("Section 8, PDF p. 4", replacement["source_reference"]["page_or_locator"])
        self.assertEqual(
            replacement["source_reference"]["commencement_evidence"]["effective_date"],
            boundary,
        )
        self.assertEqual(
            replacement["source_reference"]["supporting_current_text_evidence"]["snapshot_date"],
            "2026-05-01",
        )
        self.assertEqual(original["evidence_coverage"]["source_references"][-1]["page_or_locator"],
                         "Article 174 footnote 1, PDF p. 111.")
        replacement_claims = " ".join(ref["claim"] for ref in replacement["evidence_coverage"]["source_references"])
        self.assertIn("all constitutional amendments through the 106th Amendment Act", replacement_claims)
        self.assertIn("Section 8 directs substitution", replacement_claims)
        self.assertIn("2026-05-01", replacement_claims)
        self.assertIn("Gazette facsimile", replacement["verification_notes"])
        self.assertIn("assent record", replacement["verification_notes"])
        self.assertIn("Gazette facsimile", original["verification_notes"])
        self.assertIn("assent record", original["verification_notes"])

    def test_rejects_invalid_calendar_date(self):
        record(self.data, "21A_v1")["effective_from"] = "2010-02-30"
        self.assert_error(self.data, "invalid date")

    def test_rejects_overlapping_intervals(self):
        record(self.data, "21A_pre_86th")["effective_to"] = "2010-04-02"
        self.assert_error(self.data, "overlapping intervals")

    def test_rejects_invalid_interval_boundaries(self):
        record(self.data, "21A_pre_86th")["effective_to"] = "1950-01-26"
        self.assert_error(self.data, "must be later than effective_from")
        self.data = copy.deepcopy(DATASET)
        record(self.data, "21A_pre_86th")["effective_to"] = "2010-03-31"
        self.assert_error(self.data, "gap between")

    def test_rejects_duplicate_version_ids(self):
        record(self.data, "45_v2")["version_id"] = "21A_v1"
        self.assert_error(self.data, "duplicate version_id")

    def test_rejects_missing_or_malformed_source_references(self):
        record(self.data, "21A_v1")["source_reference"].pop("source_document")
        self.assert_error(self.data, "source_document")
        self.data = copy.deepcopy(DATASET)
        record(self.data, "45_v2")["source_reference"]["commencement_evidence"]["page_or_locator"] = " "
        self.assert_error(self.data, "page_or_locator")

    def test_commencement_evidence_date_must_match_interval_start(self):
        record(self.data, "21A_v1")["source_reference"]["commencement_evidence"]["effective_date"] = "2010-04-02"
        self.assert_error(self.data, "does not match interval boundary")

    def test_rejects_invalid_text_and_provision_status_combinations(self):
        record(self.data, "21A_pre_86th")["text"] = "invented text"
        self.assert_error(self.data, "not_in_force requires null text")
        self.data = copy.deepcopy(DATASET)
        record(self.data, "45_pre_86th")["text"] = None
        self.assert_error(self.data, "in_force requires non-empty text")

    def test_accepts_and_checks_omission_state(self):
        omitted = copy.deepcopy(record(self.data, "45_v2"))
        omitted.update({
            "version_id": "45_omitted",
            "text": None,
            "effective_from": "2020-01-01",
            "effective_to": None,
            "operation_type": "omitted",
            "provision_status": "omitted",
            "source_amendment": {
                "amendment_number": 999,
                "title": "Test Amendment",
                "act_date": "2019-01-01"
            },
            "source_section": "section 1"
        })
        omitted["source_reference"]["commencement_evidence"]["effective_date"] = "2020-01-01"
        omitted["source_reference"]["commencement_evidence"]["source_document"] = "test Act"
        omitted["source_reference"]["commencement_evidence"]["page_or_locator"] = "section 1"
        self.data["records"].remove(record(self.data, "45_v2"))
        predecessor = record(self.data, "45_pre_86th")
        predecessor["effective_to"] = "2020-01-01"
        predecessor["source_reference"]["end_boundary_evidence"]["effective_date"] = "2020-01-01"
        self.data["records"].append(omitted)
        self.assertEqual(validate_dataset(self.data), [])
        omitted["operation_type"] = "substituted"
        self.assert_error(self.data, "omitted requires null text and operation_type omitted")

    def test_dataset_level_schema_rejects_missing_metadata(self):
        del self.data["coverage_note"]
        self.assert_error(self.data, "coverage_note")

    def test_schema_file_is_dataset_schema(self):
        schema = json.loads(DATASET_SCHEMA.read_text(encoding="utf-8"))
        self.assertIn("records", schema["properties"])
        self.assertEqual(schema["properties"]["records"]["items"]["$ref"], "article_version.schema.json")

    def test_legacy_records_without_evidence_coverage_remain_valid(self):
        self.assertEqual(validate_dataset(self.data), [])

    def test_validates_evidence_coverage_date_and_provenance(self):
        row = record(self.data, "21A_v1")
        row["evidence_coverage"] = {
            "verified_through": "2026-05-01",
            "source_references": [{
                "source_document": "Synthetic fixture only",
                "page_or_locator": "page 1",
                "claim": "Synthetic coverage claim; not legal evidence.",
            }],
        }
        self.assertEqual(validate_dataset(self.data), [])
        row["evidence_coverage"]["verified_through"] = "2026-02-30"
        self.assert_error(self.data, "invalid date")

    def test_rejects_coverage_before_legal_start_or_at_exclusive_end(self):
        row = record(self.data, "21A_v1")
        row["evidence_coverage"] = {
            "verified_through": "2010-03-31",
            "source_references": [{
                "source_document": "Synthetic fixture only",
                "page_or_locator": "page 1",
                "claim": "Synthetic coverage claim; not legal evidence.",
            }],
        }
        self.assert_error(self.data, "before effective_from")
        self.data = copy.deepcopy(DATASET)
        row = record(self.data, "21A_v1")
        row["effective_to"] = "2026-05-01"
        row["evidence_coverage"] = {
            "verified_through": "2026-05-01",
            "source_references": [{
                "source_document": "Synthetic fixture only",
                "page_or_locator": "page 1",
                "claim": "Synthetic coverage claim; not legal evidence.",
            }],
        }
        self.assert_error(self.data, "before exclusive effective_to")

    def test_rejects_missing_or_malformed_evidence_coverage_provenance(self):
        row = record(self.data, "21A_v1")
        row["evidence_coverage"] = {"verified_through": "2026-05-01", "source_references": []}
        self.assert_error(self.data, "array is shorter than minItems")
        row["evidence_coverage"]["source_references"] = [{
            "source_document": "Synthetic fixture only", "page_or_locator": "page 1", "claim": " "
        }]
        self.assert_error(self.data, "claim must be non-empty")


if __name__ == "__main__":
    unittest.main()
