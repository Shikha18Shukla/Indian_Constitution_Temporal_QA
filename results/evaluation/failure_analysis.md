# Focused failure analysis: Q010, Q011 and Q020

**Scope:** Read-only inspection of the unchanged benchmark, raw A/B/C run records, the same-run System B retrieved chunks, the frozen SQLite index, and local primary-source PDFs. No Gemini calls were made. Run `20261030T173545036179Z-5d548d32`; all three questions use reference date `2026-05-01`.

## Q010 — commencement appointment mechanism

**Question:** Under section 1(2) of the 86th Amendment Act, how was its commencement date to be appointed?  
**Reference date:** `2026-05-01`  
**Expected answer:** The Central Government may appoint the date by notification in the Official Gazette.  
**Gold evidence:** “Section 1(2): the Act shall come into force on such date as the Central Government may, by notification in the Official Gazette, appoint.” (`amendment-86-official`; benchmark verification status `verified`; local `raw/amendments/086_Amendment_2002.pdf`, section 1(2), PDF page 1).

**System A actual answer:** “Under Section 1(2) of the Constitution (Eighty-Sixth Amendment) Act, 2002, the Central Government was to appoint the commencement date by notification in the Official Gazette.” This is correct; no failure.

**System B actual answer:** “The available context is insufficient to answer how the commencement date of the 86th Amendment Act was to be appointed under section 1(2).” It abstains because its prompt requires answers to be supported by retrieved context and to say when context is insufficient.

**System B top five actually retrieved:**

1. `chunk-ce820add9f351a61e2157bff` — `raw/amendments/042_Amendment_1976.pdf`, PDF p. 26; article metadata `None`; score `0.07889344262295082`; `article_match=False`.
   > interim order had been furnished to the party against whom such interim order was made and an opportunity had been given to such party to be heard in the matter, cease to have effect (if not vacated earlier),- (a) on the expiry of a period of one month from the appointed day, if the copies of such pending petition and the documents in support of the plea for the interim order are not furnished to such party before th…
2. `chunk-ee4c4ae4bb314ecea899fe96` — `raw/amendments/044_Amendment_1978.pdf`, PDF p. 10; article metadata `None`; score `0.07762196326288762`; `article_match=False`.
   > has been withdrawn, and the High Court shall on receipt thereof, proceed to dispose of the case in conformity with such judgment.". 22. Amendment of article 150.-In article 150 of the Constitution, for the words "after consultation with", the words "on the advice of" shall be substituted. 23. Amendment of article 166.-In article 166 of the Constitution, clause (4) shall be omitted. 24. Amendment of article 172.-(1) I…
3. `chunk-0a6d3719a7d1c3bb0fb2273b` — `raw/amendments/044_Amendment_1978.pdf`, PDF p. 8; article metadata `None`; score `0.07339305359107338`; `article_match=False`.
   > President shall act in accordance with the advice tendered after such reconsideration.". 12. Amendment of article 77.-In article 77 of the Constitution, clause (4) shall be omitted. 13. Amendment of article 83.-(1) In article 83 of the Constitution, in clause (2), for the words "six years" in both the places where they occur, the words "five years" shall be substituted. (2) The amendments made by sub-section (1) to c…
4. `chunk-255295494983409df8a52851` — `raw/constitution/Constitution_of_India_2024.pdf`, PDF p. 126; article metadata `208`; score `0.06709401709401709`; `article_match=False`.
   > 208. Rules of procedure.—(1) A House of the Legislature of a State may make rules for regulating, subject to the provisions of this Constitution, its procedure and the conduct of its business. (2) Until rules are made under clause (1), the rules of procedure and standing orders in force immediately before the commencement of this Constitution with respect to the Legislature for the corresponding Province shall have …
5. `chunk-b10fc4cdb60d4b618a6e5e90` — `raw/constitution/Constitution_of_India_2024.pdf`, PDF p. 290; article metadata `None`; score `0.06642452597882295`; `article_match=False`.
   > Name Territories 1[19.] Tripura The territory which immediately before the commencement of this Constitution was being administered as if it were a Chief Commissioner’s Province under the name of Tripura 2[and the territories referred to in Part II of the First Schedule to the Constitution (One Hundredth Amendment) Act, 2015, notwithstanding anything contained in clause (d) of section 3 of the Constitution (Ninth Ame…

None is the 86th Amendment Act section 1(2) passage. The relevant source is present in the frozen corpus: `chunk-eb75d49aac3dff04f65a838a`, `raw/amendments/086_Amendment_2002.pdf`, PDF page 1, `article_number: null`. Its indexed text contains the exact appointment clause: “It shall come into force on such date as the Central Government may, by notification in the Official Gazette, appoint.” A read-only search of all 1,123 rows found the passage. Under the repository’s BM25-style lexical formula, it ranks **139th** for Q010’s wording. The Act uses “Eighty-sixth” while the question says “86th,” and the source uses “appoint” while the question says “appointed”; these forms weaken lexical overlap. The hybrid top five consequently omitted the section and surfaced unrelated amendment passages. The problem is retrieval rank, not missing corpus coverage or unsupported gold. The question is clear and asks for the mechanism, not the later appointed date. The gold is fully supported by the local official Act PDF, §1(2), page 1.

**Classification:** retrieval ranking defect; context-constrained generation abstention; source present; question clear; gold supported.

## Q011 — Act title date

**Question:** What date is printed immediately below the title of the Constitution (Eighty-sixth Amendment) Act, 2002?  
**Reference date:** `2026-05-01`  
**Expected answer:** 12 December 2002 is printed below the Act title. This is the Act's stated date and must not be treated as its commencement date.  
**Gold evidence:** “[12th December, 2002.]” (`amendment-86-official`; local `raw/amendments/086_Amendment_2002.pdf`, title page/date line).

**System A actual answer:** “I am uncertain, as I do not have access to the exact text layout and printing details of the Gazette of India for the Constitution (Eighty-sixth Amendment) Act, 2002.” This is an abstention. The System A prompt tells the model to answer directly and state uncertainty if uncertain; its design has no retrieval or document input. The cited local primary source nevertheless prints `[12th December, 2002.]` immediately below the Act title on page 1. The question is not ambiguous and the evidence is not missing. The abstention reflects parametric knowledge/confidence limitations and is consistent with the uncertainty instruction. It is a missed answer under the benchmark, though it avoids guessing. It should not be “fixed” by giving System A access to the source, which would change its condition.

**System B actual answer:** “Based on the retrieved context, the date printed immediately below the title of the Constitution (Eighty-sixth Amendment) Act, 2002 is [12th December, 2002.] [chunk-eb75d49aac3dff04f65a838a].” It correctly reports the printed date and cites `chunk-eb75d49aac3dff04f65a838a`, the retrieved Act PDF page 1 chunk that contains the title date. It does not label that date as commencement. No B failure.

**Gold/source assessment:** Fully supported by the locally available primary Amendment Act PDF, page 1. The expected answer correctly distinguishes the Act’s stated date from commencement.

## Q020 — textual comparison of Articles 14 and 21

**Question:** What wording difference in the beneficiary phrase can be observed between Articles 14 and 21?  
**Reference date:** `2026-05-01`  
**Expected answer:** Article 14 says 'any person'; Article 21 begins 'No person'. Both use person-based wording in these clauses.

**Gold evidence:**

- Article 14: “The State shall not deny to any person equality before the law or the equal protection of the laws within the territory of India.” — `chunk-6100b381e336b62ecb405068`, PDF page 37.
- Article 21: “No person shall be deprived of his life or personal liberty except according to procedure established by law.” — `chunk-d6191916210d8ec466f42f4e`, PDF page 42.

**System A actual answer:**

> Based on Indian constitutional law as of the reference date, the wording difference in the beneficiary phrase between Articles 14 and 21 is as follows:
> 
> * **Article 14** uses the beneficiary phrase **"any person"** ("The State shall not deny to *any person* equality before the law...").
> * **Article 21** uses the beneficiary phrase **"any person"** as well (*"No person* shall be deprived of his life or personal liberty..."). 
> 
> *(Note: If the comparison intended is with Article 15, 16, 19, 29, or 30—which use the terms "citizen" or "any section of the citizens"—please clarify, as both Article 14 and Article 21 actually share the exact same beneficiary phrase: "any person".)*

A quotes Article 21’s “No person” text, then mislabels the phrase as “any person” and asserts the wording is identical. This is a factual inconsistency in generation. The exact clauses make the requested textual distinction clear. “Beneficiary phrase” is somewhat technical, but the question says “wording difference” and the benchmark explicitly makes this a textual, not doctrinal, comparison. No retrieval or corpus coverage issue applies to A.

**System B actual answer:** “Based on the provided retrieved context, there is no mention or text regarding Articles 14 and 21. Therefore, the available context is insufficient to answer the question.” It says the retrieved context contains neither Article and abstains.

**System B top five actually retrieved:**

1. `chunk-f3a0d14fca678233138f872d` — `raw/amendments/025_Amendment_1971.pdf`, PDF p. 1; article metadata `None`; score `0.07624434389140272`; `article_match=False`.
   > THE CONSTITUTION (TWENTY-FIFTH AMENDMENT) ACT, 1971 THE CONSTITUTION (TWENTY-FIFTH AMENDMENT) ACT, 1971 Statement of Objects and Reasons appended to the Constitution (Twenty-fifth Amendment) Bill, 1971 which was enacted as the Constitution (Twenty-fifth Amendment) Act, 1971 STATEMENT OF OBJECTS AND REASONS Article 31 of the Constitution as it stands specifically provides that no law providing for the compulsory acqui…
2. `chunk-82e07463ef08c4a26907faaa` — `raw/constitution/Constitution_of_India_2024.pdf`, PDF p. 298; article metadata `None`; score `0.07508610792192882`; `article_match=False`.
   > in the said sub- paragraph as special pay an amount equivalent to the difference between the salary so specified and the salary which he was drawing immediately before such commencement. 1[(3) Any person who, immediately before the commencement of the Constitution (Seventh Amendment) Act, 1956, was holding office as the Chief Justice of the High Court of a State specified in Part B of the First Schedule and has on su…
3. `chunk-b82b8a15b2e0b751a280983e` — `raw/constitution/Constitution_of_India_2024.pdf`, PDF p. 178; article metadata `251`; score `0.07100855310049893`; `article_match=False`.
   > 251. Inconsistency between laws made by Parliament under articles 249 and 250 and laws made by the Legislatures of States.—Nothing in articles 249 and 250 shall restrict the power of the Legislature of a State to make any law which under this Constitution it has power to make, but if any provision of a law made by the Legislature of a State is repugnant to any provision of a law made by Parliament which Parliament ha…
4. `chunk-5d58cd27ff406256773f01fc` — `raw/constitution/Constitution_of_India_2024.pdf`, PDF p. 187; article metadata `271`; score `0.06925675675675676`; `article_match=False`.
   > 271. Surcharge on certain duties and taxes for purposes of the Union.—Notwithstanding anything in articles 269 and 270, Parliament may at any time increase any of the duties or taxes referred to in those articles 1[except the goods and services tax under article 246A,] by a surcharge for purposes of the Union and the whole proceeds of any such surcharge shall form part of the Consolidated Fund of India. [272. Taxes w…
5. `chunk-8411bde1084882f2d0aea512` — `raw/constitution/Constitution_of_India_2024.pdf`, PDF p. 186; article metadata `270`; score `0.06826144738431798`; `article_match=False`.
   > 1[270. Taxes levied and distributed between the Union and the States.—(1) All taxes and duties referred to in the Union List, except the duties and taxes referred to in 2[articles 268, 269 and 269A], respectively, surcharge on taxes and duties referred to in article 271 and any cess levied for specific purposes under any law made by Parliament shall be levied and collected by the Government of India and shall be dist…

The five results are unrelated passages (25th Amendment statement; Constitution Articles 251, 270, 271 and a schedule passage). None has Article 14 or 21 metadata or the operative text. Yet the frozen index contains both exact chunks, with correct metadata:

- `chunk-6100b381e336b62ecb405068` — `article_number: 14`, `raw/constitution/Constitution_of_India_2024.pdf`, PDF page 37; contains “any person”.
- `chunk-d6191916210d8ec466f42f4e` — `article_number: 21`, same Constitution PDF, PDF page 42; contains “No person”.

The direct retrieval defect is in `systems/static_index.py:143-146`: the Article identifier regex accepts singular “Article” or “Art.” followed by a number, but not plural “Articles”. The question’s “Articles 14 and 21” therefore produces no requested Article identifiers, so the metadata-priority branch at lines 233-252 does not activate and generic hybrid RRF runs. In the exact question’s BM25-style lexical ordering, Article 14 is rank 46 and Article 21 is rank 41, far outside the top five. The miss is not caused by absent text or incorrect metadata. B’s abstention is consistent with the context it received, after the retrieval failure.

**Gold/source assessment:** Fully supported by the local Constitution PDF identified by the benchmark as the 1 May 2026 snapshot: PDF p. 37 (Article 14) and p. 42 (Article 21). Read-only text extraction confirms the relevant phrases; both occur in the indexed chunks. The question is sufficiently clear for the intended comparison. “Compare the opening words” could be a plainer formulation in a future benchmark revision, but this is not a current gold defect.

## System C

System C also abstained on these three questions with `no_verified_version_for_reference_date`. It has no verified temporal records for the requested Articles or the amendment-text facts. Its Article 21A/45 pilot records remain partially verified, and Articles 14/21 have no pilot versions. These abstentions are consistent with the verified-only gate, not substantive answer failures.

## Prioritized improvements supported by evidence

### Actual defects

1. **Recognize plural Article identifiers in System B.** Q020 directly demonstrates that “Articles 14 and 21” bypasses the Article metadata-priority branch despite both correct chunks being present. Preserve suffix-aware matching so Article 21 and 21A remain distinct.
2. **Improve retrieval of amendment-section questions.** Q010’s relevant chunk exists but ranks 139th lexically. Add general query/source matching for Amendment Act names/numbers and legal word forms such as “86th”/“Eighty-sixth” and “appointed”/“appoint”, then validate recall at top five without adding date filtering.
3. **Review Base LLM comparison consistency.** Q020’s answer contradicts its own quoted text. A transparent evaluation check for quote/conclusion consistency is justified; adding retrieval to System A is not.
4. **Separate execution status from answer outcome in evaluation.** System B’s runner marks Q010/Q020 `completed` because generation returned successfully, although both answer texts abstain. Later reporting should preserve successful API execution while separately labeling answer-level abstention; do not rewrite this run.

### Possible future improvements (not defects established here)

- Consider the plainer phrasing “Compare the opening words ‘any person’ in Article 14 and ‘No person’ in Article 21” in a future benchmark version. The existing question/gold remain sufficiently clear and supported.
- Q011’s A abstention follows the existing uncertainty instruction and no-retrieval design. Decide in a future methodology review whether this is an acceptable Base LLM outcome on exact document facts; do not change A’s condition based on this single result.
- Expand verified historical Article records before assessing System C’s temporal answer quality.

No systems, benchmark records, index content or verification statuses were changed. The accompanying JSON includes full top-five chunk text, metadata and corpus matches for reproducibility.
