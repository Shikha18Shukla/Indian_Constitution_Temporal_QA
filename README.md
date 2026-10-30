# Temporal-Aware Evidence-Grounded Retrieval for Legal Question Answering

> **Research Project | AI/ML | NLP | Generative AI | RAG | LegalTech**

## Overview

Legal question-answering systems based on Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) can provide useful answers to legal questions. However, legal information is not static. Constitutional provisions can be amended, inserted, substituted, or omitted over time.

A retrieval system that retrieves the correct provision today may therefore provide an incorrect answer to a question concerning an earlier period.

This project investigates **temporal-aware evidence-grounded retrieval for legal question answering**, with a focus on **Indian Constitutional Law**.

The system aims to identify and retrieve the version of a constitutional provision that was legally applicable at the relevant point in time and use that evidence to generate an answer with traceable legal sources.

---

## Research Problem

Conventional LLM-based and standard RAG-based legal QA systems generally do not explicitly model the temporal validity of legal provisions.

This creates a potential problem when:

- a constitutional provision has been amended;
- an article has been inserted or omitted;
- the wording of an article has changed;
- a question refers to a historical date;
- multiple versions of the same legal provision exist.

For example, a question may ask:

> "What was the constitutional provision applicable in India in a particular year?"

A standard RAG system may retrieve the latest version of the provision instead of the version applicable at that historical point in time.

### Research Question

**Can temporal-aware retrieval improve the temporal correctness and evidence grounding of legal question answering compared with conventional LLM-based and standard RAG approaches?**

---

## Objectives

The major objectives of this project are:

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

The project specifically focuses on:

- Constitution of India
- Constitutional Articles
- Constitutional Amendment Acts
- Historical versions of constitutional provisions
- Amendment-aware temporal retrieval

The initial dataset contains selected major Constitutional Amendment Acts that affect substantive constitutional provisions.

---

## Proposed System

The proposed system follows the pipeline:

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
       Constitutional          Amendment
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

## System A: Base LLM

System A sends only the legal question and its reference date to the configured Gemini model. It does not retrieve project documents, access the project corpus, use a vector database, or enable web search/tools. Successful and failed attempts are appended to `results/system_a/runs.jsonl`.

Install the dependencies from the repository root:

```powershell
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set `GEMINI_API_KEY` to the key created in Google AI Studio. The `.env` file is ignored by Git. `GEMINI_MODEL_NAME`, `GENERATION_TEMPERATURE`, and `MAX_OUTPUT_TOKENS` configure generation. The same settings module is intended for Systems B and C.

Run a question:

```powershell
python -m systems.system_a --question-id Q001 --reference-date 2020-01-01 --question "What does Article 21A provide?"
```

Run the mocked tests (no API key or network call required):

```powershell
python -m unittest discover -s tests -v
```
