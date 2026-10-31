# Q032 evidence-coverage abstention analysis

Q032 asks what Article 174 wording System C can substantiate for **2026-05-02**. Its reference date is 2026-05-02. The verified replacement Article 174 record has an inclusive `evidence_coverage.verified_through` cutoff of **2026-05-01**. Its legal `effective_to` is null; that open legal interval does not extend evidentiary support beyond the coverage date.

## System C

The native record logs `abstention_reason=beyond_evidence_coverage`, no selected version, no retrieved chunk IDs/chunks, and no source provenance. `generation_started_at` and generation duration are null. Thus the cutoff gate worked before retrieval and generation: no Article 174 text reached either. This is the expected abstention test result. Q032 is excluded from the substantive Q021–Q031 accuracy denominator.

## Systems A and B

- **A** says it is uncertain about System C's internal evidence. It provides no Article 174 answer and has no corpus access; this does not test evidence-coverage enforcement.
- **B** says its context does not describe System C, then quotes Article 174 from the fixed consolidated snapshot and cites static chunks. The snapshot is as of 2026-05-01; it does not establish that the wording is supported for 2026-05-02. The text citation supports the quoted wording, not the next-day evidence coverage. Do not score this as a supported answer to Q032.

Q032 is therefore recorded separately: C expected coverage abstention; A no answer from parametric knowledge; B static-current-text response without evidence for the requested date. The separate adjudicated CSV labels all three Q032 rows `coverage_test_only`; none is in the Q021–Q031 temporal-validity denominator or treated as a normal substantive legal answer.
