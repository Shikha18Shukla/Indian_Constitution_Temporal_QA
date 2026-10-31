# Citation Provenance Audit

## Scope and outcome

This audit traces citation identifiers from the retrieval indexes through the FastAPI comparison response to the React interface. The API now resolves both `chunk-…` and `temporal-…` identifiers against evidence actually returned for that run. The interface expands each citation and displays the retrieved passage and recorded provenance. Missing metadata is displayed as **“Not available in source metadata”**; the interface does not infer unavailable source facts.

No legal text, canonical version record, benchmark, experiment output, or SQLite index was changed or regenerated.

## Files inspected

- `systems/temporal_index.py`
- `systems/temporal_corpus.py`
- `systems/system_b.py`
- `systems/system_c.py`
- `systems/static_index.py`
- `processed/canonical/article_versions_pilot.json`
- `webapp/app.py`
- `frontend/src/lib/api.ts`
- `frontend/src/types.ts`
- `frontend/src/App.tsx`
- `tests/test_web_api.py`

## Citation generation and resolution flow

### System B

The frozen SQLite index stores each retrieved passage with its `chunk_id`, `chunk_text`, source document, PDF page, Article number, heading/section, locator, and corpus snapshot. System B places those exact IDs in its evidence prompt. The API extracts bracketed `chunk-…` identifiers from the generated answer and resolves each identifier only against that run's returned prompt evidence (falling back to retrieved evidence where appropriate). It returns the ID, a resolved/unresolved flag, and the matching evidence object. A citation mentioned by the model but absent from that run's evidence is retained as unresolved; the API does not fabricate a match.

### System C

System C first selects records that pass the existing verified-status, legal-interval, and evidence-coverage gates. `TemporalArticleIndex` derives each `temporal-…` ID from the version ID, text offsets, and passage text, then carries source reference, Article number, version ID, effective interval, verification status, and evidence coverage in the chunk metadata. Only these selected-version chunks reach retrieval and generation. The API now recognizes the temporal prefix as well as the static prefix and resolves returned IDs against System C's retrieved evidence.

### Frontend

`frontend/src/lib/api.ts` passes through the actual API response; it does not synthesize citations. `frontend/src/App.tsx` renders citation IDs as expandable details with source document, Article/section, page, passage, version, legal interval, and evidence cutoff. A PDF page is read from the explicit `page_number` field or parsed from an existing recorded locator such as `PDF p. 106`; the UI labels the latter as coming from the recorded locator. Other missing fields use the explicit unavailable-metadata label.

## Verified mappings for the requested IDs

| Citation ID | Passage and source | Article / section | Page / locator | Temporal metadata |
|---|---|---|---|---|
| `temporal-b866c870df1726976fa0a678` | Actual Article 174 original-version passage from `The Constitution of India (1949)`, local scan `raw/sources/Constitution_of_India_English_1949.pdf` (SHA-256 `9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007`). Text is taken from the canonical record and chunked without changing its legal characters. | Article 174; original version `174_original_1949` | Article 174, PDF p. 106 (1-based), printed p. 89; canonical `source_locator` | `[1950-01-26, 1951-06-18)`; evidence through inclusive `1951-06-17`; status `verified` |
| `temporal-52328e6b839e4aae3dd6b302` | Actual Article 174 replacement passage from Section 8 of the Constitution (First Amendment) Act, 1951, `raw/amendments/001_Amendment_1951.pdf` (SHA-256 `316dae4a42e11ccab825e47b495a8bf2ff0bebbb8877cfe61ba0756c19d1e9c9`). | Article 174; Section 8; version `174_first_amendment_s8` | PDF p. 4 (1-based), as recorded in the canonical source reference | `[1951-06-18, null)`; evidence through inclusive `2026-05-01`; status `verified` |
| `chunk-b7bfe1824bde4311da347023` | Actual passage in the frozen static index, from `raw/constitution/Constitution_of_India_2024.pdf` (source PDF SHA-256 `4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b`). Its text includes the Article 174 consolidated wording and the existing footnote marker. | Article 174; heading “Sessions of the State Legislature, prorogation and dissolution” | PDF page 111 (1-based); extracted character offsets 307:792 | No version ID, legal interval, or evidence coverage in static index metadata. The static index remains non-temporal by design. |

The static chunk's snapshot identifier is `6bb6c11f1d96dba6041ed6657a0306bc0c67c7b0095b7fa80407b3cf2add1424`; the consolidated PDF SHA-256 is `4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b`. Neither value is a temporal effective date.

### Retrieved passage text

These are the exact `chunk_text` values returned for the three IDs (including the static index's footnote marker and brackets):

**`temporal-b866c870df1726976fa0a678`**

> 174. (1) The House or Houses of the Legislature of the State shall be summoned to meet twice at least in every year, and six months shall not intervene between their last sitting in one session and the date appointed for their first sitting in the next session. (2) Subject to the provisions of clause (1), the Governor may from time to time— (a) summon the House or either House to meet at such time and place as he thinks fit; (b) prorogue the House or Houses; (c) dissolve the Legislative Assembly.

**`temporal-52328e6b839e4aae3dd6b302`**

> 174. Sessions of the State Legislature, prorogation and dissolution.-(1) The Governor shall from time to time summon the House or each House of the Legislature of the State to meet at such time and place as he thinks fit, but six months shall not intervene between its last sitting in one session and the date appointed for its first sitting in the next session. (2) The Governor may from time to time- (a) prorogue the House or either House; (b) dissolve the Legislative Assembly.

**`chunk-b7bfe1824bde4311da347023`**

> 1[174. Sessions of the State Legislature, prorogation and dissolution.—(1) The Governor shall from time to time summon the House or each House of the Legislature of the State to meet at such time and place as he thinks fit, but six months shall not intervene between its last sitting in one session and the date appointed for its first sitting in the next session. (2) The Governor may from time to time— (a) prorogue the House or either House; (b) dissolve the Legislative Assembly.]

### Text fidelity note

The original Article 174 temporal passage contains an em dash (U+2014); the replacement passage uses hyphen-minus separators (U+002D), as recorded from the amendment source. The static consolidated passage contains em dashes (U+2014). These are the stored code points, not a display-only inference. The UI displays the actual passage returned by the relevant index and does not normalize these characters.

## Provenance fields not available on every citation

- Static chunks have no historical `version_id`, effective interval, or coverage cutoff. Those fields correctly show as unavailable for System B.
- The canonical Article 174 records store PDF page information in `source_reference.page_or_locator`; temporal chunk metadata does not have a separate `page_number` field. The UI uses only the explicit locator text to display a page, marked as parsed from that locator.
- A citation that is present in an answer but absent from returned evidence has no resolvable passage or provenance. It remains visible as unresolved, with missing values explicitly shown.
- System A is parametric-only and provides no retrieved evidence. Citation provenance is therefore unavailable for System A unless its answer happens to mention an identifier; such an identifier will remain unresolved.
- The static citation text includes the consolidated edition's footnote marker and surrounding brackets, because that is how the existing indexed passage was stored. This audit leaves the index unchanged.

## Tests and build

Added focused API tests in `tests/test_web_api.py` for passage resolution, non-fabricated citation IDs, actual temporal ID resolution with version metadata, static ID resolution and its absent temporal fields, explicit treatment of missing metadata, and exclusion of partially verified evidence from the API response.

- Focused API tests: **11/11 passed**.
- Full Python test suite: **95/95 passed**.
- Frontend production build (`npm run build`): **passed** (`tsc -b` and Vite build).

The static citation test queries the existing SQLite index with a local deterministic test embedder. It does not rebuild or modify the index and does not download an embedding model. No Gemini calls were made.

## Limitations

The API can resolve only citation IDs in the bracketed `chunk-…` or `temporal-…` format and only when the corresponding passage was returned for that run. Other citation styles are not mapped. Provenance is limited to metadata already present in each source record. The static corpus's replacement glyphs remain an extraction-quality issue; the UI exposes rather than conceals that source text.
