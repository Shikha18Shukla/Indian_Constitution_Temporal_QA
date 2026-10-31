# Updated Research Conclusion — Development and Prospective Held-Out Evidence

## Research question

For date-dependent questions about selected provisions of the Constitution of India, does version-aware temporal retrieval improve temporal validity and citation correctness compared with a Base LLM and Static RAG?

## Previously adjudicated development evidence

The development Article 174 subset Q021–Q031 contained 11 questions. The adjudicated report records temporal-validity accuracy of System A 7/11 (63.6%), System B 5/11 (45.5%), and System C 11/11 (100%). System C selected the expected Article 174 version in all 11 cases. For that subset, fully supported answer citations were recorded for System B on 3/11 and System C on 9/11. These are development results for one Article, not a broad or independent confirmation. Q032 remains a separate evidence-cutoff control and is not part of the substantive denominator.

## Prospective held-out run

The successful live run is execution `20261031T084946583103Z-5efff8b3`, manifest `b87ac71c2a5b1c9190a270aadf61302942ae422dad5acf40bb8a601dea2809cd`. Its summary reconciles to 30 completed, zero failed, zero run-level abstentions, and zero skipped: ten completed outputs per system on Q033–Q042. The earlier failed attempt `20261031T083022845114Z-a2028157` was a transient environment failure; it is not the final demonstration result.

The runner passed identical question wording and reference dates to A, B, and C. C’s temporal citation IDs resolve to `174_original_1949` for Q033–Q036 and `174_first_amendment_s8` for Q037–Q042. These intervals are respectively `[1950-01-26, 1951-06-18)` with evidence through 1951-06-17, and `[1951-06-18, null)` with evidence through 2026-05-01. The JSONL runner export does not preserve a separate `selected_version_ids` field, so this is citation-to-canonical-record mapping, not direct selector telemetry.

C answered Q033–Q039 with substantive Article 174 claims grounded by its version-specific citation. On Q040–Q042, C’s answer text stated that the original comparator was not present in the date-eligible evidence. Those are three answer-content refusals within completed runs, not wrapper abstentions or failures. The questions require comparing both versions, while the existing System C condition retrieves only the version eligible on the reference date. This is a demonstrated scope limitation.

A and B also answered some questions correctly. A answered several original-text items but made a wrong version claim on Q033 and a wrong cross-version comparison on Q040; it added an unsupported amendment-history claim on Q038. B answered Q037–Q039, while its answer text refused Q033–Q036 and Q040–Q042 because its retrieved context did not supply the requested original-version comparison. B’s cited IDs resolve to real static-index passages; those passages are largely the consolidated 2026 Article and First Amendment replacement text. They do not establish the original wording required for the historical comparison items. A’s no-citation behavior is part of the Base LLM condition and is not scored as a citation defect.

## Citation and retrieval evidence

The citation provenance audit established that static citations resolve to actual SQLite chunks and temporal citations resolve to real Article-version passages with source metadata. In the held-out run, C’s temporal IDs identify the expected date-eligible passage, but for Q040–Q042 the replacement passage alone cannot support the original side of the requested comparison. B’s citation IDs resolve, but a resolved citation is not automatically supporting evidence for the historical claim. Citation support therefore remains distinct from version selection and answer correctness.

The held-out runner output does not contain full top-k retrieved-passage arrays for B or a separate selector telemetry field for C. Retrieval recall@k and direct logged selector accuracy cannot be calculated from this export. No such metrics are estimated here. The derived `held_out_full_comparison.json` has mojibake in some expected-answer quotation marks; the UTF-8 benchmark JSON remains the source of truth. The raw run output and benchmark have not been changed.

## Research conclusion

**Overall evidence remains inconclusive, with descriptive results supportive of temporal RAG on the single-version Article 174 questions.** The development subset favored C on temporal validity and citation support, and in the prospective run C’s temporal citations map to the appropriate historical or replacement text on Q033–Q039. However, the set is small, focused on one Article and one amendment transition, and not fully independent or blinded: Article 174 and System C had already been implemented and tested before Q033–Q042 were run. Baselines sometimes answer correctly, and the comparison questions Q040–Q042 expose a limitation of the current one-date/one-eligible-version retrieval condition.

These observations do not prove that the research hypothesis holds generally. They do not establish broad performance across other Articles, amendments, or legal domains. A confirmatory claim would require prospective evaluation on independently verified Article timelines and questions not used during system development, while preserving the approved three-system methodology.

## Reproducibility paths

- Successful prospective run: `results/benchmark_runs/held_out_article174/b87ac71c2a5b1c9190a270aadf61302942ae422dad5acf40bb8a601dea2809cd/20261031T084946583103Z-5efff8b3/`.
- Held-out question set: `benchmark/held_out_article174_questions.json`.
- Held-out run summary and manifest: `summary.json`, `manifest.json` in the run directory.
- Raw outputs: `system_a.jsonl`, `system_b.jsonl`, `system_c.jsonl` in the run directory.
- Development adjudication: `results/evaluation/adjudicated_per_question_scores.csv` and `results/evaluation/article174_temporal_comparison.md`.
- Citation provenance review: `results/evaluation/citation_provenance_audit.md`.
