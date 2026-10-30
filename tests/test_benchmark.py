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


if __name__ == "__main__":
    unittest.main()
