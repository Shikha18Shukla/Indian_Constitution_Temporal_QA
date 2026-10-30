# System A — Base LLM

System A uses Gemini as a base model. The request contains one text prompt constructed only from a question and its reference date. No retrieval, database, project documents, corpus context, web search or API tools are configured.

## Setup

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `GEMINI_API_KEY` to a real key from Google AI Studio. Never commit `.env`; it is ignored by `.gitignore`. The checked-in `.env.example` contains only a placeholder.

Settings in `.env`:

| Variable | Default | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | required | Gemini API authentication |
| `GEMINI_MODEL_NAME` | `gemini-3.5-flash-lite` | Configurable Gemini generation model shared across systems |
| `GENERATION_TEMPERATURE` | `0.0` | Sampling temperature |
| `MAX_OUTPUT_TOKENS` | `1024` | Maximum response length |
| `GEMINI_REQUEST_TIMEOUT_SECONDS` | `45` | Maximum time for one Gemini request (valid range: 1–600 seconds) |
| `GEMINI_MAX_RETRIES` | `2` | Retries after the initial request for transient 503/504/network failures (0–2) |
| `GEMINI_RETRY_BACKOFF_SECONDS` | `1.0` | Exponential backoff base, with jitter (0–30 seconds) |

The model name and generation parameters live in `systems/generation_settings.py` so later systems can share these settings without changing the experimental configuration. The SDK timeout applies separately to each request attempt. SDK retries are disabled; the shared client retries only transient 503/504 and network failures, at most twice, using exponential backoff with jitter. Invalid keys, rate limits, invalid requests, and other API errors are not retried. Each experiment still creates one JSONL record with its total attempt count, final status, and per-attempt error details.

Gemini 3.x deprecates sampling parameters including temperature. System A omits `temperature` from the Gemini request for Gemini 3.x models; the existing JSONL `temperature` field is retained as `null` for those runs to show that no temperature override was sent. For other model families, the configured temperature is sent and recorded.

## Run one experiment

From the repository root:

```powershell
python -m systems.system_a --question-id Q001 --reference-date 2020-01-01 --question "What does Article 21A provide?"
```

If `--question-id` is omitted, the CLI assigns a unique ad hoc ID. Before calling Gemini, the CLI prints a waiting message with the model, per-attempt timeout, and transient retry limit. One JSON object per experiment is appended to `results/system_a/runs.jsonl`. Failed runs record `run_status`, `error_message`, attempt count, final status, and per-attempt error details; successful runs contain the requested experiment fields and raw model answer.

## Tests

```powershell
python -m unittest discover -s tests -v
```

Tests inject mocked generation callbacks and do not call Gemini or require an API key.

## System B — Static RAG

System B uses one fixed PDF snapshot: `raw/constitution/Constitution_of_India_2024.pdf` and the extractable text pages in `raw/amendments/*.pdf`. The Constitution filename does not match the cover's edition marker: the PDF says it is current as of 1 May 2026. The Constitution's cover, preface, abbreviations, and table of contents (PDF pages 1–31) are omitted; page 32 onward is indexed. Amendment PDFs with no extractable text are listed as excluded in the index metadata; the pipeline does not run OCR. `processed/articles.json` and `processed/articles_clean.json` are not used because their extraction quality is inconsistent and they lack page locators. The partially verified canonical historical versions are not used.

PDF text is whitespace-normalized, then chunked within each page to about 1,800 characters with 200-character overlap. Short page provisions remain together when under the target size. Each chunk retains its relative source path, source type, 1-based PDF page, article number and heading when confidently detected (otherwise null), text, stable content-derived ID, snapshot hash, and page/character-offset locator. PDF extraction can still contain reading-order, hyphenation, or scan/text-layer defects; check cited PDF pages before treating a retrieved passage as authoritative wording.

FastEmbed's CPU ONNX implementation uses `BAAI/bge-small-en-v1.5` (384 dimensions; first use downloads the small model files). A single SQLite file stores chunk text, metadata, normalized vectors, the embedding model name, source hashes, exclusions, and corpus snapshot ID. Search computes exact cosine similarity over the local snapshot. This avoids a separate database service or a heavyweight framework and is suitable for this corpus size; no date filter is accepted by the retrieval function.

Install the added PDF and embedding dependencies with the repository requirements, then build the index from the repository root:

```powershell
python -m pip install -r requirements.txt
python -m systems.system_b build-index
```

The first build may need network access to download the embedding model. It writes `processed/static_rag/index.sqlite3`; the index is reproducibly rebuilt from the PDFs and records SHA-256 hashes for the fixed corpus inputs. Optional build settings include `--embedding-model`, `--chunk-size`, `--overlap`, `--batch-size`, and `--index-path`.

Run a question using the shared `.env` Gemini key and generation settings:

```powershell
python -m systems.system_b ask --question-id Q001 --reference-date 2020-01-01 --question "What does Article 21A provide?"
```

`--top-k` overrides `SYSTEM_B_TOP_K` (default 5). Reference date is passed to the answer prompt and logged, but never passed to retrieval. Each success or failure is appended once to `results/system_b/runs.jsonl` with retrieved text, scores, provenance, snapshot, generation settings, total API attempt count, final status, and any per-attempt errors. System B reuses System A's Gemini generation client and retry settings; it makes no web calls and supplies no API tools.

Retrieval combines exact dense cosine ranking with dependency-free BM25-style lexical ranking using weighted Reciprocal Rank Fusion (lexical rank weight 4, RRF constant 60). Article number and heading metadata are included in lexical matching, so literal inserted identifiers such as `21A` can match even when the embedding model ranks a generic passage higher. Logged `retrieval_score` is the fused rank score; `dense_score`, `dense_rank`, and `lexical_rank` retain the component evidence. Constitution article metadata is carried across page breaks when the next page continues an Article, and reset at structural page headings.

When a question explicitly names an Article (including suffixes such as `21A`), System B places all matching Constitution Article chunks before general hybrid results. If those matches span multiple chunks, it returns all of them even when that exceeds `--top-k`, preserving source page and chunk order so a multi-part provision is not cut off. Exact metadata matches receive an explicit Article-match score boost; `hybrid_score` preserves the unboosted RRF score. If no Article metadata matches, the normal hybrid ranking is used. This is identifier-based retrieval only; it does not apply date filters.

Inspect retrieval without making a Gemini call:

```powershell
python -m systems.system_b diagnose-retrieval
```

This prints the Article 14, 19, 21, 21A and 45 diagnostic questions, retrieved text, provenance and Article metadata, final and unboosted hybrid scores, and dense/lexical ranks. Use `--index-path` to inspect another index and `--top-k` to change the number of general hybrid fallback chunks.

`--max-context-tokens` overrides `SYSTEM_B_MAX_CONTEXT_TOKENS` (default 4000). The budget is an approximate `ceil(characters / 4)` over each complete evidence block, including its citation and source locator labels. A passage and its metadata are included together or omitted together; retrieved text is never silently truncated. Run diagnostics report retrieved and included chunk counts, individual chunk lengths, character/token estimates, prompt length, retrieval completion/elapsed time, and generation start/elapsed time to stderr and in the JSONL context diagnostics. Token counts are estimates rather than Gemini tokenizer measurements.

Run all mocked tests, including System A and canonical-versioning checks:

```powershell
python -m unittest discover -s tests -v
python -m unittest discover -s processed/canonical -v
```

System B tests use temporary PDFs, deterministic mocked embeddings, and mocked generation callbacks; they do not download FastEmbed weights or call Gemini.

## System C — Temporal RAG

System C is a separate date-aware pipeline. It loads and validates `processed/canonical/article_versions_pilot.json` with the dataset schema and canonical semantic validator. **Only records whose `verification_status` is exactly `verified` are eligible** (`VERIFIED_STATUS_THRESHOLD` in `systems/temporal_corpus.py`). `partially_verified` and `unverified` records are excluded before the temporal index is built. The current four-record pilot remains useful for inspection, but all four records are partially verified, so it currently supplies no evidence to answer generation; System C abstains without calling Gemini.

For each question, the reference date is checked against the half-open interval `[effective_from, effective_to)`: start is inclusive, end is exclusive, and `effective_to: null` has no recorded end. Only the selected verified version records enter `TemporalArticleIndex`; date filtering therefore happens before chunk retrieval and ranking. An explicit Article identifier narrows this verified set first, including exact suffix matching (`21` is distinct from `21A`). Article chunks retain version ID, interval, verification status, source document, locator, amendment, and section. Multi-chunk versions are returned together for explicit Article questions and list/comprehensive questions. The temporal index uses the same `BAAI/bge-small-en-v1.5` CPU embedder and BM25 plus weighted RRF configuration as System B when eligible text exists; no new model is introduced. It builds its small selected-version index in memory and does not alter System B's fixed SQLite index.

`effective_from` and `effective_to` define legal eligibility using `[effective_from, effective_to)`. A record must also include `evidence_coverage.verified_through`; this is an inclusive evidence cutoff, not a legal end date. System C excludes records with missing coverage and reference dates later than that cutoff, even when `effective_to` is null. `source_amendment.act_date` is retained as assent-date provenance and is never treated as commencement or effective date. Commencement evidence remains separately recorded in `source_reference`. Retrieved evidence is passed to Gemini with explicit source citations and an abstain-if-insufficient instruction. No eligible verified version, a verified not-in-force/omitted state, or no matching evidence causes a deterministic abstention before generation; System C never falls back to the current Constitution or the partially verified pilot text.

Run System C from the repository root:

```powershell
python -m systems.system_c ask --question-id Q001 --reference-date 2011-01-01 --question "What does Article 21A provide?"
python -m systems.system_c ask --question-id Q005 --reference-date 2011-01-01 --question "What is the purpose of Article 45?"
```

The CLI accepts `--dataset-path`, `--embedding-model`, and `--top-k`. It uses the shared `.env` Gemini key and shared generation settings, and appends one success, failure, or abstention record to `results/system_c/runs.jsonl`. The run includes requested Article identifiers, selected version IDs and intervals, verification states, excluded candidate summaries, retrieved chunk IDs and provenance, model settings, abstention reason, and retrieval/generation timings. An abstention is logged and printed without a Gemini request.

The canonical pilot is **not historical gold evidence**: its four records remain `partially_verified`, and System C will not answer from them. The unresolved issues documented in `processed/canonical/README.md` remain: original Constitution page evidence for Article 21A's prior absence, page-image verification of the Act and Gazette, and complete Article 45 history/source edition evidence. Verify these sources and change a record's status only through separate evidence review before expecting the corresponding historical dates to become answerable.

Run all tests, including synthetic verified temporal fixtures:

```powershell
python -m unittest discover -s tests -v
python -m unittest discover -s processed/canonical -v
```

System C tests use clearly labelled synthetic records marked verified for selector/index mechanics and mocked Gemini generation. They do not upgrade or rely on the pilot's verification statuses and make no live API calls.
