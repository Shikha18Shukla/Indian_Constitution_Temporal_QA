# Teacher Review Sheet

**Project:** Temporal-Aware Evidence-Grounded Retrieval for Legal Question Answering: An Indian Constitution Law Study Comparing a Base LLM, Static RAG, and Temporal RAG.

**Research question:** For date-dependent questions about selected provisions of the Constitution of India, does version-aware temporal retrieval improve temporal validity and citation correctness compared with a Base LLM and Static RAG?

## Systems and review instructions

- **System A — Base LLM:** Gemini generation using the question and reference date, with no project-corpus retrieval. Citation scoring is not applicable.
- **System B — Static RAG:** Gemini generation with passages from the fixed static corpus. The reference date does not filter that corpus.
- **System C — Temporal RAG:** selects verified Article version evidence inside the legal interval and evidence-coverage cutoff before retrieval and generation.

This sheet separates benchmark gold expectations from actual recorded answers and researcher notes. Output summaries below are faithful summaries, not verbatim replacements; the raw run files remain authoritative. Check the source locators independently and record any correction before approval. No teacher approval has been entered.

## Article 174 source and version reference

| Version | Legal interval (half-open) | Evidence cutoff (inclusive) | Primary source locator |
|---|---|---|---|
| `174_original_1949` | `[1950-01-26, 1951-06-18)` | `1951-06-17` | Constitution of India (1949), Article 174, PDF p.106 (1-based), printed p.89; visually inspected; SHA-256 `9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007`. |
| `174_first_amendment_s8` | `[1951-06-18, null)` | `2026-05-01` | Constitution (First Amendment) Act, 1951, Section 8, PDF p.4; SHA-256 `316dae4a42e11ccab825e47b495a8bf2ff0bebbb8877cfe61ba0756c19d1e9c9`. Supporting official consolidated Constitution: Article 174/footnote, PDF p.111; edition as on 2026-05-01; SHA-256 `4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b`. |

The 1951-06-18 date is the Article-specific effective date shown in the consolidated annotation. The Act’s printed title date, assent date, publication date, and effective date are distinct. The replacement record has no legal end date; its evidence does not extend beyond 2026-05-01.

## Prospective held-out set: Q033–Q042

**Qualification:** these questions were formulated prospectively, but the Article 174 timeline and System C had already been implemented and tested. This set is not fully independent or blinded and must not be described as an external confirmatory evaluation. Q040–Q042 require both historical versions while System C retrieves only the version eligible on the reference date; treat them as diagnostic/limitation tests unless the methodology is separately revised.

### Q033 — 1950-05-01

**Question:** Under original Article 174 on 1 May 1950, which earlier clause qualified the Governor’s powers listed in clause (2)?

**Expected answer / key facts:** The clause (2) powers were subject to the provisions of clause (1).

**Expected version:** `174_original_1949` — [1950-01-26, 1951-06-18) ; evidence through 1951-06-17 inclusive
**Primary source(s):** `raw/sources/Constitution_of_India_English_1949.pdf` — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007.
**Observed System A:** Says original Article 174 had no numbered clauses and therefore no clause (2); contradicts the verified original text.
**Observed System B:** Says the retrieved context lacks original wording and abstains; cites the consolidated Article and First Amendment text, not the original clause qualification.
**Observed System C:** States clause (2) was subject to clause (1), with the original-version temporal citation.
**Citation review:** A has no citations by design. B IDs resolve to consolidated Article 174 (PDF p.111) and First Amendment Section 8 (PDF p.4); neither supports the original clause claim. C temporal ID maps to 174_original_1949, PDF p.106 / printed p.89; supports the answer.
**Use category:** Candidate for final Article 174 question set after teacher review.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q034 — 1950-11-01

**Question:** In original Article 174(2)(a), what words described the Governor’s discretion over the meeting time and place on 1 November 1950?

**Expected answer / key facts:** “At such time and place as he thinks fit.”

**Expected version:** `174_original_1949` — [1950-01-26, 1951-06-18) ; evidence through 1951-06-17 inclusive
**Primary source(s):** `raw/sources/Constitution_of_India_English_1949.pdf` — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007.
**Observed System A:** Quotes the Governor’s discretion as “as he thinks fit” and identifies original clause (2)(a).
**Observed System B:** Misattributes the time/place power to the replacement text’s clause (1), then says original clause (2)(a) is not available.
**Observed System C:** Quotes “at such time and place as he thinks fit” with the original-version citation.
**Citation review:** A has no citations by design. B IDs resolve, but its evidence is consolidated Article text / amendment annotation, not original clause (2)(a). C temporal ID maps to the original Article passage and supports the quote.
**Use category:** Candidate for final Article 174 question set after teacher review.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q035 — 1951-02-01

**Question:** Under original Article 174(2)(c), what legislative body could the Governor dissolve on 1 February 1951?

**Expected answer / key facts:** The Legislative Assembly.

**Expected version:** `174_original_1949` — [1950-01-26, 1951-06-18) ; evidence through 1951-06-17 inclusive
**Primary source(s):** `raw/sources/Constitution_of_India_English_1949.pdf` — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007.
**Observed System A:** Answers “Legislative Assembly.”
**Observed System B:** Says original clause (2)(c) is absent from retrieved context and abstains.
**Observed System C:** Answers “Legislative Assembly” with original-version citation.
**Citation review:** A has no citations by design. B IDs resolve to consolidated/current and First Amendment passages; they do not establish original clause (2)(c). C original-version temporal passage supports “Legislative Assembly”.
**Use category:** Candidate for final Article 174 question set after teacher review.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q036 — 1951-06-16

**Question:** Where did the original Article 174 place both its twice-yearly meeting requirement and its six-month interval rule on 16 June 1951?

**Expected answer / key facts:** Both requirements appeared in clause (1).

**Expected version:** `174_original_1949` — [1950-01-26, 1951-06-18) ; evidence through 1951-06-17 inclusive
**Primary source(s):** `raw/sources/Constitution_of_India_English_1949.pdf` — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007.
**Observed System A:** Places both the twice-yearly meeting rule and six-month rule in original clause (1).
**Observed System B:** Says the original clause placement cannot be established from retrieved passages; cites Section 8 replacement text.
**Observed System C:** Places both requirements in original clause (1), with original-version citation.
**Citation review:** A has no citations by design. B Section 8 citation resolves to the replacement text, not the original clause (1). C original-version temporal passage supports both rules’ location.
**Use category:** Candidate for final Article 174 question set after teacher review.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q037 — 1951-06-18

**Question:** On the first day the substituted Article 174 took effect, did clause (1) say the Governor “may” or “shall” summon the House or each House?

**Expected answer / key facts:** It says the Governor “shall” from time to time summon the House or each House of the State Legislature.

**Expected version:** `174_first_amendment_s8` — [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source(s):** `raw/amendments/001_Amendment_1951.pdf` — Section 8, PDF p. 4 (1-based); SHA-256 316dae4a42e11ccab825e47b495a8bf2ff0bebbb8877cfe61ba0756c19d1e9c9; full page image visually inspected.<br>`raw/constitution/Constitution_of_India_2024.pdf` — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b.
**Observed System A:** Answers “shall” and describes the replacement clause (1) summons.
**Observed System B:** Answers “shall”; cites the consolidated Article, the consolidated amendment footnote, and the First Amendment text.
**Observed System C:** Answers “shall” and cites the replacement-version passage.
**Citation review:** A has no citations by design. B citations resolve to Article 174 (p.111), First Amendment Section 8 (p.4), and an Article 176 indexed passage whose footnote states Article 174 substitution w.e.f. 18-6-1951; together they support “shall” and the boundary. C replacement temporal passage supports the operative word.
**Use category:** Candidate for final Article 174 question set after teacher review.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q038 — 2010-04-01

**Question:** As of 1 April 2010, what two textual qualifications governed the Governor’s summons under Article 174(1)?

**Expected answer / key facts:** The Governor could summon the House or each House at such time and place as he thinks fit, but six months could not intervene between the last sitting in one session and the appointed first sitting in the next.

**Expected version:** `174_first_amendment_s8` — [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source(s):** `raw/amendments/001_Amendment_1951.pdf` — Section 8, PDF p. 4 (1-based); SHA-256 316dae4a42e11ccab825e47b495a8bf2ff0bebbb8877cfe61ba0756c19d1e9c9; full page image visually inspected.<br>`raw/constitution/Constitution_of_India_2024.pdf` — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b.
**Observed System A:** Gives the time/place discretion and six-month rule, then adds an unsupported account attributing changes to the 38th and 44th Amendments.
**Observed System B:** Gives “from time to time” and the six-month safeguard; cites the consolidated Article text, but not a dated interval source.
**Observed System C:** Gives “from time to time” and the six-month safeguard with a replacement-version citation.
**Citation review:** A has no citations by design. B and C cite the Article 174 passage containing the operative text; B’s citation does not itself prove the 2010 date applicability. C’s evidence is the version eligible for that date and supports the requested wording.
**Use category:** Candidate for final Article 174 question set after teacher review.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q039 — 1960-01-26

**Question:** Under substituted Article 174(2)(b), applicable on 26 January 1960, which body is expressly named as the one the Governor may dissolve?

**Expected answer / key facts:** The Legislative Assembly.

**Expected version:** `174_first_amendment_s8` — [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source(s):** `raw/amendments/001_Amendment_1951.pdf` — Section 8, PDF p. 4 (1-based); SHA-256 316dae4a42e11ccab825e47b495a8bf2ff0bebbb8877cfe61ba0756c19d1e9c9; full page image visually inspected.<br>`raw/constitution/Constitution_of_India_2024.pdf` — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b.
**Observed System A:** Answers “Legislative Assembly,” attributing the wording to the substituted provision.
**Observed System B:** Answers “Legislative Assembly,” citing the consolidated Article and First Amendment text; the citations do not explicitly establish the 1960 applicability date.
**Observed System C:** Answers “Legislative Assembly” with the replacement-version citation.
**Citation review:** A has no citations by design. B cited passages support the replacement wording/body, but the cited IDs do not explicitly establish the 1960 date boundary. C replacement temporal citation maps to the date-eligible version and supports the body.
**Use category:** Candidate for final Article 174 question set after teacher review.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q040 — 2020-01-26

**Question:** Compare original Article 174 with the replacement in force on 26 January 2020: where was the Governor’s summoning authority placed, and how did its operative verb change?

**Expected answer / key facts:** Originally, clause (2)(a), subject to clause (1), said the Governor “may” summon the House or either House at a time and place he thinks fit. The replacement places summoning in clause (1) and says the Governor “shall” summon the House or each House at a time and place he thinks fit, subject to the six-month interval rule.

**Expected version:** `174_first_amendment_s8` — [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source(s):** `raw/sources/Constitution_of_India_English_1949.pdf` — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007.<br>`raw/amendments/001_Amendment_1951.pdf` — Section 8, PDF p. 4 (1-based); SHA-256 316dae4a42e11ccab825e47b495a8bf2ff0bebbb8877cfe61ba0756c19d1e9c9; full page image visually inspected.<br>`raw/constitution/Constitution_of_India_2024.pdf` — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b.
**Observed System A:** Incorrectly places original summoning power in clause (1) and attributes the replacement to the Seventh Amendment; the gold says original clause (2)(a), “may”, versus replacement clause (1), “shall”.
**Observed System B:** Says retrieved material lacks the original Article and cannot compare; cites the replacement text.
**Observed System C:** Says only the date-eligible replacement version is in retrieved temporal evidence and cannot compare it to the original; cites replacement passage.
**Citation review:** A has no citations by design. B Section 8 citation resolves and supports replacement text only. C citation resolves to the date-eligible replacement passage only; neither retrieved citation supplies the original comparator.
**Use category:** Diagnostic / limitation test (cross-version comparison; not a standard single-version temporal retrieval item).
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q041 — 2000-01-26

**Question:** Comparing the original Article 174 with the substituted text applicable on 26 January 2000, which express yearly-frequency phrase was removed, and which inter-session safeguard remained?

**Expected answer / key facts:** The original clause (1) expressly required the House or Houses to meet “twice at least in every year.” The replacement no longer states that yearly frequency formula; it retains the rule that six months shall not intervene between the last sitting in one session and the appointed first sitting in the next.

**Expected version:** `174_first_amendment_s8` — [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source(s):** `raw/sources/Constitution_of_India_English_1949.pdf` — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007.<br>`raw/amendments/001_Amendment_1951.pdf` — Section 8, PDF p. 4 (1-based); SHA-256 316dae4a42e11ccab825e47b495a8bf2ff0bebbb8877cfe61ba0756c19d1e9c9; full page image visually inspected.<br>`raw/constitution/Constitution_of_India_2024.pdf` — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b.
**Observed System A:** Identifies the yearly-frequency phrase and six-month safeguard, but paraphrases the original phrase order; the answer says the First Amendment removed it.
**Observed System B:** Says original wording is absent; cites the replacement text, which supports the retained six-month rule but not the original phrase.
**Observed System C:** Says verified date-eligible evidence contains only replacement text and cannot make the comparison; cites replacement passage.
**Citation review:** A has no citations by design. B Section 8 citation resolves and supports the replacement safeguard, not the original frequency phrase. C replacement citation supports only the retained safeguard; original comparator is absent.
**Use category:** Diagnostic / limitation test (cross-version comparison; not a standard single-version temporal retrieval item).
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q042 — 2026-05-01

**Question:** In the original and substituted versions of Article 174, how did the stated object of the Governor’s prorogation power change?

**Expected answer / key facts:** The original clause (2)(b) said “prorogue the House or Houses”; the replacement clause (2)(a) says “prorogue the House or either House.”

**Expected version:** `174_first_amendment_s8` — [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source(s):** `raw/sources/Constitution_of_India_English_1949.pdf` — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007.<br>`raw/amendments/001_Amendment_1951.pdf` — Section 8, PDF p. 4 (1-based); SHA-256 316dae4a42e11ccab825e47b495a8bf2ff0bebbb8877cfe61ba0756c19d1e9c9; full page image visually inspected.<br>`raw/constitution/Constitution_of_India_2024.pdf` — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b.
**Observed System A:** Expresses uncertainty and speculates that the object was conceptually unchanged; it does not identify the textual change from “House or Houses” to “House or either House”.
**Observed System B:** Says the context does not explain a change in object; cites current consolidated Article and First Amendment text, but not original Article text.
**Observed System C:** Says original text is absent from the date-eligible temporal evidence and cannot compare; cites replacement passage.
**Citation review:** A has no citations by design. B citations resolve to consolidated/replacement text and do not support the original wording. C citation resolves to the replacement passage only and cannot support the comparison.
**Use category:** Diagnostic / limitation test (cross-version comparison; not a standard single-version temporal retrieval item).
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

## Development questions Q021–Q031 — previously used during implementation/evaluation

These are useful for source review and classroom discussion, but they are not held out: they informed development and prior evaluation. Do not count them as prospective unseen questions. The summaries below reflect the adjudicated score file and Article 174 temporal comparison.

### Q021 — 1951-06-17

**Question:** What exact operative text did Article 174 contain on 17 June 1951?

**Expected answer / key facts:** 174. (1) The House or Houses of the Legislature of the State shall be summoned to meet twice at least in every year, and six months shall not intervene between their last sitting in one session and the date appointed for their first sitting in the next session. (2) Subject to the provisions of clause (1), the Governor may from time to time— (a) summon the House or either House to meet at such time and place as he thinks fit; (b) prorogue the House or Houses; (c) dissolve the Legislative Assembly.

**Expected version:** `174_original_1949` — [1950-01-26, 1951-06-18) ; evidence through 1951-06-17 inclusive
**Primary source(s):** `raw/sources/Constitution_of_India_English_1949.pdf` — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007<br>`raw/constitution/Constitution_of_India_2024.pdf` — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b
**Observed A:** Uses replacement wording one day before the transition; wrong version.
**Observed B:** Abstains because original text is absent from top retrieved context.
**Observed C:** Returns the original Article operative text; the adjudication corrected its earlier score to correct.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q022 — 1951-06-17

**Question:** Under the original Article 174, how often had the State Legislature to meet, and what maximum gap was specified?

**Expected answer / key facts:** It was to be summoned to meet at least twice in every year, and six months were not to intervene between the last sitting in one session and the appointed first sitting in the next session.

**Expected version:** `174_original_1949` — [1950-01-26, 1951-06-18) ; evidence through 1951-06-17 inclusive
**Primary source(s):** `raw/sources/Constitution_of_India_English_1949.pdf` — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007
**Observed A:** States a twelve-month maximum gap, contrary to the six-month text.
**Observed B:** Abstains; retrieves replacement-era text rather than original.
**Observed C:** States both twice-yearly and six-month requirements.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q023 — 1951-06-17

**Question:** What powers did clause (2) give the Governor under Article 174 on 17 June 1951?

**Expected answer / key facts:** Subject to clause (1), the Governor could summon the House or either House at a time and place he thought fit, prorogue the House or Houses, and dissolve the Legislative Assembly.

**Expected version:** `174_original_1949` — [1950-01-26, 1951-06-18) ; evidence through 1951-06-17 inclusive
**Primary source(s):** `raw/sources/Constitution_of_India_English_1949.pdf` — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007
**Observed A:** Misstates the historical amendment effect and omits the correct original powers.
**Observed B:** Lists replacement-era powers rather than original clause (2) powers.
**Observed C:** Lists the original three powers and clause (1) qualification.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q024 — 2026-05-01

**Question:** What inter-session interval rule appears in the replacement Article 174 as of 1 May 2026?

**Expected answer / key facts:** Six months shall not intervene between the last sitting in one session and the date appointed for the first sitting in the next session.

**Expected version:** `174_first_amendment_s8` — [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source(s):** `raw/constitution/Constitution_of_India_2024.pdf` — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b
**Observed A:** States the six-month non-intervention rule.
**Observed B:** States the rule and cites a retrieved passage.
**Observed C:** States the rule with a temporal citation.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q025 — 2026-05-01

**Question:** Under Article 174 as of 1 May 2026, what may the Governor do under clause (2)?

**Expected answer / key facts:** The Governor may prorogue the House or either House and dissolve the Legislative Assembly.

**Expected version:** `174_first_amendment_s8` — [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source(s):** `raw/constitution/Constitution_of_India_2024.pdf` — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b
**Observed A:** Lists prorogation and dissolution powers.
**Observed B:** Lists both powers, with no answer-level citation in the adjudicated record.
**Observed C:** Lists both powers.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q026 — 2026-05-01

**Question:** What is the complete operative wording of the substituted Article 174 shown in the official Constitution edition as on 1 May 2026?

**Expected answer / key facts:** 174. Sessions of the State Legislature, prorogation and dissolution.—(1) The Governor shall from time to time summon the House or each House of the Legislature of the State to meet at such time and place as he thinks fit, but six months shall not intervene between its last sitting in one session and the date appointed for its first sitting in the next session. (2) The Governor may from time to time—(a) prorogue the House or either House; (b) dissolve the Legislative Assembly.

**Expected version:** `174_first_amendment_s8` — [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source(s):** `raw/constitution/Constitution_of_India_2024.pdf` — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b
**Observed A:** Complete-text answer has a word-level mismatch (“Houses” for “House”).
**Observed B:** Content is supported by citation; strict answer quote retains extraction brackets and was not silently corrected.
**Observed C:** Complete replacement text is correct after presentation-whitespace normalization.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q027 — 2026-05-01

**Question:** What operation did Section 8 of the Constitution (First Amendment) Act, 1951 perform on Article 174?

**Expected answer / key facts:** Section 8 substituted Article 174 with a replacement text.

**Expected version:** `174_first_amendment_s8` — [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source(s):** `raw/amendments/001_Amendment_1951.pdf` — Section 8, PDF p. 4 (1-based); visually inspected; SHA-256 316dae4a42e11ccab825e47b495a8bf2ff0bebbb8877cfe61ba0756c19d1e9c9
**Observed A:** Correctly says Section 8 substituted Article 174.
**Observed B:** Correctly identifies substitution and cites amendment evidence.
**Observed C:** Correctly identifies substitution with temporal citation.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q028 — 2026-05-01

**Question:** From what date did the Section 8 substitution of Article 174 take effect?

**Expected answer / key facts:** The official consolidated Article 174 annotation states that the Section 8 substitution took effect on 18 June 1951 (1951-06-18). The Act’s printed title date is not being substituted for the effective-date evidence.

**Expected version:** `174_first_amendment_s8` — [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source(s):** `raw/constitution/Constitution_of_India_2024.pdf` — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b
**Observed A:** Gives the Seventh Amendment and 1956 date; wrong amendment/date.
**Observed B:** Identifies First Amendment substitution but abstains on exact effective date.
**Observed C:** Gives 18 June 1951 from temporal evidence.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q029 — 1951-06-17

**Question:** Which Article 174 version was in force on 17 June 1951, and what annual-meeting rule did it state?

**Expected answer / key facts:** The original version, 174_original_1949, was in force. It required the House or Houses to be summoned to meet at least twice in every year.

**Expected version:** `174_original_1949` — [1950-01-26, 1951-06-18) ; evidence through 1951-06-17 inclusive
**Primary source(s):** `raw/sources/Constitution_of_India_English_1949.pdf` — Article 174, PDF p. 106 (1-based), printed p. 89; visually inspected; SHA-256 9d907654a9f8000c0629000b6011e8b112a2d2b7f599a3130c618235b2b38f007<br>`raw/constitution/Constitution_of_India_2024.pdf` — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b
**Observed A:** Identifies original version and annual rule.
**Observed B:** Abstains on original version.
**Observed C:** Identifies original version, twice-yearly rule and six-month gap.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q030 — 1951-06-18

**Question:** Which wording of Article 174 applied beginning on 18 June 1951?

**Expected answer / key facts:** The First Amendment replacement, version 174_first_amendment_s8, applied from 18 June 1951. Clause (1) provides that the Governor summons the House or each House at a time and place he thinks fit, subject to the six-month inter-session limit; clause (2) permits prorogation or dissolution as stated there.

**Expected version:** `174_first_amendment_s8` — [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source(s):** `raw/amendments/001_Amendment_1951.pdf` — Section 8, PDF p. 4 (1-based); visually inspected; SHA-256 316dae4a42e11ccab825e47b495a8bf2ff0bebbb8877cfe61ba0756c19d1e9c9<br>`raw/constitution/Constitution_of_India_2024.pdf` — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b
**Observed A:** Has material replacement-text wording errors.
**Observed B:** Abstains despite relevant passages in the corpus.
**Observed C:** Gives the replacement wording from the applicable temporal record.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

### Q031 — 2026-05-01

**Question:** As of 1 May 2026, which verified Article 174 version and operative rule does the documented record support?

**Expected answer / key facts:** The documented version is 174_first_amendment_s8. It requires that six months shall not intervene between the last sitting in one session and the appointed first sitting in the next session.

**Expected version:** `174_first_amendment_s8` — [1951-06-18, null) ; evidence through 2026-05-01 inclusive
**Primary source(s):** `raw/constitution/Constitution_of_India_2024.pdf` — Article 174 and footnote 1, PDF p. 111; Preface, PDF p. 2; SHA-256 4c8e93689ec245e26db08e22b5ff3ad645c98736f0e5b7c8b6638acd7861f85b
**Observed A:** Describes original text as if it were current; wrong version framing.
**Observed B:** Gives current operative rules but does not identify the expected version.
**Observed C:** Identifies `174_first_amendment_s8` and gives the operative text.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

## Diagnostic control: Q032 — not a substantive legal-answer item

**Question:** What Article 174 wording can System C substantiate for 2 May 2026 from its verified Article-version evidence?
**Reference date:** 2026-05-02
**Expected outcome:** System C abstains because the replacement version’s evidence cutoff is 2026-05-01; 2026-05-02 is outside supported evidence coverage. The abstention must not be counted as a substantive correct answer.
**Observed:** A expresses uncertainty about System C; B says its context does not define System C/coverage (while also discussing Article text); C returns an explicit verified-evidence insufficiency answer. The C wrapper abstention was separately logged in the development run.
**Citation verification:** A: N/A. B citations resolve to static Article passages but do not evidence System C’s coverage gate. C: no Article passage is used or cited; the logged C outcome is an evidence-coverage abstention.
**Use category:** Diagnostic / evidence-coverage abstention control; exclude from substantive correctness denominator.
**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

## Proposed correction for teacher-review Q4 only

**Proposed wording:** “Under Article 174 as applicable on 1 January 2000, what is the maximum permitted interval between the last sitting of one session and the date appointed for the first sitting of the next session?”

**Reference date:** `2000-01-01`.

This wording is proposed for the teacher-review material only. It does not edit or replace any wording in frozen `benchmark/questions.json` or any recorded experiment. Expected legal point, subject to teacher review: six months shall not intervene between the specified sittings; replacement Article 174 applies on this date, within evidence coverage. Source: First Amendment Act, Section 8, PDF p.4, and official consolidated Article 174, PDF p.111. No system output or answer citation exists for this proposed wording yet; citation status is not applicable until evaluated.

**Teacher decision:** [ ] Approve as written  [ ] Request correction  [ ] Do not use  
**Comments / legal corrections:** ______________________________________________________  
____________________________________________________________________________

## Teacher review outcome

**Approval recorded:** No. All checkboxes above are intentionally blank pending teacher review.
