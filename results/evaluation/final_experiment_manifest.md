# Final experiment readiness manifest

**Created:** 2026-10-31T07:29:19Z  
**Status:** READY FOR AN EXPLICIT LIVE RUN. No live run has been performed.

## Frozen inputs and provenance

- **Benchmark:** `indian-constitution-temporal-qa-article174-v2`; SHA-256 `da991b43f616bbe9c48c56f7335ea09c5773d9a60e0fd02e362331202865ee1a`; 32 questions, 25 eligible and 7 pending. Q001–Q020 are byte-for-byte unchanged as question records from the prior benchmark; no original pilot outputs or scores were changed.
- **Canonical dataset:** `indian-constitution-article-version-pilot-86th-amendment`; SHA-256 `c15a559cd91bd364a7408983ff86f3fbbfa75ba72d151828fedd7497df596611`; 6 records. Article 174 records are verified with evidence cutoffs 1951-06-17 and 2026-05-01. Article 21A and Article 45 records remain partially verified and are ineligible for System C.
- **Static index:** `6bb6c11f1d96dba6041ed6657a0306bc0c67c7b0095b7fa80407b3cf2add1424`; 1123 chunks; embedding model `BAAI/bge-small-en-v1.5`; SQLite file SHA-256 `42502e3cc66fa72bd4c288c440098b2a1e617e291a96cf9aad22acd4f2587adb`. The index was not rebuilt.
- **Benchmark version:** `indian-constitution-temporal-qa-article174-v2`. The pilot execution manifest includes benchmark SHA-256 and index snapshot ID.

## Systems and generation configuration

| System | Condition | Retrieval and temporal policy |
|---|---|---|
| A | Base LLM | No retrieval, corpus context, or web search. |
| B | Static RAG | Existing fixed index; no temporal filter; default top-k 5 and context budget 4,000 approximate tokens. |
| C | Temporal RAG | Verified versions only; legal intervals use `[effective_from, effective_to)` and evidence coverage is inclusive. Default top-k 5. |

Shared generation configuration: model default `gemini-3.5-flash-lite` (`GEMINI_MODEL_NAME` can override it); configured temperature `0.0` (omitted from Gemini 3.x request); maximum output 1,024 tokens; per-attempt timeout 45 seconds; at most 2 retries for transient 503/504/network errors, exponential backoff with jitter, base 1 second; SDK retries disabled. Runtime model/settings must be confirmed from live run records. The actual `.env` was not inspected.

## Evaluation settings

Each eligible question is passed unchanged, including its exact reference date, to A, B, and C. Select only `evaluation_status == suitable_for_evaluation`; retain failures, answer abstentions, expected temporal abstentions, and skips as separate outcomes. Report answer correctness, completeness, unsupported claims, and temporal validity where assessable. For B, check citation correctness and verify each cited chunk supports the associated claim. Citation scoring is not applicable to A; expected C abstentions are not substantive correct answers. Use 25 eligible questions as the per-system primary denominator and state all counts/denominators. Do not score pending questions.

## Question selection

**Eligible (25):** `Q001`, `Q002`, `Q003`, `Q004`, `Q005`, `Q006`, `Q007`, `Q008`, `Q009`, `Q010`, `Q011`, `Q019`, `Q020`, `Q021`, `Q022`, `Q023`, `Q024`, `Q025`, `Q026`, `Q027`, `Q028`, `Q029`, `Q030`, `Q031`, `Q032`.

**Skipped pending source verification (7):** `Q012`, `Q013`, `Q014`, `Q015`, `Q016`, `Q017`, `Q018`. Q012–Q014 require the pending Gazette date/source verification; Q015–Q018 require historical evidence for Articles 21A/45. They remain excluded from scoring.

Q032 is a suitable, explicit abstention check at `2026-05-02`: mocked System C abstained with reason `beyond_evidence_coverage` because the verified Article 174 evidence cutoff is `2026-05-01`. Its expected answer is null; the open legal end date is not treated as evidence beyond the cutoff.

## Preflight execution and checks

Mocked runner execution: `20261031T072752560263Z-387a0f8b`; deterministic runner manifest ID `87405932c0e89fb3d41bb0b3bb04df07288e271b32f266da83d5e75b3146ac02`. Outputs: `results\benchmark_runs\87405932c0e89fb3d41bb0b3bb04df07288e271b32f266da83d5e75b3146ac02\20261031T072752560263Z-387a0f8b`. Counts: 65 mocked, 10 abstained, 21 skipped, 0 failed, 0 completed live calls. A and B each recorded 25 mocked runs and 7 skips; C recorded 15 mocked outcomes, 10 eligibility abstentions, and 7 skips. No Gemini calls were made. Q032’s specific cutoff abstention is present in `system_c.jsonl`.

- Benchmark validation: passed, 32 questions; 25 suitable; 7 pending.
- Canonical validator: passed, 6 records.
- Full `tests/` suite: passed, 83 tests.
- Canonical versioning suite: passed, 19 tests.
- Input equality check: all three mocked output files contain the exact benchmark question text and reference date for every record; pending rows are explicitly skipped.

## Ready-to-copy live command

Run from the repository root only when authorized:

```powershell
C:\Users\shikh\AppData\Local\Programs\Python\Python310\python.exe benchmark/run_benchmark.py --live
```

This manifest freezes inputs and settings; it does not authorize or start the live benchmark.
