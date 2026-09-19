# Module Reference — `src/enterprise_rag`

> **Level** 🟡 Building Production Systems · **Module** 04 · **Doc** 9 of 10 · **Time** reference — use as needed
> **Prerequisites:** docs 1–8 of this module
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/docs/05-src-modules-reference.md`; `docs/06-architecture-end-to-end.md` §8
> **Code:** `project/src/enterprise_rag/`

## How to use this

This is the "where is X implemented?" document. Every function in the package, two or three lines each, grouped by the concept it serves. Read the eight teaching documents first; come here when you are in the code.

## The package in one paragraph

A multi-tenant RAG platform with ABAC enforced at two points: a pre-filter pushed into the vector store (`authz/policy.py::compile_prefilter`) and an authoritative post-retrieval re-check (`authz/enforcement.py::enforce`) that runs before any text reaches the LLM. Documents are loaded and chunked (`ingest/`), embedded into per-tenant Chroma collections (`ingest/store.py`), and retrieved by one of several swappable strategies (`retrieval/strategies.py`) combining dense search, BM25, query expansion, RRF and reranking. The request flow is a LangGraph state machine (`graph/`): authorize → plan → retrieve → enforce → grade → generate → verify, with a refuse branch. Every request is a replayable JSON trace (`observability/trace.py`), and an evaluation harness (`evaluation/harness.py`) scores retrieval, groundedness and — as a hard gate — a zero-tolerance leak rate.

## Core types — `models.py`

| Symbol | Purpose |
|---|---|
| `ResourceAttributes` | A document's ACL attributes plus non-ACL metadata. `sensitivity_level` maps the string to its rank for numeric comparison. `source_updated_at` / `ingested_at` are content timestamps; `authority_rank` breaks ties when passages disagree |
| `Principal` | The authenticated caller. `clearance_level`; `from_dict()` |
| `Document`, `Chunk`, `ScoredChunk`, `Citation`, `Answer` | The data shapes. `Chunk.to_metadata()` flattens for Chroma (lists → `grp__<group>: True` columns); `attrs_from_metadata()` inverts it. `ScoredChunk.citation` renders `[DOC-ID#N]` |
| `SENSITIVITY_RANK`, `today_iso()` | The ladder; the default "as of" date for embargo |

## Identity and configuration

| Module | Symbol | Purpose |
|---|---|---|
| `identity.py` | `get_principal(user_id)` | Resolves a principal **fresh** and returns a copy, so revocation takes effect on the next request and a demo mutating the result cannot corrupt shared state. `list_principals()` |
| `config.py` | `Settings`, `SETTINGS` | Every tunable: paths, models (`fast_model` vs `synthesis_model`), chunking, `dense_k`/`bm25_k` = 40, `fusion_k` = 50, `rerank_k` = 6, `min_rerank_score`, `max_cost_per_run_usd` = 0.10, rate-limit and circuit-breaker thresholds. `collection_for(tenant_id)`. Loads `OPENAI_API_KEY` from a repo-root `.env` |

## Authorisation — `authz/`

| Module | Symbol | Purpose |
|---|---|---|
| `policy.py` | `_rule_tenant_isolation` … `_rule_external_contractor` | The six deny rules, each `(principal, resource, ctx) → Decision or None` |
| | `_rule_group_membership` | The one allow rule: `public` or non-empty group intersection |
| | `decide(principal, resource, ctx)` | Deny rules in order, short-circuit on first deny; then allow; then `default_deny` |
| | `_attach_obligations` | `redact_pii`, `audit_access` on an allow |
| | `compile_prefilter(principal)` | The decidable subset → Chroma `where` (tenant, sensitivity ceiling, region, group overlap, external-source exclusion). Explicitly excludes embargo, need-to-know, obligations, live revocation |
| | `explain_prefilter`, `merge_filters` | Human-readable summary; AND-ing a caller's non-ACL filter (safe: `$and` only narrows) |
| `enforcement.py` | `enforce(principal, candidates, ctx, came_from_prefilter)` | Layer 2. Re-runs `decide()` per candidate against attrs from the ACL catalog; applies redaction and audit; flags `filter_disagreements`. Returns `EnforcementReport` |
| | `verify_citations(principal, cited_doc_ids)` | Re-fetches and re-decides each cited doc; drops hallucinated or unauthorised ids |
| | `redact_pii`, `_apply_redaction` | Regex email masking |
| `rate_limit.py` | `check(tenant_id)`, `reset()` | Fixed-window per-tenant counter, same `Decision` shape. In-process only |

## Ingestion — `ingest/`

| Module | Symbol | Purpose |
|---|---|---|
| `loader.py` | `load_corpus(corpus_dir, tenant_id, acl_manifest_path)` | Parse markdown frontmatter (`doc_id`, `title` only), join with the manifest by `doc_id`; raise on no `doc_id` or no manifest match |
| | `load_ticket_export(path, tenant_id, ...)` | The second connector — a JSON ticket export with a different shape, same refuse-on-no-match discipline |
| `acl_manifest.py` | `load_acl_manifest(path, tenant_id)` | `doc_id → ResourceAttributes` from the permissions-only JSON |
| `chunker.py` | `_split_by_heading`, `_pack`, `chunk_document`, `chunk_corpus` | Heading-aware split, paragraph packing with overlap, title+section prefix, inherited ACL |
| `pipeline.py` | `validate_acl(doc)` | Known sensitivity, non-empty groups, known region, `public` consistency |
| | `ingest(tenant_id, reset, batch_size, loader, incremental)` | Orchestrates load → validate → catalog → chunk → embed → index. Tenant-scoped reset. Persists rejections and sync timestamps. `incremental` skips unchanged text (only when `reset=False`). Returns `IngestReport` |
| | `_content_hash(doc)` | SHA-256 of text only |
| `freshness.py` | `record_sync`, `record_rejection`, `last_synced`, `all_freshness`, `recent_rejections`, `get_content_hash`, `set_content_hash` | Per-source freshness, the persisted dead-letter queue, and content hashes — all in the catalog's SQLite file |
| `store.py` | `get_client`, `get_collection(tenant_id)` | Chroma client; one cosine collection per tenant |
| | `upsert_chunks`, `dense_search(tenant_id, embedding, where, k)`, `fetch_all_allowed(tenant_id, where)` | Write; filtered vector query; the authorised pool for BM25 |
| | `get_doc_attrs(doc_id)` | Delegates to the catalog; falls back to a Chroma scan only for uncatalogued test chunks |
| | `reset_store(tenant_id=...)`, `collection_stats` | Scoped reset; counts by source and sensitivity |
| `catalog.py` | `get_connection`, `_migrate` | SQLite; adds missing columns in place |
| | `upsert_doc_attrs`, `upsert_many`, `get_doc_attrs`, `update_attr(doc_id, **fields)`, `all_doc_ids`, `reset_catalog(tenant_id=...)` | The authoritative ACL rows. `update_attr` is the live-ACL-change demo: one row write, no re-embed |

## Retrieval — `retrieval/`

| Module | Symbol | Purpose |
|---|---|---|
| `lexical.py` | `tokenize`, `BM25Index(chunks).search(query, k)` | Hyphen-preserving tokens; BM25 over the authorised pool, built per request |
| `expansion.py` | `generate_multi_queries(llm, question, n, history)` | `[original] + N` rewrites, deduped; history-aware; degrades to `[original]` |
| | `generate_hyde_passage(llm, question)` | The probe; `None` on failure |
| | `decompose(llm, question, history)` | Up to `max_subquestions`; `[]` if not needed or on failure |
| `fusion.py` | `reciprocal_rank_fusion(ranked_lists, k, top_n)` | Rank-based merge; merges `retrieved_by` provenance |
| `rerank.py` | `LLMReranker.rerank(question, candidates, top_k)` | One batched 0–10 scoring call; fusion order on failure |
| | `CrossEncoderReranker.rerank(...)` | Local cross-encoder; same interface |
| `strategies.py` | `RetrievalContext` | Principal, `where`, LLM, settings, trace fields, `history` |
| | `dense_only`, `bm25_only`, `hybrid`, `multi_query`, `hyde`, `enterprise`, `get_strategy(name)`, `STRATEGIES` | The six strategies and the registry |

## The LLM client — `llm/client.py`

| Symbol | Purpose |
|---|---|
| `LLMClient.chat`, `chat_json`, `embed` | Chat, JSON-mode chat (returns `{}` on decode failure), batched embeddings through `_EMBED_CACHE` |
| `_with_retries(fn, attempts, purpose)` | Breaker check first; exponential backoff with full jitter on rate-limit/timeout; 5xx retries and counts toward the breaker; 4xx raises immediately and never trips it |
| `_CircuitBreaker`, `circuit_breaker_state`, `reset_circuit_breaker` | Process-wide; opens after 3 consecutive exhaustions; 30 s cooldown; half-open trial |
| `Usage.add(model, prompt, completion, purpose)`, `merge` | Tokens and USD, by purpose |
| `LLMUnavailable` | Raised after retries; every caller degrades on it |

## The graph — `graph/`

| Module | Symbol | Purpose |
|---|---|---|
| `state.py` | `RAGState` | The `TypedDict` that flows through every node; `content_filters` and `conversation_history` are optional and additive |
| `prompts.py` | `PROMPT_VERSION`, `SYNTHESIS_SYSTEM`/`_USER`, `PARTIAL_COVERAGE_NOTE`, `SUFFICIENCY_SYSTEM`, `GROUNDEDNESS_SYSTEM`, `REFUSAL_TEMPLATE` | Versioned templates; synthesis rule 7 resolves conflicts by authority then recency |
| `nodes.py` | `authorize`, `plan`, `retrieve`, `enforce`, `grade`, `route_after_grade`, `generate`, `verify`, `refuse` | The eight nodes and the conditional edge |
| | `_format_context`, `_response_cache_key`, `_RESPONSE_CACHE`, `clear_response_cache` | Context block with authority/recency labels; the cache keyed on question + filter + surviving chunk ids + coverage note |
| `build.py` | `build_graph()` | Compiles and caches the `StateGraph` |
| | `RAGPlatform.ask(question, principal, strategy, as_of, write_trace, filters, history)` | Rate-limit check first; fresh client/usage/trace; invoke; returns `{"answer", "trace", "state"}` |

## Observability and evaluation

| Module | Symbol | Purpose |
|---|---|---|
| `observability/trace.py` | `RunTrace` — `start`, `end`, `finish(usage)`, `to_dict`, `write`, `timeline` | One replayable JSON record per run |
| `evaluation/harness.py` | `load_cases`, `_ndcg_binary`, `_score_case`, `run_eval(strategy, cases, kinds)`, `compare_strategies(strategies)` | The harness |
| | `CaseResult.passed`, `.refusal_advisory` | Fails on any leak or recall < 1.0; `distracted` never fails; security cases gate only on leaks |
| | `EvalReport` — `recall_at_k`, `mrr`, `ndcg`, `groundedness`, `leak_count`, `leak_rate`, `refusal_accuracy`, `pass_rate`, `total_cost`, `p50_latency`, `summary_row`, `render` | Aggregates |

## Scripts and tests

| Path | Purpose |
|---|---|
| `scripts/ingest.py` | Build the index |
| `scripts/ask.py --user <id> "<question>"` · `--list-users` | Ask as a persona |
| `scripts/demo_access_control.py [--matrix]` | The visibility matrix (no LLM cost) and the full demo, including live revocation |
| `scripts/evaluate.py [--kinds security] [--compare ...]` | The gate; the strategy comparison |
| `scripts/calibrate_judge.py` | LLM judge vs hand labels |
| `scripts/demo_second_connector.py`, `demo_incremental_sync.py`, `demo_acl_catalog_update.py` | The three moderate-effort additions |
| `tests/` | 62 fast tests (policy, fusion, chunking, enforcement, golden-set integrity) + 6 live; `verify_security_reference.py` asserts the ABAC document matches the running policy |

**Next →** [Coverage Map](10_Coverage_Map.md)
