# Teacher Demonstration Report — Prospective Article 174 Set

**Research objective:** test whether date-aware retrieval can provide the Article 174 wording applicable on a stated date, with evidence traceability, compared with a parametric Base LLM and a fixed-corpus Static RAG system.

## Systems

- **A — Base LLM:** receives the question and reference date; no project-corpus retrieval.
- **B — Static RAG:** retrieves from the frozen, non-temporal corpus snapshot.
- **C — Temporal RAG:** applies verified-version legal interval and evidence-coverage gates before retrieval.

## Successful execution record

- Execution ID: `20261031T084946583103Z-5efff8b3`.
- Run directory: `results/benchmark_runs/held_out_article174/b87ac71c2a5b1c9190a270aadf61302942ae422dad5acf40bb8a601dea2809cd/20261031T084946583103Z-5efff8b3/`.
- Manifest ID: `b87ac71c2a5b1c9190a270aadf61302942ae422dad5acf40bb8a601dea2809cd`.
- Benchmark: `indian-constitution-temporal-qa-article174-prospective-heldout-v1`; SHA-256 `b02f76053afb96ec56477c3097e683eac0b4c3af7ad2de97bb3fdca6cdcfd7a9`.
- Static index snapshot: `6bb6c11f1d96dba6041ed6657a0306bc0c67c7b0095b7fa80407b3cf2add1424` (not rebuilt).
- Counts from run `summary.json`: **30 completed; 0 failed; 0 run-level abstentions; 0 skipped**. Each system completed 10/10.
- The earlier execution `20261031T083022845114Z-a2028157` was a transient environment failure before answers were available. It is not the final result and is not included in the outcome below.

The successful run’s JSONL records show identical question wording and reference dates for A, B and C on Q033–Q042. The summaries below are faithful summaries of the stored answers, not verbatim replacements. Verbatim outputs remain in the three system JSONL files linked above.

## Questions, expected answers and observed outputs

### Q033 — 1950-05-01

**Question:** Under original Article 174 on 1 May 1950, which earlier clause qualified the Governor’s powers listed in clause (2)?
**Expected answer:** The clause (2) powers were subject to the provisions of clause (1).
**Date-eligible version:** `174_original_1949`, [1950-01-26, 1951-06-18) ; evidence through 1951-06-17 inclusive
**Primary source:** The Constitution of India (1949), local image-based scan — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007.
**System A (observed):** Says original Article 174 had no numbered clauses and therefore no clause (2); contradicts the verified original text.
**System B (observed):** Says the retrieved context lacks original wording and abstains; cites the consolidated Article and First Amendment text, not the original clause qualification.
**System C (observed):** States clause (2) was subject to clause (1), with the original-version temporal citation.
**Citation observation:** A has no citations by design. B IDs resolve to consolidated Article 174 (PDF p.111) and First Amendment Section 8 (PDF p.4); neither supports the original clause claim. C temporal ID maps to 174_original_1949, PDF p.106 / printed p.89; supports the answer.

### Q034 — 1950-11-01

**Question:** In original Article 174(2)(a), what words described the Governor’s discretion over the meeting time and place on 1 November 1950?
**Expected answer:** “At such time and place as he thinks fit.”
**Date-eligible version:** `174_original_1949`, [1950-01-26, 1951-06-18) ; evidence through 1951-06-17 inclusive
**Primary source:** The Constitution of India (1949), local image-based scan — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007.
**System A (observed):** Quotes the Governor’s discretion as “as he thinks fit” and identifies original clause (2)(a).
**System B (observed):** Misattributes the time/place power to the replacement text’s clause (1), then says original clause (2)(a) is not available.
**System C (observed):** Quotes “at such time and place as he thinks fit” with the original-version citation.
**Citation observation:** A has no citations by design. B IDs resolve, but its evidence is consolidated Article text / amendment annotation, not original clause (2)(a). C temporal ID maps to the original Article passage and supports the quote.

### Q035 — 1951-02-01

**Question:** Under original Article 174(2)(c), what legislative body could the Governor dissolve on 1 February 1951?
**Expected answer:** The Legislative Assembly.
**Date-eligible version:** `174_original_1949`, [1950-01-26, 1951-06-18) ; evidence through 1951-06-17 inclusive
**Primary source:** The Constitution of India (1949), local image-based scan — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007.
**System A (observed):** Answers “Legislative Assembly.”
**System B (observed):** Says original clause (2)(c) is absent from retrieved context and abstains.
**System C (observed):** Answers “Legislative Assembly” with original-version citation.
**Citation observation:** A has no citations by design. B IDs resolve to consolidated/current and First Amendment passages; they do not establish original clause (2)(c). C original-version temporal passage supports “Legislative Assembly”.

### Q036 — 1951-06-16

**Question:** Where did the original Article 174 place both its twice-yearly meeting requirement and its six-month interval rule on 16 June 1951?
**Expected answer:** Both requirements appeared in clause (1).
**Date-eligible version:** `174_original_1949`, [1950-01-26, 1951-06-18) ; evidence through 1951-06-17 inclusive
**Primary source:** The Constitution of India (1949), local image-based scan — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007.
**System A (observed):** Places both the twice-yearly meeting rule and six-month rule in original clause (1).
**System B (observed):** Says the original clause placement cannot be established from retrieved passages; cites Section 8 replacement text.
**System C (observed):** Places both requirements in original clause (1), with original-version citation.
**Citation observation:** A has no citations by design. B Section 8 citation resolves to the replacement text, not the original clause (1). C original-version temporal passage supports both rules’ location.

### Q037 — 1951-06-18

**Question:** On the first day the substituted Article 174 took effect, did clause (1) say the Governor “may” or “shall” summon the House or each House?
**Expected answer:** It says the Governor “shall” from time to time summon the House or each House of the State Legislature.
**Date-eligible version:** `174_first_amendment_s8`, [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source:** The Constitution (First Amendment) Act, 1951, local image-based scan — Section 8, PDF p. 4 (1-based); SHA-256 316dae4a42e11ccab825e47b495a8bf2ff0bebbb8877cfe61ba0756c19d1e9c9; full page image visually inspected.; The Constitution of India, Government of India official consolidated edition as on 1 May 2026 — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b.
**System A (observed):** Answers “shall” and describes the replacement clause (1) summons.
**System B (observed):** Answers “shall”; cites the consolidated Article, the consolidated amendment footnote, and the First Amendment text.
**System C (observed):** Answers “shall” and cites the replacement-version passage.
**Citation observation:** A has no citations by design. B citations resolve to Article 174 (p.111), First Amendment Section 8 (p.4), and an Article 176 indexed passage whose footnote states Article 174 substitution w.e.f. 18-6-1951; together they support “shall” and the boundary. C replacement temporal passage supports the operative word.

### Q038 — 2010-04-01

**Question:** As of 1 April 2010, what two textual qualifications governed the Governor’s summons under Article 174(1)?
**Expected answer:** The Governor could summon the House or each House at such time and place as he thinks fit, but six months could not intervene between the last sitting in one session and the appointed first sitting in the next.
**Date-eligible version:** `174_first_amendment_s8`, [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source:** The Constitution (First Amendment) Act, 1951, local image-based scan — Section 8, PDF p. 4 (1-based); SHA-256 316dae4a42e11ccab825e47b495a8bf2ff0bebbb8877cfe61ba0756c19d1e9c9; full page image visually inspected.; The Constitution of India, Government of India official consolidated edition as on 1 May 2026 — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b.
**System A (observed):** Gives the time/place discretion and six-month rule, then adds an unsupported account attributing changes to the 38th and 44th Amendments.
**System B (observed):** Gives “from time to time” and the six-month safeguard; cites the consolidated Article text, but not a dated interval source.
**System C (observed):** Gives “from time to time” and the six-month safeguard with a replacement-version citation.
**Citation observation:** A has no citations by design. B and C cite the Article 174 passage containing the operative text; B’s citation does not itself prove the 2010 date applicability. C’s evidence is the version eligible for that date and supports the requested wording.

### Q039 — 1960-01-26

**Question:** Under substituted Article 174(2)(b), applicable on 26 January 1960, which body is expressly named as the one the Governor may dissolve?
**Expected answer:** The Legislative Assembly.
**Date-eligible version:** `174_first_amendment_s8`, [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source:** The Constitution (First Amendment) Act, 1951, local image-based scan — Section 8, PDF p. 4 (1-based); SHA-256 316dae4a42e11ccab825e47b495a8bf2ff0bebbb8877cfe61ba0756c19d1e9c9; full page image visually inspected.; The Constitution of India, Government of India official consolidated edition as on 1 May 2026 — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b.
**System A (observed):** Answers “Legislative Assembly,” attributing the wording to the substituted provision.
**System B (observed):** Answers “Legislative Assembly,” citing the consolidated Article and First Amendment text; the citations do not explicitly establish the 1960 applicability date.
**System C (observed):** Answers “Legislative Assembly” with the replacement-version citation.
**Citation observation:** A has no citations by design. B cited passages support the replacement wording/body, but the cited IDs do not explicitly establish the 1960 date boundary. C replacement temporal citation maps to the date-eligible version and supports the body.

### Q040 — 2020-01-26

**Question:** Compare original Article 174 with the replacement in force on 26 January 2020: where was the Governor’s summoning authority placed, and how did its operative verb change?
**Expected answer:** Originally, clause (2)(a), subject to clause (1), said the Governor “may” summon the House or either House at a time and place he thinks fit. The replacement places summoning in clause (1) and says the Governor “shall” summon the House or each House at a time and place he thinks fit, subject to the six-month interval rule.
**Date-eligible version:** `174_first_amendment_s8`, [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source:** The Constitution of India (1949), local image-based scan — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007.; The Constitution (First Amendment) Act, 1951, local image-based scan — Section 8, PDF p. 4 (1-based); SHA-256 316dae4a42e11ccab825e47b495a8bf2ff0bebbb8877cfe61ba0756c19d1e9c9; full page image visually inspected.; The Constitution of India, Government of India official consolidated edition as on 1 May 2026 — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b.
**System A (observed):** Incorrectly places original summoning power in clause (1) and attributes the replacement to the Seventh Amendment; the gold says original clause (2)(a), “may”, versus replacement clause (1), “shall”.
**System B (observed):** Says retrieved material lacks the original Article and cannot compare; cites the replacement text.
**System C (observed):** Says only the date-eligible replacement version is in retrieved temporal evidence and cannot compare it to the original; cites replacement passage.
**Citation observation:** A has no citations by design. B Section 8 citation resolves and supports replacement text only. C citation resolves to the date-eligible replacement passage only; neither retrieved citation supplies the original comparator.

### Q041 — 2000-01-26

**Question:** Comparing the original Article 174 with the substituted text applicable on 26 January 2000, which express yearly-frequency phrase was removed, and which inter-session safeguard remained?
**Expected answer:** The original clause (1) expressly required the House or Houses to meet “twice at least in every year.” The replacement no longer states that yearly frequency formula; it retains the rule that six months shall not intervene between the last sitting in one session and the appointed first sitting in the next.
**Date-eligible version:** `174_first_amendment_s8`, [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source:** The Constitution of India (1949), local image-based scan — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007.; The Constitution (First Amendment) Act, 1951, local image-based scan — Section 8, PDF p. 4 (1-based); SHA-256 316dae4a42e11ccab825e47b495a8bf2ff0bebbb8877cfe61ba0756c19d1e9c9; full page image visually inspected.; The Constitution of India, Government of India official consolidated edition as on 1 May 2026 — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b.
**System A (observed):** Identifies the yearly-frequency phrase and six-month safeguard, but paraphrases the original phrase order; the answer says the First Amendment removed it.
**System B (observed):** Says original wording is absent; cites the replacement text, which supports the retained six-month rule but not the original phrase.
**System C (observed):** Says verified date-eligible evidence contains only replacement text and cannot make the comparison; cites replacement passage.
**Citation observation:** A has no citations by design. B Section 8 citation resolves and supports the replacement safeguard, not the original frequency phrase. C replacement citation supports only the retained safeguard; original comparator is absent.

### Q042 — 2026-05-01

**Question:** In the original and substituted versions of Article 174, how did the stated object of the Governor’s prorogation power change?
**Expected answer:** The original clause (2)(b) said “prorogue the House or Houses”; the replacement clause (2)(a) says “prorogue the House or either House.”
**Date-eligible version:** `174_first_amendment_s8`, [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source:** The Constitution of India (1949), local image-based scan — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007.; The Constitution (First Amendment) Act, 1951, local image-based scan — Section 8, PDF p. 4 (1-based); SHA-256 316dae4a42e11ccab825e47b495a8bf2ff0bebbb8877cfe61ba0756c19d1e9c9; full page image visually inspected.; The Constitution of India, Government of India official consolidated edition as on 1 May 2026 — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b.
**System A (observed):** Expresses uncertainty and speculates that the object was conceptually unchanged; it does not identify the textual change from “House or Houses” to “House or either House”.
**System B (observed):** Says the context does not explain a change in object; cites current consolidated Article and First Amendment text, but not original Article text.
**System C (observed):** Says original text is absent from the date-eligible temporal evidence and cannot compare; cites replacement passage.
**Citation observation:** A has no citations by design. B citations resolve to consolidated/replacement text and do not support the original wording. C citation resolves to the replacement passage only and cannot support the comparison.

## What the run demonstrates

### Observations

- C’s recorded temporal citation IDs for Q033–Q036 resolve to the verified original version `174_original_1949`; for Q037–Q042 they resolve to `174_first_amendment_s8`, which is the date-eligible version for those reference dates. This mapping was checked against the canonical records and `TemporalArticleIndex`. The benchmark runner’s JSONL does **not** persist a separate `selected_version_ids` field, so the citation mapping is evidence of the passage used, not direct selector telemetry.
- C provided substantive answers for Q033–Q039. Its Q040–Q042 answer texts say the original comparator is absent from the date-eligible evidence. These are answer-content refusals, even though the runner status is `completed`; they are not run-level abstentions or failures.
- B produced answer-content refusals on Q033–Q036 and Q040–Q042 (seven questions). The wrapper still records them as completed API runs. B’s cited IDs resolve to actual indexed passages. The static Article 174 passage is the consolidated text on PDF p.111; the amendment passage is Section 8 on PDF p.4. Those sources do not supply the original wording needed by Q033–Q036 or the original side of Q040–Q042.
- B answered Q037–Q039. The cited consolidated Article / Section 8 wording supports the operative replacement text. Temporal support is stronger where its citation set includes the consolidated footnote annotation; citations to the Article text alone do not establish every historical date claim.
- A returned substantive outputs for Q033–Q041 and an uncertainty/non-answer for Q042. It is parametric-only; absence of citations is expected and is not a citation failure. Answers include a wrong historical clause claim on Q033, a wrong comparison on Q040, and an unsupported amendment-history assertion in Q038.
- There were no explicit run-level abstentions in the successful summary. Content-level refusal counts are different: B seven, C three, and A one uncertainty/non-answer (Q042).

### Interpretation and limits

Q033–Q039 are the strongest demonstration candidates: System C’s cited passage maps to the expected date-eligible version, and its answers state the requested points. Baselines sometimes answer correctly too: A and C agree on Q034–Q036; all three answer Q037; all three identify the Legislative Assembly in Q039. The run therefore illustrates both useful temporal grounding and cases where the baselines answer successfully.

Q040–Q042 expose a scope limitation: each asks for a cross-version comparison while System C retrieves only the version eligible for the single reference date. C cites the replacement version and declines the unsupported comparison. The gold facts themselves are supported by the original Constitution and Section 8, but both sides are not delivered to C under its current retrieval condition. These items are diagnostic and should not be represented as ordinary single-version retrieval wins or losses.

This is a prospective held-out question set only in the sense that its wording was prepared for this run. Article 174, its temporal records, and System C had already been developed and tested. It is not fully independent or blinded, and it covers one Article and one amendment transition. Do not generalize these observations to constitutional QA broadly or describe them as proof of the hypothesis.

## Citation and logging limitations

- System B citations in answers resolve against the frozen index. Its runner JSONL does not include the full top-k retrieval array, so retrieval recall@k and complete per-run passage support cannot be reconstructed from this run export alone.
- System C answers include temporal citation IDs and those IDs map to verified version-specific passages and coverage metadata. The benchmark runner export omits the selector’s separate selected-version and retrieved-evidence fields; do not report direct selection telemetry as if logged.
- `results/evaluation/held_out_full_comparison.json` is a derived convenience file. Its curly quotation marks in some expected-answer strings display as mojibake. The UTF-8 benchmark source `benchmark/held_out_article174_questions.json` is the source for exact wording and gold answers. No benchmark or raw run file was edited.
- Source locators: original Constitution Article 174, PDF p.106 / printed p.89; First Amendment Section 8, PDF p.4; official consolidated Constitution Article 174/footnote, PDF p.111; consolidated edition preface, PDF p.2. Source hashes are recorded in the canonical records and question source references.

## Reproducibility

- Successful run manifest: `results/benchmark_runs/held_out_article174/b87ac71c2a5b1c9190a270aadf61302942ae422dad5acf40bb8a601dea2809cd/20261031T084946583103Z-5efff8b3/manifest.json`.
- Summary: `results/benchmark_runs/held_out_article174/b87ac71c2a5b1c9190a270aadf61302942ae422dad5acf40bb8a601dea2809cd/20261031T084946583103Z-5efff8b3/summary.json`.
- Raw output files: `system_a.jsonl`, `system_b.jsonl`, and `system_c.jsonl` in that same run directory.
- Gold/source definitions: `benchmark/held_out_article174_questions.json`; canonical Article 174 records: `processed/canonical/article_versions_pilot.json`.
