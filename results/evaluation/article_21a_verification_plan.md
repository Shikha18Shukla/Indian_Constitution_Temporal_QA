# Article 21A historical timeline: source-verification plan

**Purpose:** Plan the primary-source checks needed to establish Article 21A’s original absence, insertion, commencement mechanism, appointed commencement date, and half-open validity intervals. This is a planning document only. The canonical dataset, dates, statuses, schemas, and code were not changed; no record is marked verified.

## Current conclusion

The repository supports important parts of the timeline, but does **not** yet establish the complete historical intervals to the project’s source-verification standard. All pilot records remain `partially_verified`.

The leading proposed states use half-open intervals:

- **Not in force:** `[1950-01-26, 2010-04-01)` with null text.
- **Inserted Article in force:** `[2010-04-01, null)` with the Article 21A text. Here `null` means no later end boundary has been established in the record; it does not prove perpetual validity or validity beyond the latest checked source endpoint.

The first interval requires proof both that Article 21A was absent when the Constitution commenced and that no intervening amendment inserted it before 1 April 2010. The second requires the insertion text, the actual appointed commencement date, and a post-insertion history check through a stated endpoint.

## Claim-by-claim evidence map

| Claim to establish | Exact evidence needed | Evidence currently present | Primary/corroborative status | Remaining unresolved claim |
|---|---|---|---|---|
| **1. Article 21A was absent from the original Constitution** | Inspect the authoritative original Constitution’s Article sequence around Articles 21–22 and establish that no Article 21A appears there. | `raw/sources/Constitution_of_India_English_1949.pdf`: PDF p. 29, printed p. 12. The source ledger records this scan page as visually inspected; Article 21 is followed by Article 22. | The 1949 Constitution scan is a **primary source** for what the original Constitution contained. | This proves absence from the original text, not continuous absence through 31 March 2010. A later constitutional amendment could have changed the Article sequence; the intervening amendment history has not been exhaustively checked. |
| **2. The constitutional provisions commenced on 26 January 1950** | Inspect Article 394’s commencement clause in the original Constitution. | Same original scan: PDF p. 250; printed p. 233 according to the contents, with no folio visible on the inspected leaf. The ledger records visual inspection. Article 394 says remaining provisions commence on 26 January 1950. | The original Constitution is a **primary source** for its commencement clause. | Article 394 establishes the Constitution’s commencement rule; combined with the original absence it supports the start of the proposed not-in-force state. It does not establish the rest of that interval. |
| **3. The 86th Amendment Act inserted Article 21A and supplies its operative words** | Inspect section 2, including the words directing insertion after Article 21 and the exact provision text. | `raw/amendments/086_Amendment_2002.pdf`, PDF p. 1, section 2, “Insertion of new article 21A.” It states the insertion instruction and the Article 21A wording. The ledger says the local PDF text was checked and the relevant page visually inspected. | The enacted Amendment Act is a **primary source** for the insertion operation and the text enacted. | The Act says how the Article is to be inserted but, under section 1(2), does not itself assign the actual commencement date. Keep the displayed Article text separate from marginal heading and Act quotation punctuation according to the existing README convention. |
| **4. Section 1(2) delegates commencement to a Gazette notification** | Inspect section 1(2) of the Act. It must show that the Act comes into force on a date appointed by the Central Government by Official Gazette notification. | `raw/amendments/086_Amendment_2002.pdf`, PDF p. 1, section 1(2): “It shall come into force on such date as the Central Government may, by notification in the Official Gazette, appoint.” | The enacted Amendment Act is a **primary source** for the commencement mechanism. | Section 1(2) is a rule authorizing appointment; it does not establish which date was appointed. It must not be used alone to infer 1 April 2010. |
| **5. S.O. 427(E) appointed 1 April 2010** | Obtain and inspect the actual Gazette notification page. Confirm the issue and instrument identity, the notification date and the operative clause appointing 1 April 2010 for the 86th Amendment Act provisions. Record PDF page and printed page only after inspecting that document. | The ledger records official India Code **indexed text** for S.O. 427(E): notification dated 16 February 2010; Gazette of India, Extraordinary, No. 591, publication date 19 February 2010; appointed commencement date 1 April 2010. No PDF page/printed page locator or local hash is available. | The Gazette notification itself is the required **primary source** and is currently missing locally. The official index entry is **official indexed-text evidence**, useful as corroboration but not a locally inspected Gazette page. | The notification text, actual issue page, and its page/folio have not been inspected from the correct Gazette PDF. No locator may be inferred from the indexed text. |
| **6. Pre-insertion interval is exactly `[1950-01-26, 2010-04-01)`** | Combine (a) original absence and Constitution commencement, (b) a complete intervening Article 21A amendment-history check showing no earlier insertion/other state, and (c) the actual S.O. 427(E) appointed date, with section 2 establishing insertion. | Original Constitution pages and the 86th Act are local. S.O. 427(E) date facts are present only as official indexed text. The repository has 18 selected Amendment Act PDFs and 160 extracted operations. | Original Constitution, relevant amendment Acts and Gazette notifications are **primary**. The selected operation JSON and incomplete Act sample are **derivative/incomplete research aids**, not proof of continuity. | No exhaustive record establishes that Article 21A did not arise earlier during 1950–2010. The correct page-level Gazette notice is also unavailable. The old interval end is therefore not fully verified. |
| **7. Post-insertion interval begins on 1 April 2010 and continues through a defined endpoint** | Use the actual Gazette notice for the inclusive start; then check all later constitutional amendments affecting Article 21A through an explicitly stated endpoint. Establish whether `effective_to` remains unknown/null at that endpoint. | The local 86th Act supplies insertion and section 1(2); the official index supplies the appointed date; `raw/constitution/Constitution_of_India_2024.pdf`, PDF p. 42, contains Article 21A in the Constitution identified as of 1 May 2026 and a footnote: inserted by the 86th Amendment Act, section 2, with effect from 1 April 2010. | The commencement Gazette and later relevant Amendment Acts are **primary**. The as-of-2026 consolidated Constitution is an official consolidated source and **corroborates** the text/status printed in that edition; it is not the complete change-by-change history by itself. | No complete post-2010 Article 21A amendment audit through 1 May 2026 is recorded. The `null` end is not evidence of validity after that snapshot or forever. The endpoint convention must be declared. |

## Date distinctions for the source review

Do not collapse these dates or infer one from another:

| Date | Event | Evidence form and status |
|---|---|---|
| **2002-12-12 (12 December 2002)** | Date printed below the title of the Constitution (Eighty-sixth Amendment) Act, 2002 | Local Act PDF, p. 1. The page prints the date but does not label it as “assent.” Existing amendment metadata separately asserts the same date as assent; the title-page date alone does not verify that label. It is not the commencement date. |
| **2010-02-16 (16 February 2010)** | Notification date of S.O. 427(E) | Stated in official India Code indexed text. The correct Gazette page is not locally available/inspected. |
| **2010-02-19 (19 February 2010)** | Publication/issue date of Gazette of India, Extraordinary No. 591 | Stated in official India Code indexed text. The correct Gazette page is not locally available/inspected. |
| **2010-04-01 (1 April 2010)** | Appointed commencement date for the 86th Amendment Act provisions | Stated in official indexed text and corroborated by the as-of-2026 consolidated Constitution’s Article 21A footnote. The actual notification page remains to be inspected. |

Section 1(2) establishes the **mechanism**, not the appointed date. The date printed under the Act title is not evidence of commencement. The notification date, Gazette publication date, and effective commencement date are separate legal events.

## Documents to obtain or re-inspect: checklist

### A. Existing primary documents — re-check and preserve exact locators

- [x] **Original Constitution scan already present:** `raw/sources/Constitution_of_India_English_1949.pdf` (342-page, image-only scan; SHA-256 and file details are recorded in the ledger).
  - [x] Verify Article 21 and the immediate Article 22 sequence on **PDF p. 29 / printed p. 12**. Exact claim: Article 21A does not appear in the original Article sequence.
  - [x] Verify Article 394 on **PDF p. 250 / printed p. 233 per contents**. Exact claim: the remaining provisions commenced on 26 January 1950. Do not represent the contents’ printed page locator as a visible folio on that leaf.
  - [ ] For the audit record, preserve/reconfirm the inspected page images and tie each observation to the existing SHA-256. The original scan proves the original baseline only; it does not prove continuous absence until 2010.
- [x] **86th Amendment Act already present:** `raw/amendments/086_Amendment_2002.pdf` (2-page searchable PDF; checksum recorded in the source ledger).
  - [x] Section **1(2), PDF p. 1**. Exact claim: Central Government may appoint the commencement date by notification in the Official Gazette. This is a mechanism, not the date itself.
  - [x] Section **2, PDF p. 1**. Exact claims: a new Article 21A is inserted after Article 21; record the enacted operative text exactly from the page image, including punctuation. The existing pilot convention excludes the marginal heading and the Act’s enclosing quotation marks from its `text` field.
  - [ ] Reconfirm page-image wording against the pilot text during source sign-off. Preserve the exact local PDF hash and locator already recorded; do not copy line-wrap artifacts as legal spaces.

### B. Missing primary instrument for the 2010 boundary

- [ ] **Obtain the correct official Gazette of India, Extraordinary, No. 591, dated 19 February 2010, containing S.O. 427(E).** The notification is dated 16 February 2010.
  - It must visibly identify S.O. 427(E) and state that the provisions of the Constitution (Eighty-sixth Amendment) Act, 2002 come into force on **2010-04-01 (1 April 2010)**.
  - Record the exact file name, issuing authority/department as printed, publication/issue date, issue number, notification date, PDF page, printed page/folio if visible, text/image status and SHA-256 after obtaining and inspecting the actual file.
  - No PDF or printed page number is known from the indexed text. Leave these locators blank/unknown until the correct document is examined.
- [ ] **Do not use the existing local Gazette candidate as a substitute:** `raw/sources/SO_427_E_2010.pdf` is identified in the ledger as Gazette of India Weekly No. 51 dated 18 December 2010, not Extraordinary No. 591. It does not prove any S.O. 427(E) fact.

### C. Missing historical-completeness evidence

- [ ] **Obtain a complete official primary amendment-history set for 26 January 1950 through 1 April 2010**, or an authoritative historical Constitution with complete Article amendment annotations and effective dates that is adequate to prove the full chain.
  - Exact claim: no earlier amendment inserted Article 21A or otherwise created an Article 21A state between the original Constitution and the effective date of the 86th Amendment.
  - The local `raw/amendments/` directory contains **18 selected Act PDFs**, not the full 1st–85th Amendment Act series. `processed/amendment_operations.json` contains 160 extracted operations from selected sources; absence from that file is not proof of nonexistence.
  - Review relevant Act and commencement sources systematically. Record all candidate operations and dispositions, including explicit “no Article 21A operation” results with source coverage stated; do not rely only on a parser’s no-match result.
- [ ] **Obtain/review complete Article 21A amendment history after 1 April 2010 through a declared cutoff**, using primary Amendment Acts and commencement notifications (or a complete authoritative annotated history backed by those instruments).
  - Exact claim: the inserted wording remained unchanged and in force through the chosen cutoff, if that is the intended dataset scope.
  - The current official consolidated Constitution file is dated as of 1 May 2026 and shows Article 21A plus the 86th Amendment annotation on PDF p. 42. It is useful corroboration for that snapshot, but it does not itself supply the full amendment-by-amendment audit required by the ledger.
  - Explicitly decide whether the record is bounded at the 1 May 2026 snapshot or asserts validity after it. Do not treat `effective_to: null` as “forever.”

## Required timeline decision after evidence review

A reviewer should be able to support each boundary as follows before any verification-status change is considered:

1. **Start:** Original Constitution Article 394 sets commencement of the remaining provisions to 1950-01-26; the original Article 21/22 sequence establishes Article 21A was not in the original text.
2. **Continuity to insertion:** Complete authoritative amendment history proves no earlier Article 21A operation created an in-force version during `[1950-01-26, 2010-04-01)`.
3. **Transition text:** 86th Amendment Act section 2 expressly inserts the quoted provision after Article 21.
4. **Effective transition date:** S.O. 427(E), in the inspected Gazette issue, appoints 2010-04-01. This is the exclusive end of the pre-insertion interval and inclusive start of the inserted state under `[start, end)` semantics.
5. **Post-insertion end/scope:** Complete later-history check establishes the applicable state only through the chosen evidence cutoff. If no later end is found, record null as “no boundary established through this cutoff,” not proof of perpetual validity.

Until these claims have been independently checked against the required documents, retain the existing `21A_pre_86th` and `21A_v1` statuses as `partially_verified`. This plan does not authorize or perform a canonical data update.
