# Scoring methodology note — live run 20261031T073135193342Z-58165fa8

## Scope

This note documents the scoring audit for one live run only. The run was not repeated, and no API calls were made. It does not alter `final_per_question_scores.csv`, `final_summary.json`, raw outputs, benchmark items, or system behavior.

## Gold reference and common criteria

For every eligible question, all three systems receive the same benchmark question and reference date. Scores should be judged against that question's `expected_answer`, `expected_key_facts` (where present), and primary-source `gold_evidence`, using the same question-level criteria for A, B and C:

1. **Factual/key-fact correctness:** all requested central facts are present and no material contrary fact is introduced.
2. **Temporal correctness:** for date-specific items, the legally applicable Article version and interval boundary must be correct. For C, separately verify that its selected version is the expected version and is within both the legal interval and evidence coverage.
3. **Complete operative text:** for questions asking for exact/complete wording, preserve every legal word, clause, punctuation mark and clause order. Permit formatting-only transformations (line wrapping, whitespace, and optional spacing after an em dash before a clause marker) after removing response wrappers, Markdown emphasis, citation tokens and known index footnote delimiters. Do not normalize away differences in words, punctuation marks, dash type, capitalization, clause numbering or operation language.
4. **Abstention:** an answer-content refusal is not a correct substantive answer. Keep it distinct from a run-level abstention and from an API/runner failure.
5. **Citations:** assess B citation-ID resolution separately from evidentiary support. A citation resolves if its ID is among that question's retrieved chunks. Support is complete only when the cited passage(s) substantiate the relevant answer claim. A retrieval-limited refusal may have citations that support the explanation of insufficiency without supporting the requested gold proposition; report that nuance. A has no citation metric by design. For C, record version/source provenance separately from textual correctness.

This rubric uses the same gold facts across systems while respecting their experimental conditions; it does not require citations from A or allow C to bypass verified-only eligibility.

## Counting rules

- **Eligible denominator:** 25 questions for each system (75 scored system-question records total).
- **Strict accuracy:** strictly correct substantive answers divided by all 25 eligible questions. Any answer-content abstention is not correct in this denominator.
- **Answered-only accuracy:** strictly correct substantive answers divided by eligible questions with a substantive answer. Remove answer-content refusals from this denominator; do not treat them as correct.
- **Run-level abstentions:** statuses recorded by the runner/system (C has ten: Q001–Q009 and Q032).
- **Answer-content refusals:** refusal language in the returned answer, including a response whose wrapper status is completed. C adds Q010, Q011, Q019 and Q020, for 14 unique answer-content refusals overall. A has one answer-content refusal (Q032), B has seven (Q010, Q020, Q021, Q022, Q028, Q029, Q030). These counts describe answer text, not API failures.
- **Failures:** no failed runs in the eligible raw outputs. A successful API call that returns a refusal is not a run failure.
- **Skipped:** Q012–Q018 are pending and excluded; seven per system, 21 skipped rows total. They are not in the 75 score rows.

## Text fidelity adjudication for Q021 and Q026

The UTF-8 JSONL strings contain U+2014 EM DASH, and no U+FFFD REPLACEMENT CHARACTER, in the questioned answer text. Terminal output rendered U+2014 poorly; that display artifact was mistakenly described in the evaluation as a replacement glyph.

- **Q021/System C:** the expected operative text is present verbatim in the raw answer, and C selected `174_original_1949`. The score should be correct on the common gold rubric. The recorded incorrect score should be changed only after formal score adjudication; it is not changed by this note.
- **Q026/System A:** the response says “prorogue the Houses or either House,” whereas the expected text is “prorogue the House or either House.” This is a word-level mismatch and remains incorrect.
- **Q026/System B and C:** the operative provision matches the gold after collapsing whitespace and removing presentation/source wrappers. Both use U+2014; neither has U+FFFD. Each has one inserted space after the second em dash before “(a)”; under the formatting-only normalization defined above, the answers are substantively and textually correct. If the project requires literal byte/spacing identity instead, specify that in advance and apply it symmetrically; such identity is not the present benchmark criterion. Proposed score changes are not applied here.

With that normalization, the proposed metric changes would be: A remains 16/25 and 16/24 answered-only; B becomes 16/25 and 16/18; C becomes 11/25 and 11/11. These are prospective calculations, not the published scores. Correspondingly, if Q026 B is judged fully supported, B citation support would be 15 fully supported and 3 partially supported (rather than 14 and 4). The Q022, Q028 and Q032 support limitations remain.

## Citation case adjudication

The four cases labeled partially supported in the existing summary are Q022, Q026, Q028 and Q032. Their IDs resolve to retrieved chunks. Q022's citation supports the answer's statement that the retrieved material is the substituted text, but it cannot establish the original provision requested. Q028's First Amendment section supports the operation, not its effective date. Q032's text citations do not prove coverage beyond the 2026-05-01 snapshot. Q026's consolidated Article chunk (p. 111) and First Amendment section 8 chunk (p. 4) support the current text and its substitution; the original partial classification was based on a false U+FFFD diagnosis and should be re-adjudicated under the same whitespace policy as answer scoring.

## Research-paper readiness

The raw-run accounting is internally reproducible: 25 eligible IDs × 3 = 75 scored rows, 7 pending items skipped per system, 65 completed API calls, ten C pre-generation run-level abstentions, and no API/runner failures. The reported accuracy arithmetic follows its stated denominators, but Q021/Q026 text scoring and Q026 citation support require adjudication. The current report should not be used as final paper results until those score decisions and the Unicode description are corrected and the evaluation artifacts are versioned together.

Even after correction, this is one live run on 25 eligible questions, with only the Article 174 portion enabling temporal evaluation. Treat it as a pilot; do not infer system superiority or broad temporal-RAG performance.
