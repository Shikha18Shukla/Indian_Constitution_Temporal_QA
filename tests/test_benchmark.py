"""Benchmark schema and gold-evidence validation tests; no network or system calls."""

from __future__ import annotations

import copy
import json
import sqlite3
import unittest
from pathlib import Path

from benchmark.validate_benchmark import DATA_PATH, validate_benchmark


class BenchmarkValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = json.loads(Path(DATA_PATH).read_text(encoding="utf-8"))

    def test_dataset_passes_schema_and_semantic_validation(self):
        self.assertEqual(validate_benchmark(self.dataset), [])

    def test_static_index_snapshot_provenance_matches_index_metadata(self):
        index_path = Path(__file__).resolve().parents[1] / self.dataset["corpus_provenance"]["index_path"]
        with sqlite3.connect(f"file:{index_path}?mode=ro", uri=True) as conn:
            index_metadata = dict(conn.execute("SELECT key, value FROM metadata"))
        self.assertEqual(self.dataset["corpus_provenance"]["corpus_snapshot"], index_metadata["corpus_snapshot"])
        self.assertEqual(int(self.dataset["corpus_provenance"]["chunk_count"]), int(index_metadata["chunk_count"]))

    def test_article_19_gold_excerpts_are_exact_index_substrings(self):
        index_path = Path(__file__).resolve().parents[1] / self.dataset["corpus_provenance"]["index_path"]
        question = next(q for q in self.dataset["questions"] if q["question_id"] == "Q002")
        with sqlite3.connect(f"file:{index_path}?mode=ro", uri=True) as conn:
            indexed = {
                row[0]: row[1]
                for row in conn.execute("SELECT chunk_id, chunk_text FROM chunks")
            }
        for evidence in question["gold_evidence"]:
            self.assertIn(evidence["evidence_text"], indexed[evidence["chunk_id"]])

    def test_duplicate_question_ids_are_rejected(self):
        data = copy.deepcopy(self.dataset)
        data["questions"].append(copy.deepcopy(data["questions"][0]))
        self.assertTrue(any("duplicate question_id" in error for error in validate_benchmark(data)))

    def test_missing_required_field_is_rejected(self):
        data = copy.deepcopy(self.dataset)
        del data["questions"][0]["question"]
        self.assertTrue(any("missing required property 'question'" in error for error in validate_benchmark(data)))

    def test_invalid_calendar_date_is_rejected(self):
        data = copy.deepcopy(self.dataset)
        data["questions"][0]["reference_date"] = "2026-02-30"
        self.assertTrue(any("invalid calendar date" in error for error in validate_benchmark(data)))

    def test_gold_evidence_cannot_point_to_partially_verified_source(self):
        data = copy.deepcopy(self.dataset)
        question = data["questions"][0]
        question["source_references"][0]["verification_status"] = "partially_verified"
        errors = validate_benchmark(data)
        self.assertTrue(any("non-verified source" in error for error in errors))

    def test_gold_evidence_cannot_point_to_canonical_pilot(self):
        data = copy.deepcopy(self.dataset)
        question = data["questions"][0]
        question["source_references"][0]["source_type"] = "canonical_pilot"
        errors = validate_benchmark(data)
        self.assertTrue(any("canonical pilot records cannot be gold" in error for error in errors))

    def test_pending_historical_questions_have_no_gold_answer(self):
        data = copy.deepcopy(self.dataset)
        question = next(q for q in data["questions"] if q["question_category"] == "historical_version")
        question["expected_answer"] = "unverified text"
        self.assertTrue(any("pending question must not contain expected_answer" in error for error in validate_benchmark(data)))

    def test_article_174_extension_has_twelve_traceable_questions(self):
        additions = [q for q in self.dataset["questions"] if q["question_id"] >= "Q021"]
        self.assertEqual(len(additions), 12)
        self.assertEqual({q["expected_version_id"] for q in additions if q["question_id"] in {"Q029", "Q030", "Q031"}}, {"174_original_1949", "174_first_amendment_s8"})
        self.assertTrue(all(q["source_references"] and q["expected_key_facts"] and q["evaluation_criteria"] for q in additions))

    def test_article_174_cutoff_is_an_explicit_supported_abstention(self):
        question = next(q for q in self.dataset["questions"] if q["question_id"] == "Q032")
        self.assertIsNone(question["expected_answer"])
        self.assertEqual(question["expected_temporal_status"], "evidence_coverage_exceeded")
        self.assertTrue(any(ref["source_type"] == "verified_canonical_record" for ref in question["source_references"]))
        self.assertEqual(validate_benchmark(self.dataset), [])

    def test_cutoff_abstention_cannot_have_a_substantive_gold_answer(self):
        data = copy.deepcopy(self.dataset)
        question = next(q for q in data["questions"] if q["question_id"] == "Q032")
        question["expected_answer"] = "Article 174 says ..."
        self.assertTrue(any("evidence-coverage abstention must have null expected_answer" in error for error in validate_benchmark(data)))

    def test_prospective_held_out_article174_dataset_is_schema_valid_and_covered(self):
        project_root = Path(__file__).resolve().parents[1]
        held_path = project_root / "benchmark" / "held_out_article174_questions.json"
        held = json.loads(held_path.read_text(encoding="utf-8"))
        self.assertEqual(validate_benchmark(held), [])
        self.assertEqual([q["question_id"] for q in held["questions"]], [f"Q{i:03d}" for i in range(33, 43)])
        self.assertFalse({q["question_id"] for q in held["questions"]} & {q["question_id"] for q in self.dataset["questions"]})
        self.assertNotIn("Q032", {q["question_id"] for q in held["questions"]})
        canonical = json.loads((project_root / "processed" / "canonical" / "article_versions_pilot.json").read_text(encoding="utf-8"))
        versions = {r["version_id"]: r for r in canonical["records"] if r["article_number"] == "174"}
        self.assertEqual({q["expected_version_id"] for q in held["questions"]}, set(versions))
        for question in held["questions"]:
            self.assertEqual(question["target_articles"], ["174"])
            record = versions[question["expected_version_id"]]
            self.assertEqual(record["verification_status"], "verified")
            refdate = question["reference_date"]
            self.assertGreaterEqual(refdate, record["effective_from"])
            self.assertTrue(record["effective_to"] is None or refdate < record["effective_to"])
            self.assertLessEqual(refdate, record["evidence_coverage"]["verified_through"])
            self.assertTrue(all(ref["verification_status"] == "verified" and ref["source_locator"] for ref in question["source_references"]))


if __name__ == "__main__":
    unittest.main()
