# Historical Article source-verification ledger

This ledger records source findings for the historical-version pilot Articles 21A and 45. It is an evidence review, not a replacement Article-version dataset. It does not change `article_versions_pilot.json`, any existing verification status, benchmark answers, Systems A/B/C, or amendment extraction data.

## Priority and benchmark scope

The benchmark's historical questions Q015–Q018 target Articles 21A and 45. Amendment questions Q008–Q010 and effective-date questions Q011–Q014 concern the 86th Amendment Act, 2002, and Articles 21A/45. No other Article is targeted by those question categories. Section 3 of the 86th Amendment Act is the only relevant amendment operation in the current extracted operations file for Article 45; that file is a parser product and not a complete legal history.

## Primary sources located and inspected

| Source | Availability and inspection | Locator and checksum |
|---|---|---|
| Original Constitution, `raw/sources/Constitution_of_India_English_1949.pdf` | Local 342-page image-only scan; cover PDF p. 1 reads “THE CONSTITUTION OF INDIA.” Preamble PDF p. 18 states adoption by the Constituent Assembly on 26 November 1949. No publication imprint or exact publication date is visible on the inspected cover/title pages. | Article 21: PDF p. 29, printed p. 12. Article 45: PDF p. 39, printed p. 22. Article 394: PDF p. 250, printed p. 233 per contents (folio not visible on the inspected leaf). SHA-256 `9d907654a9f800c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007`; 213,220,509 bytes. |
| Constitution (Eighty-sixth Amendment) Act, 2002, `raw/amendments/086_Amendment_2002.pdf` | Two-page searchable-text PDF. Page 1 was rendered and visually inspected; it contains sections 1(2), 2 and 3. Page 2 was also inspected. | Sections 1(2), 2 and 3 are on PDF p. 1; no printed page number is visible. SHA-256: `588aa67f5dc92dba88553ab0348aad7f9eed36b71305997cd21fe5837525f854`. |
| Local Gazette candidate, `raw/sources/SO_427_E_2010.pdf` | 234-page image-only scan. Its cover (PDF p. 1) identifies *The Gazette of India*, Weekly, No. 51, New Delhi, Saturday, 18 December 2010, Part II, Section 3, Sub-section (ii). This is **not** the required Extraordinary Gazette No. 591 dated 19 February 2010. S.O. 427(E) was not established from this local candidate; no substitution was made. | Cover PDF p. 1; printed page number not applicable. SHA-256 `409429e8fb9eada89f79aa78524dd89f6a0945f56bc0fd5dfb975be1bafbd62d`; 8,913,904 bytes. PDF metadata says OmniPage CSDK 15.5 and 2012-03-16 processing dates; those are not Gazette dates. |
| Official India Code indexed Gazette source, `rte_goi_2009.pdf` | The indexed text supplied for the official India Code source identifies S.O. 427(E) and the issue/date details below. The PDF itself was not opened or visually inspected; the local candidate above is a different issue. | Gazette Extraordinary No. 591, published 19 February 2010; S.O. 427(E) dated 16 February 2010; appointed date 1 April 2010. PDF page, printed page and local hash are unavailable and are not asserted. |
| Current Constitution, local `raw/constitution/Constitution_of_India_2024.pdf` | Cover identifies the edition as on 1 May 2026; preface says amendments through the 106th Amendment Act, 2023. The relevant Article 45 page was rendered and visually inspected. | Article 45: PDF p. 54, printed p. 23. Article 21A: PDF p. 42. SHA-256: `4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b`. |
| Official India Code pre-commencement consolidated Constitution | Remote indexed excerpt shows the original Article 45 wording and notes the 86th Amendment substitution was not yet in force. PDF fetch timed out; no local copy or visual page inspection. | Printed p. 23 in indexed text. No local checksum. Corroboration only, not exhaustive primary-Act proof. |

The original Constitution scan visually establishes this exact Article 45 text on PDF p. 39, printed p. 22: “45. The State shall endeavour to provide, within a period of ten years from the commencement of this Constitution, for free and compulsory education for all children until they complete the age of fourteen years.” The original Article 21 page (PDF p. 29, printed p. 12) shows Article 21 followed directly by Article 22; Article 21A is absent from that original sequence. Article 394 appears on PDF p. 250; the contents locator assigns printed p. 233 although a folio is not visible on the inspected page. The printed Article 394 text says Article 394 and listed provisions came into force at once, and remaining provisions came into force on 26 January 1950. These source facts do not establish uninterrupted Article 45 wording through 2010.

The Constitution cover shows only its title; the Preamble records adoption on 26 November 1949. The reviewed pages do not establish an exact publication date or publisher imprint. That distinction is retained in the ledger.

## Article 45 continuity

The current consolidated Constitution's visually inspected printed page 23 shows the replacement Article 45 text and a footnote that it was substituted by section 3 of the 86th Amendment Act, effective 1 April 2010. This is useful corroboration for the current text and amendment reference. It is not used to establish the old Article 45 text.

The original Constitution scan directly supports the wording appearing as Article 45 in the adopted text. The official India Code pre-commencement consolidated-text index also displays that wording and says the 86th Amendment substitution was not yet in force, but its remote PDF has not been visually inspected. This supports the old wording before commencement, while the absence of earlier changes is not established by the selected local operations or selected Act PDFs alone.

## Article 45 amendment-history audit, 1950–2010

### Finding and scope

Only one Article 45-targeting change is identified in the evidence reviewed: section 3 of the Constitution (Eighty-sixth Amendment) Act, 2002, which expressly substitutes Article 45. The local Act PDF (`raw/amendments/086_Amendment_2002.pdf`, PDF p. 1, section 3) was inspected; the section heading says “Substitution of new article for article 45” and the operative text supplies the replacement. No earlier Article 45 amendment operation was found in the repository's 160 extracted operations.

This is not an exhaustive inspection of all 85 preceding primary Amendment Acts. The repository contains only these 18 selected amendment PDFs: 001 (1951), 024 (1971), 025 (1971), 042 (1976), 044 (1978), 052 (1985), 061 (1988), 073 (1992), 074 (1992), 086 (2002), 091 (2003), 093 (2005), 101 (2016), 102 (2018), 103 (2019), 104 (2019), 105 (2021), and 106 (2023). The amendment operations (160), amendments list (18), and metadata list (18) likewise cover a selected subset, not a full Act sequence.

The current official consolidated Constitution (`raw/constitution/Constitution_of_India_2024.pdf`, PDF p. 54) annotates Article 45's substitution to section 3 of the 86th Amendment, effective 1 April 2010. The official India Code pre-commencement consolidated-text search index also displays the original Article 45 wording and says the 86th substitution was not yet in force. Its remote PDF could not be fetched for page-image inspection, so this remains corroboration rather than locally checked primary-page evidence. On the evidence presently available, the sole candidate relevant Act is the 86th Amendment; a complete act-by-act proof that there were no earlier changes remains outstanding.

### False-positive “section 45” references checked

- **42nd Amendment, 1976:** its section 45 (local PDF p. 18) amends Constitution Article 312, not Constitution Article 45. The actual page was visually inspected.
- **44th Amendment, 1978:** its section 45 (local PDF p. 18; contents on p. 5) amends the 42nd Amendment Act by omitting that Act's sections 18, 19, 21, 22, 31, 32, 34, 35, 58 and 59. It does not amend Constitution Article 45. Both pages were visually inspected.
- `processed/amendment_notes.json` contains a parser record assigned to `article=48` whose note tail says “art. 45 (w.e.f. 1-4-2010). 3.” It is a page-note association artifact and is not treated as a second Article 45 event.

### Date distinction and interval decision

The 86th Amendment Act's local PDF p. 1 prints `[12th December, 2002.]` below its title. The page does not label that date as commencement. Section 1(2) says the Act comes into force on a date appointed by Central Government notification in the Official Gazette. The repository metadata's `2002-12-12` same-day commencement claim is therefore not accepted. The official India Code indexed text gives notification date 16 February 2010, Gazette publication date 19 February 2010 / issue No. 591, and appointed commencement date 1 April 2010. The 2026 official consolidated Constitution footnote corroborates the Article 45 effective date. The supplied `raw/sources/SO_427_E_2010.pdf` remains the wrong Gazette issue (Weekly No. 51, 18 December 2010); the correct Gazette PDF page has not been visually inspected, and no page number or hash is recorded for it.

The original scan establishes Article 45 wording on PDF p. 39 / printed p. 22. Official consolidated text corroborates that the 86th replacement was pending before commencement. Nevertheless, because the complete 1st–85th primary Act set is missing and the actual Gazette page has not been visually inspected, uninterrupted validity from 26 January 1950 to immediately before 1 April 2010 is **not yet established to the project's primary-source standard**. The interval remains unresolved and `45_pre_86th` remains `partially_verified`.

## Decisions by proposed version

All four proposals are `partially_verified`. None is fully verified because a version requires both source-supported operative text/state and its complete effective interval.

- `21A_pre_86th`: the original Constitution scan shows Article 21 followed by Article 22; the 86th Amendment section 2 inserts Article 21A. The official index supplies the appointed date, but the all-amendment search for any earlier Article 21A state is incomplete and the Gazette page image is unavailable.
- `21A_v1`: its text is visible in section 2 of the inspected Act page. The official indexed Gazette text supplies 1 April 2010; the PDF page is not visually inspected, and the post-2010 amendment audit remains incomplete.
- `45_pre_86th`: original wording is directly established from PDF p. 39 / printed p. 22, and Article 394 is visible on PDF p. 250. The amendment history audit identifies only the 86th Amendment as a candidate, but the full 1st–85th act-by-act evidence and the Gazette commencement instrument remain incomplete; continuity through 2010 remains unresolved.
- `45_v2`: its text is visible in section 3 of the inspected Act and in the 2026 consolidated text. The official Gazette index supplies the start date; its PDF page is uninspected, and the post-2010 change audit remains incomplete.

The proposed texts are copied into the ledger so reviewers can see which wording is under review. Their presence in this file does not make them legal gold or alter the canonical pilot statuses.

## Data-quality findings left unchanged

- `processed/amendment_metadata.json` labels Amendment 86's commencement as 12 December 2002 (the printed Act date) and `same_day`. Section 1(2) instead delegates commencement to a Gazette notification; the official India Code indexed text gives 1 April 2010 and the local 2026 official consolidation footnote corroborates it; the actual S.O. 427(E) page remains uninspected.
- `processed/amendment_operations.json` labels Article 45 section 3 as `amended`; the Act states it substitutes Article 45.
- All four `article_versions_pilot.json` records remain `partially_verified`.

## Evidence needed before a status change

1. Locate the exact publication/imprint details for the Constitution edition if publication metadata is required; the local cover only supplies the title and the Preamble supplies adoption date. The Article 21, Article 45 and Article 394 pages have now been inspected and recorded.
2. If page-level verification becomes available, inspect the correct official Gazette Extraordinary No. 591 containing S.O. 427(E), then record its notification header, appointed-date clause, printed/PDF page locators and local hash. The indexed dates are already recorded separately above; no locator or hash is inferred.
3. Audit the complete 1st–85th Amendment Act sequence or obtain a locally inspected official pre-commencement annotated Constitution edition sufficient to establish Article 45 continuity.
4. For post-2010 intervals, check the complete later amendment history through the declared corpus endpoint. Define how `null effective_to` is scoped to that endpoint.
5. Keep Act date/assent, Gazette publication, notification date, and commencement date as separate provenance fields. Record hashes for exact source bytes actually inspected.

No code, canonical pilot record, benchmark answer, source extraction, or system implementation was changed by this review. The four pilot verification statuses remain `partially_verified`. The official India Code indexed text is recorded without a PDF page locator, local checksum, or claim of visual verification; the mismatched Gazette scan remains separately identified.
