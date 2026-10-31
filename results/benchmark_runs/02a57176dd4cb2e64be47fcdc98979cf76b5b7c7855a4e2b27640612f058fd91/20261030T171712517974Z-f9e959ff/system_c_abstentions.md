# System C abstentions — exploratory pilot

System C enforces a verified-only temporal selector. All four canonical pilot records are partially_verified, so none reaches the eligible temporal corpus. No version is selected, no chunk is retrieved, and generation is not called. These are abstentions under the configured rule, not failed or substantive answers; they do not demonstrate Temporal RAG performance.

Verified threshold: `verified`. Records available: 4; verified: 0. All four pilot records remain partially verified.

| Question | Reference date | Requested Articles | Selected versions | Retrieved chunks | Result |
|---|---|---|---|---|---|
| Q001 | 2026-05-01 | 14 | none | 0 | abstained: `no_verified_version_for_requested_article_and_date` |
| Q002 | 2026-05-01 | 19 | none | 0 | abstained: `no_verified_version_for_requested_article_and_date` |
| Q003 | 2026-05-01 | 21 | none | 0 | abstained: `no_verified_version_for_requested_article_and_date` |
| Q004 | 2026-05-01 | 21A | none | 0 | abstained: `no_verified_version_for_requested_article_and_date` |
| Q005 | 2026-05-01 | 45 | none | 0 | abstained: `no_verified_version_for_requested_article_and_date` |
| Q006 | 2026-05-01 | 14 | none | 0 | abstained: `no_verified_version_for_requested_article_and_date` |
| Q007 | 2026-05-01 | 21 | none | 0 | abstained: `no_verified_version_for_requested_article_and_date` |
| Q008 | 2026-05-01 | 21A | none | 0 | abstained: `no_verified_version_for_requested_article_and_date` |
| Q009 | 2026-05-01 | 45 | none | 0 | abstained: `no_verified_version_for_requested_article_and_date` |
| Q010 | 2026-05-01 | none explicit | none | 0 | abstained: `no_verified_version_for_reference_date` |
| Q011 | 2026-05-01 | none explicit | none | 0 | abstained: `no_verified_version_for_reference_date` |
| Q019 | 2026-05-01 | none explicit | none | 0 | abstained: `no_verified_version_for_reference_date` |
| Q020 | 2026-05-01 | none explicit | none | 0 | abstained: `no_verified_version_for_reference_date` |

Each full System C record is preserved in `system_c_raw.jsonl`, including excluded candidate version IDs/statuses, effective intervals, selection and retrieval fields, and abstention reason. System C made no generation/API calls. The abstentions are expected behavior under the configured verified-only rule and do not demonstrate Temporal RAG answer performance.
