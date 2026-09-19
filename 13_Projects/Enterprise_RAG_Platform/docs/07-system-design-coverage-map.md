# System Design Coverage Map — what this project proves vs. what's cheat-sheet only

**What this is:** every pointer named in `../../DevRev-SystemDesign-Prep.docx` §4 ("Problem Type B —
Enterprise RAG with Access Control") and the relevant parts of §6 (cross-cutting concerns), checked
against what `enterprise_rag_platform` actually implements — not what the docs merely describe.

**Why this matters for the interview:** for a ✅ item you can say *"I built this — let me show you"*
and point at a running demo. For a ❌ item you are speaking from the cheat sheet, not the code —
know the difference before the round so you don't overclaim what the demo proves.

**Legend:** ✅ covered and runnable · 🟡 partial (the concept exists, scaled down or simplified) · ❌ not built

**The "To close this gap" column** on every ❌/🟡 row below tells you what it would actually take:
- **Code — low/moderate/large** effort: a real codebase change, roughly sized
- **Data/content only**: no architecture change, just more authored examples
- **Verbal only**: infeasible or out of scope to genuinely demo locally (production infra, real scale) — answer from the prep doc, and say so if asked whether it's built. Where this applies, the table also carries a **"What to say"** column with the actual answer to give, worded ready to speak.

---

## §4.3 — Access Control Patterns (the doc's core ask)

| Pointer | Status | Where | To close this gap |
|---|---|---|---|
| Pre-filter as the recommended default | ✅ | `authz/policy.py::compile_prefilter()` — Layer 1 | — |
| Post-filter rejected explicitly, with reasons | ✅ | Module docstrings argue this directly — a ready-made trade-off answer | — |
| Per-tenant index partitioning | ✅ | One Chroma collection per tenant (physical isolation) | — |
| Per-security-group partitioning | ❌ | Only per-tenant partitioning exists, not per-group indexes | **Code — large.** `store.py::get_collection()` would need to key on `(tenant_id, group)` instead of just `tenant_id`, and every retrieval strategy would need to fan out across the principal's group-collections and merge results. This is also the pattern the prep doc itself frames as the *exception* ("when tenants are few, large, and regulated"), not the default — so it's reasonable to leave this as a verbal alternative unless asked to build it. |
| Re-check against source of truth before citing | ✅ | `authz/enforcement.py::verify_citations()` — Layer 2, reads the SQLite ACL catalog fresh | — |
| LLM never the enforcement point | ✅ | Proven, not just claimed — prompt-injection test in the eval suite | — |
| ACLs as group identifiers, not resolved user lists (no reindex on membership change) | ✅ | `scripts/demo_access_control.py::live_revocation_demo()` (principal side) + `scripts/demo_acl_catalog_update.py` (document side) | — |

This is the strongest section — every named pattern is not just discussed but **runnable**.

---

## §4.2 — Ingestion Pipeline

| Pointer | Status | Notes | To close this gap |
|---|---|---|---|
| Multi-source connectors (Confluence, SharePoint, Jira, Zendesk...) | ✅ | `ingest/loader.py::load_ticket_export()` — a second connector, a JSON export with no frontmatter at all, feeding the exact same `pipeline.ingest()` path via its new `loader=` parameter, into its own tenant (`scripts/demo_second_connector.py`) | — |
| Incremental sync / CDC / delta tokens | ✅ | `pipeline.ingest(incremental=True)` — content-hash comparison per document (`freshness.py::get_content_hash()`/`set_content_hash()`); only changed documents re-chunk/re-embed (`scripts/demo_incremental_sync.py`) | — |
| Common Document schema (content, URI, tenant, timestamps, ACL descriptor) | ✅ | `ResourceAttributes.source_updated_at` (from the corpus file's mtime, set in `loader.py`) and `.ingested_at` (stamped in `pipeline.ingest()`) — carried through Chroma metadata and the ACL catalog | — |
| Structure-aware chunking + overlap + parent-doc linkage | ✅ | `ingest/chunker.py` — heading-based split, overlap, `doc_id` back-link | — |
| Embed + upsert with tenant/ACL metadata on every chunk | ✅ | `ingest/store.py::upsert_chunks()` | — |
| Dead-letter queue + per-source freshness metrics | ✅ | `ingest/freshness.py` — `record_sync()`/`record_rejection()`, called from `pipeline.ingest()`; a persisted, queryable `rejected_docs` table plus a per-source `source_freshness.last_synced_at`, sharing the ACL catalog's SQLite file | — |

---

## §4.4 — Retrieval Quality

| Pointer | Status | Notes | To close this gap |
|---|---|---|---|
| Hybrid dense + BM25 | ✅ | `retrieval/lexical.py`, `hybrid`/`enterprise` strategies | — |
| Reranking over a large candidate pool | ✅ | `config.py` — `dense_k`/`bm25_k`=40, `fusion_k`=50, reranked down to `rerank_k`=6; the mechanism was always correct, this was a config value not a design gap | — |
| Query rewriting / decomposition for multi-hop | ✅ | `retrieval/expansion.py` — multi-query, HyDE, decompose | — |
| History-aware rewriting for conversational queries | ✅ | `RAGPlatform.ask(..., history=...)` — threaded into `expansion.py::generate_multi_queries()`/`decompose()` via `RetrievalContext.history`; live-verified to resolve "that incident" into the specific named incident from a prior turn, including picking up a workspace id mentioned only in the earlier answer | — |
| Metadata filters as first-class (source, recency, doc type) | ✅ | `RAGPlatform.ask(..., filters=...)` — `authz/policy.py::merge_filters()` ANDs a caller-supplied, non-ACL clause onto the compiled ACL pre-filter in `authorize`; safe by construction since `$and` can only narrow, never loosen | — |
| Always cite; prefer refusal over a fluent guess | ✅ | `grade`/`refuse` graph nodes, citation verification | — |

---

## §4.5 — Evaluation

| Pointer | Status | Notes | To close this gap | What to say (verbal-only rows) |
|---|---|---|---|---|
| recall@k, MRR (retrieval) vs. groundedness (generation) kept separate | ✅ | `evaluation/harness.py` — two explicit metric families | — | — |
| nDCG | ✅ | `evaluation/harness.py::_ndcg_binary()` — binary-relevance nDCG (expected-doc membership, not a 1-3 graded score); graded relevance would need every golden-set case re-authored with a per-doc grade, which is the one piece deliberately left out — see the note in the source | — |
| Golden set of 100-300 real customer questions | 🟡 | The golden-set *mechanism* is real; only 22 synthetic cases, not real customer questions at that scale | **Data/content only.** No code change — `data/golden_set.json` just needs more authored cases. Since there's no real customer, this specific gap can only ever be closed with more synthetic cases, not "real" ones — worth naming that limit if asked directly. | — |
| Permission-specific eval suite (personas × restricted content) | ✅ | `security`-kind cases, `leak_rate` — the hard release gate | — | — |
| LLM-as-judge calibrated against human labels | ✅ | `scripts/calibrate_judge.py` — runs the real `GROUNDEDNESS_SYSTEM` prompt against 6 hand-labeled cases spanning fully-grounded/fabricated/wrong-date/partial, reports agreement rate + mean absolute error against the human labels (live run: 100% agreement, MAE 0.033) | — |
| Online signals (thumbs up/down, escalation rate, unanswered-query clustering) | ❌ | This is an offline eval harness only, no production feedback loop | **Verbal only**, mostly. This needs a live serving surface (an API/UI capturing feedback) that doesn't exist at all in this project — genuinely out of scope for a local demo. If you want *some* code signal, a `record_feedback(run_id, rating)` stub appended to `RunTrace`/a feedback JSONL file is a low-effort gesture, but it won't demonstrate the clustering/escalation-rate part. | *"In production, every answer would capture a thumbs up/down and citation click-through, tied to the same `run_id` the trace already produces. Escalation-to-human rate becomes a proxy for retrieval failure — if it climbs, retrieval or grading regressed before anyone files a ticket. Refused/unanswered questions get embedded and clustered periodically; a cluster is a content gap, and it becomes a backlog item for whoever owns that source system, not a dead end for the user. I'd reuse the golden-set harness's `EvalReport` shape for this — same metrics, sourced from live traffic instead of a fixed case list — rather than building a second, separate metrics system."* |

---

## §4.6 — Likely Follow-Ups

| Follow-up | Status | To close this gap | What to say (verbal-only rows) |
|---|---|---|---|
| "How fast does a permission change propagate?" | ✅ Directly demoed — event-driven, zero reindex, both principal-side and document-side | — | — |
| "Retrieval returns nothing — what does the user see?" | ✅ Covered — explicit refusal path, never a silent empty answer | — | — |
| "Cost at 10M chunks?" | ❌ Not demonstrated — this is a 22-doc/86-chunk toy corpus; answer from the cheat sheet, not the code | **Verbal only**, in the main — no local demo can honestly show 10M-chunk economics. The one *piece* of this that is a tractable code change is response/embedding caching (see the caching row below); building that would let you show the cache-hit mechanism even though it can't prove behavior at real scale. | *"Five levers, in order of impact: (1) route by difficulty — a small/cheap model for query rewriting, HyDE, grading, and reranking, the large model reserved only for final synthesis — this platform already does exactly that with `fast_model` vs `synthesis_model`, so the pattern is proven, just not the scale. (2) Aggressive Layer-1 prefiltering already shrinks the candidate pool before the expensive reranking step runs — the bigger the corpus, the more that filter is doing. (3) Cache embeddings and full responses for repeated/near-duplicate questions — never pay to re-embed or re-generate the same thing twice. (4) Tiered storage — hot, recently-queried embeddings stay in the fast index; cold ones move to cheaper storage and get rehydrated on demand. (5) A smaller, cheaper model specifically for reranking, since it runs on every request but only needs a relevance judgment, not full reasoning."* |
| "Same fact, conflicting sources — which wins?" | ✅ | `ResourceAttributes.authority_rank` (new, non-ACL) + `source_updated_at`, surfaced in `_format_context()`; `SYNTHESIS_SYSTEM` rule 7 instructs preferring higher authority, then more recent, and naming the conflict. Live-verified against two synthetic conflicting passages (not merged into the flagship 22-doc corpus, to avoid perturbing every doc-count reference elsewhere) — the model reliably picked the correct higher-authority value in every trial; it only reliably *named* the conflict when the question hinted one might exist, otherwise it silently picked the right number without disclosure. An honest, observed gap, not a mechanism failure — noted in `docs/05`. | — |

---

## Relevant §6 Cross-Cutting Concerns

| Area | Status | Where / note | To close this gap |
|---|---|---|---|
| Tenant ID enforced at data layer, not app code | ✅ | `tenant_isolation` rule, per-tenant Chroma collection | — |
| Data residency (region-locking) | ✅ | `data_residency` rule | — |
| Noisy-neighbour controls (per-tenant rate limits/budgets) | ✅ | `authz/rate_limit.py::check()` — fixed-window per-tenant counter, checked at the very top of `RAGPlatform.ask()` before an `LLMClient` is even constructed, so a rate-limited request costs nothing; live-verified end to end (refused, `trace.cost_usd == 0.0`) | — |
| Prompt injection defense | ✅ | Architectural — demoed in the eval suite (S07) | — |
| PII detection/redaction | ✅ | `redact_pii` obligation | — |
| Full audit trail | ✅ | `audit_events`, `observability/trace.py::RunTrace` | — |
| Secrets manager for connector credentials | ❌ N/A | No real external connectors exist to have credentials | **N/A until connectors exist.** Only becomes a real gap once the multi-source-connectors item (§4.2) is built; not independently actionable before that. |
| Full run tracing (prompt version, tokens, latency, cost) | ✅ | `RunTrace` — extensive | — |
| Alerting on drift, per-tenant dashboards | ❌ | Not built | **Code — large**, and mostly out of scope for a Python backend demo — real dashboards/alerting normally mean wiring to Prometheus/Grafana or similar, not something to build from scratch here. A cheap, code-only gesture: a script that reruns `evaluation/harness.py` on a schedule and diffs the summary row against the last run, flagging if `leak_count`/`refusal_acc`/`groundedness` moved past a threshold — demonstrates the *concept* of drift detection without a real dashboard. |
| Model routing by difficulty (small model for routing, large for synthesis) | ✅ | `config.py` — `fast_model` vs `synthesis_model`, literally this pattern | — |
| Caching (embeddings/retrieval/response) | ✅ | `llm/client.py::embed()` — in-process `(model, text)` cache, only the uncached portion is billed; `graph/nodes.py::generate()` — response cache keyed on `(question, ACL filter, exact context, coverage note)`, so a cache hit is only ever served for a genuinely identical, freshly-re-enforced situation | — |
| Circuit breakers / timeouts / bulkheads | ✅ | `llm/client.py::_CircuitBreaker` — process-wide, trips open after `circuit_breaker_failure_threshold` (3) consecutive genuine-outage exhaustions, short-circuits every call with zero network attempts for `circuit_breaker_cooldown_s` (30s), then allows a half-open trial call; live-verified tripping and short-circuiting | — |
| Per-run cost/token budget enforcement | ✅ | `graph/nodes.py::generate()` checks `usage.cost_usd` against `SETTINGS.max_cost_per_run_usd` (default $0.10) before the most expensive call and routes to `refuse` if already exceeded — halt-and-escalate, not loop, same instinct as `agent_platform`'s step/spend budget | — |

---

## Punch list — code-change gaps, sorted by effort

Everything below is a **Code** row from the tables above, grouped by size, for whenever there's time
to close a few before the interview. Data-only, N/A, and verbal-only gaps are omitted — they aren't
codebase work.

**Trivial / low effort** — all done:
- ~~Bump `dense_k`/`bm25_k`/`fusion_k` in `config.py` so reranking sees a realistic-sized pool (§4.4)~~
- ~~Add `ingested_at`/`source_updated_at` fields to `ResourceAttributes` (§4.2)~~
- ~~Add an nDCG calculation to `evaluation/harness.py` (binary-relevance, not graded) (§4.5)~~
- ~~Enforce a per-run cost ceiling using the `Usage`/`RunTrace` numbers that already exist (§6)~~

**Low-moderate effort** — all done:
- ~~Extend `IngestReport.rejected` into a real per-source last-sync + rejected-docs record (§4.2)~~
- ~~In-process caching: embed-call cache in `llm/client.py`, response cache in `graph/nodes.py` (§6)~~
- ~~Expose non-ACL metadata (`source`, recency, doc type) as an optional user-facing retrieval filter (§4.4)~~

**Moderate effort** — all done:
- ~~A second synthetic connector (different file format) to prove the ingestion normalization step generalizes (§4.2)~~
- ~~Content-hash-based incremental sync in `pipeline.ingest()` (§4.2)~~
- ~~Conversation history threaded into `expansion.py`/`RAGState` for multi-turn query rewriting (§4.4)~~
- ~~A calibration script comparing LLM-judge scores against hand-labeled cases (§4.5)~~
- ~~Per-tenant rate limiting in `RAGPlatform.ask()` (§6)~~
- ~~A circuit breaker around LLM calls in `llm/client.py` (§6)~~
- ~~Source-authority/recency conflict resolution (§4.6)~~

Two real bugs were caught and fixed while building this batch, both worth telling in the interview:
1. **`reset=True` was a global reset, not tenant-scoped.** Ingesting the new second-connector tenant
   with `reset=True` silently wiped the unrelated 22-doc `meridian` corpus, because `store.reset_store()`
   deleted the whole `chroma_dir` and `catalog.reset_catalog()` deleted the whole SQLite file,
   regardless of which tenant was being ingested. Fixed: both now accept a `tenant_id` and scope the
   reset to just that tenant's collection/rows; `pipeline.ingest()` passes its own `tenant_id` through
   by default.
2. **A stored content hash survived a reset it shouldn't have.** Running `reset=True` together with
   `incremental=True` skipped re-embedding 21 of 22 documents into a freshly-*emptied* index, because
   their hashes matched records from *before* the reset — producing a near-empty index that still
   reported "22 documents indexed" as if it had succeeded. Fixed: incremental skipping now only
   applies when `reset=False`; a reset always re-embeds and re-hashes everything, since the
   destination it would be comparing against no longer exists.

Also caught: an existing `authority_rank` column addition needed a schema *migration*, not just
`CREATE TABLE IF NOT EXISTS` (which doesn't add columns to a table that already exists) — a
demo-database version of the same class of bug that hits any long-lived SQLite/Postgres table.
`catalog.py::_migrate()` now adds missing columns in place via `PRAGMA table_info` + `ALTER TABLE`.

**Large / likely out of scope for this demo**
- Per-security-group index partitioning (§4.3) — also not the doc's recommended default
- Real alerting/dashboards (§6) — normally external infra (Prometheus/Grafana), not custom-built here

---

## The one-paragraph interview framing

This project gives a *provably correct, runnable* answer for the single hardest thing the prep doc
calls out — *"the signal is whether a user can be shown a chunk they are not allowed to read"* —
including the Layer 1/Layer 2 split, live revocation on both the principal side and the document
side, and a real separate ACL catalog to point at when asked *"where does the source of truth
live?"* It now also demonstrates a second, differently-shaped connector into a real
validate/chunk/embed/index pipeline, incremental (hash-based) sync, conversation-history-aware
retrieval, per-tenant rate limiting, a circuit breaker, caching, and a calibrated LLM judge — with
two genuine bugs (an unscoped reset that cross-contaminated tenants, and a stale-hash interaction
with reset that silently produced a near-empty index) caught and fixed while building them, not
glossed over. It does **not** demonstrate true production scale, a real secrets vault, or a live
serving surface with production feedback signals — for those, the honest answer is to speak from
`DevRev-SystemDesign-Prep.docx` §4/§6/§8 directly, not imply the demo proves them too.

---

## See also

- `../../DevRev-SystemDesign-Prep.docx` — the source prep document this map is checked against
- `04-security-checks-reference.md` — every ABAC field/rule/persona worked in detail
- `05-src-modules-reference.md` — every function in `src/enterprise_rag`
- `06-architecture-end-to-end.md` — the full pipeline, diagrammed end to end
- `QA.md` — running log of conceptual Q&A from prep sessions
