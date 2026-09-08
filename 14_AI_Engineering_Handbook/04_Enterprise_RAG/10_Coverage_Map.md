# Coverage Map — What This Project Proves vs What Is Cheat-Sheet Only

> **Level** 🟡 Building Production Systems · **Module** 04 · **Doc** 10 of 10 · **Time** ~25 min
> **Prerequisites:** docs 1–8 of this module
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/docs/07-system-design-coverage-map.md`
> **Note:** the original checks the project against sections (§4.2–§4.6, §6) of a company-specific system-design prep guide. Those section numbers are kept as labels below so the source stays traceable; the *topics* are what matter and are stated in full.

## Why this matters

For every claim a design makes, there is a difference between *"I built this — let me show you"* and *"I know how this is done"*. Both are legitimate. Confusing them is not. The coverage map is the discipline of writing down, before any conversation, which is which — so you never overclaim what a demo proves, and so you know exactly what to say for the things it does not. Module 11 treats this as a general practice; here it is applied to Meridian Assist.

**Legend:** ✅ covered and runnable · 🟡 partial · ❌ not built. Every ❌/🟡 row carries what it would take to close, and — where closing is infeasible locally — the answer to give instead.

## Access control patterns (§4.3 — the core ask)

| Pointer | Status | Where | To close |
|---|---|---|---|
| Pre-filter as the recommended default | ✅ | `compile_prefilter()` — Layer 1 | — |
| Post-filter rejected explicitly, with reasons | ✅ | Module docstrings argue it directly | — |
| Per-tenant index partitioning | ✅ | One Chroma collection per tenant | — |
| Per-security-group partitioning | ❌ | Only per-tenant | **Code — large.** Collections keyed on `(tenant, group)`, every strategy fanning out and merging. Also the pattern the guide frames as the *exception* (few, large, regulated tenants), not the default — reasonable to leave verbal |
| Re-check against source of truth before citing | ✅ | `verify_citations()` reads the ACL catalog fresh | — |
| LLM never the enforcement point | ✅ | Proven by the injection test in the eval suite | — |
| ACLs as group identifiers, not resolved user lists (no reindex on membership change) | ✅ | `demo_access_control.py::live_revocation_demo()` (principal side); `demo_acl_catalog_update.py` (document side) | — |

The strongest section: every named pattern is runnable.

## Ingestion pipeline (§4.2)

| Pointer | Status | Where |
|---|---|---|
| Multi-source connectors | ✅ | `load_ticket_export()` — a second connector, different format, same pipeline, own tenant |
| Incremental sync / CDC | ✅ | `ingest(incremental=True)` — content-hash per document |
| Common document schema with timestamps and ACL descriptor | ✅ | `ResourceAttributes.source_updated_at` / `.ingested_at`, carried through both stores |
| Structure-aware chunking, overlap, parent linkage | ✅ | `chunker.py` |
| Embed + upsert with tenant/ACL metadata on every chunk | ✅ | `store.py::upsert_chunks()` |
| Dead-letter queue + per-source freshness | ✅ | `freshness.py` — persisted rejections and `last_synced_at` |

## Retrieval quality (§4.4)

| Pointer | Status | Where |
|---|---|---|
| Hybrid dense + BM25 | ✅ | `lexical.py`; `hybrid`/`enterprise` |
| Reranking over a large candidate pool | ✅ | 40/40 → 50 → 6 (`config.py`) |
| Query rewriting / decomposition | ✅ | `expansion.py` |
| History-aware rewriting for conversational queries | ✅ | `ask(..., history=...)` threaded into expansion; live-verified resolving "that incident" to a specific named incident from a prior turn |
| Metadata filters as first-class (source, recency, type) | ✅ | `ask(..., filters=...)` → `merge_filters()`; safe by construction |
| Always cite; prefer refusal over a fluent guess | ✅ | `grade`/`refuse`; citation verification |

## Evaluation (§4.5)

| Pointer | Status | Where / to close | What to say |
|---|---|---|---|
| Retrieval vs generation metrics kept separate | ✅ | Two families in the harness | — |
| nDCG | ✅ | Binary-relevance `_ndcg_binary()`; graded would need every case re-authored | — |
| Golden set of 100–300 real customer questions | 🟡 | Mechanism real; 22 synthetic cases. **Data only** — and can only ever be synthetic without a real customer; name that limit | — |
| Permission-specific eval suite | ✅ | `security`-kind cases; `leak_rate` gate | — |
| LLM-as-judge calibrated against human labels | ✅ | `calibrate_judge.py` — 100% agreement, MAE 0.033 on 6 hand-labelled cases | — |
| Online signals (thumbs, escalation rate, unanswered-query clustering) | ❌ | Offline harness; no serving surface. **Verbal only** | *"Every answer captures a thumbs up/down and citation click-through tied to the same `run_id`. Escalation-to-human rate is a proxy for retrieval failure. Refused questions get embedded and clustered; a cluster is a content gap and becomes a backlog item for whoever owns that source. I'd reuse the harness's `EvalReport` shape sourced from live traffic rather than build a second metrics system."* |

## Likely follow-ups (§4.6)

| Follow-up | Status | What to say |
|---|---|---|
| How fast does a permission change propagate? | ✅ Demoed — zero reindex, both principal and document side | — |
| Retrieval returns nothing — what does the user see? | ✅ Explicit refusal path, never a silent empty answer | — |
| Cost at 10M chunks? | ❌ A 22-doc corpus cannot show it. **Verbal only** | *"Five levers in order of impact: (1) route by difficulty — a small model for rewriting, HyDE, grading and reranking, the large model only for synthesis; this platform already does that with `fast_model` vs `synthesis_model`. (2) Layer 1 pre-filtering shrinks the pool before the expensive reranker — the bigger the corpus, the more it does. (3) Cache embeddings and responses for repeated or near-duplicate questions. (4) Tiered storage — hot embeddings in the fast index, cold rehydrated on demand. (5) A smaller model specifically for reranking, since it runs on every request but only needs a relevance judgement."* Module 06 has the full 20M-document treatment. |
| Same fact, conflicting sources — which wins? | ✅ | `authority_rank` + `source_updated_at`, synthesis rule 7; model reliably picks the right value, only reliably *names* the conflict when hinted — an honest observed gap |

## Cross-cutting concerns (§6)

| Area | Status | Where / to close |
|---|---|---|
| Tenant ID enforced at the data layer | ✅ | `tenant_isolation` rule + per-tenant collection |
| Data residency | ✅ | `data_residency` rule |
| Noisy-neighbour controls | ✅ | `rate_limit.py` — checked before any client is built; a refused request costs $0.00 |
| Prompt injection defence | ✅ | Architectural; eval case S07 |
| PII redaction | ✅ | `redact_pii` obligation |
| Full audit trail | ✅ | `audit_events`, `RunTrace` |
| Secrets manager for connector credentials | ❌ N/A | No real external connectors exist to have credentials; becomes actionable only when they do |
| Full run tracing | ✅ | `RunTrace` |
| Alerting on drift, per-tenant dashboards | ❌ | **Code — large**, normally external infra. Cheap gesture: a scheduled rerun of the harness that diffs the summary row against the last run |
| Model routing by difficulty | ✅ | `fast_model` vs `synthesis_model` |
| Caching (embeddings / responses) | ✅ | `_EMBED_CACHE`; response cache keyed on already-enforced context |
| Circuit breakers / timeouts | ✅ | `_CircuitBreaker` — trips after 3, 30 s cooldown, half-open; live-verified |
| Per-run cost budget | ✅ | `generate` checks `usage.cost_usd` against the ceiling and refuses rather than spends |

## What was closed, and what it taught

Every low- and moderate-effort code gap on the original punch list was closed: pool sizing, timestamps, nDCG, the cost ceiling, freshness and the dead-letter queue, caching, user-facing metadata filters, a second connector, incremental sync, conversation history, judge calibration, rate limiting, the circuit breaker, conflict resolution. Two real bugs were caught doing it — the unscoped reset and the stale content hash, both in the ingestion document — plus a schema migration that `CREATE TABLE IF NOT EXISTS` could not do.

Two items remain large and deliberately out of scope: per-group index partitioning (also not the recommended default) and real dashboards/alerting (external infrastructure).

## The one-paragraph framing

This project gives a *provably correct, runnable* answer for the single hardest thing about enterprise RAG — *whether a user can be shown a chunk they are not allowed to read* — including the Layer 1/Layer 2 split, live revocation on both the principal and document side, and a real separate ACL catalog to point at when asked where the source of truth lives. It also demonstrates a second, differently-shaped connector, incremental sync, history-aware retrieval, per-tenant rate limiting, a circuit breaker, caching and a calibrated judge — with two genuine bugs caught and fixed in the open. It does **not** demonstrate production scale, a real secrets vault, or a live serving surface with production feedback. For those, the honest answer is to speak from the design knowledge in Modules 06 and 08, and to say so.

## Checkpoint

- For any three ✅ rows, name the file and function you would open to prove it.
- For the two ❌ verbal-only rows, deliver the "what to say" answer without notes.
- What distinguishes a 🟡 from a ❌, and give one example of each.
- Why is per-group partitioning left unbuilt even though it is named in the source guide?

**Next →** [Module 05 · Agentic Workflow Platforms](../05_Agentic_Workflow_Platforms/README.md)
