# Temporal Article pilot: evidence-gap audit

**Scope:** Read-only review of `processed/canonical/article_versions_pilot.json`, `source_verification_ledger.json`, `README.md`, `article_version.schema.json`, and `validate_article_versions.py`. No source records, dates, verification statuses, or code were changed.

## Executive summary

All four records remain **`partially_verified`**. The repository has strong primary-source evidence for the original Article 45 text, the 86th Amendment Act’s Article 21A insertion and Article 45 substitution wording, and the Constitution’s commencement on 26 January 1950. It has official India Code **indexed text** for S.O. 427(E), including the 1 April 2010 appointed commencement date, but not the correct local Gazette PDF/page image. It does not contain a complete amendment-history source set to establish continuous Article 45 wording from 1950 through 31 March 2010, or a complete subsequent history for the two post-2010 open-ended records.

The pilot uses half-open intervals: `[effective_from, effective_to)`. Thus a 2010-04-01 boundary excludes that date from the preceding record and includes it in the replacement/insertion record. `effective_to: null` means no later boundary is established in the record; it must not be read as proof of perpetual validity. The pilot README and ledger say so explicitly.

## Records at a glance

| Version ID | Article | Claimed interval | Claimed legal state/text | Current status | Can be fully verified from sources currently in repository? |
|---|---|---|---|---|---|
| `21A_pre_86th` | 21A | `[1950-01-26, 2010-04-01)` | Not in force; `text: null` denotes that Article 21A did not exist as a provision during the interval | `partially_verified` | **No.** Original sequence and later insertion are evidenced, but the exhaustive intervening history and page-level Gazette evidence are missing. |
| `21A_v1` | 21A | `[2010-04-01, null)` | Inserted operative wording is in force from the appointed date; no end date is established | `partially_verified` | **No, under the ledger’s standard.** Wording and indexed commencement evidence exist, but the Gazette page image and complete post-2010 history/endpoint are missing. |
| `45_pre_86th` | 45 | `[1950-01-26, 2010-04-01)` | Original Article 45 wording remained continuously in force up to the substitution boundary | `partially_verified` | **No.** The original text and start date are supported, but continuity across the intervening period is unresolved. |
| `45_v2` | 45 | `[2010-04-01, null)` | 86th Amendment replacement wording is in force from the appointed date; no end date is established | `partially_verified` | **No, under the ledger’s standard.** Replacement text and current snapshot are available, but page-level Gazette evidence and full post-2010 history/endpoint are missing. |

## Evidence and gaps by record

### 1. `21A_pre_86th` — before Article 21A’s insertion

- **Claimed interval:** `[1950-01-26, 2010-04-01)`.
- **Status:** `partially_verified`.
- **Exact legal claim:** Article 21A was not in force at any time from the Constitution’s commencement up to, but not including, 1 April 2010. The null text is an intentional non-existence state, not unknown wording.
- **Evidence available:**
  - `raw/sources/Constitution_of_India_English_1949.pdf`: the original Constitution scan’s Article 21 sequence on PDF p. 29 (printed p. 12) places Article 22 immediately after Article 21; the ledger records the page as visually inspected and Article 21A absent there.
  - The same scan’s Article 394 on PDF p. 250 (printed p. 233 per the contents; folio not visible on the inspected leaf) establishes that the remaining Constitution provisions commenced on 26 January 1950.
  - `raw/amendments/086_Amendment_2002.pdf`, section 2, PDF p. 1, expressly provides for insertion of new Article 21A after Article 21.
  - The official India Code indexed text for S.O. 427(E) states the 1 April 2010 appointed date; the index entry distinguishes the notification and Gazette issue facts described below.
  - The ledger says no Article 21A operation appears in the repository’s 160 extracted operations, but also says this is selected/incomplete data and not proof of full history.
- **Exact missing primary-source evidence:** An exhaustive authoritative record of the intervening constitutional amendment history sufficient to rule out an earlier insertion, removal, or other Article 21A state during 1950–2010. The 1st–85th Amendment Act PDFs are not all present; only a selected set of 18 Act PDFs and 160 parsed operations are available. Also missing is a locally obtained, page-locatable/visually inspected copy of the actual Gazette instrument S.O. 427(E) in Gazette of India, Extraordinary No. 591, published 19 February 2010.
- **Can current repository sources finish verification?** No, not to the ledger’s rule that primary evidence establish the text/state and full interval. They establish original absence at the original Article sequence and the eventual insertion, but do not exhaustively establish what happened throughout the gap or supply the Gazette page image.
- **Most useful next source:** An authoritative, complete amendment-history source covering the Constitution from 26 January 1950 to 1 April 2010, ideally the official primary Amendment Act/Gazette collection or an official historical consolidation with complete amendment annotations and effective dates. Obtain the correct page-level Gazette copy for S.O. 427(E) as well. A single 1949 scan cannot establish a 60-year interval by itself.

### 2. `21A_v1` — Article 21A after insertion

- **Claimed interval:** `[2010-04-01, null)`.
- **Status:** `partially_verified`.
- **Exact legal claim:** From 1 April 2010, Article 21A’s operative text is: “21A. The State shall provide free and compulsory education to all children of the age of six to fourteen years in such manner as the State may, by law, determine.” No later end boundary is recorded.
- **Evidence available:**
  - `raw/amendments/086_Amendment_2002.pdf`, section 2, PDF p. 1, locally available and visually inspected, contains the insertion instruction and the quoted Article 21A text.
  - `raw/constitution/Constitution_of_India_2024.pdf`, the official consolidated Constitution titled “The Constitution of India [As on 1st May, 2026],” contains Article 21A on PDF p. 42. The ledger records the current text as extractable.
  - Official India Code indexed text for Gazette notification S.O. 427(E) states the commencement date. The local current Constitution footnote also identifies the 86th Amendment insertion as effective 1 April 2010 (the ledger records the relevant current-page evidence).
- **Exact missing primary-source evidence:** The actual Gazette S.O. 427(E) PDF page and stable locator/image for the 1 April 2010 commencement (the official indexed text has no PDF/printed page locator and no local hash); a complete Article 21A amendment-history audit after 1 April 2010 through the declared source endpoint; and an explicit endpoint/snapshot rule for `effective_to: null`. The current 1 May 2026 consolidated text shows Article 21A at that snapshot but, by itself, is not the exhaustive history check identified as outstanding in the ledger.
- **Can current repository sources finish verification?** No, according to the ledger’s verification standard. The provision’s wording is strongly supported, and the indexed commencement fact is available, but the record’s start evidence is only partially verified at page level and its post-2010 continuity/end boundary has not been established.
- **Most useful next source:** The correct page-level Gazette issue containing S.O. 427(E), followed by authoritative amendment Acts/notifications or a complete official Article 21A amendment-history table from 1 April 2010 through 1 May 2026. Define whether the record is a snapshot-bounded version through 1 May 2026 or claims an open interval beyond that date; null alone cannot answer this.

### 3. `45_pre_86th` — original Article 45 before substitution

- **Claimed interval:** `[1950-01-26, 2010-04-01)`.
- **Status:** `partially_verified`.
- **Exact legal claim:** This original wording remained in force continuously from 26 January 1950 until immediately before the substituted Article 45 took effect: “45. The State shall endeavour to provide, within a period of ten years from the commencement of this Constitution, for free and compulsory education for all children until they complete the age of fourteen years.”
- **Evidence available:**
  - `raw/sources/Constitution_of_India_English_1949.pdf`, PDF p. 39 (printed p. 22), visually inspected, directly supports the original Article 45 wording.
  - Article 394 in that scan (PDF p. 250; printed p. 233 per contents) supports 26 January 1950 as the commencement of remaining provisions.
  - The 86th Amendment Act, section 3, PDF p. 1, expressly substitutes a new Article 45.
  - The official India Code indexed text of S.O. 427(E) states the appointed date 1 April 2010. The official current consolidated Constitution also shows the new wording and attributes its substitution to section 3 effective 1 April 2010.
  - The ledger reports that 18 local Amendment Act PDFs were reviewed; no Article 45 operation was found in the selected Acts before Amendment 86. It also identifies and rejects apparent section-45 false positives in the 42nd and 44th Amendment Acts. This is evidence from a subset, not exhaustive continuity proof.
  - An official India Code-hosted pre-commencement consolidated-text source is cited in the pilot and ledger as showing the old wording, but its PDF was not locally obtained or visually inspected. The ledger treats it only as an indexed-text/consolidation cross-check, not as proof of the full interval.
- **Exact missing primary-source evidence:** Complete evidence that no intervening amendment changed, omitted, or replaced Article 45 between 26 January 1950 and the 86th Amendment’s commencement. The repository does not contain every 1st–85th Amendment Act PDF. The cited pre-commencement India Code PDF is not locally available/page-inspected. The actual Gazette page for S.O. 427(E) is also not locally inspected.
- **Can current repository sources finish verification?** No. The old text and start date are directly established, and the 86th Amendment endpoint is strongly supported at Act/index level, but continuous validity is explicitly unresolved in the ledger. Neither the selected operation file nor a current consolidated text proves that no intermediate operation occurred.
- **Most useful next source:** First obtain and visually inspect the cited official India Code pre-commencement Constitution PDF, especially printed p. 23 and its complete Article 45 amendment footnotes. For a primary-source standard, pair that with an exhaustive official 1st–85th Amendment Act/Gazette review (or an official historical consolidation whose annotations establish the complete amendment chain), plus the page-level S.O. 427(E) Gazette copy. This is the record with the largest continuity gap.

### 4. `45_v2` — replacement Article 45 after substitution

- **Claimed interval:** `[2010-04-01, null)`.
- **Status:** `partially_verified`.
- **Exact legal claim:** From 1 April 2010, the substituted operative text is: “45. The State shall endeavour to provide early childhood care and education for all children until they complete the age of six years.” No later end boundary is recorded.
- **Evidence available:**
  - `raw/amendments/086_Amendment_2002.pdf`, section 3, PDF p. 1, locally available and visually inspected; it expressly substitutes the new Article 45 text.
  - `raw/constitution/Constitution_of_India_2024.pdf`, PDF p. 54 (printed p. 23), visually inspected. The current Article 45 wording and its footnote attribute the substitution to 86th Amendment Act section 3 effective 1 April 2010.
  - Official India Code indexed S.O. 427(E) text states 1 April 2010 as the appointed date. It is indexed text only, not an inspected Gazette page.
- **Exact missing primary-source evidence:** The page-level Gazette commencement instrument; a complete authoritative Article 45 change-history review from 1 April 2010 through the selected source endpoint; and a clear endpoint convention for `effective_to: null`. The current consolidated snapshot corroborates the text at 1 May 2026, but the ledger says the full post-2010 history/interval closure has not been performed.
- **Can current repository sources finish verification?** No, not under the ledger’s stated standard. The text and commencement date have strong local/official-index support, but date-page provenance and full post-2010 continuity are outstanding.
- **Most useful next source:** The correct page-level Gazette copy of S.O. 427(E), then an authoritative post-2010 Article 45 amendment-history source through 1 May 2026 (and beyond only if that is the defined scope). The local current Constitution is already useful for the 2026 snapshot but should be paired with complete amendment annotations/Acts rather than treated as proof of all intervening history on its own.

## Date distinctions that must remain separate

The evidence in the ledger supports different events, with different strengths and source forms:

| Date | Meaning | Evidence/status in repository |
|---|---|---|
| 1949-11-26 (26 November 1949) | Constitution adoption statement | Visible in the original scan’s Preamble; this is not its general commencement date. |
| 1950-01-26 (26 January 1950) | Constitution commencement for remaining provisions; start claimed for both baseline states | Article 394 in the visually inspected original Constitution scan, PDF p. 250. |
| 2002-12-12 (12 December 2002) | Date printed below the 86th Amendment Act title | Locally inspected Act PDF, p. 1. `processed/amendment_metadata.json` also asserts this as assent date, but the title-page date itself is not labelled “assent” on the page. Do not infer commencement from it. |
| 2010-02-16 (16 February 2010) | S.O. 427(E) notification date | Official India Code indexed text; actual PDF/page not locally inspected. |
| 2010-02-19 (19 February 2010) | Publication/issue date of Gazette of India, Extraordinary No. 591 | Official India Code indexed text; actual PDF/page not locally inspected. |
| 2010-04-01 (1 April 2010) | Appointed commencement date for the 86th Amendment Act provisions | Official India Code indexed text, corroborated by the local 2026 consolidated Constitution’s amendment annotation; actual S.O. 427(E) Gazette page image/locator is missing locally. |

The local file `raw/sources/SO_427_E_2010.pdf` is **not** the cited S.O. 427(E) issue. The ledger identifies it as Gazette of India Weekly No. 51 dated 18 December 2010, so it cannot supply the missing page evidence for Gazette Extraordinary No. 591.

## What the schema and validator establish—and do not establish

The record schema requires date fields, source references, operation and provision status, and verification notes. The validator checks valid calendar dates, interval ordering and adjacency/overlap, evidence-date matches to interval boundaries, and text/state combinations such as null text for `not_in_force`. These are useful data-integrity checks. They cannot establish that a cited source is authentic, that its page was inspected, that the text is legally operative, or that the amendment history is exhaustive. A passing validation result must not be used to upgrade a `partially_verified` legal record.

## Verification disposition and recommended evidence order

No record is ready to be marked verified from the current evidence ledger. The most efficient next evidence sequence is:

1. Obtain the **correct official Gazette PDF/page** for Gazette Extraordinary No. 591 (19 February 2010) containing S.O. 427(E), dated 16 February 2010; inspect the notification text and record its real PDF/printed locators. This addresses the shared 1 April 2010 interval boundary for all four records.
2. Obtain and inspect the official India Code pre-commencement Constitution PDF cited for Article 45’s old wording (printed p. 23, including amendment annotations); preserve the exact file and source metadata locally.
3. Close Article 45’s 1950–2010 continuity gap with an exhaustive primary Act/Gazette audit or a complete authoritative historical consolidation with full amendment annotations.
4. Establish Article 21A’s pre-insertion history from an authoritative full amendment record, not merely the original 1949 sequence or the selected 160 parsed operations.
5. Complete post-2010 Article 21A and Article 45 change audits through a declared endpoint, then decide whether each record is snapshot-bounded or open-ended. Keep null `effective_to` as “no end established,” not “valid forever.”

Until those evidence checks are actually completed and reviewed, keep all four records at their existing `partially_verified` status. This report makes no status or date determination beyond the source facts and limitations already recorded in the ledger.
