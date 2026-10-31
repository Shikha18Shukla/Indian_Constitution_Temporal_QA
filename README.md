# Temporal-Aware Evidence-Grounded Retrieval for Legal Question Answering

**Research Project | AI/ML | NLP | Generative AI | RAG | LegalTech**

## Overview

Legal question-answering systems based on Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) can provide useful answers to legal questions. However, legal information is not static. Constitutional provisions can be amended, inserted, substituted, or omitted over time.

A retrieval system that retrieves the correct provision today may therefore provide an incorrect answer to a question concerning an earlier period.

This project investigates **temporal-aware evidence-grounded retrieval for legal question answering**, with a focus on **Indian Constitutional Law**.

The system aims to identify and retrieve the version of a constitutional provision that was legally applicable at the relevant point in time and use that evidence to generate an answer with traceable legal sources.

---

## Research Problem

Conventional LLM-based and standard RAG-based legal QA systems generally do not explicitly model the temporal validity of legal provisions.

This creates potential problems when:

- A constitutional provision has been amended.
- An Article has been inserted or omitted.
- The wording of an Article has changed.
- A question refers to a historical date.
- Multiple versions of the same legal provision exist.

For example, a question may ask:

> What was the constitutional provision applicable in India in a particular year?

A standard RAG system may retrieve the latest version of the provision instead of the version applicable at that historical point in time.

### Research Question

**Can temporal-aware retrieval improve the temporal correctness and evidence grounding of legal question answering compared with conventional LLM-based and standard RAG approaches?**

---

## Objectives

1. Collect reliable constitutional and amendment documents from authoritative sources.
2. Extract and structure the Constitution of India and Constitutional Amendment Acts.
3. Identify changes made to constitutional provisions by amendments.
4. Construct temporal versions of affected constitutional provisions.
5. Create a version-aware legal corpus with temporal metadata.
6. Develop temporal-aware retrieval for legal question answering.
7. Ground generated answers in retrieved constitutional evidence.
8. Create a benchmark containing temporally sensitive constitutional questions.
9. Compare standard retrieval with temporal-aware retrieval.
10. Evaluate answer accuracy, retrieval effectiveness, citation correctness, and temporal accuracy.

---

## Domain

**Indian Constitutional Law**

The project focuses on:

- Constitution of India
- Constitutional Articles
- Constitutional Amendment Acts
- Historical versions of constitutional provisions
- Amendment-aware temporal retrieval

The initial dataset contains selected major Constitutional Amendment Acts that affect substantive constitutional provisions.

---

## System Architecture and Pipeline

![Project Pipeline](https://github.com/user-attachments/assets/f892692d-61c5-47a9-91c3-dc7ad247a925)

The proposed system follows this workflow:

```text
                    User Question
                         |
                         v
              Temporal Information
                  Identification
                         |
                         v
              Query Understanding
                         |
                         v
             Temporal-Aware Retrieval
                         |
             +-----------+-----------+
             |                       |
             v                       v
       Constitutional           Amendment
          Versions              Metadata
             |                       |
             +-----------+-----------+
                         |
                         v
                 Relevant Evidence
                         |
                         v
                      LLM / QA
                         |
                         v
              Evidence-Grounded Answer
                         |
                         v
             Source + Temporal Information
```

---

## Three-System Experimental Design

The research compares three systems using the same generation model and comparable generation settings.

### System A: Base LLM

System A uses a Gemini model to answer legal questions using parametric knowledge only.

- Receives the legal question and reference date.
- Does not retrieve project documents.
- Does not access the project corpus.
- Does not use a vector database or web search.
- Records model configuration, prompt, outputs and execution metadata.

Successful and failed attempts are recorded in:

`results/system_a/runs.jsonl`

### System B: Static RAG

System B uses a fixed snapshot of the collected constitutional corpus.

- Extracts and chunks constitutional and amendment documents.
- Generates embeddings for the document chunks.
- Uses hybrid lexical and dense retrieval.
- Retains source and Article metadata.
- Generates evidence-grounded answers with retrieved citations.
- Does not apply date-based version filtering.

The static corpus and index are maintained separately from the temporal version dataset.

### System C: Temporal RAG

System C introduces date-aware version selection before retrieval.

- Identifies the reference date in the question.
- Selects eligible constitutional Article versions.
- Applies verified legal validity intervals.
- Applies evidence-coverage constraints.
- Retrieves evidence from eligible versions.
- Generates answers grounded in the selected legal evidence.
- Abstains when sufficient verified evidence is unavailable.

Legal validity intervals follow the half-open convention:

`[effective_from, effective_to)`

Evidence coverage uses an inclusive `verified_through` date. Legal validity and evidence coverage are treated as separate concepts.

Only records with verified status and sufficient evidence coverage are eligible for temporal retrieval.

---

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Generation Model | Gemini API |
| Embedding Model | BAAI/bge-small-en-v1.5 |
| Vector Storage | SQLite |
| Dense Retrieval | Embedding-based similarity |
| Lexical Retrieval | BM25-style retrieval |
| Retrieval Strategy | Hybrid Retrieval with Reciprocal Rank Fusion |
| Data Processing | PyMuPDF, Python |
| Testing | Python unittest |
| Version Control | Git and GitHub |

---

## Dataset and Evidence Management

The project uses constitutional documents and selected Constitutional Amendment Acts.

The data-processing workflow includes:

1. Collecting Constitution and amendment documents.
2. Extracting constitutional text from PDF files.
3. Structuring Articles and amendment metadata.
4. Identifying amendment operations.
5. Constructing historical Article-version records.
6. Recording source provenance and effective dates.
7. Validating legal intervals and evidence coverage.

Historical Article versions are maintained separately from the static consolidated corpus.

Source verification is essential: extracted text, amendment notes and metadata are not automatically treated as authoritative legal evidence.

---

## Benchmark and Evaluation

A benchmark of temporally sensitive constitutional questions is used to compare the three systems.

The evaluation considers:

- Answer correctness
- Temporal validity
- Citation correctness and evidence support
- Retrieval effectiveness
- Unsupported claims
- Abstention behaviour
- Response latency and API usage

The same eligible question wording and reference date are used across the three experimental conditions.

Pending questions that lack sufficient source verification are excluded from evaluation until their evidence requirements are satisfied.

The **development benchmark** is `benchmark/questions.json` (Q001–Q032); these questions have been used during system development, prior pilots, or failure analysis and are not a held-out test set. The separate `benchmark/held_out_article174_questions.json` contains prospective cases Q033–Q042 and is frozen for later evaluation. Article 174 systems and evidence were already developed before these questions were authored, so this set is prospective but not fully independent or blinded. The existing benchmark runner continues to read `questions.json`; it will not execute the held-out file.

---

## Project Structure

```text
Indian_Constitution_Temporal_QA/
│
├── benchmark/
│   ├── questions.json                 # development benchmark Q001–Q032
│   ├── held_out_article174_questions.json # prospective cases Q033–Q042; separate
│   ├── schema.json
│   ├── run_benchmark.py
│   └── validate_benchmark.py
│
├── processed/
│   ├── canonical/
│   │   ├── article_version.schema.json
│   │   ├── article_versions_pilot.json
│   │   ├── source_verification_ledger.json
│   │   └── validate_article_versions.py
│   │
│   └── static_rag/
│
├── raw/
│   ├── amendments/
│   ├── constitution/
│   └── sources/
│
├── systems/
│   ├── generation_settings.py
│   ├── static_corpus.py
│   ├── static_index.py
│   ├── system_a.py
│   ├── system_b.py
│   ├── system_c.py
│   ├── temporal_corpus.py
│   └── temporal_index.py
│
├── tests/
│
├── results/
│
├── .env.example
├── requirements.txt
└── README.md
```

---

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Shikha18Shukla/Indian_Constitution_Temporal_QA.git
cd Indian_Constitution_Temporal_QA
```

### 2. Create a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Set your Gemini API key in `.env`:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL_NAME=gemini-3.5-flash-lite
GENERATION_TEMPERATURE=0.0
MAX_OUTPUT_TOKENS=1024
```

Keep your actual `.env` file and API key private. Never commit secrets to GitHub.

---

## Running the Systems

### System A — Base LLM

```powershell
python -m systems.system_a --question-id Q001 --reference-date 2020-01-01 --question "What does Article 21A provide?"
```

### System B — Static RAG

```powershell
python -m systems.system_b ask --question-id Q005 --reference-date 2026-05-01 --question "What does the current Article 45 direct the State to endeavour to provide?"
```

### System C — Temporal RAG

System C uses the verified Article-version dataset and its evidence-coverage constraints. Records without sufficient verification are excluded from temporal retrieval.

Refer to `systems/README.md` for the system-specific commands and configuration.

---

## Running Tests

Run the complete test suite:

```powershell
python -m unittest discover -s tests -v
```

Validate the canonical Article-version dataset:

```powershell
python processed/canonical/validate_article_versions.py
```

Validate the benchmark:

```powershell
python benchmark/validate_benchmark.py
```

---

## Research Scope and Limitations

This project focuses on selected constitutional provisions and their amendment histories rather than claiming exhaustive historical coverage of every provision of the Constitution.

Historical version records are included in temporal retrieval only when their legal validity and supporting evidence meet the project's verification requirements.

The research distinguishes between:

- Legal validity dates
- Amendment enactment and commencement
- Source publication dates
- Evidence coverage dates

The availability and completeness of primary-source documents may limit the historical periods that can be evaluated.

---

## Research Significance

This project investigates whether explicitly modelling legal time and version validity can improve the reliability of retrieval-augmented legal question answering.

By comparing a Base LLM, Static RAG and Temporal RAG, the research aims to examine the importance of temporal version selection, evidence grounding and source traceability in legal information retrieval.

The proposed approach can contribute to research in:

- Temporal Information Retrieval
- Retrieval-Augmented Generation
- Legal Question Answering
- Evidence-Grounded AI
- Explainable and Reliable AI Systems

---

## Author

**Shikha Shukla**

B.Tech — Artificial Intelligence

GitHub: [Shikha18Shukla](https://github.com/Shikha18Shukla)

**Repository:** [Indian Constitution Temporal QA](https://github.com/Shikha18Shukla/Indian_Constitution_Temporal_QA)

