# Evaluation benchmark — initial version

This folder holds the versioned, traceable question set for comparing System A (Base LLM), System B (Static RAG), and System C (Temporal RAG). Each system receives the same `question` and `reference_date` from this file. The explicit `evaluation_status` controls inclusion; `verification_status` continues to describe evidence readiness.

## Contents and validation

- `schema.json` describes the dataset envelope, question records, gold evidence, and provenance references.
- `questions.json` contains the original 20 questions unchanged plus the 12-question Article 174 extension. The extension is benchmark version `indian-constitution-temporal-qa-article174-v2`.
- `validate_benchmark.py` applies the local schema subset plus semantic checks: unique question IDs and source IDs, valid calendar dates, verified evidence provenance for gold answers, no partially verified pilot records as gold, verified canonical coverage evidence only when it matches the canonical record, and explicit evidence-coverage abstention expectations.
- `run_benchmark.py` plans or executes the same selected questions against A, B, and C, writing per-system JSONL plus manifest and summary files.
- `../tests/test_benchmark.py` covers valid data, duplicate IDs, missing fields, invalid dates, unsupported gold evidence, and pending historical answers.
- `../tests/test_benchmark_runner.py` covers dispatch, skipping, failure, abstention, output separation, manifest identity, and dry-run behavior.

Run from the repository root:

```powershell
python benchmark/validate_benchmark.py
python -m unittest discover -s tests -p "test_benchmark.py" -v
python -m unittest discover -s tests -p "test_benchmark_runner.py" -v
```

The validator uses Python's standard library; it does not make network requests, call an LLM, or mutate the corpus. A pass is a data/software check and does not replace legal-source review.

## Run the benchmark

Dry-run is the default and does not launch any system:

```powershell
python benchmark/run_benchmark.py --dry-run
```

Mocked mode exercises orchestration without Gemini calls. System A and B outcomes are labeled `mocked`; System C checks actual verified-version eligibility and logs abstention when no eligible version exists. This mode does not perform RAG retrieval or claim substantive answers:

```powershell
python benchmark/run_benchmark.py --mocked
```

Live calls require the explicit `--live` option:

```powershell
python benchmark/run_benchmark.py --live
```

Each run gets a unique execution directory under `results/benchmark_runs/`, grouped under a deterministic manifest ID. It contains `manifest.json`, `summary.json`, `skipped_questions.json`, and separate `system_a.jsonl`, `system_b.jsonl`, and `system_c.jsonl` files. Every system file records every benchmark ID: suitable questions are planned/run, and pending questions are explicitly marked skipped with a reason. Failures are persisted and do not stop remaining dispatches. A System C abstention is counted as `abstained`, never `completed`.

The runner selects only `evaluation_status: "suitable_for_evaluation"`. Pending questions remain in each output as skipped and appear with IDs and reasons in the summary. The current benchmark has 32 questions: 25 selected and 7 pending/skipped (21 skipped system-runs across three systems). The original pilot’s Q001–Q020 and its 13/7 eligibility split are unchanged; the 12 Article 174 additions are source-verified and suitable for evaluation preparation.

Manifest identity is reproducible for the same benchmark bytes, run mode, selection, system order, and runner version. Actual execution IDs and timestamps differ between runs. The manifest records the benchmark SHA-256 and static corpus snapshot, but excludes API keys and other secrets.

## Categories and counts

| Category | Prepared | Suitable for evaluation preparation | Pending source verification |
|---|---:|---:|---:|
| Direct Article lookup | 11 | 11 | 0 |
| Constitutional interpretation/reasoning (text-constrained) | 2 | 2 | 0 |
| Amendment-related | 4 | 4 | 0 |
| Historical-version | 8 | 4 | 4 |
| Effective-date | 5 | 2 | 3 |
| Multi-Article | 2 | 2 | 0 |
| **Total** | **32** | **25** | **7** |

The project-wide planning goal remains approximately **209** questions. The 32 prepared here are an evidence-backed starting set, not a quota. No category allocation for the remaining 177 questions is fixed, and questions should be added only when suitable sources and gold evidence are available. “Suitable for evaluation preparation” means the current answer/evidence has a checked source record in this repository; it does not mean the benchmark or systems are validated for a formal study.

`questions.json` records the SQLite `corpus_snapshot` value `6bb6c11f1d96dba6041ed6657a0306bc0c67c7b0095b7fa80407b3cf2add1424`, along with index path, chunk count, and embedding model. Article 19 gold evidence uses exact substrings of the indexed passages, including amendment footnote markers. The index stores two em dash glyphs in surrounding Article 19 text as U+FFFD; those damaged characters are excluded from excerpts rather than silently normalized. The indexed source text is not rewritten.

## Source and temporal rules

The current-text questions cite the local Constitution PDF, whose cover identifies the snapshot as of 1 May 2026, and preserve indexed chunk IDs plus PDF page locators. Article text questions concern that snapshot only. The local PDF's extraction and index may normalize line breaks and typography; exact quotations should be checked against the PDF page image before publication or legal reliance.

Amendment questions cite the local two-page 86th Amendment Act PDF and its sections. Its `[12th December, 2002.]` title date is recorded only as the Act's printed date. Section 1(2) delegates appointment of commencement to a Central Government Gazette notification. The Gazette evidence for S.O. 427(E) distinguishes:

- notification date: 16 February 2010;
- Gazette issue/publication date: 19 February 2010;
- appointed commencement date: 1 April 2010.

The official Gazette PDF is cited by URL and notification number, but its text and page locator have not been checked from a local archived copy. Therefore Q012–Q014 deliberately have null answer keys and no gold evidence. Do not collapse these three dates or infer commencement from the Act title. Populate those answers only after inspecting and archiving the source.

## Historical questions and System C

The Article 21A and Article 45 pilot records remain `partially_verified`; Q015–Q018 therefore contain no expected answer, no gold evidence, and no expected version ID. Article 174 has two independently verified, bounded records: `174_original_1949` through 1951-06-17 and `174_first_amendment_s8` through 2026-05-01. Their source references identify pilot record IDs only as pending engineering/source leads; they are not gold evidence. System C must abstain for these dates under its verified-only selection rule. The current snapshot questions for Articles 21A and 45 do not upgrade or rely on those pilot records.

Historical questions Q029–Q031 use the verified Article 174 records and their primary-source locators. Q032 is an explicit expected System C abstention on 2026-05-02 because evidence coverage ends 2026-05-01; its null answer key is intentional and is not a claim that Article 174 ceased to be legally in force. The validator checks its cutoff evidence against the verified canonical record. Inserted provisions require a verified prior not-in-force state. Do not populate expected historical wording from parser output or a partially verified pilot record.

## Initial evidence scope and limitations

- Q001–Q007 use Constitution snapshot text. Reasoning questions are deliberately constrained to what the cited clauses say; they do not require case-law doctrine.
- Q008–Q011 use text in the local 86th Amendment Act.
- Q012–Q014 identify notification, Gazette publication, and commencement date concepts but are pending primary-source review; they are not scored questions.
- Q015–Q018 are blocked historical questions, not scored questions.
- Q019–Q020 are narrow comparisons of current snapshot text.

The benchmark's `verification_status` is question-level readiness. `gold_evidence[].verification_status` and `source_references[].verification_status` retain evidence/source status separately. A record marked `verified` is still limited to the scope and locator noted in its source reference. Review especially source snapshot identity, exact page-image typography, Gazette page locator, and the completeness of Article 19(1)'s indexed adjacent passages before using scores in a publication. The seven pending questions remain unchanged: three Gazette date questions and four historical-version questions for Articles 21A and 45, blocked by partially verified records.


## Article 174 extension

Q021–Q023 ask about the original wording and Governor powers as of 1951-06-17, using the visually inspected 1949 Constitution scan (PDF p. 106, printed p. 89). Q024–Q026 cover the six-month interval rule, Governor powers, and full replacement wording in the official 2026-05-01 consolidated edition (PDF p. 111). Q027–Q028 test the Section 8 substitution and its annotated effective date; Q029–Q031 test the original/ replacement boundary and the evidence-supported dates. Q032 deliberately expects System C to abstain on 2026-05-02: the replacement record has an open legal end but evidence coverage only through 2026-05-01. It has no substantive gold answer.

The benchmark schema now permits `expected_key_facts` and `evaluation_criteria`; `verified_historical_version` identifies bounded Article 174 selections, and `evidence_coverage_exceeded` identifies the explicit abstention expectation. Gold excerpts for the two Article 174 versions link to verified source records. A dedicated `verified_canonical_record` reference is accepted only when the validator confirms its version ID, verified status, and exact evidence cutoff in the canonical dataset. The canonical record is not used as a substitute for the original/Act/consolidated legal sources.

The static index snapshot remains `6bb6c11f1d96dba6041ed6657a0306bc0c67c7b0095b7fa80407b3cf2add1424`; this extension does not rebuild or alter the index. Historical Article 174 source excerpts cite the original Constitution, First Amendment Act, and official consolidated edition. The index’s extracted Article 174 punctuation has replacement-character corruption in dash glyphs; the gold legal wording follows the visually inspected official page text and is not normalized to match damaged extraction.


## Development set and prospective held-out set

- **Development benchmark:** `questions.json`, Q001–Q032. Q001–Q020 were used in earlier pilots/failure analysis; Q021–Q032 were added after Article 174 version implementation and boundary testing. These are development/diagnostic cases, not held-out evidence.
- **Prospective held-out Article 174 set:** `held_out_article174_questions.json`, Q033–Q042. It contains ten new source-backed cases using only verified versions `174_original_1949` and `174_first_amendment_s8`. Dates are inside the version-specific legal intervals and inclusive evidence cutoffs. Q032's separate evidence-coverage abstention test is not repeated.

The Q033–Q042 file is separate and frozen before its first execution; it must not be used to tune prompts, retrieval or generation settings. It is **prospective, not a fully independent or blinded external set**: the Article 174 versions and boundary behavior were already developed and tested before its questions were authored. Do not describe results on it as fully independent confirmation.

The normal benchmark runner reads only `questions.json`, so it will not select or execute Q033–Q042. The held-out file can be validated separately with the existing schema/semantic validator:

```powershell
python benchmark/validate_benchmark.py benchmark/held_out_article174_questions.json
```

The category counts and eligibility totals above refer only to the development `questions.json`; the prospective set contains 10 verified questions (4 targeting the original version, 6 targeting the replacement). The static corpus snapshot and all experiment settings remain unchanged.
