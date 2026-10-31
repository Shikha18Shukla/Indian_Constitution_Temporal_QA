"""Tests for benchmark dispatch and output persistence; no API calls are made."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from benchmark.run_benchmark import SYSTEMS, build_manifest, build_system_argv, run_benchmark
from benchmark.validate_benchmark import DATA_PATH


def _load_data():
    return json.loads(Path(DATA_PATH).read_text(encoding="utf-8"))


class BenchmarkRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_root = Path(self.temp_dir.name) / "runs"

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_mock(self, executor=None):
        return run_benchmark(output_root=self.output_root, mode="mocked", executor=executor)

    def test_pending_questions_are_skipped_with_ids_and_reasons(self):
        summary = self.run_mock(lambda _system, _question: {"status": "mocked"})
        self.assertEqual(summary["skipped_question_count"], 7)
        skipped = summary["skipped_question_ids_and_reasons"]
        self.assertEqual(len(skipped), 7)
        self.assertTrue(all("pending_source_verification" in row["reason"] for row in skipped))
        self.assertEqual(summary["counts"]["skipped"], 21)

    def test_identical_question_and_date_are_dispatched_to_each_system(self):
        calls = []

        def executor(system, question):
            calls.append((system, question["question_id"], question["question"], question["reference_date"]))
            return {"status": "mocked"}

        self.run_mock(executor)
        eligible = [q for q in _load_data()["questions"] if q["evaluation_status"] == "suitable_for_evaluation"]
        self.assertEqual(len(calls), len(eligible) * len(SYSTEMS))
        for q in eligible:
            passed = [row for row in calls if row[1] == q["question_id"]]
            self.assertEqual({row[0] for row in passed}, set(SYSTEMS))
            self.assertEqual({row[2] for row in passed}, {q["question"]})
            self.assertEqual({row[3] for row in passed}, {q["reference_date"]})

    def test_system_outputs_are_separate_and_keep_every_question_id(self):
        summary = self.run_mock(lambda _system, _question: {"status": "mocked"})
        run_dir = Path(summary["run_directory"])
        for system in SYSTEMS:
            path = run_dir / f"{system}.jsonl"
            self.assertTrue(path.is_file())
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(rows), 32)
            self.assertEqual({row["system"] for row in rows}, {system})
            self.assertEqual({row["question_id"] for row in rows}, {q["question_id"] for q in _load_data()["questions"]})

    def test_system_c_abstention_is_logged_and_not_counted_as_completed(self):
        def executor(system, _question):
            if system == "system_c":
                return {"status": "completed", "system_run_status": "abstained", "raw_answer": "abstain", "abstention_reason": "no verified version"}
            return {"status": "completed", "raw_answer": "mock"}

        summary = run_benchmark(output_root=self.output_root, mode="mocked", executor=executor)
        self.assertEqual(summary["per_system_counts"]["system_c"]["abstained"], 25)
        self.assertEqual(summary["per_system_counts"]["system_c"]["completed"], 0)
        rows = [json.loads(line) for line in (Path(summary["run_directory"]) / "system_c.jsonl").read_text(encoding="utf-8").splitlines()]
        eligible = [row for row in rows if row["status"] == "abstained"]
        self.assertEqual(len(eligible), 25)
        self.assertTrue(all(row["abstention_reason"] == "no verified version" for row in eligible))

    def test_article_174_cutoff_mock_abstention_has_specific_reason(self):
        summary = self.run_mock()
        rows = [json.loads(line) for line in (Path(summary["run_directory"]) / "system_c.jsonl").read_text(encoding="utf-8").splitlines()]
        row = next(item for item in rows if item["question_id"] == "Q032")
        self.assertEqual(row["status"], "abstained")
        self.assertEqual(row["abstention_reason"], "beyond_evidence_coverage")
        self.assertEqual(row["reference_date"], "2026-05-02")

    def test_failed_run_is_recorded_and_other_runs_continue(self):
        def executor(system, question):
            if system == "system_b" and question["question_id"] == "Q001":
                raise RuntimeError("mock failure")
            return {"status": "mocked"}

        summary = self.run_mock(executor)
        self.assertEqual(summary["counts"]["failed"], 1)
        rows = [json.loads(line) for line in (Path(summary["run_directory"]) / "system_b.jsonl").read_text(encoding="utf-8").splitlines()]
        failed = next(row for row in rows if row["question_id"] == "Q001")
        self.assertEqual(failed["status"], "failed")
        self.assertIn("mock failure", failed["error_reason"])

    def test_manifest_is_reproducible_for_same_benchmark_and_mode(self):
        data = _load_data()
        raw = Path(DATA_PATH).read_bytes()
        first = build_manifest(data, raw, "dry-run")
        second = build_manifest(data, raw, "dry-run")
        self.assertEqual(first, second)
        self.assertEqual(first["manifest_id"], second["manifest_id"])

    def test_dry_run_is_defaultable_and_never_calls_executor(self):
        def forbidden(*_args):
            raise AssertionError("dry-run called an executor")

        summary = run_benchmark(output_root=self.output_root, mode="dry-run", executor=forbidden)
        self.assertEqual(summary["counts"]["planned"], 75)
        self.assertEqual(summary["counts"]["skipped"], 21)
        self.assertEqual(summary["counts"]["completed"], 0)
        self.assertEqual(summary["counts"]["failed"], 0)
        for system in SYSTEMS:
            rows = [json.loads(line) for line in (Path(summary["run_directory"]) / f"{system}.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertTrue(all(row["execution_time_seconds"] == 0.0 for row in rows))

    def test_cli_mapping_preserves_question_and_reference_date(self):
        question = next(q for q in _load_data()["questions"] if q["question_id"] == "Q001")
        for system in SYSTEMS:
            argv = build_system_argv(system, question)
            self.assertEqual(argv[argv.index("--question") + 1], question["question"])
            self.assertEqual(argv[argv.index("--reference-date") + 1], question["reference_date"])
            self.assertEqual(argv[argv.index("--question-id") + 1], question["question_id"])


if __name__ == "__main__":
    unittest.main()

