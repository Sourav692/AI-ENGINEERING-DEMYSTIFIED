# Enterprise RAG on Databricks

> **Level** 🟠 Scale, Security, Operations · **Module** 08 · **Doc** 3 of 6 · **Time** ~60 min
> **Prerequisites:** all of Module 04; Module 06 doc 3 (build vs buy)
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/docs/03-theory-databricks.md`; `databricks/README.md`
> **Lab:** `../04_Enterprise_RAG/project/notebooks/04-databricks-enterprise-rag.ipynb` (runs in a Databricks workspace; ~12 min serverless); `../04_Enterprise_RAG/project/databricks/validate_*.py` (REST validation scripts)

## Why this matters

Module 04 built enterprise RAG by hand: a policy engine, an identity file, a BM25 index, a reranker, a trace layer, an eval harness. This document rebuilds the same system on the Lakehouse, where most of that machinery becomes a platform primitive — **and where one specific gap decides the entire architecture.** Being able to present both versions, and explain why the second is better, is the point. It is Module 06's build-vs-buy table applied in full: the permission *policy* stays yours; everything around it is bought.

## The headline

| Hand-built (Module 04) | Databricks primitive |
|---|---|
| ACL manifest synced into a SQLite catalog | Delta columns in Unity Catalog |
| `authz/policy.py` — the rules engine | **UC row filters + column masks** (SQL UDFs) |
| `identity.py` — a JSON file of personas | **SCIM groups + `is_account_group_member()`** |
| Post-retrieval re-check in Python | **UC enforcing the row filter, on behalf of the user** |
| PII redaction regex | **UC column mask** |
| ChromaDB | **Mosaic AI Vector Search** (Delta Sync index) |
| BM25 + hand-written RRF | **`query_type="HYBRID"`** (native) |
| `LLMReranker` | **`databricks_reranker`** (managed, reranks top 50) |
| OpenAI embeddings | `databricks-gte-large-en` (managed, auto-computed) |
| LangGraph script | LangGraph **inside** Mosaic AI Agent Framework |
| `observability/trace.py` | **MLflow Tracing → UC tables** |
| The eval harness | **`mlflow.genai.evaluate()`** + custom scorers |
| "Who read what?" | **`system.access.audit`** |
| Cost attribution | **`system.billing.usage`** |

A large reduction in code to write, test and defend. It comes with one sharp edge, and everything bends around it.

## The two facts that shape the architecture

### Fact 1 — Vector Search does not enforce UC fine-grained security

From the documentation, verbatim: *"Row and column level permissions are not supported. However, you can implement your own application level ACLs using the filter API."* **Databricks Vector Search does not enforce Unity Catalog row filters or column masks.**

### Fact 2 — and it will not even build on a governed table

Not in the limitations page; found by trying. Attach a row filter to the chunks table, create the Delta Sync index, and:

```
BadRequest: Failed to create delta sync index ... Table main.meridian_rag.chunks
  cannot have both row/column security and online materialized views.
```

**A Delta Sync index cannot be built on a table that has a row filter or column mask attached.** Fact 1 alone would let you build the naive architecture and merely have it be insecure. Fact 2 means the naive architecture does not build at all — the platform stops you. Arguably a kindness, but it forces a physical split you must design for up front.

The reasoning: **the index is a derived copy.** The sync pipeline reads the source table with its own identity and writes vectors into a serving system with no concept of your users. There is no query-time user to evaluate `is_account_group_member()` against.

> Operational gotcha found the same way: `CREATE OR REPLACE TABLE` does **not** detach an attached row filter or mask. A half-finished run leaves the table permanently un-indexable until you `DROP ROW FILTER` / `DROP MASK`. Make setup idempotent.

### The forced physical design: two objects, not one

```
   kb.chunks                 UNGOVERNED base table
      │                      SELECT granted ONLY to the sync service principal
      │
      ├──────────────>       VECTOR SEARCH INDEX     (Delta Sync reads this)
      │                      layer ① — ACL applied by the query filter
      │
      └──────────────>       kb.chunks_secure        GOVERNED dynamic view
                             SELECT granted to humans and agents
                             layer ② — ACL + PII masking enforced by Unity Catalog
```

The security consequence people miss: because the base table carries no policies, *granting anyone `SELECT` on it bypasses the entire access model.* Locking it to the pipeline identity stops being hygiene and becomes load-bearing:

```sql
REVOKE SELECT ON TABLE kb.chunks        FROM `analysts`;   -- nobody reads the base table
GRANT  SELECT ON VIEW  kb.chunks_secure TO   `analysts`;   -- everyone reads the view
```

A **dynamic view** carries the row rules *and* the column masking in one object — and here it is not one option among three, it is the only mechanism that coexists with the index.

### The two enforcement points, neither trusting the other

```
    ┌──────────────────────────────────────────────────────────────────────┐
    │ LAYER 1 — Vector Search `filters`      (application-level ACL)       │
    │   compiled from the caller's groups, passed on every query           │
    │   → unauthorised vectors are never scored or returned                │
    │   → an OPTIMISATION and a first line of defence                      │
    └──────────────────────────────────────────────────────────────────────┘
                                    │ chunk_ids
                                    v
    ┌──────────────────────────────────────────────────────────────────────┐
    │ LAYER 2 — re-read those chunk_ids from the GOVERNED Delta view,      │
    │           ON BEHALF OF THE USER                                      │
    │   → Unity Catalog applies the row filter and column mask itself      │
    │   → THIS is the authoritative decision, enforced by the platform     │
    └──────────────────────────────────────────────────────────────────────┘
```

**Why this is better than the Python version:** in Module 04, Layer 2 was code you wrote and had to prove correct with tests. Here Layer 2 is **Unity Catalog** — the same engine that governs every dashboard and notebook in the company. "The policy engine is the authority" stops being an aspiration and becomes literally true. The text returned to the model is the text from Layer 2, never the text the index returned. The index gives *candidate IDs and ranking*; the governed view gives *content you are allowed to read*.

## The architecture: medallion, for RAG

```
  SOURCES                 BRONZE              SILVER                    GOLD / SERVING
  Confluence  ┐                                                     ┌─ Vector Search index
  Zendesk     │  Lakeflow   raw docs      chunks + ACL columns      │   (Delta Sync)
  Salesforce  ├─ Connect ─> + metadata ─> + embeddings source ──────┤
  SharePoint  │  / Auto     (Volumes      (NO policies attached)    └─ kb_chunks_secure
  Jira        ┘  Loader      + Delta)                                     (governed view)
                                 │              │
                          ai_parse_document   Lakeflow Declarative
                          for PDFs            Pipeline does the chunking
```

**Bronze** — raw documents in a UC Volume, source metadata in Delta; PDFs through `ai_parse_document`. Admin-only.

**Silver** — one row per chunk, and this is where the ACL columns live: `tenant_id`, `source_system`, `sensitivity` and `sensitivity_lvl`, `region`, `contains_pii`, `need_to_know`, `valid_from`/`valid_until`, and **one BOOLEAN per group** (`grp_public`, `grp_support_t3`, `grp_engineering`, …). `TBLPROPERTIES (delta.enableChangeDataFeed = true)` — CDF is how the Delta Sync index knows what changed and what makes incremental re-embedding cheap.

**Gold** — the Vector Search index (Delta Sync, embeddings computed by Databricks) and `kb_chunks_secure`, the governed view. It *must* be a view, not a filter on the base table — Fact 2.

## Encoding the ACL so the index can filter on it

Vector Search filters work on **scalar columns**; there is no array-containment operator, so `allowed_groups ARRAY<STRING>` cannot be filtered directly. Two encodings:

**Option A — one BOOLEAN per group** (the choice, when the group set is bounded — tens, not thousands):

```python
# Storage-Optimized endpoint → SQL-string filters
filters = ("tenant_id = 'meridian' AND sensitivity_lvl <= 2 "
           "AND region IN ('GLOBAL', 'EU') "
           "AND (grp_public = true OR grp_support_t3 = true OR grp_engineering = true)")
```

```python
# Standard endpoint → dictionary filters
filters_json = {
    "tenant_id": "meridian",
    "sensitivity_lvl <=": 2,
    "region": ["GLOBAL", "EU"],
    "grp_public OR grp_support_t3 OR grp_engineering": [True, True, True],   # ⚠ positional
}
```

> **Gotcha: the multi-column `OR` is positional.** This cost two failed runs against a live index. `{"a OR b": v}` does *not* mean "either column equals `v`". The value must be an array with **exactly one element per OR clause**:
>
> ```
>   {"grp_a OR grp_b": [True, True]}   ->   grp_a = True OR grp_b = True     ✅
>   {"grp_a OR grp_b": True}           ->   400: "input must be an array"    ❌
>   {"grp_a OR grp_b": [True]}         ->   400: "length of value = 1 is not equal to number of clauses"  ❌
> ```
>
> Generate the clause and the array from the same list so they cannot drift. This is a strong extra argument for Storage-Optimized endpoints, whose SQL-string filters have no such footgun.

**Option B — fan out one row per (chunk, group)**, then `group_id IN (…)`. Unbounded group support, but it multiplies *vectors*, not just rows — the expensive thing. Only when group cardinality breaks Option A.

**Endpoint choice:**

| | Standard | Storage-Optimized |
|---|---|---|
| latency | 20–50 ms | 300–500 ms |
| capacity | ~320M vectors | 1B+ |
| cost | higher | ~7× lower |
| filters | dict | **SQL string** — reviewable by a security person |

For an internal assistant where the LLM call dominates, 300–500 ms of retrieval is invisible next to a 2 s generation. **Storage-Optimized**, and spend the saved budget on reranking.

## The governed layer — where the real enforcement lives

An entitlements table, not hard-coded groups:

```sql
CREATE TABLE meridian.security.user_entitlements (
  user_email STRING, clearance_lvl INT, region STRING, compartment STRING, is_external BOOLEAN);
```

The whole policy as one function — compare it to the seven Python rules:

```sql
CREATE OR REPLACE FUNCTION meridian.security.chunk_row_filter(
  tenant_id STRING, sensitivity_lvl INT, region STRING, need_to_know STRING,
  valid_from DATE, valid_until DATE, source_system STRING)
RETURN
  is_account_group_member('kb_admins')                       -- platform admins bypass
  OR EXISTS (
    SELECT 1 FROM meridian.security.user_entitlements e
    WHERE e.user_email = current_user()
      AND tenant_id = 'meridian'                                            -- 1 tenant isolation
      AND sensitivity_lvl <= e.clearance_lvl                                -- 2 clearance ladder
      AND (region = 'GLOBAL' OR region = e.region)                          -- 3 data residency
      AND (valid_from  IS NULL OR valid_from  <= current_date())            -- 4 embargo / expiry, at QUERY time
      AND (valid_until IS NULL OR valid_until >= current_date())
      AND (need_to_know IS NULL OR need_to_know = e.compartment)            -- 5 need-to-know
      AND (NOT e.is_external OR source_system NOT IN ('contract','pricing','postmortem'))  -- 6 external
  );
```

On a governed table that is *not* the index source, attach it with `ALTER TABLE … SET ROW FILTER … ON (…)`. For the index source, the same predicate lives in the `chunks_secure` view's `WHERE`, alongside the PII mask as a `CASE` on `content`.

**Same policy, one SQL function — and now it protects the table for every reader**: the agent, a notebook, a dashboard, a `SELECT` from the SQL editor. In Module 04, the policy only protected callers who went through your code.

**The PII obligation becomes a column mask** — `regexp_replace` on `content` when `contains_pii` and the caller is not in `pii_readers`. A UC column mask is a deterministic governance policy; `ai_mask` is an AI transform and must never be what stands between a user and PII. And the regex gotcha from Module 04 applies here: a `\w` inside a Spark SQL string dies silently in the escaping chain; use explicit ranges and assert on real data.

**Group membership drives it all.** `is_account_group_member()` reads SCIM-synced account groups. The IdP is already the source of truth, so **live revocation is free**: remove someone in Okta or Entra, SCIM syncs, the next query drops those rows. No reindex, no cache, no code.

## Identity: on-behalf-of-user is what makes Layer 2 real

Layer 2 is only meaningful if the query runs **as the user**:

| | Service-principal auth | **On-behalf-of-user (OBO)** |
|---|---|---|
| identity used | one shared SP | the actual end user |
| UC row filters | ❌ the SP's own access | ✅ enforced automatically |
| column masks | ❌ | ✅ enforced automatically |
| use when | everyone sees the same data | **per-user data access** |

Mechanics: the user hits a Databricks App or agent endpoint; Databricks downscopes the user's credentials to the declared scopes and forwards them as `x-forwarded-access-token`; agent code calls `get_user_workspace_client()` **inside the request handler, not at startup**; the SQL query on `kb_chunks_secure` runs as the user and UC applies the filter and mask. Declare only `sql` and `serving.serving-endpoints`.

Caveats to state out loud: OBO for agent serving endpoints is **public preview** and needs admin enablement; token forwarding can take up to ~5 minutes to reflect a permissions refresh; the token exists only at request time.

**The design consequence:** the *Vector Search query itself* still runs as the service principal, because the index has no user-level security. That is precisely why Layer 1 is only a filter and Layer 2 is the authority. If you ever find yourself relying on the index query alone, you have a bug.

## Retrieval — mostly free, and better

```python
results = index.similarity_search(
    query_text="What does MRD-4290 mean?",
    query_type="HYBRID",                 # dense + BM25, fused internally
    columns=["chunk_id", "doc_id", "title", "sensitivity", "source_system"],
    filters=acl_filter,                  # layer 1, always
    num_results=20,
    reranker={"model": "databricks_reranker",
              "parameters": {"columns_to_rerank": ["title", "content"]}},
)
```

One parameter replaces the BM25 index, the fusion code and — crucially — the "rebuild the lexical index per request" scaling limitation Module 04 had to flag. The managed reranker replaces `LLMReranker`. Multi-query, HyDE and decomposition stay in agent code: they are prompt-and-orchestration patterns, and the LangGraph ports over essentially unchanged calling Foundation Model APIs. RRF across *several generated queries* is still yours; the hybrid fusion inside one query is the platform's.

One behavioural difference: in Module 04, enforcement ran *before* reranking. Here Layer 1 precedes the reranker and Layer 2 follows it. Anything Layer 2 drops leaves a gap in the context — the right failure direction: **material vanishes rather than leaks.**

## The agent, evaluation, observability

**Agent:** the LangGraph inside a Mosaic AI Agent Framework `ResponsesAgent` — authorize → plan → retrieve ① → enforce ② → grade → generate → verify — logged with MLflow, registered in Unity Catalog, deployed to Model Serving, fronted by a Databricks App. Because the model is a UC securable, "who can deploy this agent" is the same permission system as "who can read this table".

**Evaluation:** `mlflow.genai.evaluate()` with the same three families. The leak gate is a custom deterministic scorer:

```python
@scorer
def no_leak(inputs, outputs, expectations):
    forbidden = set(expectations.get("forbidden_docs", []))
    surfaced  = set(outputs.get("retrieved_doc_ids", [])) | set(outputs.get("cited_doc_ids", []))
    leaked = forbidden & surfaced
    return {"value": 0.0 if leaked else 1.0, "rationale": f"leaked: {sorted(leaked)}" if leaked else "clean"}
```

The golden set becomes a UC table — versioned, permissioned, lineage-tracked. Module 04's lesson carries over and matters more: `Correctness` and `RetrievalGroundedness` are judges and vary run to run; `no_leak` is set arithmetic and does not. **Only the deterministic one blocks a deploy.** And the platform-specific superpower: the leak test can be a **plain SQL assertion** against the governed view, run as the persona's identity, with no agent in the loop — `SELECT count(*) FROM kb.chunks_secure WHERE doc_id = 'CT-VTX-001'` must be 0. That tests the enforcement point itself, not your code's use of it.

**Observability:** MLflow Traces for "why was this answer wrong"; `system.access.audit` for "did this user ever read that document"; `system.billing.usage` for "which tenant is burning budget"; `system.access.table_lineage` for "what feeds this table"; production monitoring for drift. **The honest gap:** the audit table covers the *Delta* read; a Vector Search query is not a UC table read. Because Layer 2 re-reads every candidate from the governed table, the trail is complete for anything the user *saw* — but log what the index returned before enforcement into your own Delta audit table. Rows returned by the index and dropped by the view is precisely Module 04's "pre-filter disagreement" signal, now a metric you can alert on.

## Multi-tenancy and CI/CD

Strongest to weakest: **catalog per tenant** + index per tenant (a hard boundary, the natural unit for residency and per-tenant encryption — the default for regulated customers); schema per tenant; row-level `tenant_id` with the filter. Use **1 + 3 together**, the same defence-in-depth as Module 04. Add per-tenant AI Gateway rate limits and tag endpoints and warehouses so cost attributes per tenant.

Everything is a bundle (DABs): pipelines, jobs, indexes, endpoints, the app, *and* the row-filter and mask SQL — dev → staging → prod. Prompts in the MLflow Prompt Registry. Gate the pipeline on eval regression, **`no_leak` = 1.0**, and the SQL permission assertions. Canary the endpoint via traffic splitting.

## Honest trade-offs

**Genuinely better:** access control enforced by the platform, at the table, for every consumer; live revocation via SCIM with no code; managed hybrid search and reranking (the worst scaling limitation disappears); audit, lineage and cost already trusted by the security team; one governance model for data, models, prompts and eval datasets.

**Harder or needs care:** the Vector Search ACL gap is a real trap — the first thing to tell anyone building this; OBO is public preview; **the index is eventually consistent with the governed table** — a newly restricted document can sit in the index until the next sync, which is why Layer 2 is non-negotiable rather than belt-and-braces; no array containment forces the boolean-per-group encoding, a schema change whenever a group appears; cost shifts from per-token to per-hour — at low volume serverless-everything can cost more than the OSS build, at enterprise volume it is dramatically cheaper and someone else runs it.

## What was actually verified

Everything below was **executed against a live workspace**, not written from the docs.

**Unity Catalog governance — all confirmed:** the seven-rule row filter compiles and attaches; Tier-1 sees 2 of 5 rows; contract and post-mortem return `count(*) = 0`; a clearance change takes effect on the next query with no DDL and no reindex; embargo via `current_date()` hides an unpublished advisory even at restricted clearance with the right compartment; `is_external` blocks commercial sources despite max clearance; the column mask redacts conditionally — **the same column, in the same query, redacted in one row and untouched in another**; CDF confirmed.

**Vector Search — confirmed, with two corrections:** `HYBRID` is one parameter; dict filters support equality, `IN`, `>=`, `NOT`; SQL-string filters are rejected on Standard endpoints (Storage-Optimized-only); ABAC filters return exactly the right per-persona sets — 6/6, including the cross-tenant principal with every group and top clearance returning **zero rows**. The multi-column `OR` claim was **wrong** — it is positional (corrected above). The managed reranker's parameter shape was accepted but the workspace returned a configuration error — **unverified end to end**; confirm per workspace.

**The notebook, executed end to end (~12 min):** the gap demonstrated — querying the index unfiltered as a Tier-3 engineer returned `['CT-VTX-001', 'PR-002']`, documents the row filter forbids; Layer 2 catching a deliberately broken Layer-1 filter — `DROPPED BY UNITY CATALOG: ['CT-VTX-001', 'PR-002', 'SA-2026-07']`; and the release gate:

```
persona       layer1 overshoot      REACHED MODEL   gate
secops        ['SA-2026-07']        none            PASS
sec_mgr       ['SA-2026-07']        none            PASS
TOTAL LEAKS REACHING THE MODEL: 0   ->   GATE PASSED
```

The overshoot column is exactly as designed — embargo and need-to-know cannot be pushed into the index filter — and Layer 2 stops it.

Two more gotchas the run surfaced: the `\w` regex problem above, and a ready index that transiently reports `not ready` between syncs — treat as retryable with backoff.

## Interview lens

> *"On Databricks most of what I hand-built becomes a platform primitive — but Vector Search does not enforce Unity Catalog row filters, and it will not even build an index on a governed table. So the physical design is forced: an ungoverned base table locked to the sync principal, feeding the index and a governed dynamic view. Layer 1 is the index filter, compiled from the caller's groups. Layer 2 is a re-read of the candidate IDs from the governed view on behalf of the user, where Unity Catalog itself decides. That's better than my Python version, because the authority is the platform's — and the leak test becomes a SQL assertion against the enforcement point itself."*

## Checkpoint

- State the two facts and explain why Fact 2 forces a physical split.
- Why is locking the base table to the sync principal load-bearing rather than hygiene?
- Explain the positional-`OR` gotcha and why Storage-Optimized endpoints avoid it.
- What does on-behalf-of-user change, and what still runs as the service principal?
- Why is `no_leak` the only scorer allowed to block a deploy?
- What is the honest gap in the audit trail, and how do you close it?
- Which trade-off makes Layer 2 non-negotiable rather than belt-and-braces?

**Next →** [Multi-Channel Delivery and Human Escalation](04_Multi_Channel_And_HITL_Escalation.md)
