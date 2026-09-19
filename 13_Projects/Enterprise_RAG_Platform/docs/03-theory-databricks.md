# Enterprise RAG with Access Control — on Databricks

The same problem as `01-theory.md`, rebuilt on the Lakehouse. Read that one first for the concepts;
this one is about **what changes when the platform gives you governance for free — and the one place
it very deliberately does not.**

---

## 1. The headline

Most of what I hand-built in the Python version is a platform primitive on Databricks:

| Hand-built (OSS version) | Databricks primitive |
|---|---|
| ACL frontmatter on markdown files, synced into a separate SQLite catalog | Delta columns in Unity Catalog |
| `authz/policy.py` — my rules engine | **UC row filters + column masks** (SQL UDFs) |
| `identity.py` — a JSON file of personas | **SCIM groups + `is_account_group_member()`** |
| Post-retrieval re-check in Python | **UC enforcing the row filter, on-behalf-of-user** |
| PII redaction regex | **UC column mask** |
| ChromaDB | **Mosaic AI Vector Search** (Delta Sync index) |
| BM25 + my own RRF | **`query_type="HYBRID"`** (native) |
| `LLMReranker` | **`databricks_reranker`** (managed, reranks top 50) |
| OpenAI embeddings | `databricks-gte-large-en` (managed, auto-computed) |
| LangGraph script | LangGraph **inside** Mosaic AI Agent Framework |
| `observability/trace.py` | **MLflow Tracing → UC tables** |
| My eval harness | **`mlflow.genai.evaluate()`** + custom scorers |
| "who read what?" | **`system.access.audit`** |
| Cost attribution dict | **`system.billing.usage`** |

That is a big reduction in code I have to write, test, and defend. But it comes with one sharp edge,
and everything in this design bends around it.

---

## 2. ⚠️ The two facts that shape the whole architecture

### Fact 1 — Vector Search does not *enforce* UC fine-grained security

> **Databricks Vector Search does not enforce Unity Catalog row filters or column masks.**
>
> From the docs, verbatim: *"Row and column level permissions are not supported. However, you can
> implement your own application level ACLs using the filter API."*

### Fact 2 — and it will not even *build* on a governed table

This one is not in the limitations page, and I only found it by trying. Attach a row filter to your
chunks table, then create the Delta Sync index, and you get:

```
BadRequest: Failed to create delta sync index main.meridian_rag.chunks_idx
  in UC for source table main.meridian_rag.chunks, with error:
  Table main.meridian_rag.chunks cannot have both row/column security
  and online materialized views.
```

**A Delta Sync index cannot be built on a table that has a row filter or a column mask attached.**

Fact 1 alone would let you build the naive architecture and merely have it be insecure. Fact 2 means
the naive architecture **does not build at all** — the platform stops you. Which is arguably a
kindness, but it forces a physical split you need to design for up front.

> **Operational gotcha found the same way:** `CREATE OR REPLACE TABLE` does **not** detach an
> already-attached row filter or column mask. A half-finished run leaves the table permanently
> un-indexable until you `DROP ROW FILTER` / `DROP MASK` or drop the schema. Make your setup
> idempotent.

The reasoning is straightforward once you see it: **the index is a derived copy.** The Delta Sync
pipeline reads the source table with its own identity and writes vectors into a serving system that
has no concept of your users. There is no query-time user to evaluate `is_account_group_member()`
against — so Databricks refuses to pretend otherwise.

```
  ✗ WHAT YOU'D TRY FIRST — and Databricks rejects at index-creation time

    governed Delta table  ──sync──>  ✗ BadRequest: cannot have both row/column
       (row filter)                    security and online materialized views
```

**So the physical design is forced: two objects, not one.**

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

**The security consequence is the part people miss:** because the base table carries no policies,
*granting anyone `SELECT` on it bypasses the entire access model.* Locking it to the pipeline identity
stops being hygiene and becomes load-bearing:

```sql
REVOKE SELECT ON TABLE kb.chunks        FROM `analysts`;   -- nobody reads the base table
GRANT  SELECT ON VIEW  kb.chunks_secure TO   `analysts`;   -- everyone reads the view
```

A **dynamic view** carries the row rules *and* the column masking in one object, so it is the natural
fit — and here it is not one option among three, it is the only mechanism that coexists with the
index.

**The two enforcement points, neither trusting the other:**

```
  ✓ RIGHT

    ┌──────────────────────────────────────────────────────────────────────┐
    │ LAYER 1 — Vector Search `filters`      (application-level ACL)       │
    │   compiled from the caller's groups, passed on every query           │
    │   → unauthorised vectors are never scored or returned                │
    │   → this is an OPTIMISATION and a first line of defence              │
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

**Why this is better than my Python version:** in the OSS build, layer 2 was code I wrote and had to
prove correct with tests. Here, layer 2 is **Unity Catalog**. The authority is the platform's, the
same engine that governs every dashboard and notebook in the company. "The policy engine is the
authority" stops being an aspiration and becomes literally true.

The text returned to the model is the text that came back from **layer 2**, never the text the vector
index returned. The index gives you *candidate IDs and ranking*; the governed view gives you
*content you are allowed to read*.

---

## 3. The architecture

### Medallion, for RAG

```
  SOURCES                 BRONZE              SILVER                    GOLD / SERVING
  ─────────               ──────              ──────                    ──────────────

  Confluence  ┐                                                     ┌─ Vector Search index
  Zendesk     │  Lakeflow   raw docs      chunks + ACL columns      │   (Delta Sync)
  Salesforce  ├─ Connect ─> + metadata ─> + embeddings source ──────┤
  SharePoint  │  / Auto     (Volumes      (NO policies attached -   └─ kb_chunks_secure
  Jira        ┘  Loader      + Delta)      see Fact 2 in §2)              (governed view)
                                 │              │
                          ai_parse_document   Lakeflow Declarative
                          for PDFs            Pipeline does the
                                              chunking
```

**Bronze** — raw documents land in a **UC Volume**, with source metadata in a Delta table. PDFs go
through `ai_parse_document`. Nothing is filtered yet; this layer is admin-only.

**Silver** — one row per **chunk**, and this is where the ACL columns live:

```sql
CREATE TABLE meridian.kb.chunks (
  chunk_id        STRING NOT NULL,
  doc_id          STRING,
  title           STRING,
  section         STRING,
  content         STRING,          -- what gets embedded
  -- ── ACL columns, denormalised onto every chunk ──
  tenant_id       STRING,
  source_system   STRING,
  sensitivity     STRING,          -- public | internal | confidential | restricted
  sensitivity_lvl INT,             -- 0..3, so the index can do a numeric <= filter
  region          STRING,          -- EU | US | GLOBAL
  contains_pii    BOOLEAN,
  need_to_know    STRING,          -- compartment tag, or NULL
  valid_from      DATE,
  valid_until     DATE,
  -- ── group membership, one BOOLEAN per group (see §4) ──
  grp_public      BOOLEAN,
  grp_support_t1  BOOLEAN,
  grp_support_t3  BOOLEAN,
  grp_engineering BOOLEAN,
  grp_sales       BOOLEAN,
  grp_legal       BOOLEAN,
  grp_security    BOOLEAN,
  updated_at      TIMESTAMP
)
TBLPROPERTIES (delta.enableChangeDataFeed = true);
```

Change Data Feed matters: it is how the Vector Search Delta Sync index knows what changed, and it is
what makes incremental re-embedding cheap.

**Gold** — two things sit on top of silver:
1. the **Vector Search index** (Delta Sync, embeddings computed by Databricks), and
2. **`kb_chunks_secure`** — the governed **view** carrying the row rules and the PII masking.
   This is what the agent re-reads from, as the user. It must be a view, not a filter on the base
   table — see Fact 2 in §2.

---

## 4. Encoding the ACL so the index can filter on it

Vector Search filters work on **scalar columns**. There is no documented array-containment operator,
so `allowed_groups ARRAY<STRING>` cannot be filtered on directly. Two workable encodings:

**Option A — one BOOLEAN column per group** *(what I'd choose)*

Works when the group set is bounded and reasonably stable (tens, not thousands).

```python
# Storage-optimized endpoint → SQL-string filters
filters = (
    "tenant_id = 'meridian' "
    "AND sensitivity_lvl <= 2 "
    "AND region IN ('GLOBAL', 'EU') "
    "AND (grp_public = true OR grp_support_t3 = true OR grp_engineering = true)"
)
```

```python
# Standard endpoint → dictionary filters
filters_json = {
    "tenant_id": "meridian",
    "sensitivity_lvl <=": 2,
    "region": ["GLOBAL", "EU"],
    # ⚠ multi-column OR is POSITIONAL - one value per clause (see below)
    "grp_public OR grp_support_t3 OR grp_engineering": [True, True, True],
}
```

> ### ⚠ Gotcha: the multi-column `OR` is positional
>
> This one cost me two failed runs against a live index, and it is not obvious from the docs.
> `{"a OR b": v}` does **not** mean *"either column equals `v`"*. The value must be an **array with
> exactly one element per OR clause**, matched positionally:
>
> ```
>   {"grp_a OR grp_b": [True, True]}   ->   grp_a = True OR grp_b = True     ✅
>   {"grp_a OR grp_b": True}           ->   400: "input must be an array"    ❌
>   {"grp_a OR grp_b": [True]}         ->   400: "length of value = 1 is not
>                                             equal to number of clauses"    ❌
> ```
>
> So the array length must be regenerated every time the caller's group count changes:
>
> ```python
> groups = ["grp_public", "grp_support_t3", "grp_engineering"]   # from the caller's claims
> filters_json[" OR ".join(groups)] = [True] * len(groups)
> ```
>
> **This is a strong extra argument for Storage-Optimized endpoints.** Their SQL-string filters have
> no such footgun — `(grp_public = true OR grp_support_t3 = true)` means exactly what it reads like.

**Option B — fan out one row per (chunk, group)**, then filter `group_id IN (…caller's groups…)`.

Unbounded group support, but it multiplies **vectors**, not just rows — which is the expensive thing.
Only reach for it when the group cardinality genuinely breaks Option A.

> **Storage-Optimized endpoints take SQL-string filters, and that is a real reason to prefer them
> here.** An access-control predicate written as SQL is reviewable by a security person. The
> dictionary form on Standard endpoints gets awkward fast once you have several OR groups.

**Endpoint choice:**

| | Standard | Storage-Optimized |
|---|---|---|
| latency | 20–50 ms | 300–500 ms |
| capacity | ~320M vectors | 1B+ |
| cost | higher | ~7× lower |
| filters | dict | **SQL string** |

For an internal support assistant where the LLM call dominates anyway, 300–500 ms of retrieval is
invisible next to a 2-second generation. **Storage-Optimized**, and spend the saved budget on
reranking.

---

## 5. The governed layer — where the real enforcement lives

This is the part I could not buy in the OSS version. Unity Catalog does it in SQL.

> **Note on mechanism.** Because of Fact 2 in §2, the policy lives in a **dynamic view** rather than
> a row filter attached to the base table — an attached filter would make the table un-indexable. The
> rules below are identical either way; only the object they hang on changes. If you have a governed
> table that is *not* the index source, `SET ROW FILTER` is still the stronger choice, because it
> protects the table however it is queried.

### An entitlements table, not hard-coded groups

```sql
CREATE TABLE meridian.security.user_entitlements (
  user_email    STRING,
  clearance_lvl INT,        -- 0..3
  region        STRING,
  compartment   STRING,     -- need-to-know tag, nullable
  is_external   BOOLEAN
);
```

### The row filter — the whole policy, as one function

```sql
CREATE OR REPLACE FUNCTION meridian.security.chunk_row_filter(
  tenant_id       STRING,
  sensitivity_lvl INT,
  region          STRING,
  need_to_know    STRING,
  valid_from      DATE,
  valid_until     DATE,
  source_system   STRING
)
RETURN
  -- platform admins bypass, for pipeline and support access
  is_account_group_member('kb_admins')
  OR EXISTS (
    SELECT 1
    FROM meridian.security.user_entitlements e
    WHERE e.user_email = current_user()
      -- 1. tenant isolation
      AND tenant_id = 'meridian'
      -- 2. clearance ladder
      AND sensitivity_lvl <= e.clearance_lvl
      -- 3. data residency
      AND (region = 'GLOBAL' OR region = e.region)
      -- 4. embargo / expiry, evaluated at QUERY time
      AND (valid_from  IS NULL OR valid_from  <= current_date())
      AND (valid_until IS NULL OR valid_until >= current_date())
      -- 5. need-to-know compartment
      AND (need_to_know IS NULL OR need_to_know = e.compartment)
      -- 6. external principals: no commercial sources
      AND (NOT e.is_external OR source_system NOT IN ('contract','pricing','postmortem'))
  );

-- Attach to a table that is NOT a vector index source:
ALTER TABLE meridian.kb.chunks_governed
  SET ROW FILTER meridian.security.chunk_row_filter
  ON (tenant_id, sensitivity_lvl, region, need_to_know, valid_from, valid_until, source_system);
```

For the **index source table** the same predicate goes in a view instead, because the table itself
must stay policy-free:

```sql
CREATE OR REPLACE VIEW meridian.kb.chunks_secure AS
SELECT chunk_id, doc_id, title,
       CASE WHEN NOT contains_pii THEN content
            WHEN is_account_group_member('pii_readers') THEN content
            ELSE regexp_replace(content, '[\w.+-]+@[\w-]+\.[\w.-]+', '[REDACTED_EMAIL]')
       END AS content,
       source_system, sensitivity, region
FROM meridian.kb.chunks c
WHERE EXISTS (SELECT 1 FROM meridian.security.user_entitlements e
              WHERE e.user_email = current_user()
                AND c.tenant_id = 'meridian'
                AND c.sensitivity_lvl <= e.clearance_lvl
                AND (c.region = 'GLOBAL' OR c.region = e.region)
                AND (c.valid_from IS NULL OR c.valid_from <= current_date())
                AND (c.need_to_know IS NULL OR c.need_to_know = e.compartment)
                AND (NOT e.is_external OR
                     c.source_system NOT IN ('contract','pricing','postmortem')));
```

Compare that to the seven Python rules in `authz/policy.py`. **Same policy, one SQL function, and now
it protects the table for *every* reader** — the agent, a notebook, a dashboard, a `SELECT` from the
SQL editor. In the OSS build, my policy only protected callers who went through my code.

### The PII obligation becomes a column mask

```sql
CREATE OR REPLACE FUNCTION meridian.security.pii_mask(content STRING, contains_pii BOOLEAN)
RETURN CASE
  WHEN NOT contains_pii THEN content
  WHEN is_account_group_member('pii_readers') THEN content
  ELSE regexp_replace(content, '[\\w.+-]+@[\\w-]+\\.[\\w.-]+', '[REDACTED_EMAIL]')
END;

-- again, only on a table that is NOT a vector index source:
ALTER TABLE meridian.kb.chunks_governed
  ALTER COLUMN content SET MASK meridian.security.pii_mask USING COLUMNS (contains_pii);
```

On the index source, the same `CASE` lives in `chunks_secure` (shown above).

> Note: this is a **UC column mask** — a deterministic governance policy — not `ai_mask`. `ai_mask`
> is an AI transform for content redaction; it is not an access-control primitive and should never be
> the thing standing between a user and PII.

### Group membership drives it all

`is_account_group_member('…')` reads **SCIM-synced account groups**. Your IdP is already the source of
truth, which means **live revocation is free**: remove someone from a group in Okta/Entra, SCIM syncs,
and the next query drops those rows. No reindexing, no cache to bust, no code involved.

---

## 6. Identity: on-behalf-of-user is what makes this work

Layer 2 is only meaningful if the query runs **as the user**. Two options:

| | App / service principal auth | **On-behalf-of-user (OBO)** |
|---|---|---|
| identity used | one shared SP | the actual end user |
| UC row filters | ❌ SP's own access | ✅ **enforced automatically** |
| column masks | ❌ | ✅ **enforced automatically** |
| use when | everyone sees the same data | **per-user data access** ← us |

Mechanics:

```
  user → Databricks App / Agent endpoint
             │  Databricks downscopes the user's credentials to the declared scopes
             │  and forwards them as the  x-forwarded-access-token  header
             v
         agent code: get_user_workspace_client()   ← MUST be called inside the
             │                                        request handler, not at startup
             v
         SQL warehouse query on kb_chunks_secure  →  UC applies row filter + mask
```

Scopes to declare: `sql` (query the governed view) and `serving.serving-endpoints` (call the model).
Grant nothing you don't need — the downscoped token is a real security boundary.

**Honest caveats to state out loud:**
- OBO for agent serving endpoints is **public preview**; a workspace admin must enable it.
- Token forwarding can take **up to ~5 minutes** to reflect a permissions cache refresh.
- The token exists **only at request time** — you cannot build a client at startup and reuse it.

**And the design consequence:** the *Vector Search query itself* still runs as the service principal,
because the index has no user-level security. That's precisely why layer 1 is only a filter and
layer 2 is the authority. If you ever find yourself relying on the index query alone, you have a bug.

---

## 7. Retrieval — mostly free, and better than mine

### Hybrid search is one parameter

```python
results = index.similarity_search(
    query_text="What does MRD-4290 mean?",
    query_type="HYBRID",          # ← dense + BM25, fused internally
    columns=["chunk_id", "doc_id", "title", "sensitivity", "source_system"],
    filters=acl_filter,           # ← layer 1, always
    num_results=20,
)
```

That single parameter replaces my `rank_bm25` index, my `BM25Index` class, and — crucially — the
"rebuild the lexical index per request" scaling problem I had to flag as a known limitation. It's
managed, it's incremental, and it's the *same* reason: enterprise text is full of `MRD-4290`,
`ws_vtx_eu_001`, `ING-2291` that embeddings blur together.

### Reranking is a parameter too

```python
    reranker={"model": "databricks_reranker",
              "parameters": {"columns_to_rerank": ["title", "content"]}},
```

Reranks the top ~50 candidates before returning `num_results`. That's my `LLMReranker`, managed —
lower latency, no prompt to maintain, no JSON parsing to defend.

> Ordering still matters, exactly as before: the reranker sees only what the **layer-1 filter** let
> through, so a restricted user's top-k is the best of *their* pool. Note the one behavioural
> difference from my OSS build — there, enforcement ran *before* reranking; here layer 1 (filter)
> precedes it and layer 2 (governed re-read) follows it. Anything layer 2 drops leaves a gap in the
> context, which is the right failure direction: **material vanishes rather than leaks.**

### What still lives in agent code

**Multi-Query / RAG-Fusion, HyDE, and decomposition** are prompt-and-orchestration patterns, so they
stay in the agent — the LangGraph from the OSS build ports over essentially unchanged, calling
Foundation Model APIs instead of OpenAI. Reciprocal Rank Fusion is still mine, because I'm fusing
across *several generated queries*; the hybrid fusion inside a single query is Databricks'.

---

## 8. The agent

Mosaic AI Agent Framework, with the existing LangGraph inside it:

```
   ┌─────────────────────────────────────────────────────────────────────────┐
   │  ResponsesAgent (MLflow)                                                │
   │                                                                         │
   │   authorize ──> plan ──> retrieve ──> ENFORCE ──> rerank ──> grade ──>  │
   │      │           │          │            │                              │
   │   resolve     multi-      Vector      re-read chunk_ids from            │
   │   caller +    query,      Search      kb_chunks_secure  AS THE USER     │
   │   compile     HyDE,       HYBRID      (UC row filter = the authority)   │
   │   filter      decompose   + filter                                      │
   │                           + rerank                                      │
   │                                                                         │
   │   ──> generate ──> verify ──> answer + citations                        │
   └─────────────────────────────────────────────────────────────────────────┘
              │                                    │
        Foundation Model API              MLflow Tracing → UC tables
        (Llama / Claude / GPT via
         Model Serving, one gateway)
```

Lifecycle: log with MLflow → register in **Unity Catalog** (`catalog.schema.model`) → `agents.deploy()`
→ Model Serving endpoint → fronted by a **Databricks App**.

Because the model is a UC securable, "who can deploy this agent" is the same permission system as
"who can read this table". One governance model for data *and* models.

---

## 9. Evaluation

`mlflow.genai.evaluate()` replaces my harness, with the same three families:

```python
import mlflow
from mlflow.genai.scorers import Correctness, RetrievalGroundedness, scorer

@scorer
def no_leak(inputs, outputs, expectations):
    """The release gate. Deterministic - no judge, no model, no coin flip."""
    forbidden = set(expectations.get("forbidden_docs", []))
    surfaced  = set(outputs.get("retrieved_doc_ids", [])) | set(outputs.get("cited_doc_ids", []))
    leaked = forbidden & surfaced
    return {"value": 0.0 if leaked else 1.0, "rationale": f"leaked: {sorted(leaked)}" or "clean"}

mlflow.genai.evaluate(
    data=eval_dataset,                       # a UC-managed dataset, versioned
    predict_fn=ask_as_user,
    scorers=[Correctness(), RetrievalGroundedness(), no_leak],
)
```

The golden set becomes a **UC table**, so it is versioned, permissioned and lineage-tracked like any
other data asset — a real improvement over a JSON file in a repo.

**The lesson from the OSS build carries over unchanged, and it matters more here:** keep
`forbidden_docs` (must be denied — gates the release) separate from `distractor_docs` (readable but
irrelevant — a precision metric), and **never gate a release on an LLM judge**. `Correctness` and
`RetrievalGroundedness` are judges and will vary run to run; `no_leak` is set arithmetic and will not.
Only the deterministic one blocks a deploy.

**The Databricks-specific superpower:** the leak test can be written as a **plain SQL assertion**
against the governed view, with no agent in the loop at all:

```sql
-- Would this user ever be able to see this document? UC answers definitively.
SELECT count(*) FROM meridian.kb.chunks_secure WHERE doc_id = 'CT-VTX-001';
-- run as the Tier-1 agent's identity → must be 0
```

That is a *stronger* assertion than anything I could write in Python, because it tests the enforcement
point itself rather than my code's use of it.

For deeper work: **MemAlign** aligns a custom judge to your SMEs' labels via a UC labeling session,
and `optimize_prompts()` (GEPA) tunes registered prompts against a scorer. Both are worth naming as
the path from "we have evals" to "our evals agree with our experts".

---

## 10. Observability, and what you get for free

| Question | Where it's answered |
|---|---|
| Why was this answer wrong? | **MLflow Traces** — every span, retrieved IDs, prompt version, tokens |
| Did this user ever read that document? | **`system.access.audit`** — UC logs every table access |
| Which tenant is burning the budget? | **`system.billing.usage`** — DBUs by SKU, warehouse, endpoint |
| What feeds this table? | **`system.access.table_lineage`** |
| Is quality drifting? | MLflow **production monitoring** — scorers on sampled live traces |

Traces ingest into **UC tables**, so trace analysis is just SQL and joins to your other data.

> **The honest gap:** `system.access.audit` covers the *Delta* read. A Vector Search query is not a UC
> table read, so it does not appear there in the same way. Because layer 2 re-reads every candidate
> from the governed table, the audit trail is still complete for anything the user actually saw — but
> if you need "what did the index return before enforcement", log that yourself into a Delta audit
> table. I'd do that anyway: **rows returned by the index but dropped by the governed view** is
> precisely the "pre-filter disagreement" security signal from the OSS design, and on Databricks it's
> a metric you can alert on.

---

## 11. Multi-tenancy

Strongest to weakest, pick by contract:

1. **Catalog per tenant** + index per tenant — a UC catalog is a hard boundary and the natural unit
   for data residency and per-tenant encryption. Default for enterprise/regulated customers.
2. **Schema per tenant** within a shared catalog — cheaper, still cleanly grantable.
3. **Row-level `tenant_id`** with the row filter — most efficient, thinnest boundary.

Use **1 + 3 together**, the same defence-in-depth as the OSS build: physical separation *and* a
tenant predicate. Then add per-tenant **AI Gateway rate limits** so one tenant can't starve another,
and tag serving endpoints and warehouses so `system.billing.usage` can attribute cost per tenant.

---

## 12. CI/CD

Everything is a bundle (**DABs**): pipelines, jobs, indexes, serving endpoints, the app, *and* the
row-filter/mask SQL. Deploy dev → staging → prod as environments.

**Prompts** live in the **MLflow Prompt Registry** — versioned artefacts, referenced by version, with
a rollback that's a pointer flip rather than a redeploy. Exactly the discipline from the OSS design,
now with a home.

Gate the pipeline on: eval score regression, **`no_leak` must be 1.0**, and the SQL permission
assertions above. Blue/green or canary the serving endpoint via traffic splitting.

---

## 13. Honest trade-offs

**What Databricks makes genuinely better**
- Access control is enforced by the *platform*, at the *table*, for *every* consumer — not just mine.
- Live revocation via SCIM, with no code and no reindex.
- Hybrid search and reranking are managed; my worst scaling limitation (per-request BM25) disappears.
- Audit, lineage and cost attribution are free and already trusted by the security team.
- One governance model for data, models, prompts, and eval datasets.

**What gets harder or needs care**
- **The Vector Search ACL gap is a real trap.** It is the first thing I'd tell anyone building this,
  and the first thing I'd check in a review.
- **OBO is public preview** — plan for the enablement step and the token-refresh delay.
- **The index is eventually consistent with the governed table.** A newly-restricted document can sit
  in the index until the next sync; layer 2 is what makes that safe, and it's why layer 2 is
  non-negotiable rather than belt-and-braces.
- **No array containment in filters** forces the boolean-column-per-group encoding, which is a schema
  change whenever a new group appears. Manageable, but it needs an owner.
- **Cost shifts from per-token to per-hour.** A Vector Search endpoint and a SQL warehouse bill while
  provisioned. At low query volume, serverless-everything can cost more than the OSS build; at
  enterprise volume it is dramatically cheaper and someone else runs it.

---

## 14. The whole thing

```
 ┌──────────────┐   Lakeflow Connect / Auto Loader / ai_parse_document
 │  SOURCES     │──────────────────────────────────────────┐
 │ Confluence   │                                          v
 │ Zendesk      │                            ┌───────────────────────────┐
 │ Salesforce   │                            │ BRONZE  UC Volume + Delta │
 │ SharePoint   │                            └─────────────┬─────────────┘
 └──────────────┘                                          │ Lakeflow Declarative Pipeline
                                                           │ (chunk + map source perms → ACL cols)
                                                           v
                                            ┌──────────────────────────────┐
                                            │ SILVER  meridian.kb.chunks   │
                                            │  + ACL columns               │
                                            │  + ROW FILTER  ← the policy  │
                                            │  + COLUMN MASK ← PII         │
                                            └───────┬──────────────┬───────┘
                                       Delta Sync   │              │  governed reads
                                        (CDF)       v              v
                                     ┌──────────────────┐   ┌──────────────────┐
                                     │ VECTOR SEARCH    │   │ kb_chunks_secure │
                                     │ storage-optimised│   │ (UC enforces)    │
                                     │ HYBRID + rerank  │   └────────▲─────────┘
                                     └────────┬─────────┘            │
                                              │ ①filter+rank         │ ②authoritative
                                              │  (as SP)             │  re-read AS USER
                                              v                      │
   ┌──────────────────────────────────────────────────────────────────────────────┐
   │  MOSAIC AI AGENT   (LangGraph inside a ResponsesAgent)                        │
   │  authorize → plan → retrieve ① → ENFORCE ② → grade → generate → verify        │
   └───────────┬───────────────────────────────────────────────┬──────────────────┘
               │ Foundation Model API                          │ MLflow Traces
               v                                               v
        Model Serving endpoint                          UC trace tables
               │                                        system.access.audit
               v                                        system.billing.usage
        Databricks App  ── x-forwarded-access-token ──> on-behalf-of-user
```

**The two numbered arrows are the design.** ① is fast and approximate and runs as a service principal.
② is authoritative and runs as the user, and Unity Catalog — not my code — decides.

---

## 15. What was actually verified

Everything below was **executed against a live Databricks workspace** (AWS `us-east-2`, Unity Catalog
metastore, serverless SQL warehouse) rather than written from the docs. Test objects were created in
throwaway schemas and dropped afterwards; the Vector Search index was built on an existing endpoint
and deleted.

### Unity Catalog governance — all confirmed ✅

| Claim | Result |
|---|---|
| The 7-rule row filter UDF compiles and attaches | ✅ `ALTER TABLE … SET ROW FILTER … ON (7 cols)` |
| Tier-1 (clearance 1, EU) sees only permitted rows | ✅ 2 of 5 rows |
| Contract and post-mortem invisible to Tier-1 | ✅ `count(*) = 0` for both |
| Clearance change takes effect with no DDL and no reindex | ✅ contract + post-mortem appeared on the next query |
| Embargo via `current_date()` hides an unpublished advisory | ✅ 0 rows even at restricted clearance **with** the right compartment |
| `is_external` blocks commercial sources despite max clearance | ✅ only helpcenter + ticket survived |
| Column mask redacts conditionally on `contains_pii` | ✅ `dan.okafor@…` → `[REDACTED_EMAIL]`; the non-PII row's email left intact |
| `delta.enableChangeDataFeed` | ✅ confirmed via `SHOW TBLPROPERTIES` |

The conditional mask result is the one worth showing someone: **the same column, in the same query,
redacted in one row and untouched in another**, decided by a data-driven flag rather than by the
caller's code.

### Vector Search — confirmed, with two corrections ⚠️

| Claim | Result |
|---|---|
| `query_type="HYBRID"` is a single parameter | ✅ |
| Dict filters: equality, `IN` list, `>=`, `NOT` | ✅ all four |
| SQL-string filters rejected on a **Standard** endpoint | ✅ `400 … must be a valid JSON string` — confirms these are Storage-Optimized-only |
| ABAC filters return exactly the right per-persona document set | ✅ 6/6 personas exact match (Tier-1, Tier-3, sales, US-Tier-3 residency, cross-tenant → **empty**, external) |
| **Multi-column `OR` takes a scalar** | ❌ **WRONG — it is positional and needs one value per clause.** Corrected above. |
| Managed `databricks_reranker` | ⚠️ parameter shape accepted, but this workspace returned *"a workspace-level configuration is preventing us from accessing the reranker model"* — so **unverified end-to-end**. Treat reranker availability as something to confirm per workspace, not assume. |

The cross-tenant test is the one to keep: a principal in another tenant, holding **every** group and
the highest clearance, returned **zero rows**.

### The Databricks notebook, executed end to end

`notebooks/04-databricks-enterprise-rag.ipynb` now runs to completion in a real workspace
(~12 min, serverless). Verbatim output from the successful run:

**The gap, demonstrated** — querying the index unfiltered as a Tier-3 engineer who cannot read
contracts:

```
documents the ROW FILTER forbids me, returned by the index: ['CT-VTX-001', 'PR-002']
```

**Layer 2 catching a deliberately broken layer-1 filter:**

```
layer 1 returned (broken filter) : [CT-VTX-001, HC-002, HC-003, PM-2026-03-14, PR-002, SA-2026-07, ...]
layer 2 allowed  (UC decides)    : [HC-002, HC-003, PM-2026-03-14, RB-101, TK-4471]
DROPPED BY UNITY CATALOG         : ['CT-VTX-001', 'PR-002', 'SA-2026-07']
```

**The release gate — and why the overshoot column matters:**

```
persona       layer1 overshoot      REACHED MODEL   gate
tier1         -                     none            PASS
acct_mgr      -                     none            PASS
contractor    -                     none            PASS
secops        ['SA-2026-07']        none            PASS
sec_mgr       ['SA-2026-07']        none            PASS
us_tier3      -                     none            PASS
other_tenant  -                     none            PASS
TOTAL LEAKS REACHING THE MODEL: 0   ->   GATE PASSED
```

`secops` and `sec_mgr` show layer-1 overshoot on the embargoed advisory — **exactly as designed**,
because embargo and need-to-know cannot be pushed into the index filter. Layer 2 stops it. That
column is the clearest possible argument for why layer 2 is not optional.

Also confirmed: the governed view showing 3 of 8 rows to a Tier-1 agent while the base table holds
8; `count(*) = 0` for all four forbidden documents; live revocation adding the post-mortem on the
next query with no reindex; the column mask redacting `[REDACTED_EMAIL]` where `contains_pii` is
true and leaving the non-PII row intact; and two role-appropriate answers to one question — the
engineer got the cardinality root cause, the account manager got the MSA credit tiers and the
routing rule.

### Two more gotchas the run surfaced

- **A `\w` in a regex inside a Spark SQL string dies silently.** The Python -> SQL escaping chain
  eats it and the pattern matches nothing, so a PII mask *looks* attached and redacts nothing. Use
  explicit ranges (`[A-Za-z0-9._%+-]+@...`). Test masks against real data, never assume.
- **A ready index can transiently report `not ready`.** It re-enters a maintenance state between
  syncs, so treat that specific error as retryable with backoff rather than fatal.

### What this changes about the design

Nothing structural — the two-layer architecture stands. But it does sharpen the endpoint
recommendation: **Storage-Optimized isn't just cheaper, it also avoids the positional-`OR` footgun**,
because its filter is SQL. If you are on a Standard endpoint, generate the OR clause and its value
array from the same list in code so they cannot drift apart.

---

## Sources

- [Vector Search — limitations (row/column permissions not supported)](https://docs.databricks.com/aws/en/generative-ai/vector-search)
- [Query an AI Search index — filter syntax, hybrid, reranker](https://docs.databricks.com/aws/en/ai-search/query-ai-search)
- [Databricks Apps — on-behalf-of-user authentication](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/auth)
- [Agent Framework — agent authentication](https://docs.databricks.com/aws/en/generative-ai/agent-framework/agent-authentication)
- [Unity Catalog — row filters and column masks](https://docs.databricks.com/data-governance/unity-catalog/manage-privileges/privileges.html)
