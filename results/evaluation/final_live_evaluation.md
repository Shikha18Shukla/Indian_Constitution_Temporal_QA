# Final live evaluation — 20261031T073135193342Z-58165fa8

**Scope:** This report evaluates only the live run `20261031T073135193342Z-58165fa8` in `results\benchmark_runs\e6546e0d74b90e3e05a0581954ea0163fcab80033552d23bcec9b16c54ad3f6d\20261031T073135193342Z-58165fa8`. It does not change the benchmark, systems, canonical data, or methodology. No model calls or benchmark reruns were made for this evaluation.

## Run reconciliation

The run manifest and `summary.json` agree: **25 eligible questions** were attempted per system; Q012–Q018 (**7 pending questions**) were skipped by each system. Raw wrapper JSONL contains 32 rows per system (25 eligible plus 7 skipped). The summary records 65 completed, 10 run-level abstentions, 0 failures and 21 skipped system rows. Native generation-attempt logs reconcile to 25 A, 25 B and 15 C calls (65 total); C’s remaining ten are pre-generation abstentions.

Benchmark SHA-256: `da991b43f616bbe9c48c56f7335ea09c5773d9a60e0fd02e362331202865ee1a`. Generation model recorded in native logs: `gemini-3.5-flash-lite`. Static index snapshot: `6bb6c11f1d96dba6041ed6657a0306bc0c67c7b0095b7fa80407b3cf2add1424` (1123 chunks; `BAAI/bge-small-en-v1.5`). All three systems received identical question text and reference date for every eligible ID.

## Scoring method and results

Manual/rule-assisted evaluation compares the answer with the benchmark gold answer, key facts and documented evidence. No LLM-as-judge was used. Strict correctness requires the core requested facts and no material error; questions requesting exact operative wording are judged for faithful text. Answer-content abstentions count as not correct in strict accuracy. Answered-only accuracy removes those abstentions from its denominator. The runner’s completed status is an execution outcome, not evidence of a correct answer. C’s four generated evidence-refusal answers are counted as answer-content abstentions even though their wrapper status is completed.

| System | Correct | Incorrect substantive | Answer-content abstentions | Strict accuracy (correct / 25) | Answered-only accuracy (correct / substantive answers) |
|---|---:|---:|---:|---:|---:|
| A — Base LLM | 16 | 8 | 1 | 64.0% | 66.7% (16/24) |
| B — Static RAG | 15 | 3 | 7 | 60.0% | 83.3% (15/18) |
| C — Temporal RAG | 9 | 2 | 14 | 36.0% | 81.8% (9/11) |

These are descriptive scores on this benchmark/run only. They do not establish that one system outperforms another; System C’s supported question domain is narrower because it requires verified temporal versions.

## Temporal evaluation: Q021–Q032

System C selected the expected version for **11/11** substantive Article 174 questions Q021–Q031: `174_original_1949` on the pre-transition dates and `174_first_amendment_s8` on/after 18 June 1951 as applicable. It correctly refused Q032 on 2 May 2026 because the replacement record’s evidence coverage is verified only through 1 May 2026. This cutoff is an evidence limit, not a legal cessation date.

C’s Q021 and Q026 fail the strict exact-text criterion because generated output contains U+FFFD replacement glyphs in the reproduced text. Core legal propositions otherwise match the selected versions. Q030 also has a corrupted dash glyph. These are text-fidelity defects, not evidence of wrong temporal selection.

### All System C abstentions / refusals

Run-level temporal abstentions (10):

| Question IDs | Recorded reason | Evaluation |
|---|---|---|
| Q001, Q002, Q003, Q006, Q007 | `no_verified_legal_version` | Expected: the requested Articles 14, 19 and 21 have no verified versions in System C. |
| Q004, Q005, Q008, Q009 | `no_verified_legal_version` | Expected: Articles 21A and 45 have only partially verified records, which must be excluded. |
| Q032 | `beyond_evidence_coverage` | Expected: reference date 2026-05-02 is one day after the Article 174 record’s 2026-05-01 evidence cutoff. |

Four additional System C answers (Q010, Q011, Q019, Q020) are generated refusals although wrapper status is completed. These four are separate from the ten run-level abstentions, so the unique answer-content refusal total is 14. Specifically, Q010/Q011 lack a requested Article target, and the system’s fallback selection did not provide relevant amendment evidence. Q019/Q020 similarly refuse because their target Articles are unavailable. This reveals a routing/fallback issue, not an API failure. Q032 remains the expected evidence-coverage refusal.

## System B citation audit

For the **18 citation-bearing B answers**, all **18/18 cited chunk IDs resolve to chunks retrieved in that same question’s run**. Manual support review found 14 fully supported, four partially supported and zero wholly unsupported citations. Partial cases: Q022’s citation does not substantiate the requested original version; Q026 has relevant text with extraction glyph corruption; Q028’s Section 8 citation proves the amendment operation but not its effective date; Q032’s cited current text does not prove applicability on 2 May or the cutoff. Citation ID resolution and claim support are reported separately. B abstentions have no citations and are not treated as supported answers.

## Question-level findings

- **Q010:** A correctly states that commencement was appointed by Central Government notification in the Official Gazette. B fails by retrieval/answer abstention despite the relevant section existing in the corpus but not its top-five context. C semantically refuses because no Article is identified and its fallback temporal evidence is irrelevant.
- **Q011:** All identify 12 December 2002 as the printed date. A overstates that the title date itself establishes Presidential assent; this distinction is not established by the question’s cited evidence. C refuses unnecessarily.
- **Q020:** A incorrectly says Article 21 uses “any person”; it starts “No person”. B misses relevant corpus evidence in top-five retrieval and abstains. C cannot answer because those Articles have no verified temporal versions.
- **Q021/Q022/Q023:** A applies post-amendment text before the boundary, states 12 months instead of the original twice-yearly/six-month requirements, and misstates original powers. B’s static corpus lacks the original 1949 text and abstains on Q021/Q022; on Q023 it gives replacement powers for the pre-amendment date. C selects and answers from the original version; Q021 has exact-text glyph corruption.
- **Q026:** B and C retrieve/state the replacement provision, but U+FFFD damages exact transcription. Strict exact-text scoring treats this as incorrect; it does not alter the core rule.
- **Q028:** A identifies the wrong amendment and date. B abstains because the relevant effective-date annotation did not appear in top-five retrieval. C gives the correct 18 June 1951 transition date.
- **Q030/Q031:** C uses the correct replacement version. A’s Q030 wording is materially inaccurate; B abstains on Q030. A’s Q031 wording is also inaccurate; B gives the core current rule but omits the expected version ID.
- **Q032:** C correctly abstains beyond the 1 May 2026 evidence cutoff. A gives a generic System C unavailability response; B presents current text despite the reference date exceeding the documented evidence cutoff, a temporal overreach.

## Latency and API usage

Runner-recorded execution time (wrapper/orchestration time, not isolated Gemini latency):

| System | n | Mean | Median | Min–max |
|---|---:|---:|---:|---:|
| A | 25 | 5.750s | 4.497s | 3.652–28.711s |
| B | 25 | 6.811s | 6.847s | 5.553–8.830s |
| C generation-completed calls | 15 | 5.228s | 5.109s | 4.827–5.673s |

The JSONL does not record token usage or cost, so API usage is unavailable. No missing values were estimated.

## Reproducibility

- Run manifest: `results\benchmark_runs\e6546e0d74b90e3e05a0581954ea0163fcab80033552d23bcec9b16c54ad3f6d\20261031T073135193342Z-58165fa8\manifest.json`
- Run summary: `results\benchmark_runs\e6546e0d74b90e3e05a0581954ea0163fcab80033552d23bcec9b16c54ad3f6d\20261031T073135193342Z-58165fa8\summary.json`
- Raw wrapper outputs: `results\benchmark_runs\e6546e0d74b90e3e05a0581954ea0163fcab80033552d23bcec9b16c54ad3f6d\20261031T073135193342Z-58165fa8\system_a.jsonl`, `results\benchmark_runs\e6546e0d74b90e3e05a0581954ea0163fcab80033552d23bcec9b16c54ad3f6d\20261031T073135193342Z-58165fa8\system_b.jsonl`, `results\benchmark_runs\e6546e0d74b90e3e05a0581954ea0163fcab80033552d23bcec9b16c54ad3f6d\20261031T073135193342Z-58165fa8\system_c.jsonl`
- Per-question scoring: `results/evaluation/final_per_question_scores.csv`
- Machine-readable summary: `results/evaluation/final_summary.json`

Scoring applies only to the 25 questions eligible in this run; Q012–Q018 are skipped pending source verification. This is the first full live run, and should be interpreted as a measured pilot, not as conclusive evidence of comparative system performance.
