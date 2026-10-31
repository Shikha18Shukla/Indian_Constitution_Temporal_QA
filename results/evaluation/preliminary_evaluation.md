# Preliminary evaluation of the first live benchmark pilot

**Status:** Preliminary exploratory evaluation only. This is not the final research evaluation. It covers the 13 questions marked `suitable_for_evaluation`; seven pending questions were excluded. System C abstained on every eligible question because it had no verified version available, so temporal answer quality is not measurable.

## Run and evidence inspected

- Run: `20261030T173545036179Z-5d548d32`; started `2026-10-30T17:35:45.036Z` and finished `2026-10-30T17:38:16.999Z`.
- Benchmark: `indian-constitution-temporal-qa-initial-v1`, SHA-256 `0b312358cad107446245e12fd01ada11b6cd7a396f8c3d47866d5c8c9c667fd9`.
- All 13 included questions used reference date `2026-05-01` and the identical benchmark wording/date across A, B and C.
- System B used the frozen static index snapshot `6bb6c11f1d96dba6041ed6657a0306bc0c67c7b0095b7fa80407b3cf2add1424` (1123 chunks; `BAAI/bge-small-en-v1.5`). No index rebuild or temporal filtering was part of this evaluation.
- Generation model recorded for A and B: `gemini-3.5-flash-lite`.
- Inspected benchmark `expected_answer` and `gold_evidence`, all per-system run JSONL, and matched every System B cited chunk ID against that question’s native `results/system_b/runs.jsonl` retrieved-chunk records, including chunk text, Article metadata, source file and page locator.

## Rubric and denominators

A question is **strictly correct** only if the answer covers the core expected gold propositions without a material factual error. Plain-language abstentions are reported separately and count as not correct for task accuracy. Accuracy is therefore correct answers / all 13 eligible questions. We also report substantive accuracy among non-abstained answers so abstention behavior is visible rather than hidden.

Completeness is manually scored 0–1 per question against the required gold propositions; a correct but under-explained answer can be partial. The mean includes all 13 eligible questions, with abstentions at 0. System A citation measures are **not applicable** because A is deliberately parametric-only. For B, citation correctness means every cited ID resolves to an actually retrieved chunk in that same run; citation support means the cited chunk text supports the attached statement. We report citation rates across the 11 B answers containing citations; the two B abstentions contain no citations and are not treated as supported answers. An ID resolving is separated conceptually from whether its text proves the claim.

The evaluation is evidence-based manual/rule-assisted comparison with the benchmark gold and local chunk text; it does not use LLM-as-judge. Interpretive expansions beyond the gold excerpt are called out, not silently converted into verified facts.

## Results

| Measure | System A — Base LLM | System B — Static RAG | System C — Temporal RAG |
|---|---:|---:|---:|
| Eligible questions | 13 | 13 | 13 |
| Correct / task accuracy (correct ÷ 13; abstentions not correct) | 11/13 = **84.6%** | 11/13 = **84.6%** | Not scored |
| Substantive accuracy (correct ÷ non-abstained) | 11/12 = **91.7%** | 11/11 = **100%** | Not measurable |
| Manual completeness total / maximum | 11.0/13 = **84.6%** | 11/13 = **84.6%** | Not scored |
| Abstentions in answer content | 1 | 2 | 13 |
| Run-level failures | 0 | 0 | 0 |
| Citation IDs resolving / citation-bearing answers | N/A | 11/11 = **100%** | No answers/citations |
| Cited claims supported / citation-bearing answers | N/A | 11/11 = **100%** | No answers/citations |

The substantive-accuracy denominators exclude abstentions and are supplementary; the all-eligible denominator is the primary comparison. B’s runner records all 13 executions as `completed`, but Q010 and Q020’s answer text explicitly abstains. This manual outcome classification is reflected in the score CSV; it does not rewrite run logs.

### Per-question findings

- **Q001–Q006:** A and B answer the core Article 14, 19, 21, 21A and 45 text questions correctly. A’s Q002 adds a property/44th Amendment explanation beyond the benchmark’s cited excerpts; it is not counted as an error, but it is an extra claim that this question’s gold evidence does not itself establish. A’s Q006 says “any person” extends to non-citizens/foreigners. That is an inference from the quoted phrase, not a separate proposition expressly stated in the gold excerpt. B’s citations point to the relevant Article 14/19/21/21A/45 chunks and support the attached claims.
- **Q007:** A says “No,” which is correct but incomplete because it omits the stated exception (“except according to procedure established by law”). B includes and cites the qualification.
- **Q008–Q009:** Both systems correctly answer Sections 2 and 3. B’s cited chunk `chunk-eb75d49aac3dff04f65a838a` is from `raw/amendments/086_Amendment_2002.pdf`, PDF page 1, and contains the insertion/substitution provisions.
- **Q010:** A correctly describes the Central Government appointing commencement by Official Gazette notification. B abstains. The eligible gold answer is present in section 1(2) of the 86th Amendment Act, but B’s actual top five retrieved chunks do not include the relevant Act chunk. This is a retrieval/context failure rather than a missing-gold-source issue.
- **Q011:** A abstains despite the answer being in the Act text. B correctly reports the printed title date `[12th December, 2002.]` and cites the Act chunk. It does not call this the commencement date.
- **Q019:** A and B correctly distinguish Article 21A’s six-to-fourteen years from Article 45’s care/education until age six. B’s citations resolve to the Article 21A Constitution chunk and the 86th Amendment Act chunk containing Article 45’s replacement provision.
- **Q020:** A is factually wrong on the requested wording distinction. Article 14 says “any person”; Article 21 begins “No person.” A quotes the Article 21 words but then claims both use the exact same “any person” phrase. B abstains; its top five retrieved chunks do not include Article 14 or Article 21 operative text. These are separate failure modes: parametric answer error for A and retrieval failure followed by abstention for B.

### System B citation audit

There are 11 B answers containing citations. All cited IDs resolve to chunks retrieved in that same question run, and manual inspection of those chunk texts supports the claims to which they are attached (11/11 supported citation-bearing answers). Examples include:

- Q001: `chunk-6100b381e336b62ecb405068`, Article 14, `Constitution_of_India_2024.pdf`, PDF page 37; contains the equality guarantee.
- Q002: Article 19 chunks `chunk-d21f8f962357632e557f6731` (page 40), `chunk-b9871ed7fee6588a145ac1da` and `chunk-e7ded89feba8e3774bb1a453` (page 41); together show clauses (a)–(g), the printed (f) omission marker and the omission note.
- Q004: `chunk-1078db9e04620397c7d1e229`, Article 21A, Constitution PDF page 42, contains the operative education provision; the cited 86th Amendment Act chunk also contains section 2.
- Q005: `chunk-f1dbc92527e9d297fff1dfca`, Article 45, Constitution PDF page 54, contains the current early-childhood provision.
- Q010 and Q020 have no citation IDs because they abstain. For Q010 the top five include unrelated pages/chunks rather than the 86th Amendment section 1(2); for Q020 they include unrelated amendment/Constitution material rather than Articles 14 and 21. Neither was a false cited-evidence case.

## System C abstentions and temporal evidence

System C logged abstention for all 13 eligible questions, with no selected version IDs and no retrieved evidence passed to generation. The reason was lack of a verified eligible version (the exact runner reason is `no_verified_version_for_requested_article_and_date` for Article-targeted cases and `no_verified_version_for_reference_date` where no single Article was identified). This behavior is consistent with its verified-only gate.

The canonical pilot contains four relevant Article 21A/45 records—`21A_pre_86th`, `21A_v1`, `45_pre_86th` and `45_v2`—and all remain `partially_verified`. They cannot serve as System C historical gold/evidence. The pilot has no canonical versions for Articles 14, 19 or 21. Thus System C’s 13 abstentions are not scored as correct or incorrect substantive answers; historical temporal answer quality is **not yet measurable**.

## Completeness, temporal scope, latency and usage

The completeness scores are manual coverage scores, not another accuracy metric. A receives 11/13 points: Q007 is partial (0.5) and Q011 is an abstention (0); Q020 receives 0.5 because it quotes both clauses but fails the comparison. B receives 11/13: Q010 and Q020 abstain. Citation support does not imply answer completeness or retrieval recall.

The 13 eligible questions all use reference date `2026-05-01`. The scored set contains current-snapshot text and 86th Amendment Act text, not a verified historical-version test. A and B’s answers are checked against that stated current snapshot and the Act source; the pilot cannot establish temporal reasoning across historical intervals. System B remains static and applies no date filtering.

Runner-recorded per-question latency (13 each):

| System | Mean | Median | Range |
|---|---:|---:|---:|
| A | 4.60s | 4.32s | 3.94–6.87s |
| B | 6.70s | 6.38s | 5.42–8.94s |
| C | 0.39s | 0.39s | 0.33–0.48s |

Token counts and detailed API usage metadata were not present in the run records; latency is available, usage is not. The seven pending questions Q012–Q018 were excluded from every system’s scoring (21 explicitly logged skipped system-runs). There were no live execution failures.

## Limitations and conclusion

This small, single-run set is exploratory and only 13/20 prepared questions are eligible. Scores are sensitive to this short hand-checked set and are not statistical claims. Current-version gold answers depend on the benchmark’s cited Constitution snapshot/excerpts; local extracted typography includes known glyph/normalization limitations documented in the benchmark README. System A has no retrieval evidence by design, so its claims are compared with gold but cannot be source-cited from its run. B’s citation support was checked, but successful citations do not mask retrieval failures in Q010 and Q020. System C supplies no substantive answers, so no A/B/C temporal-performance comparison is possible.

**Preliminary conclusion:** A and B both have 11 strictly correct answers on the 13 eligible questions. A’s errors are one abstention (Q011) and one incorrect comparison (Q020); B’s are two retrieval-driven abstentions (Q010, Q020). Among B’s citation-bearing answers, all citations resolved and supported their associated claims. These results should guide targeted review, not be presented as final research findings.

## Artifacts

- Per-question scored records: `results/evaluation/per_question_scores.csv`
- Machine-readable metrics: `results/evaluation/summary.json`
- Raw run outputs remain unchanged in `results/benchmark_runs/02a57176dd4cb2e64be47fcdc98979cf76b5b7c7855a4e2b27640612f058fd91/20261030T173545036179Z-5d548d32`.
