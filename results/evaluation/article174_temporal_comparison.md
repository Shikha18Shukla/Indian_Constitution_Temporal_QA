# Article 174 temporal comparison — run 20261031T073135193342Z-58165fa8

## Scope and metric

This offline adjudication covers Q021–Q031 from the specified run. Q032 is addressed separately. No run/API calls were made. Original scores, outputs, benchmark and evaluation report remain unchanged; adjudicated results are in `adjudicated_per_question_scores.csv`.

**Primary metric — temporal validity accuracy:** for these 11 date-dependent questions, does the answer state/apply the legal Article 174 state applicable on the reference date, without a wrong-version application, false effective date or contradictory time-specific rule? Abstentions count as not correct. This is distinct from completeness and exact legal-text correctness: a system can use the right period/version and still generate a wrong detail. System C internal selection is reported separately from its answer.

For exact-text items, presentation whitespace alone is normalized. Words, legal punctuation and dash type are preserved. The raw JSONL has U+2014 EM DASH, not U+FFFD REPLACEMENT CHARACTER, on Q021/Q026. B's Q026 quotation includes square-bracket extraction delimiters around the provision; these are punctuation beyond the gold and are not ignored under the requested rule. C's only Q026 difference is whitespace after an em dash.

## Results (Q021–Q031; denominator 11 per system)

| Measure | A — Base LLM | B — Static RAG | C — Temporal RAG |
|---|---:|---:|---:|
| **Temporal validity accuracy** | 7/11 = **63.6%** | 5/11 = **45.5%** | 11/11 = **100%** |
| Strict substantive answer correctness after adjudication | 4/11 = **36.4%** | 3/11 = **27.3%** | 11/11 = **100%** |
| Answer-content abstentions | 0/11 | 5/11 | 0/11 |
| Correct internal version selection | N/A | N/A | 11/11 = **100%** |
| Fully supported answer citations | N/A | 3/11 = **27.3%** | 9/11 = **81.8%** |

Temporal validity requires a correct historical/current state and no material contradiction about the applicable date/version; substantive correctness additionally requires the requested provision facts. Wrong-version/effective-date errors are: A Q021 (substituted text on 17 June 1951) and Q028 (wrong amendment/date); B Q023 (post-substitution powers on 17 June); C none. A Q022's twelve-month claim and Q023's claim that the First Amendment added the summoning power are separate time-specific legal errors and fail temporal validity.

## Per-question evidence and judgments

| ID / reference date | Expected version and gold source | A: temporal / substantive | B: temporal / substantive; top-five evidence | C: selection / retrieval / answer |
|---|---|---|---|---|
| Q021 / 1951-06-17 | `174_original_1949`; 1949 Constitution Article 174, PDF p.106/printed p.89; consolidated transition note | Fail / wrong version: uses replacement wording a day early | No answer / abstention; no original text in top five (0/1) | Original selected and `temporal-b866c870df1726976fa0a678` retrieved; pass / correct. Raw answer contains gold text verbatim; original incorrect score corrected. |
| Q022 / 1951-06-17 | `174_original_1949`; original Article 174 | Fail / wrong: says twelve-month maximum instead of six months | No answer / abstention; retrieved current/substituted text, not original (0/1) | Original selected/retrieved; pass / correct. |
| Q023 / 1951-06-17 | `174_original_1949`; original clause (2) | Fail / incomplete and temporally misleading: omits original summoning power and says First Amendment added it | Fail / wrong version: gives replacement-period powers; original evidence absent (0/1) | Original selected/retrieved; pass / correct, all three original powers and clause (1) condition. |
| Q024 / 2026-05-01 | `174_first_amendment_s8`; consolidated Article 174 six-month clause | Pass / correct | Pass / correct; top five include Article text and `chunk-a8006a35aacce04c0f993b14`, whose page-4 tail contains Section 8's Article 174 replacement (1/1) | Replacement selected/retrieved; pass / correct. |
| Q025 / 2026-05-01 | `174_first_amendment_s8`; clause (2) | Pass / correct | Pass / correct; Article 174 text in top five (1/1), but no answer citation | Replacement selected/retrieved; pass / correct, but no answer-level citation. |
| Q026 / 2026-05-01 | `174_first_amendment_s8`; consolidated text p.111 | Pass for period / wrong exact wording: says “Houses” instead of “House” | Pass for period / wrong exact quote: bracket extraction delimiters remain in quoted provision; cited source supports underlying legal text | Replacement selected/retrieved; pass / correct after whitespace-only normalization. |
| Q027 / 2026-05-01 | Section 8 substitution; First Amendment Act and consolidated annotation | Pass / correct | Pass / correct; `chunk-65f576e658d501619b5ef67a` includes footnote: First Amendment s.8 substituted Article 174 w.e.f. 18-6-1951 (1/1) | Replacement selected/retrieved; pass / correct. |
| Q028 / 2026-05-01 | Effective date 1951-06-18; consolidated annotation | Fail / wrong: attributes substitution to Seventh Amendment, 1956 | No complete answer / abstention; Section 8 retrieved, but effective-date annotation absent from top five (0/1 for date) | Replacement selected/retrieved; pass / correct, states 18-6-1951. |
| Q029 / 1951-06-17 | `174_original_1949`; twice-yearly rule and transition annotation | Pass / correct: identifies original form and annual rule | No answer / abstention; original text absent from top five (0/1) | Original selected/retrieved; pass / correct. |
| Q030 / 1951-06-18 | `174_first_amendment_s8`; Section 8 and w.e.f. annotation | Pass for boundary / wrong text: “Houses” instead of “House” | No answer / abstention; Article text retrieved, transition annotation absent (partial; no complete evidence) | Replacement selected/retrieved on effective_from; pass / correct. |
| Q031 / 2026-05-01 | `174_first_amendment_s8`; version and six-month rule; coverage through 2026-05-01 | Pass for date-compatible rule / incomplete and textually inaccurate, no version ID | Pass for rule's date / incomplete strict answer: gives rule but not the requested version. Current Article text retrieved, but no canonical version/coverage metadata (partial) | Replacement selected/retrieved; pass / correct, identifies version and rule. |

The full raw answers and B top-five chunk IDs are in the adjudicated CSV. C selected the original version for Q021–Q023 and Q029; the replacement for Q024–Q028 and Q030–Q031. It retrieved one correct version-specific evidence chunk for each of the 11 questions.

## Adjudication changes (raw data and original scores unchanged)

- **Q021 / System C:** incorrect → correct. Its selected version is original and its raw answer contains the complete gold text verbatim, including U+2014; the prior U+FFFD explanation was false.
- **Q026 / System C:** incorrect → correct. Words and legal punctuation match; only presentation whitespace after an em dash differs.
- **Q026 / System B:** strict answer remains incorrect because its quoted text copies square-bracket extraction delimiters; the citation support judgment changes from partial to fully supported for the underlying legal provision, supported by Article 174 p.111 and Section 8 p.4.
- **Q031 / System B:** correct → incorrect under the common strict criteria. The question asks which verified version and rule; the answer gives the rule but identifies no version.
- **Q032 / A, B and C:** the separate adjudicated CSV labels each `coverage_test_only`, not a normal substantive score. The test's expected/executed behavior is documented separately below; original Q032 score rows remain unchanged.

The separate adjudicated CSV includes each original judgment, adjudicated judgment, change flag and reason.

## Retrieval@5 and citations

For B, a conservative question-level **complete required-evidence-at-5** check is 4/11 (36.4%): Q024–Q027. Q030 is partial: replacement Article text is retrieved, but not the transition annotation. Q031 is partial: current rule text is retrieved, but no version ID/evidence-coverage metadata exists in the static index. Article 174 operative-text passage recall is 5/9 (55.6%) across Q021–Q026, Q029–Q031: Q024, Q025, Q026, Q030 and Q031 retrieve the current Article text; the 1949 original text is absent for Q021–Q023 and Q029. These are manual evidence-requirement checks, not a benchmark-native chunk-ID recall measure, because several gold evidence entries have no static chunk ID.

Transition evidence needed for Q027/Q028/Q030/Q031: B retrieves the Article 174 footnote annotation for Q027 in chunk 65f; it does not retrieve the effective-date annotation for Q028/Q030, and static B has no canonical cutoff metadata for Q031. C's temporal retrieval recall for expected version chunks is 11/11.

B has six citation-bearing responses/explanations in this subset; all IDs resolve. Three are fully supported (Q024, Q026's legal content, Q027); three are partial (Q022, Q028, Q031). Q024's cited `chunk-a800...` does contain Section 8 Article 174 text in addition to the earlier Article 85 material. Q022 citations support the explanation that retrieved evidence is substituted text, not the requested original rule. Q028 proves substitution but not its effective date. Q031 supports the six-month rule but not version identification. B gives uncited substantive answers on Q023 and Q025; Q021/Q029/Q030 are abstentions. C has nine visible, fully supported temporal citations (9/11); Q023 and Q025 omit answer-level citations despite evidence in the logs. A has no citation metric by design.

## Research interpretation

1. **Higher temporal validity in this subset?** Yes: C 11/11 (100%), A 7/11 (63.6%), B 5/11 (45.5%).
2. **Better temporal citation support than B?** Yes descriptively: C 9/11 fully supported visible citations; B 3/11. This is not a broad comparative estimate.
3. **Does selection guarantee correct generation?** No as a general principle; the measures are separate. Here, after adjudicating Q021/Q026, C's 11/11 selections correspond to 11/11 correct answers. That narrow result cannot establish general reliability. A/B demonstrate correct temporal state with other factual errors, abstentions, retrieval gaps and citation omissions.
4. **Remaining errors:** A wrong date/version on Q021/Q028; incorrect historical rule/power claims Q022/Q023; wording errors Q026/Q030/Q031. B lacks original text, applies the wrong version on Q023, misses effective-date evidence Q028, abstains on five temporal items, has exact-quote delimiter noise Q026, and omits the version in Q031. C omits visible citations Q023/Q025; its unrelated fallback/refusal defect on Q010/Q011/Q019/Q020 is outside this temporal subset.

## Held-out status and conclusion

This is **not genuinely held out**. Q001–Q020 were used in prior pilots/failure analysis. Q021–Q032 were authored after Article 174 versions and boundary retrieval had been implemented/tested, and directly exercise those known records/cutoffs. Treat the results as development/diagnostic evidence. The observed subset is directionally consistent with partial support for the hypothesis, but the overall research claim remains **inconclusive**. Freeze systems and rubric, then test prospectively on an independent set from other source-verified timelines not used in implementation/debugging. Do not invent or use unverified histories to fill the set.
