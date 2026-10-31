"""API contract tests use patched system results and never call Gemini."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

from systems.generation_settings import GenerationSettings
from systems.static_index import SQLiteVectorIndex
from systems.system_b import DEFAULT_INDEX_PATH
from systems.system_c import run_experiment as run_system_c
from systems.temporal_corpus import TemporalCorpus, load_temporal_corpus
from systems.temporal_index import TemporalArticleIndex
from webapp import app as web_api


class WebApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.history_path = Path(self.temp_dir.name) / "history.jsonl"
        self.history_patch = patch.object(web_api, "HISTORY_PATH", self.history_path)
        self.history_patch.start()

    def tearDown(self):
        self.history_patch.stop()
        self.temp_dir.cleanup()

    def test_health_reports_per_system_availability(self):
        with patch.object(web_api, "_health_systems", return_value={"A": True, "B": False, "C": True}), \
             patch.object(web_api, "_api_key_is_configured", return_value=True):
            result = web_api.health()
        self.assertEqual(result["status"], "degraded")
        self.assertFalse(result["all_systems_available"])
        self.assertEqual(result["systems_available"], {"A": True, "B": False, "C": True})

    def test_compare_runs_only_selected_systems_and_saves_actual_result_shape(self):
        calls = []

        def runner(system, question, reference_date, question_id):
            calls.append((system, question, reference_date, question_id))
            if system == "A":
                return {"run_status": "succeeded", "raw_answer": "Answer A", "retrieval_used": False}
            return {
                "run_status": "succeeded", "raw_answer": "Answer C [chunk-c1]",
                "retrieval_used": True, "temporal_filtering_used": True,
                "selected_version_ids": ["174_original_1949"],
                "effective_intervals": [{
                    "version_id": "174_original_1949", "effective_from": "1950-01-26",
                    "effective_to": "1951-06-18", "evidence_verified_through": "1951-06-17",
                }],
                "verification_statuses": [{"version_id": "174_original_1949", "status": "verified"}],
                "retrieved_chunks": [{
                    "chunk_id": "chunk-c1", "chunk_text": "Evidence text",
                    "source_document": "Constitution scan", "page_number": 106,
                    "article_number": "174", "source_locator": "PDF page 106",
                }],
                "generation_settings": {"max_output_tokens": 1024},
            }

        request_data = {
                "question": "What powers did the Governor have under Article 174?",
                "reference_date": "1951-02-01",
                "systems": ["A", "C"],
            }
        with patch.object(web_api, "_run_selected_system", side_effect=runner):
            payload = web_api.compare(web_api.CompareRequest.model_validate(request_data))
        self.assertEqual([call[0] for call in calls], ["A", "C"])
        self.assertTrue(all(call[1] == payload["question"] for call in calls))
        self.assertTrue(all(call[2] == payload["reference_date"] for call in calls))
        self.assertEqual(payload["systems"]["A"]["answer"], "Answer A")
        self.assertEqual(payload["systems"]["A"]["retrieved_evidence"], [])
        self.assertEqual(payload["systems"]["C"]["selected_version_id"], "174_original_1949")
        self.assertEqual(payload["systems"]["C"]["evidence_coverage"][0]["verified_through"], "1951-06-17")
        self.assertEqual(payload["systems"]["C"]["citations"][0]["citation_id"], "chunk-c1")
        citation = payload["systems"]["C"]["citations"][0]
        self.assertTrue(citation["found_in_retrieved_evidence"])
        self.assertEqual(citation["evidence"]["chunk_text"], "Evidence text")
        self.assertEqual(citation["evidence"]["source_document"], "Constitution scan")
        self.assertEqual(web_api.history(limit=20)["count"], 1)

    def test_citation_ids_only_resolve_to_passages_in_generation_evidence(self):
        record = {
            "run_status": "succeeded",
            "raw_answer": "Supported [chunk-real] and unsupported [chunk-not-retrieved].",
            "context_chunks": [{"chunk_id": "chunk-real", "chunk_text": "Real retrieved wording."}],
            "retrieved_chunks": [
                {"chunk_id": "chunk-real", "chunk_text": "Real retrieved wording."},
                {"chunk_id": "chunk-retrieved-not-in-prompt", "chunk_text": "Retrieved but not sent."},
            ],
        }
        result = web_api._format_system_result("B", record, None, 0.1, None)
        self.assertEqual([item["citation_id"] for item in result["citations"]], [
            "chunk-real", "chunk-not-retrieved",
        ])
        self.assertTrue(result["citations"][0]["found_in_retrieved_evidence"])
        self.assertEqual(result["citations"][0]["evidence"]["chunk_text"], "Real retrieved wording.")
        self.assertFalse(result["citations"][1]["found_in_retrieved_evidence"])
        self.assertIsNone(result["citations"][1]["evidence"])

    def test_real_temporal_citation_ids_resolve_with_verified_version_metadata(self):
        source_corpus = load_temporal_corpus()
        cases = (
            ("1951-02-01", "temporal-b866c870df1726976fa0a678", "174_original_1949", "1951-06-17"),
            ("2026-05-01", "temporal-52328e6b839e4aae3dd6b302", "174_first_amendment_s8", "2026-05-01"),
        )
        for reference_date, expected_id, version_id, cutoff in cases:
            with self.subTest(version_id=version_id):
                eligible = source_corpus.select(reference_date, ["174"])
                self.assertTrue(all(row["verification_status"] == "verified" for row in eligible))
                index = TemporalArticleIndex(eligible, reference_date)
                hits = index.search("What does Article 174 provide?", top_k=5, article_numbers=["174"])
                hit = next(item for item in hits if item.metadata["chunk_id"] == expected_id)
                result = web_api._format_system_result("C", {
                    "run_status": "succeeded",
                    "raw_answer": f"Answer [{expected_id}]",
                    "selected_version_ids": [version_id],
                    "effective_intervals": [{
                        "version_id": version_id,
                        "effective_from": hit.metadata["effective_from"],
                        "effective_to": hit.metadata["effective_to"],
                        "evidence_verified_through": cutoff,
                    }],
                    "verification_statuses": [{"version_id": version_id, "status": "verified"}],
                    "retrieved_chunks": [{**hit.metadata, "retrieval_score": hit.score}],
                }, None, 0.1, None)
                citation = result["citations"][0]
                self.assertEqual(citation["citation_id"], expected_id)
                self.assertTrue(citation["found_in_retrieved_evidence"])
                self.assertEqual(citation["evidence"]["chunk_text"], hit.metadata["chunk_text"])
                self.assertEqual(citation["evidence"]["version_id"], version_id)
                self.assertEqual(citation["evidence"]["effective_from"], hit.metadata["effective_from"])
                self.assertEqual(citation["evidence"]["effective_to"], hit.metadata["effective_to"])
                self.assertEqual(citation["evidence"]["evidence_coverage"]["verified_through"], cutoff)

    def test_static_index_citation_has_real_page_and_article_but_no_temporal_fields(self):
        class LocalOnlyEmbedder:
            def embed_query(self, _question):
                # Exercise the frozen index search path without loading or
                # downloading its production embedding model.
                return [1.0] * 384

        index = SQLiteVectorIndex(DEFAULT_INDEX_PATH, embedder=LocalOnlyEmbedder())
        hits = index.search("What does Article 174 provide?", top_k=5)
        hit = next(item for item in hits if item.metadata["chunk_id"] == "chunk-b7bfe1824bde4311da347023")
        result = web_api._format_system_result("B", {
            "run_status": "succeeded", "raw_answer": "The provision states this [chunk-b7bfe1824bde4311da347023].",
            "retrieved_chunks": [{**hit.metadata, "retrieval_score": hit.score}],
            "context_chunks": [{**hit.metadata, "retrieval_score": hit.score}],
        }, None, 0.1, None)
        citation = result["citations"][0]
        evidence = citation["evidence"]
        self.assertTrue(citation["found_in_retrieved_evidence"])
        self.assertEqual(evidence["chunk_text"], hit.metadata["chunk_text"])
        self.assertEqual(evidence["source_document"], "raw/constitution/Constitution_of_India_2024.pdf")
        self.assertEqual(evidence["page_number"], 111)
        self.assertEqual(evidence["article_number"], "174")
        self.assertNotIn("version_id", evidence)
        self.assertNotIn("effective_from", evidence)
        self.assertNotIn("evidence_coverage", evidence)

    def test_missing_source_metadata_remains_absent_instead_of_being_invented(self):
        result = web_api._format_system_result("B", {
            "run_status": "succeeded", "raw_answer": "Claim [chunk-minimal].",
            "context_chunks": [{"chunk_id": "chunk-minimal", "chunk_text": "Only the passage is known."}],
        }, None, 0.1, None)
        evidence = result["citations"][0]["evidence"]
        self.assertEqual(evidence["chunk_text"], "Only the passage is known.")
        self.assertNotIn("source_document", evidence)
        self.assertNotIn("page_number", evidence)
        self.assertNotIn("article_number", evidence)

    def test_ineligible_temporal_version_never_reaches_citation_response(self):
        partial_record = {
            "article_number": "174", "version_id": "synthetic-partial-174",
            "text": "Synthetic wording must not be retrieved.",
            "effective_from": "1950-01-26", "effective_to": None,
            "source_amendment": None, "source_section": None,
            "source_reference": {"source_document": "synthetic test fixture", "page_or_locator": "fixture"},
            "evidence_coverage": {"verified_through": "2026-05-01", "source_references": [{
                "source_document": "synthetic test fixture", "page_or_locator": "fixture", "claim": "test only",
            }]},
            "operation_type": "baseline", "verification_status": "partially_verified",
            "provision_status": "in_force",
        }
        corpus = TemporalCorpus("synthetic-citation-test", (partial_record,))
        result = run_system_c(
            "test-ineligible-citation", "What does Article 174 provide?", "2020-01-01",
            GenerationSettings(), "not-used", corpus,
            generate=lambda *_: self.fail("generator must not receive ineligible evidence"),
            output_path=Path(self.temp_dir.name) / "system_c.jsonl",
        )
        api_result = web_api._format_system_result("C", result, None, 0.1, None)
        self.assertEqual(api_result["status"], "abstained")
        self.assertEqual(api_result["abstention_reason"], "no_verified_legal_version")
        self.assertEqual(api_result["selected_version_ids"], [])
        self.assertEqual(api_result["retrieved_evidence"], [])
        self.assertEqual(api_result["citations"], [])
        self.assertNotIn("Synthetic wording must not be retrieved.", json.dumps(api_result))

    def test_compare_preserves_system_c_abstention(self):
        record = {
            "run_status": "abstained", "raw_answer": "Insufficient verified temporal evidence.",
            "abstention_reason": "beyond_evidence_coverage", "retrieval_used": False,
            "temporal_filtering_used": True, "selected_version_ids": [],
        }
        with patch.object(web_api, "_run_selected_system", return_value=record):
            payload = web_api.compare(web_api.CompareRequest.model_validate({
                "question": "What did Article 174 provide?", "reference_date": "2026-05-02", "systems": ["C"],
            }))
        result = payload["systems"]["C"]
        self.assertEqual(result["status"], "abstained")
        self.assertEqual(result["abstention_reason"], "beyond_evidence_coverage")

    def test_compare_preserves_errors_instead_of_substituting_answer(self):
        with patch.object(web_api, "_run_selected_system", side_effect=RuntimeError("network unavailable")):
            payload = web_api.compare(web_api.CompareRequest.model_validate({
                "question": "Question?", "reference_date": "2020-01-01", "systems": ["A"],
            }))
        result = payload["systems"]["A"]
        self.assertEqual(result["status"], "failed")
        self.assertIsNone(result["answer"])
        self.assertEqual(result["error"], "network unavailable")

    def test_request_validation_rejects_invalid_date_duplicate_and_empty_systems(self):
        base = {"question": "Question?", "reference_date": "2020-01-01", "systems": ["A"]}
        invalid_date = {**base, "reference_date": "2020-02-30"}
        duplicate = {**base, "systems": ["A", "A"]}
        empty = {**base, "systems": []}
        for payload in (invalid_date, duplicate, empty):
            with self.subTest(payload=payload), self.assertRaises(ValidationError):
                web_api.CompareRequest.model_validate(payload)

    def test_http_routes_are_registered(self):
        paths = {route.path for route in web_api.app.routes}
        self.assertIn("/api/health", paths)
        self.assertIn("/api/compare", paths)
        self.assertIn("/api/history", paths)


if __name__ == "__main__":
    unittest.main()
