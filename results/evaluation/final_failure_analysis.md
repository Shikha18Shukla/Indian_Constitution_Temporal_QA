# Final failure analysis — live run 20261031T073135193342Z-58165fa8

## Scope and method

This is a read-only audit of the specified live run, its manifest/summary, the three per-system JSONL outputs, the final score CSV/JSON, the benchmark gold entries, and the matching native System B/C logs and retrieved chunks. No benchmark was rerun, no API call was made, and no existing score or raw output was changed.

## 1. System C generated refusals with wrapper status `completed`

For Q010, Q011, Q019 and Q020, the response text explicitly says the available evidence is insufficient. These are **genuine answer-content abstentions**: they are coherent refusal statements, not malformed output, empty output, or API errors. Their wrapper/native run status is `completed`/`succeeded` because Gemini returned text successfully. They do not have System C's structured run-level abstention status or an abstention reason code. Therefore they must be counted separately from the ten run-level abstentions.

| ID | Response meaning | Evidence/routing observed | Assessment |
|---|---|---|---|
| Q010 | Says the verified temporal evidence has no 86th Amendment or section 1(2) information. | No Article identifier was extracted; System C nevertheless selected `174_first_amendment_s8` and retrieved its Article 174 chunk. | A genuine answer-level refusal, and a reasonable non-answer because the question asks about an Amendment Act mechanism outside the Article-version evidence. The irrelevant fallback selection is a routing/evidence-isolation defect. |
| Q011 | Says the evidence has no 86th Amendment/title-date information. | Same empty requested-Article list and unrelated Article 174 version/chunk selection. | Genuine answer-level refusal. It avoids inventing an Act date, but the fallback Article 174 evidence is unrelated and the refusal is not represented structurally. |
| Q019 | Says no evidence for Articles 21A or 45. | Empty requested-Article list; fallback selection is Article 174. | Genuine answer-level refusal. The requested records remain partially verified and are correctly ineligible under System C's verified-only gate. The question's current-snapshot gold is answerable in the static corpus, but System C must not use those unverified versions. Article detection/fallback remains a defect. |
| Q020 | Says no verified text/version for Articles 14 or 21. | Empty requested-Article list; fallback selection is Article 174. | Genuine answer-level refusal. No verified versions for Articles 14 or 21 are available in System C. The refusal is defensible; the unrelated fallback selection and lack of a structured refusal code are defects. |

The four responses are not additional to the ten run-level abstentions by question ID. The ten coded abstentions are Q001–Q009 and Q032; the four generated refusals above are separate. Accordingly, C has 10 run-level abstentions, 4 additional answer-content refusals, 15 calls marked completed by the runner, and 14 total answer-content abstentions across the 25 eligible questions. The 15 completed calls include those four refusal texts and must not be read as 15 substantive answers.

## 2. Q021 and Q026: glyph diagnosis and scoring

The raw JSONL files decode as valid UTF-8. In Q021 and Q026 answers, the dash characters are Unicode em dashes (U+2014); there are **zero U+FFFD replacement characters** in the raw answers. The same is true of the benchmark gold. The `�` appearance in prior terminal output was a display/terminal encoding artifact. It is not evidence of a corrupted API response or file encoding.

### Q021

System C selected `174_original_1949` for 1951-06-17. Its response contains the complete Q021 expected operative text as an exact substring, including the U+2014 em dash. The benchmark gold and raw response agree at that operative-text substring. The current score marks C incorrect because of an alleged replacement glyph; that reason is factually wrong, and the score conflicts with the exact raw-text comparison. This is a **clear scoring defect**, not a substantive legal-answer error or transcription/encoding problem.

System A's Q021 answer is substantively wrong: it supplies the substituted provision for a date before the 18 June 1951 boundary and makes an unsupported temporal assertion. System B abstains because its retrieved context does not contain the original version. Those judgments are unaffected by the glyph finding.

### Q026

System A's response contains a material wording difference: it says “prorogue the **Houses** or either House,” while the benchmark text says “prorogue the **House** or either House.” Its answer remains incorrect under a word- and punctuation-preserving rule.

Systems B and C provide the complete substituted provision. Their answer bodies use U+2014 em dashes, not U+FFFD; the observed textual differences from the benchmark gold are whitespace around clause separators and retrieval wrappers/footnote delimiters in B. After removing wrappers/citations and treating the inserted space after the clause-separating em dash as formatting whitespace, their operative wording matches the gold. Neither changes the words or legal punctuation. Under a defensible verbatim-content rule that ignores whitespace/layout but preserves every word and punctuation character, B and C should be correct. Under a literal byte-for-byte formatting rule they differ, but that rule is not stated in the benchmark criteria and would make line wrapping/spacing decide legal-answer correctness.

The reported Q026 errors for B/C are therefore not supported by the stated “replacement glyph” explanation. A consistent, predeclared normalization policy is needed before any score change. Do not normalize dash type, clause numbering, word forms, or punctuation; normalize whitespace/layout and remove citation/Markdown delimiters only.

The prior report also describes Q030 as having a “corrupted dash glyph.” The raw Q030 answers likewise contain U+2014 and no U+FFFD. That description should be corrected if the report is revised, even though Q030 was not scored incorrect for that reason.

### Proposed rescoring impact — not applied

The existing scores remain unchanged in the evaluation files. If the paper adopts the whitespace/layout-only normalization above:

- Q021 System C is clearly correct: C changes from 9/25 to **10/25** strict accuracy (40.0%) and from 9/11 to **10/11** answered-only accuracy (90.9%).
- Q026 System B and C become correct; System A stays incorrect because of the “House(s)” wording change. B would change from 15/25 to **16/25** (64.0%) strict and 15/18 to **16/18** (88.9%) answered-only. C would change from the Q021 adjustment's 10/25 to **11/25** (44.0%) and from 10/11 to **11/11** answered-only.
- On the same support rule, Q026 B's citations should be considered fully supportive of the operative wording: chunk `chunk-b7bfe1824bde4311da347023` is the official consolidated Article 174 passage (PDF p. 111, metadata `article_number=174`), and `chunk-a8006a35aacce04c0f993b14` contains First Amendment Act section 8's replacement text (PDF p. 4). The report's stated glyph-based partial-support rationale is not accurate. If Q026 is promoted from partial to fully supported, System B's citation summary becomes 15 fully supported, 3 partially supported, 0 unsupported, among 18 citation-bearing answers.

These are proposed impacts only. They are not written into the saved scores.

## 3. System B's four recorded partially supported citation cases

The final summary lists Q022, Q026, Q028 and Q032. All cited chunk IDs resolve to chunks retrieved in the corresponding System B run (18 citation-bearing answers overall resolve 18/18). Resolution does not itself prove the answer.

| ID | Retrieved/cited evidence | What is and is not supported |
|---|---|---|
| Q022 | `chunk-b7bfe1824bde4311da347023` (current consolidated Article 174, p. 111) and `chunk-a8006a35aacce04c0f993b14` (First Amendment Act, p. 4, including s. 8). | The response correctly says the retrieved corpus does not provide the original Article 174 wording and describes the substituted text. The citations support the fact that retrieved evidence is the substituted version, but neither supplies the original annual-meeting rule asked for. Partial support is appropriate for the question's requested gold answer; this is an evidence-coverage/retrieval limitation, not a fabricated substantive answer. |
| Q026 | Same consolidated Article 174 chunk and First Amendment Act s. 8 chunk. | Both passages contain the replacement wording/provenance. The earlier partial classification was attributed to a supposed U+FFFD corruption; that is false. Under whitespace/layout normalization, these citations fully support the operative wording. |
| Q028 | `chunk-a8006a35aacce04c0f993b14`, First Amendment Act p. 4, s. 8. | It proves the substitution operation and replacement text, but not the effective date. The official consolidated annotation stating the 18 June 1951 commencement did not appear in the retrieved top five. Partial support is appropriate. |
| Q032 | `chunk-b7bfe1824bde4311da347023` plus `chunk-a8006a35aacce04c0f993b14`. | These support the quoted Article text and substitution. They do not establish that the text is supported as in force on 2 May 2026 or that System C's evidence cutoff extends to that date. Partial support is appropriate; B's response risks temporal overextension when quoting the 1 May snapshot in response to 2 May. |

Q022 is a cited evidence-insufficiency response, so its partial label means “the citations do not establish the requested original-version facts,” not “the response's explanation is wholly unsupported.” The report should state that distinction.

## 4. Gold criteria and cross-system scoring consistency

All three systems are scored against the same question-specific benchmark `expected_answer`, gold evidence and key facts. The recorded rubric is common: core facts, no material factual error, temporal/version correctness where applicable, exact wording for questions explicitly asking for complete/exact operative text, and abstentions not counted correct in strict accuracy. System A has no citation requirement by design; B citations are assessed separately; C version selection and evidence coverage are assessed separately. This separation is appropriate to the three conditions.

The raw score rows number **75 = 25 eligible questions × 3 systems**, with one row per system/question pair. The run JSONLs contain 32 rows per system, including seven skipped questions each; those 21 skipped rows are not scored. Counts and IDs in the CSV reconcile with the 25 eligible IDs in the manifest. The three systems received identical wording and reference dates for those IDs.

However, application of the common rubric is not fully consistent: Q021 C is judged wrong for a nonexistent U+FFFD despite exact gold-text inclusion; Q026 B/C are judged wrong for whitespace/layout described as glyph corruption, while A's actual “House(s)” word difference is not identified in the final report's Q026 discussion. The claimed citation partial for Q026 rests on the same mistaken glyph reading. These issues warrant a documented adjudication before paper-level reporting.

## Conclusion

The run accounting and 75-row coverage are reproducible from raw outputs. The answer-level refusal distinction is also recoverable and should be retained. The current **score interpretation is not yet sufficiently defensible for a research paper as written** because it contains a demonstrably false Unicode diagnosis and at least one clear per-question scoring error (Q021/System C), plus an unresolved whitespace-normalization decision for Q026 and its citation status.

The experiment can be reported as a pilot after the team adopts a written text-comparison rule and re-adjudicates affected rows without changing raw outputs. Keep the one-run/25-question scope, verified-only System C abstentions, and non-comparative interpretation explicit. Do not claim comparative superiority from these results.
