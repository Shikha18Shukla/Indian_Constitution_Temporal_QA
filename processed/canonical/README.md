# Canonical historical Article version pilot

This folder is separate from the original extracted datasets and generators. It contains provisional Article 21A and Article 45 records around the Eighty-sixth Amendment, plus two bounded Article 174 records covering the original text and First Amendment substitution. It does not modify original extraction data or process the other amendment operations.

## Text and interval model

`article_versions_pilot.json` stores Article states over half-open intervals `[effective_from, effective_to)`. An interval includes its start and excludes its end. Adjacent versions meet on the same date; `effective_to: null` means the pilot records no later boundary.

The optional record-level `evidence_coverage` object separates legal validity from the date through which supporting evidence has been verified. `verified_through` is inclusive and must be accompanied by one or more source references (`source_document`, `page_or_locator`, and `claim`). It asserts continuous evidence coverage from `effective_from` through that date; it is not a legal end date. A record without this field remains schema-compatible for legacy data but is ineligible for System C retrieval. Reference dates later than `verified_through` are excluded even when `effective_to` is null. Article 21A and Article 45 currently lack evidence coverage because their continuous histories remain unsupported. Article 174 has bounded coverage only through 1951-06-17 for the original version and 2026-05-01 for the replacement; neither cutoff asserts legal validity beyond its stated interval or snapshot.

The `text` field contains the operative Article text, including its Article number and clause numbering, but **excludes marginal headings/titles**. Thus Article 21A text starts `21A. The State...`; `Right to education` is not included. Article 45 text starts `45. The State...`. This avoids mixing marginal labels into the operative wording. PDF line wraps and the Act's enclosing quotation marks are omitted; internal wording and sentence punctuation are retained. The heading/locator remains in provenance where relevant.

An inserted provision has an explicit prior `not_in_force` state with `text: null`, followed by its text. A substituted Article has the preceding text and replacement text in adjacent records. An omitted provision should retain its final text up to the omission date, then use `provision_status: "omitted"`, `operation_type: "omitted"` and `text: null`.

## Schemas and validation

- `article_version.schema.json` describes one version record.
- `article_versions_dataset.schema.json` describes the complete dataset envelope and reuses the record schema with `$ref` for `records.items`.
- `validate_article_versions.py` validates the dataset-level and record schemas, then applies cross-record interval, provenance date-match and operation/state rules. It uses Python's standard library and implements the JSON Schema keywords used by these local schema files; it does not claim to be a general-purpose JSON Schema implementation.
- `test_article_versions.py` covers valid insertion/substitution/non-in-force states and negative cases for dates, intervals, IDs, provenance, state/text combinations and dataset metadata.

Run from this directory:

```powershell
python validate_article_versions.py
python -m unittest -v
```

## Sources and evidence state

- Amendment text: `processed/amendments_raw/086_Amendment_2002.txt` and the official Legislative Department publication, [Constitution (Eighty-sixth Amendment) Act, 2002](https://www.legislative.gov.in/static/uploads/2025/07/16970eb1a68d4fe46ac40acd783a6c34.pdf). Sections 2 and 3 specify Article 21A's insertion and Article 45's replacement.
- Commencement: Gazette of India S.O. 427(E), dated 16 February 2010, appointing 1 April 2010, available in the [India Code-hosted Gazette PDF](https://www.indiacode.nic.in/bitstream/123456789/4322/1/rte_goi_2009.pdf). Each in-force amendment version's `commencement_evidence.effective_date` must equal `effective_from`.
- Article 45 before substitution: [India Code-hosted Constitution text](https://upload.indiacode.nic.in/showfile?actid=AC_AN_91_1361_00006_00006_1696917644691&filename=constitution_of_india.pdf&type=actfile), printed page 23, displaying the prior wording and a substitution footnote.
- Article 21A before insertion: [Parliament Digital Library record for the 1949 Constitution](https://eparlib.sansad.in/handle/123456789/2495437?view_type=browse). The original PDF has not yet been added and page-checked locally; the corresponding version remains `partially_verified`.

The four Article 21A and Article 45 records remain `partially_verified`. The two Article 174 records are `verified` only within their explicit evidence coverage: the original wording through 1951-06-17, and the First Amendment replacement through 2026-05-01. The official consolidated Constitution Preface and Article 174 annotation support amendment-history coverage through the 2026 snapshot. The First Amendment Gazette facsimile and an explicit primary assent record remain provenance gaps; they are not treated as Article 174 effective-date evidence. No legal validity after 2026-05-01 is claimed. Passing schema and software checks alone does not establish legal-source completeness.

The existing `processed/amendment_metadata.json` incorrectly uses assent day, 2002-12-12, as Amendment 86 commencement. The pilot preserves the Act's assent date only as metadata and uses 2010-04-01 as the effective boundary with the notification reference above.

