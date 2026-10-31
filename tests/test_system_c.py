"""System C tests use labelled synthetic verified records and mocked generation."""

import json
from pathlib import Path
import tempfile
import unittest

from systems.generation_settings import GenerationSettings
from systems.system_c import _temporal_abstention_reason, run_experiment
from systems.system_c import identify_article_numbers
from systems.temporal_corpus import (
    TemporalCorpus,
    load_temporal_corpus,
)
from systems.temporal_index import TemporalArticleIndex


def version(
    article="45", version_id="45_v1", text="45. Synthetic rule.",
    start="2000-01-01", end=None, status="verified", operation="baseline",
    provision_status="in_force", act_date=None, coverage_through="2099-12-31",
):
    source = {
        "source_document": f"SYNTHETIC TEST FIXTURE — {version_id}",
        "page_or_locator": "Synthetic fixture, paragraph 1; not legal evidence.",
        "commencement_evidence": {
            "source_document": "SYNTHETIC TEST FIXTURE — commencement",
            "page_or_locator": "Synthetic fixture boundary; not legal evidence.",
            "effective_date": start,
        },
    }
    if end:
        source["end_boundary_evidence"] = {
            "source_document": "SYNTHETIC TEST FIXTURE — end boundary",
            "page_or_locator": "Synthetic fixture boundary; not legal evidence.",
            "effective_date": end,
        }
    amendment = None
    section = None
    if operation in {"inserted", "substituted", "amended", "omitted"}:
        amendment = {
            "amendment_number": 999,
            "title": "Synthetic Amendment Act (test fixture only)",
            "act_date": act_date or "1999-01-01",
        }
        section = "Synthetic section (test fixture only)"
    return {
        "article_number": article,
        "version_id": version_id,
        "text": text,
        "effective_from": start,
        "effective_to": end,
        "source_amendment": amendment,
        "source_section": section,
        "source_reference": source,
        "evidence_coverage": {
            "verified_through": coverage_through,
            "source_references": [{
                "source_document": f"SYNTHETIC TEST FIXTURE — evidence coverage {version_id}",
                "page_or_locator": "Synthetic fixture, coverage note; not legal evidence.",
                "claim": "Synthetic fixture supports continuous coverage only through the stated test cutoff.",
            }],
        },
        "operation_type": operation,
        "verification_status": status,
        "verification_notes": "Synthetic test fixture; no legal-source verification is claimed.",
        "provision_status": provision_status,
    }


def corpus(*records):
    return TemporalCorpus("synthetic-system-c-test-fixture", tuple(records))


class RecordingEmbedder:
    def __init__(self):
        self.passages = []

    def embed_documents(self, texts):
        self.passages.extend(texts)
        return [[1.0, 0.0, 0.0] for _ in texts]

    def embed_query(self, text):
        return [1.0, 0.0, 0.0]


class SystemCTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.output_dir = Path(self.temp_dir.name)

    def test_selects_a_version_inside_its_effective_interval(self):
        rows = corpus(version(start="2000-01-01", end="2010-01-01"))
        selected = rows.select("2005-06-01", ["45"])
        self.assertEqual([item["version_id"] for item in selected], ["45_v1"])

    def test_excludes_version_before_effective_from(self):
        rows = corpus(version(start="2000-01-01"))
        self.assertEqual(rows.select("1999-12-31", ["45"]), [])

    def test_excludes_version_at_or_after_effective_to(self):
        rows = corpus(version(start="2000-01-01", end="2010-01-01"))
        self.assertEqual(rows.select("2010-01-01", ["45"]), [])
        self.assertEqual(rows.select("2010-01-02", ["45"]), [])

    def test_null_effective_to_is_open_ended(self):
        rows = corpus(version(start="2000-01-01", end=None))
        self.assertEqual([item["version_id"] for item in rows.select("2099-12-31", ["45"])], ["45_v1"])

    def test_legacy_verified_record_loads_but_is_ineligible_without_coverage(self):
        legacy = version()
        legacy.pop("evidence_coverage")
        rows = corpus(legacy)
        self.assertEqual(rows.select("2020-01-01", ["45"]), [])
        _, excluded = rows.select_with_exclusions("2020-01-01", ["45"])
        self.assertEqual(excluded[0]["exclusion_reason"], "missing_evidence_coverage")

    def test_open_legal_interval_is_eligible_through_inclusive_coverage_date_only(self):
        rows = corpus(version(end=None, coverage_through="2026-05-01"))
        self.assertEqual([r["version_id"] for r in rows.select("2026-05-01", ["45"])], ["45_v1"])
        self.assertEqual(rows.select("2026-05-02", ["45"]), [])
        _, excluded = rows.select_with_exclusions("2026-05-02", ["45"])
        self.assertEqual(excluded[0]["exclusion_reason"], "beyond_evidence_coverage")

    def test_finite_legal_end_remains_exclusive(self):
        row = version(start="2000-01-01", end="2010-01-01", coverage_through="2009-12-31")
        rows = corpus(row)
        self.assertEqual([r["version_id"] for r in rows.select("2009-12-31", ["45"])], ["45_v1"])
        self.assertEqual(rows.select("2010-01-01", ["45"]), [])
        _, excluded = rows.select_with_exclusions("2010-01-01", ["45"])
        self.assertEqual(excluded[0]["exclusion_reason"], "legal_interval_mismatch")

    def test_selects_correct_version_across_an_amendment_boundary(self):
        old = version("45", "45_old", "45. Old synthetic wording.", "2000-01-01", "2010-01-01")
        new = version(
            "45", "45_new", "45. New synthetic wording.", "2010-01-01", None,
            operation="substituted", act_date="2009-12-12",
        )
        rows = corpus(old, new)
        self.assertEqual([item["version_id"] for item in rows.select("2009-12-31", ["45"])], ["45_old"])
        self.assertEqual([item["version_id"] for item in rows.select("2010-01-01", ["45"])], ["45_new"])
        self.assertEqual(new["source_amendment"]["act_date"], "2009-12-12")
        self.assertEqual(new["effective_from"], "2010-01-01")

    def test_partially_verified_pilot_records_are_never_eligible(self):
        real_pilot = load_temporal_corpus()
        legacy_pilot_records = [row for row in real_pilot.records if row["article_number"] in {"21A", "45"}]
        self.assertEqual(len(legacy_pilot_records), 4)
        self.assertTrue(all(row["verification_status"] == "partially_verified"
                            for row in legacy_pilot_records))
        self.assertEqual(real_pilot.select("2020-01-01", ["21A"]), [])
        synthetic_partial = corpus(version(article="21A", version_id="partial", status="partially_verified"))
        self.assertEqual(synthetic_partial.select("2020-01-01", ["21A"]), [])

    def test_real_article_174_records_are_eligible_only_within_verified_coverage(self):
        real_pilot = load_temporal_corpus()
        article_174 = [row for row in real_pilot.records if row["article_number"] == "174"]
        self.assertEqual({row["version_id"] for row in article_174}, {
            "174_original_1949", "174_first_amendment_s8",
        })
        self.assertTrue(all(row["verification_status"] == "verified" for row in article_174))
        self.assertEqual({row["evidence_coverage"]["verified_through"] for row in article_174}, {
            "1951-06-17", "2026-05-01",
        })
        before = real_pilot.select("1951-06-17", ["174"])
        self.assertEqual([row["version_id"] for row in before], ["174_original_1949"])
        boundary = real_pilot.select("1951-06-18", ["174"])
        self.assertEqual([row["version_id"] for row in boundary], ["174_first_amendment_s8"])
        at_cutoff = real_pilot.select("2026-05-01", ["174"])
        self.assertEqual([row["version_id"] for row in at_cutoff], ["174_first_amendment_s8"])

        # Exercise the real temporal index on both sides of the amendment boundary
        # and at the replacement version's finite evidence cutoff; no generator/API.
        for reference_date, selected_id in (
            ("1951-06-17", "174_original_1949"),
            ("1951-06-18", "174_first_amendment_s8"),
            ("2026-05-01", "174_first_amendment_s8"),
        ):
            with self.subTest(reference_date=reference_date):
                eligible = real_pilot.select(reference_date, ["174"])
                index = TemporalArticleIndex(eligible, reference_date)
                hits = index.search("What does Article 174 provide?", article_numbers=["174"])
                self.assertTrue(hits)
                self.assertEqual({hit.metadata["version_id"] for hit in hits}, {selected_id})
                self.assertTrue(all(hit.metadata["verification_status"] == "verified" for hit in hits))

        calls = []
        beyond = run_experiment(
            "Q-ARTICLE-174-BEYOND-COVERAGE", "What does Article 174 provide?", "2026-05-02",
            GenerationSettings(), "test-key", real_pilot,
            generate=lambda *args: calls.append(args) or "must not run",
            output_path=self.output_dir / "article-174-beyond-coverage.jsonl",
        )
        self.assertEqual(calls, [])
        self.assertEqual(beyond["selected_version_ids"], [])
        self.assertEqual(beyond["retrieved_chunk_ids"], [])
        self.assertEqual(beyond["abstention_reason"], "beyond_evidence_coverage")
        self.assertEqual(beyond["run_status"], "abstained")

    def test_article_21a_and_45_records_keep_existing_temporal_exclusion(self):
        real_pilot = load_temporal_corpus()
        for article, reference_date in (("21A", "2026-05-01"), ("45", "2020-01-01")):
            with self.subTest(article=article):
                rows = [row for row in real_pilot.records if row["article_number"] == article]
                self.assertTrue(rows)
                self.assertTrue(all(row["verification_status"] == "partially_verified" for row in rows))
                self.assertTrue(all("evidence_coverage" not in row for row in rows))
                self.assertEqual(real_pilot.select(reference_date, [article]), [])

    def test_coverage_does_not_override_partially_verified_status(self):
        partial = version("21A", "partial-with-coverage", status="partially_verified")
        self.assertEqual(corpus(partial).select("2020-01-01", ["21A"]), [])
        self.assertEqual(_temporal_abstention_reason(
            corpus(partial).select_with_exclusions("2020-01-01", ["21A"])[1]
        ), "no_verified_legal_version")

    def test_assent_date_does_not_extend_the_effective_interval(self):
        inserted = version(
            "21A", "21A_fixture", "21A. Synthetic inserted text.",
            "2010-04-01", None, operation="inserted", act_date="2002-12-12",
        )
        rows = corpus(inserted)
        self.assertEqual(rows.select("2009-12-12", ["21A"]), [])
        self.assertEqual(rows.select("2010-04-01", ["21A"]), [inserted])

    def test_article_identifier_detection_preserves_inserted_suffix(self):
        self.assertEqual(identify_article_numbers("Compare Article 21 with Article 21A."), ["21", "21A"])

    def test_temporal_index_returns_only_input_eligible_versions(self):
        eligible = version("14", "14_verified", "14. Synthetic equality guarantee.")
        # This partially verified text is intentionally absent from index input.
        excluded = version("21A", "21A_partial", "UNVERIFIED SHOULD NEVER LEAK", status="partially_verified")
        selected = corpus(eligible, excluded).select("2020-01-01")
        index = TemporalArticleIndex(selected, "2020-01-01")
        hits = index.search("What does Article 14 guarantee?", article_numbers=["14"])
        self.assertEqual([hit.metadata["version_id"] for hit in hits], ["14_verified"])
        self.assertNotIn("UNVERIFIED SHOULD NEVER LEAK", " ".join(hit.metadata["chunk_text"] for hit in hits))

    def test_temporal_index_rejects_unverified_or_wrong_date_input(self):
        partial = version("21A", "partial", "Partial fixture text.", status="partially_verified")
        with self.assertRaisesRegex(ValueError, "refuses non-verified"):
            TemporalArticleIndex([partial], "2020-01-01")
        verified = version("45", "future", "Future fixture text.", start="2020-01-01")
        with self.assertRaisesRegex(ValueError, "outside reference date"):
            TemporalArticleIndex([verified], "2019-12-31")

    def test_temporal_index_rejects_missing_or_exceeded_coverage(self):
        missing = version("45", "missing-coverage", "45. Missing coverage.")
        missing.pop("evidence_coverage")
        with self.assertRaisesRegex(ValueError, "without evidence coverage"):
            TemporalArticleIndex([missing], "2020-01-01")
        bounded = version("45", "bounded", "45. Bounded coverage.", coverage_through="2020-01-01")
        with self.assertRaisesRegex(ValueError, "beyond evidence coverage"):
            TemporalArticleIndex([bounded], "2020-01-02")

    def test_extended_independent_coverage_allows_retrieval_only_through_new_cutoff(self):
        extended = version("14", "14_extended", "14. Synthetic verified evidence.",
                           coverage_through="2024-12-31")
        rows = corpus(extended)
        self.assertEqual(rows.select("2024-12-31", ["14"]), [extended])
        self.assertEqual(rows.select("2025-01-01", ["14"]), [])
        index = TemporalArticleIndex(rows.select("2024-12-31", ["14"]), "2024-12-31")
        hits = index.search("Article 14", article_numbers=["14"])
        self.assertTrue(hits)
        self.assertEqual(hits[0].metadata["evidence_coverage"], extended["evidence_coverage"])
        self.assertEqual(corpus(extended).select_with_exclusions("2025-01-01", ["14"])[1][0]["exclusion_reason"],
                         "beyond_evidence_coverage")

    def test_abstention_reason_distinguishes_temporal_exclusions(self):
        self.assertEqual(_temporal_abstention_reason([]), "no_verified_legal_version")
        legal_miss = version(start="2020-01-01")
        self.assertEqual(_temporal_abstention_reason(
            corpus(legal_miss).select_with_exclusions("2019-12-31", ["45"])[1]
        ), "legal_interval_mismatch")
        no_coverage = version()
        no_coverage.pop("evidence_coverage")
        self.assertEqual(_temporal_abstention_reason(
            corpus(no_coverage).select_with_exclusions("2020-01-01", ["45"])[1]
        ), "missing_evidence_coverage")
        old_coverage = version(coverage_through="2019-12-31")
        self.assertEqual(_temporal_abstention_reason(
            corpus(old_coverage).select_with_exclusions("2020-01-01", ["45"])[1]
        ), "beyond_evidence_coverage")

    def test_system_c_logs_coverage_abstentions_and_skips_generation(self):
        cases = [
            (version(start="2020-01-01"), "2019-12-31", "legal_interval_mismatch"),
            (version(version_id="no-coverage"), "2020-01-01", "missing_evidence_coverage"),
            (version(version_id="expired-coverage", coverage_through="2019-12-31"),
             "2020-01-01", "beyond_evidence_coverage"),
        ]
        for index, (candidate, reference_date, expected_reason) in enumerate(cases):
            with self.subTest(reason=expected_reason):
                if expected_reason == "missing_evidence_coverage":
                    candidate.pop("evidence_coverage")
                calls = []
                result = run_experiment(
                    f"Q-COVERAGE-{index}", "What does Article 45 provide?", reference_date,
                    GenerationSettings(), "test-key", corpus(candidate),
                    generate=lambda *args: calls.append(args) or "must not run",
                    output_path=self.output_dir / f"coverage-{index}.jsonl",
                )
                self.assertEqual(calls, [])
                self.assertEqual(result["run_status"], "abstained")
                self.assertEqual(result["abstention_reason"], expected_reason)
                self.assertEqual(result["selected_version_ids"], [])

    def test_abstains_without_verified_eligible_version_and_skips_generator(self):
        calls = []
        output = self.output_dir / "no-verified-runs.jsonl"
        result = run_experiment(
            "Q-PARTIAL", "What does Article 21A provide?", "2020-01-01",
            GenerationSettings(), "test-key", load_temporal_corpus(),
            generate=lambda *args: calls.append(args) or "must not run",
            output_path=output,
        )
        self.assertEqual(calls, [])
        self.assertTrue(result["abstention_status"])
        self.assertEqual(result["abstention_reason"], "no_verified_legal_version")
        self.assertEqual(result["selected_version_ids"], [])
        self.assertTrue(all(item["verification_status"] == "partially_verified"
                            for item in result["excluded_candidate_versions"]))
        logged = json.loads(output.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(logged["run_status"], "abstained")

    def test_in_force_version_with_null_text_abstains_without_current_text_fallback(self):
        not_in_force = version(
            "21A", "21A_not_in_force", None, "2000-01-01", "2010-01-01",
            operation="not_in_force", provision_status="not_in_force",
            coverage_through="2009-12-31",
        )
        output = self.output_dir / "not-in-force-runs.jsonl"
        calls = []
        result = run_experiment(
            "Q-NOT-IN-FORCE", "What does Article 21A provide?", "2005-01-01",
            GenerationSettings(), "test-key", corpus(not_in_force),
            generate=lambda *args: calls.append(args) or "must not run", output_path=output,
        )
        self.assertEqual(calls, [])
        self.assertEqual(result["abstention_reason"], "selected_version_is_not_in_force_or_has_no_text")
        self.assertEqual(result["retrieved_chunk_ids"], [])

    def test_verified_version_is_cited_and_only_eligible_text_reaches_generator(self):
        active = version("14", "14_verified", "14. VERIFIED synthetic equality guarantee.")
        partial = version("21A", "21A_partial", "PARTIAL TEXT MUST NOT REACH GENERATION",
                          status="partially_verified")
        output = self.output_dir / "verified-runs.jsonl"
        seen = []
        embedder = RecordingEmbedder()

        def generate(prompt, settings, api_key):
            seen.append(prompt)
            return "Synthetic answer [temporal-test-citation]"

        result = run_experiment(
            "Q-VERIFIED", "What does Article 14 guarantee?", "2020-01-01",
            GenerationSettings(), "test-key", corpus(active, partial), embedder=embedder,
            generate=generate, output_path=output,
        )
        self.assertEqual(len(seen), 1)
        self.assertIn("VERIFIED synthetic equality guarantee", seen[0])
        self.assertNotIn("PARTIAL TEXT MUST NOT REACH GENERATION", seen[0])
        self.assertIn(f"[{result['retrieved_chunk_ids'][0]}]", seen[0])
        self.assertIn("synthetic fixture", seen[0].lower())
        self.assertEqual(embedder.passages, [active["text"]])
        self.assertEqual(result["selected_version_ids"], ["14_verified"])
        self.assertEqual(result["verification_statuses"], [{"version_id": "14_verified", "status": "verified"}])
        self.assertTrue(result["retrieved_chunk_ids"])
        self.assertEqual(result["run_status"], "succeeded")

    def test_list_query_returns_all_chunks_for_the_retrieved_version(self):
        long_text = "19. Synthetic freedoms. " + " ".join(
            f"Clause ({letter}) grants a distinct protected freedom." for letter in "abcdefg"
        )
        eligible = version("19", "19_long", long_text)
        index = TemporalArticleIndex([eligible], "2020-01-01", chunk_size=80, overlap=10)
        hits = index.search("What freedoms are protected?", top_k=1)
        self.assertGreater(len(hits), 1)
        combined = " ".join(hit.metadata["chunk_text"] for hit in hits)
        for letter in "abcdefg":
            self.assertIn(f"({letter})", combined)


if __name__ == "__main__":
    unittest.main()
