# First live pilot: final report

**Report status:** Final report for the *preliminary exploratory pilot* only. This is not the final research evaluation, and the results do not establish that one system outperforms another.

## Research objective and methodology

The project studies temporal-aware, evidence-grounded retrieval for Indian constitutional-law question answering by comparing three fixed experimental conditions on the same question wording and reference date:

- **System A — Base LLM:** Gemini generation with no retrieval, corpus context, vector database, web search, or document lookup.
- **System B — Static RAG:** dense and lexical retrieval from the fixed Constitution/amendment corpus and SQLite index, then Gemini generation grounded in retrieved passages. The index is static; the reference date is not used to filter versions.
- **System C — Temporal RAG:** verified Article versions are selected by reference date before evidence retrieval and generation. Only versions meeting the verified threshold may be used; if no eligible verified version exists, the system abstains.

The three systems received the same benchmark question text and `reference_date` for each included ID. The recorded generation model for A and B was `gemini-3.5-flash-lite`. System C did not generate an answer in this run because it abstained before generation.

## Dataset and run identity

The benchmark contains **20 questions**: **13 marked suitable for evaluation** and **7 pending source verification**. The runner explicitly skipped the seven pending IDs Q012–Q018 for each system (21 skipped system-runs); they are excluded from every score. The eligible questions all used reference date `2026-05-01`.

- **Execution ID:** `20261030T173545036179Z-5d548d32`
- **Run start / finish:** `2026-10-30T17:35:45.036Z` / `2026-10-30T17:38:16.999Z`
- **Runner manifest ID (deterministic identifier):** `02a57176dd4cb2e64be47fcdc98979cf76b5b7c7855a4e2b27640612f058fd91`
- **SHA-256 of the saved `manifest.json` file:** `1a39b7580335b782b22d6fe1d9d4a3a306275be954201dbd48b931d987b21136`
- **Benchmark ID:** `indian-constitution-temporal-qa-initial-v1`
- **Benchmark SHA-256:** `0b312358cad107446245e12fd01ada11b6cd7a396f8c3d47866d5c8c9c667fd9`
- **Static index snapshot:** `6bb6c11f1d96dba6041ed6657a0306bc0c67c7b0095b7fa80407b3cf2add1424` (1123 chunks; embedding model `BAAI/bge-small-en-v1.5`)

The manifest ID and the hash of the serialized manifest file are different values with different meanings; both are given above to avoid treating them as interchangeable.

## Observed execution and answer outcomes

The run’s execution summary records 26 completed system calls (13 each for A and B), 13 System C abstentions, 0 execution failures, and 21 skipped system-runs. For answer scoring, the raw A/B answers were also inspected for natural-language abstentions. Those are reported separately from successful API execution: A’s Q011 response and B’s Q010 and Q020 responses completed as calls but abstained in their answer text.

| System | Eligible | Correct answers | Incorrect answers | Answer abstentions | Execution failures | Skipped questions | Primary task accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|
| A — Base LLM | 13 | 11 | 1 | 1 | 0 | 7 | **11/13 = 84.6%** |
| B — Static RAG | 13 | 11 | 0 | 2 | 0 | 7 | **11/13 = 84.6%** |
| C — Temporal RAG | 13 | Not scored | Not scored | 13 | 0 | 7 | **Unavailable** |

Answer-outcome IDs: **A** correct Q001–Q010 and Q019; incorrect Q020; abstained Q011. **B** correct Q001–Q009, Q011 and Q019; incorrect none; abstained Q010 and Q020. **C** abstained on all 13 eligible IDs (Q001–Q011, Q019 and Q020); it has no scored correct/incorrect answers. Each system skipped Q012–Q018.

**Accuracy denominator:** 13 eligible questions per system. A and B plain-language abstentions count as not correct for primary task accuracy; they are also shown in their own column. Supplementary substantive-answer accuracy (excluding answer abstentions) is A: 11/12 = 91.7%; B: 11/11 = 100%. These small denominators do not support a superiority claim and do not replace the primary 11/13 rates. System C has no substantive answers, so neither accuracy nor temporal answer quality can be calculated.

### System B citations

System B produced citation-bearing substantive answers for **11 questions**; both answer-level abstentions had no citation. All cited chunk IDs resolved to chunks actually retrieved in the corresponding question run, and manual inspection found support in those chunk texts for their attached claims: **11/11 citation-bearing answers supported**. This is distinct from retrieval coverage: Q010 and Q020 show that relevant evidence can be in the index yet absent from the retrieved top five. A citation-support score is not applicable to System A’s no-retrieval condition or System C’s abstentions.

## Focused findings: Q010, Q011 and Q020

The following distinguishes **observations** in the saved run/source records from **interpretations** about failure causes. No new Gemini calls were made.

### Q010 — appointment of the 86th Amendment Act commencement date

**Observed:** The question asks how commencement was to be appointed, with reference date `2026-05-01`. The gold answer says the Central Government may appoint the date by Official Gazette notification. System A answered this correctly. System B answered that retrieved context was insufficient. Its saved top five did not contain the relevant 86th Amendment Act section 1(2) passage. A search of the frozen index found the passage in `chunk-eb75d49aac3dff04f65a838a`, from `raw/amendments/086_Amendment_2002.pdf`, PDF page 1. The chunk contains the appointment clause. The local primary Act PDF page 1 supports the gold wording.

**Interpretation:** This is a System B retrieval-ranking failure followed by an abstention consistent with B’s context-only prompt. A read-only reproduction of the repository’s BM25-style lexical ranking put the relevant chunk at rank 139 for the question. The benchmark question is clear; its gold answer is source-supported. The source is present, so corpus coverage is not the cause.

### Q011 — date printed below the Act title

**Observed:** The question asks for the date printed below the 86th Amendment Act title, with reference date `2026-05-01`. The gold says `12 December 2002` and explicitly cautions that this is not the commencement date. System A said it was uncertain because it lacked access to the title-page layout. System B answered `[12th December, 2002.]` and cited the retrieved 86th Amendment Act chunk. The local primary Act PDF’s first page shows the date beneath the title.

**Interpretation:** The question is not ambiguous and the source is available; A’s abstention is a parametric knowledge/confidence limitation, not a source-coverage defect. It is consistent with A’s prompt instruction to state uncertainty and with its no-retrieval condition. It remains a missed answer in task scoring. The gold is supported and keeps Act date separate from commencement.

### Q020 — wording in Articles 14 and 21

**Observed:** The question asks what wording difference appears in the beneficiary phrase, with reference date `2026-05-01`. Gold evidence from the Constitution snapshot says Article 14 “any person” and Article 21 “No person.” System A quoted Article 21’s “No person” wording but then called it “any person” as well and concluded that the phrases are identical. System B abstained, saying its context lacked the Articles. Its five retrieved passages were unrelated to the operative text. The two correct chunks are in the unchanged index: Article 14 chunk `chunk-6100b381e336b62ecb405068` (PDF page 37, Article metadata 14) and Article 21 chunk `chunk-d6191916210d8ec466f42f4e` (PDF page 42, Article metadata 21). Both source passages support the gold.

**Interpretation:** A’s failure is a generation consistency/factual error; the answer contradicts its own quotation. B’s failure is retrieval. The Article metadata parser recognizes singular “Article”/“Art.” but not plural “Articles,” so Q020 does not activate Article metadata prioritization and falls back to generic hybrid ranking. In the lexical component, the two relevant chunks rank 46 and 41, outside top five. The wording is sufficiently clear for a literal comparison, although “beneficiary phrase” is more technical than necessary. The gold is supported by the identified Constitution snapshot.

The detailed same-run chunk records, source locators and excerpts are preserved in `retrieval_failure_analysis.json` and `failure_analysis.md`.

## System C and temporal evaluation

System C abstained on all **13/13 eligible questions**, with no execution failures. Its verified-only gate found no eligible verified Article version and prevented evidence from reaching generation. The four Article 21A/45 pilot records—`21A_pre_86th`, `21A_v1`, `45_pre_86th` and `45_v2`—remain `partially_verified`; the pilot contains no canonical Article versions for 14, 19 or 21. Therefore these abstentions do **not** show poor temporal retrieval accuracy. They mean temporal answer quality could not yet be evaluated. No eligible historical gold questions were scored in this run.

## Limitations

- Only 13 of 20 prepared benchmark questions were eligible; seven were pending source verification and excluded.
- This is a single exploratory live run with a small evaluation denominator. Results are descriptive, not a final research estimate or statistical comparison.
- System C supplied no substantive answers; temporal answer quality remains unavailable until verified historical Article versions are available.
- System B’s static corpus does not filter by reference date. The run assesses retrieval/generation against the fixed snapshot, not historical validity across Article intervals.
- System A has no source retrieval by design. Its answers are compared with benchmark gold, but its claims cannot be grounded in run-time project evidence.
- System B citation support was manually checked for the 11 citation-bearing answers; it does not establish complete retrieval recall, as Q010 and Q020 illustrate.
- Detailed API token/usage metrics were not recorded in the run outputs and are **unavailable**; no usage estimate is supplied.
- Answer-level abstentions are not always the same as the runner’s execution status. The runner’s `completed` label records a successful call; it does not assert a substantive answer. This report preserves both labels.

## Reproducibility and source files

Repository-relative paths below point to the unchanged original run and evaluation evidence:

- Benchmark data and eligibility: `benchmark/questions.json`; benchmark definition: `benchmark/README.md`.
- Original execution directory: `results/benchmark_runs/02a57176dd4cb2e64be47fcdc98979cf76b5b7c7855a4e2b27640612f058fd91/20261030T173545036179Z-5d548d32/`.
- Raw runner outputs: `system_a.jsonl`, `system_b.jsonl`, `system_c.jsonl`; run identity: `manifest.json`; counts and skips: `summary.json` and `skipped_questions.json` in that directory.
- Detailed System B retrieval records/chunk text: `results/system_b/runs.jsonl` (matched to this run by question ID and raw answer); unchanged static index: `processed/static_rag/index.sqlite3`.
- Evaluation source files reviewed: `results/evaluation/preliminary_evaluation.md`, `per_question_scores.csv`, `summary.json`, `failure_analysis.md`, and `retrieval_failure_analysis.json`.
- Local primary sources checked for the three focused questions: `raw/amendments/086_Amendment_2002.pdf` (PDF page 1) and `raw/constitution/Constitution_of_India_2024.pdf` (PDF pages 37 and 42).
- This report: `results/evaluation/final_pilot_report.md`.

## Consistency check and discrepancies

Counts were reconciled with the original manifest, three runner JSONL files, run summary, benchmark eligibility, and per-question CSV. The 20/13/7 counts, 11/13 A and B scores, C’s 13 abstentions, zero execution failures, and 21 skipped system-runs match the saved records. All three system outputs contain identical question text and reference dates for the 13 eligible IDs. The 11 B citation-bearing answers resolve to their same-run retrieved chunks; their support finding matches the prior manual review.

One **labeling distinction**, rather than a count discrepancy, is present: runner outputs label all A/B calls `completed`, including A Q011 and B Q010/Q020, because generation requests succeeded. The manual answer classification treats those answer texts as abstentions. The evaluation CSV and summary make this answer-level distinction explicit; the raw outputs were not rewritten. The stored `manifest_id` is also not the SHA-256 of the serialized `manifest.json`; this report records both values separately. No inconsistent question total, answer-score total, or skipped count was found.

No system code, benchmark question/gold, source status, static index, or original experiment artifact was modified. Only this report was created.
