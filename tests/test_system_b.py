"""System B tests use local PDFs, deterministic embeddings, and mocked Gemini."""

import json
from contextlib import redirect_stderr
import io
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import pymupdf as fitz

from systems.generation_settings import GenerationSettings
from systems.static_corpus import DocumentPage, chunk_pages, load_pdf_pages
from systems.static_index import SQLiteVectorIndex, build_index
from systems.system_a import GeminiResponse
from systems.system_b import (
    article_retrieval_diagnostics, build_static_prompt, prepare_static_prompt, run_experiment,
)


class TinyEmbedder:
    """Deterministic semantic stand-in: education/equality/federal topic axes."""

    def __init__(self):
        self.query_calls = []

    @staticmethod
    def vector(text):
        lowered = text.lower()
        return [
            1.0 if any(term in lowered for term in ("education", "school", "children", "provide", "compulsory")) else 0.0,
            1.0 if any(term in lowered for term in ("equality", "equal", "discrimination")) else 0.0,
            1.0 if any(term in lowered for term in ("federal", "union", "state")) else 0.0,
            0.1,
        ]

    def embed_documents(self, texts):
        return [self.vector(text) for text in texts]

    def embed_query(self, text):
        self.query_calls.append(text)
        return self.vector(text)


class SystemBTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.index_path = self.root / "index.sqlite3"
        self.output_path = self.root / "runs.jsonl"
        self.encoder = TinyEmbedder()
        self.pages = [
            DocumentPage(
                "raw/constitution/test.pdf", "constitution", 33,
                "2[21A. Right to education.—The State shall provide free and compulsory education to all children of the age of six to fourteen years in such manner as the State may, by law, determine.]",
                "a" * 64,
            ),
            DocumentPage(
                "raw/constitution/test.pdf", "constitution", 37,
                "14. Equality before law.—The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.",
                "a" * 64,
            ),
            DocumentPage(
                "raw/constitution/test.pdf", "constitution", 40,
                "19. Protection of freedoms.—(1) All citizens shall have the right— (a) to freedom of speech and expression; (b) to assemble peaceably and without arms; (c) to form associations; (d) to move freely throughout India.",
                "a" * 64,
            ),
            DocumentPage(
                "raw/constitution/test.pdf", "constitution", 41,
                "(e) to reside and settle in any part of India; (f) omitted; (g) to practise any profession or carry on any occupation, trade or business. (2) reasonable restrictions apply.",
                "a" * 64,
            ),
            DocumentPage(
                "raw/constitution/test.pdf", "constitution", 42,
                "21. Protection of life and personal liberty.—No person shall be deprived of life or personal liberty except according to procedure established by law.",
                "a" * 64,
            ),
            DocumentPage(
                "raw/amendments/086_test.pdf", "amendment_act", 2,
                "Section 2. Insertion of new article—Free and compulsory education for children.",
                "b" * 64,
            ),
            DocumentPage(
                "raw/amendments/042_test.pdf", "amendment_act", 6,
                "The State shall encourage education in technical institutions and improve industrial training.",
                "d" * 64,
            ),
            DocumentPage(
                "raw/constitution/test.pdf", "constitution", 54,
                "2[45. Provision for early childhood care and education.—The State shall endeavour to provide care.",
                "a" * 64,
            ),
        ]
        self.snapshot = "c" * 64
        self.chunks = chunk_pages(self.pages, self.snapshot)
        build_index(
            self.index_path, self.chunks, self.encoder, "test-embedding-model",
            self.snapshot,
            [{"source_document": p.source_document, "sha256": p.source_sha256} for p in self.pages],
            [],
        )
        self.index = SQLiteVectorIndex(self.index_path, self.encoder)

    def test_document_loading_preserves_pdf_page_and_notes_unextractable_documents(self):
        constitution = self.root / "constitution.pdf"
        amendments = self.root / "amendments"
        amendments.mkdir()
        amendment = amendments / "amendment.pdf"
        scanned = amendments / "scanned.pdf"
        doc = fitz.open()
        for page_num in range(32):
            page = doc.new_page()
            if page_num == 31:
                page.insert_text((72, 72), "21A. Right to education—Text on page thirty two.")
        doc.save(constitution)
        doc.close()
        doc = fitz.open()
        doc.new_page().insert_text((72, 72), "Section 2—Insertion of Article 21A.")
        doc.save(amendment)
        doc.close()
        doc = fitz.open()
        doc.new_page()
        doc.save(scanned)
        doc.close()

        pages, excluded, snapshot = load_pdf_pages(self.root, constitution, amendments)
        self.assertEqual([(p.source_document, p.page_number) for p in pages], [
            ("constitution.pdf", 32), ("amendments/amendment.pdf", 1),
        ])
        self.assertEqual(excluded[0]["source_document"], "amendments/scanned.pdf")
        self.assertEqual(len(snapshot), 64)

    def test_chunk_creation_preserves_metadata_and_stable_ids(self):
        first = chunk_pages(self.pages, self.snapshot)
        second = chunk_pages(self.pages, self.snapshot)
        self.assertEqual([item.chunk_id for item in first], [item.chunk_id for item in second])
        self.assertTrue(all(item.page_number in (2, 6, 33, 37, 40, 41, 42, 54) for item in first))
        self.assertEqual(first[0].source_document, "raw/constitution/test.pdf")
        self.assertTrue(first[0].document_id.startswith("doc-"))
        self.assertEqual(first[0].article_number, "21A")
        self.assertIn("PDF page 33", first[0].source_locator)
        self.assertEqual(first[0].corpus_snapshot, self.snapshot)
        article_45 = next(item for item in first if item.article_number == "45")
        self.assertEqual(article_45.section_or_heading, "Provision for early childhood care and education")

    def test_article_metadata_continues_across_page_breaks(self):
        pages = [
            DocumentPage("constitution.pdf", "constitution", 33,
                         "21A. Right to education.—The State shall provide free and compulsory education.", "a" * 64),
            DocumentPage("constitution.pdf", "constitution", 34,
                         "to all children of the age of six to fourteen years.", "a" * 64),
        ]
        chunks = chunk_pages(pages, self.snapshot)
        self.assertEqual([chunk.article_number for chunk in chunks], ["21A", "21A"])
        self.assertTrue(all(chunk.section_or_heading == "Right to education" for chunk in chunks))

    def test_persistent_embedding_index_and_semantic_similarity_retrieval(self):
        with sqlite3.connect(self.index_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        self.assertEqual(count, len(self.chunks))
        self.assertEqual(self.index.metadata["embedding_model"], "test-embedding-model")
        hits = self.index.search("education for children", top_k=1)
        self.assertIn("education", hits[0].metadata["chunk_text"].lower())
        self.assertGreater(hits[0].dense_score, 0.9)

    def test_article_21a_question_retrieves_operative_article_ahead_of_amendment(self):
        hits = self.index.search("What does Article 21A provide?", top_k=5)
        self.assertEqual(hits[0].metadata["article_number"], "21A")
        self.assertEqual(hits[0].metadata["source_type"], "constitution")
        self.assertIn("free and compulsory education", hits[0].metadata["chunk_text"].lower())
        unrelated_amendment = next(
            hit for hit in hits if hit.metadata["source_document"].endswith("042_test.pdf")
        )
        self.assertLess(unrelated_amendment.score, hits[0].score)

    def test_exact_operative_phrase_retrieves_article_21a(self):
        hits = self.index.search("free and compulsory education", top_k=5)
        article = next(hit for hit in hits if hit.metadata["article_number"] == "21A")
        self.assertIn("free and compulsory education", article.metadata["chunk_text"].lower())
        self.assertEqual(article.metadata["source_document"], "raw/constitution/test.pdf")

    def test_explicit_article_14_prefers_the_operative_equality_provision(self):
        hits = self.index.search("What does Article 14 guarantee?", top_k=5)
        self.assertEqual(hits[0].metadata["article_number"], "14")
        self.assertTrue(hits[0].article_match)
        self.assertIn("equality before the law", hits[0].metadata["chunk_text"].lower())

    def test_article_19_returns_adjacent_chunks_covering_the_full_freedom_list(self):
        hits = self.index.search("What freedoms are protected under Article 19?", top_k=1)
        article_hits = [hit for hit in hits if hit.metadata["article_number"] == "19"]
        self.assertEqual(len(article_hits), 2)
        combined = " ".join(hit.metadata["chunk_text"] for hit in article_hits).lower()
        for clause in ("(a)", "(b)", "(c)", "(d)", "(e)", "(g)"):
            self.assertIn(clause, combined)
        self.assertEqual([hit.metadata["page_number"] for hit in article_hits], [40, 41])

    def test_article_21_and_21a_identifiers_are_not_confused(self):
        article_21 = self.index.search("What does Article 21 provide?", top_k=5)
        article_21a = self.index.search("What does Article 21A provide?", top_k=5)
        self.assertEqual(article_21[0].metadata["article_number"], "21")
        self.assertEqual(article_21a[0].metadata["article_number"], "21A")
        self.assertTrue(all(hit.metadata["article_number"] != "21A" for hit in article_21 if hit.article_match))
        self.assertTrue(all(hit.metadata["article_number"] != "21" for hit in article_21a if hit.article_match))

    def test_article_45_question_retrieves_the_consolidated_operative_provision(self):
        hits = self.index.search("What is the purpose of Article 45?", top_k=5)
        self.assertEqual(hits[0].metadata["article_number"], "45")
        self.assertTrue(hits[0].article_match)
        self.assertIn("shall endeavour", hits[0].metadata["chunk_text"].lower())

    def test_questions_without_an_explicit_article_keep_hybrid_retrieval(self):
        before = len(self.encoder.query_calls)
        hits = self.index.search("What rights protect children?", top_k=3)
        self.assertEqual(len(self.encoder.query_calls), before + 1)
        self.assertTrue(hits)
        self.assertTrue(all(not hit.article_match for hit in hits))

    def test_local_article_diagnostic_includes_text_metadata_and_scores(self):
        report = article_retrieval_diagnostics(self.index)
        self.assertEqual([item["question_id"] for item in report], ["Q002", "Q003", "Q004", "Q001", "Q005"])
        for item in report:
            first = item["retrieved_chunks"][0]
            self.assertIn("chunk_text", first)
            self.assertIn("article_number", first)
            self.assertIn("retrieval_score", first)
            self.assertIn("hybrid_score", first)
            self.assertIn("dense_score", first)

    def test_context_prompt_cites_chunks_and_says_reference_date_does_not_filter(self):
        hits = self.index.search("education for children", top_k=2)
        prompt = build_static_prompt("Question?", "1950-01-01", hits)
        self.assertIn(f"chunk_id={hits[0].metadata['chunk_id']}", prompt)
        self.assertIn("fixed static corpus", prompt)
        self.assertIn("not been selected or filtered by effective date", prompt)
        self.assertNotIn("historical version dataset", prompt)
        empty_prompt = build_static_prompt("Question?", "1950-01-01", [])
        self.assertIn("No passages were retrieved", empty_prompt)
        self.assertIn("context is insufficient", empty_prompt)

    def test_context_budget_keeps_whole_evidence_blocks_and_tracks_omissions(self):
        hits = self.index.search("education for children", top_k=3)
        _, _, full = prepare_static_prompt("Question?", "2020-01-01", hits, max_context_tokens=4000)
        first_block_budget = full["chunk_lengths"][0]["evidence_block_approx_tokens"]
        prompt, selected, diagnostics = prepare_static_prompt(
            "Question?", "2020-01-01", hits, max_context_tokens=first_block_budget,
        )
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].metadata["chunk_id"], hits[0].metadata["chunk_id"])
        self.assertEqual(diagnostics["omitted_chunk_ids"], [hit.metadata["chunk_id"] for hit in hits[1:]])
        self.assertIn(selected[0].metadata["chunk_text"], prompt)
        self.assertEqual(prompt.count(f"chunk_id={selected[0].metadata['chunk_id']}"), 1)
        self.assertGreaterEqual(diagnostics["retrieved_chunk_count"], diagnostics["included_chunk_count"])

        no_fit_prompt, no_fit, no_fit_diagnostics = prepare_static_prompt(
            "Question?", "2020-01-01", hits, max_context_tokens=1,
        )
        self.assertEqual(no_fit, [])
        self.assertEqual(len(no_fit_diagnostics["omitted_chunk_ids"]), len(hits))
        self.assertIn("No retrieved passages fit", no_fit_prompt)

    def test_no_date_filtering_context_logging_and_failure_logging(self):
        def generator(prompt, settings, api_key):
            return "Answer with evidence [" + self.index.search("education for children", 1)[0].metadata["chunk_id"] + "]"

        first = run_experiment(
            "Q1", "What is the right to education?", "1950-01-01",
            GenerationSettings("gemini-test", 0.0, 50), "key", self.index,
            top_k=1, generate=generator, output_path=self.output_path,
        )
        second_path = self.root / "runs2.jsonl"
        second = run_experiment(
            "Q1", "What is the right to education?", "2020-01-01",
            GenerationSettings("gemini-test", 0.0, 50), "key", self.index,
            top_k=1, generate=generator, output_path=second_path,
        )
        self.assertEqual(first["retrieved_chunks"], second["retrieved_chunks"])
        self.assertFalse(first["temporal_filtering_used"])
        self.assertEqual(first["retrieved_chunks"][0]["chunk_id"], first["source_metadata"][0]["chunk_id"])
        self.assertEqual(json.loads(self.output_path.read_text(encoding="utf-8")), first)
        self.assertEqual(first["attempt_count"], 1)
        self.assertEqual(first["final_status"], "succeeded")
        self.assertEqual(first["context_diagnostics"]["retrieved_chunk_count"], 1)
        self.assertEqual(first["context_diagnostics"]["prompt_length_characters"], len(first["prompt"]))
        self.assertGreaterEqual(first["context_diagnostics"]["retrieval_elapsed_seconds"], 0)
        self.assertGreaterEqual(first["context_diagnostics"]["generation_elapsed_seconds"], 0)

    def test_generation_diagnostics_are_secret_free_and_include_timings(self):
        output = io.StringIO()
        with redirect_stderr(output):
            result = run_experiment(
                "Q-LOG", "Education diagnostics question", "2020-01-01",
                GenerationSettings(), "do-not-log-this-key", self.index,
                top_k=2, max_context_tokens=4000,
                generate=lambda *_: "mock answer", output_path=self.output_path,
            )
        events = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual([event["event"] for event in events], [
            "system_b_generation_request_start", "system_b_generation_request_complete",
        ])
        start = events[0]
        self.assertEqual(start["retrieved_chunk_count"], 2)
        self.assertEqual(start["top_k"], 2)
        self.assertEqual(len(start["individual_chunk_lengths"]), 2)
        self.assertEqual(start["prompt_length_characters"], len(result["prompt"]))
        self.assertIn("retrieval_completed_at", start)
        self.assertIn("generation_started_at", start)
        self.assertIn("generation_elapsed_seconds", events[1])
        self.assertNotIn("do-not-log-this-key", output.getvalue())
        self.assertNotIn(result["prompt"], output.getvalue())

        with self.assertRaisesRegex(RuntimeError, "simulated Gemini failure"):
            run_experiment(
                "Q2", "Education question", "2020-01-01", GenerationSettings(), "key", self.index,
                generate=lambda *_: (_ for _ in ()).throw(RuntimeError("simulated Gemini failure")),
                output_path=self.output_path,
            )
        rows = [json.loads(line) for line in self.output_path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(rows[-1]["run_status"], "failed")
        self.assertEqual(rows[-1]["error_message"], "Gemini API request failed: simulated Gemini failure")

    def test_missing_api_key_is_logged_after_retrieval(self):
        with self.assertRaisesRegex(RuntimeError, "GEMINI_API_KEY is missing"):
            run_experiment(
                "Q3", "Education question", "2020-01-01", GenerationSettings(), None,
                self.index, output_path=self.output_path,
            )
        record = json.loads(self.output_path.read_text(encoding="utf-8").splitlines()[-1])
        self.assertEqual(record["run_status"], "failed")
        self.assertTrue(record["retrieved_chunks"])
        self.assertIn("GEMINI_API_KEY", record["error_message"])

    def test_system_b_uses_shared_default_and_environment_model_override(self):
        observed_models = []
        for model_name in ("gemini-3.5-flash-lite", "gemini-test-override"):
            with patch.dict(os.environ, {"GEMINI_MODEL_NAME": model_name}, clear=True):
                settings = GenerationSettings.from_environment()
            run_experiment(
                f"MODEL-{len(observed_models)}", "Education question", "2020-01-01",
                settings, "key", self.index,
                generate=lambda _prompt, passed_settings, _key: (
                    observed_models.append(passed_settings.model_name) or "mock answer"
                ),
                output_path=self.root / f"model-{len(observed_models)}.jsonl",
            )
        self.assertEqual(observed_models, ["gemini-3.5-flash-lite", "gemini-test-override"])

    def test_retried_success_appends_only_one_system_b_record(self):
        response = GeminiResponse("grounded answer", 3, [
            {"attempt": 1, "status_code": 503, "message": "UNAVAILABLE"},
            {"attempt": 2, "status_code": 504, "message": "DEADLINE_EXCEEDED"},
        ])
        result = run_experiment(
            "Q4", "Education question", "2020-01-01", GenerationSettings(), "key",
            self.index, generate=lambda *_: response, output_path=self.output_path,
        )
        lines = self.output_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        record = json.loads(lines[0])
        self.assertEqual(record["attempt_count"], 3)
        self.assertEqual(record["final_status"], "succeeded")
        self.assertEqual(len(record["error_details"]), 2)
        self.assertEqual(result["raw_answer"], "grounded answer")


if __name__ == "__main__":
    unittest.main()
