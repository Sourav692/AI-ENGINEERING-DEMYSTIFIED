# Whiteboard Script — Enterprise RAG with Access Control, on Databricks

> **Level** 🔴 Design Mastery · **Module** 09 · **whiteboard_scripts/** · **Time** ~60 min to deliver, ~2 h to internalise
> **Prerequisites:** [The 60-Minute Whiteboard Method](../../02_System_Design_Fundamentals/05_The_60_Minute_Whiteboard_Method.md); Module 04, Module 08 doc 3
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/INTERVIEW_SCRIPT_DATABRICKS.md` — kept as a performance artefact: a full six-step script, minute by minute, with the lines that carry each step. Read the method first; rehearse from this.

---


**How to present the Lakehouse version in a 60-minute system design round, using the 6-step framework.**

Companion to `INTERVIEW_SCRIPT.md` (the platform-agnostic version). Use **this** one when the
interviewer is a Databricks customer, when you're asked "how would you do this on our stack", or when
you want to show that you build on the platform rather than beside it. Concepts live in
`docs/03-theory-databricks.md`.

---

## Before you start

**The framing sentence — say it in the first two minutes:**

> *"Anyone can build multi-source RAG. What makes it hard is that a Tier-1 agent, a Tier-3 engineer
> and an account manager must get **different correct answers to the same question**. On Databricks
> most of that is Unity Catalog's job rather than mine — with two specific exceptions that decide the
> whole physical architecture, and I'll get to them."*

That last clause is deliberate. It plants a hook, and it signals you know the sharp edge before
they ask.

**Time budget** — write it on the board:

| Min | Phase |
|---|---|
| 0–8 | Clarify + scope |
| 8–15 | Lakehouse architecture (medallion for RAG) |
| 15–35 | **Deep dive: the two Vector Search governance facts + the two-layer answer** |
| 35–45 | Retrieval, agent, evals |
| 45–55 | Multi-tenancy, failure, scale, cost |
| 55–60 | Trade-offs + week one |

---

# STEP 1 — Clarify and scope (0–8 min)

Same questions as the platform-agnostic version, **plus four that are Databricks-specific** and that
immediately show you've deployed on it before:

1. **Is Unity Catalog already the governance boundary**, or is data still in a mix of Hive metastore
   and external systems? *(If UC isn't in place, that's the first project, not the RAG.)*
2. **Where do groups come from — is SCIM syncing from Okta/Entra?** *(This is the identity backbone.
   If groups are managed by hand in the workspace, live revocation doesn't work.)*
3. **Do the source systems' permissions need to be mirrored, or is a coarser model acceptable?**
   *(Mirroring Confluence space ACLs per-document is a very different project from "five groups".)*
4. **Serverless available? Which cloud, which region?** *(Data residency is a row-filter rule, and it
   is also a workspace-placement decision.)*

Then scope out loud, and write it where it stays visible:

> *"Read-only Q&A over six sources, multi-tenant, attribute-based access, sub-3-second interactive.
> I'm descoping write actions and real-time streaming ingestion."*

**The case study to anchor on** — draw this table, it's the requirement:

| Who asks *"Why did Vertex lose data in March, and do they get credits?"* | Correct answer |
|---|---|
| Tier-1 support | Platform backlog; credits go to the account manager |
| Tier-3 engineer | The engineering root cause; account is credit-eligible |
| Account manager | The contractual credit tiers — not the root cause |
| External contractor | Nothing |
| Another tenant | Nothing at all |

---

# STEP 2 — Entities and the happy path (8–12 min)

Nouns first:

```
Catalog · Schema · Chunk · ACL columns · Account group · Entitlement · Row filter
Column mask · VS index · Endpoint · Agent · Trace · Run
```

Narrate one request before drawing a thing:

> *"A Tier-3 engineer asks in the app. The app has their forwarded token. We compile their group
> membership into a Vector Search filter and get back ranked chunk IDs. Then — and this is the part
> that matters — we re-read those chunk IDs from the governed Delta view **as that user**, so Unity
> Catalog applies the row filter and column mask itself. We rerank, check sufficiency, generate with
> citations, verify, answer. Every step lands in an MLflow trace."*

---

# STEP 3 — The architecture (12–18 min)

Draw the medallion, and label the arrows.

```
 SOURCES            BRONZE                SILVER                      GOLD
 ───────            ──────                ──────                      ────
 Confluence  ┐  Lakeflow    raw docs   chunks + ACL columns    ┌─ Vector Search index
 Zendesk     ├─ Connect  ──> in UC   ──> NO policies here! ────┤   (Delta Sync, CDF)
 Salesforce  │  Auto Loader  Volume      (see 4A)              └─ kb_chunks_secure
 SharePoint  ┘  ai_parse_    + Delta                               (governed VIEW)
                document                    ▲
                                   Lakeflow Declarative Pipeline
                                   does the chunking + maps each
                                   source system's permissions
                                   into our ACL columns
```

**Two things to say here:**

- *"The pipeline's real job isn't chunking — it's translating each source system's permission model
  into our ACL columns. Confluence space perms, Zendesk organisations, SharePoint groups. Getting
  that translation wrong is the number one cause of enterprise RAG leaks."*
- *"If a document arrives with no usable permissions, the pipeline quarantines it rather than
  defaulting it to 'internal' and hoping."*

---

# STEP 4 — Deep dive (18–40 min)

## ⭐ 4A. Lead with the trap. This is the round.

Draw the wrong design first — deliberately — then break it:

```
   ✗  "UC governs the table, so the index is governed too"

      governed Delta table ──sync──> Vector Search ──query──> every row, to everyone
         (row filter)                (row filter LOST)
```

Then say it plainly — **and there are two facts, not one:**

> **"First: Databricks Vector Search does not enforce Unity Catalog row filters or column masks. The
> docs are explicit — *'Row and column level permissions are not supported. However, you can implement
> your own application level ACLs using the filter API.'* The index is a derived copy; the sync
> pipeline reads with its own identity and writes into a serving system that has no concept of my
> users, so there's no query-time principal for `is_account_group_member()` to evaluate."**
>
> **"Second — and this one isn't in the limitations page, I found it by building it: you can't even
> *create* the index on a governed table. It fails at creation:"**
>
> ```
> BadRequest: Table main.meridian_rag.chunks cannot have both
>             row/column security and online materialized views.
> ```
>
> **"So the naive design isn't just insecure — it doesn't build. The platform stops you, which forces
> a physical split you have to design for up front."**

**Pause there.** This is the single highest-signal thing you can say in this round: it's specific,
counter-intuitive, verifiable, and most candidates get it wrong. The second fact in particular is
very hard to know without having actually built it.

### The split it forces — draw this

```
   kb.chunks              UNGOVERNED base table
      |                   SELECT granted ONLY to the sync service principal
      |
      +--------------->   VECTOR SEARCH INDEX   (Delta Sync reads this)
      |                   layer 1 - ACL applied by the query filter
      |
      +--------------->   kb.chunks_secure      GOVERNED dynamic view
                          SELECT granted to humans and agents
                          layer 2 - UC enforces ACL + PII masking
```

> **The consequence to say out loud:** *"Because the base table has no policies on it, granting anyone
> `SELECT` on it bypasses the whole access model. Locking it to the pipeline identity stops being
> hygiene and becomes load-bearing. That's a governance rule I'd write down and audit, not assume."*

And a small one that costs an afternoon if you don't know it:

> *"`CREATE OR REPLACE TABLE` does not detach an already-attached row filter. A half-finished run
> leaves the table permanently un-indexable until you drop the filter or the schema — so I make the
> setup idempotent."*

### Then the two-layer answer

```
  ① VECTOR SEARCH FILTER          — runs as the service principal
     compiled from the caller's groups, passed on every single query
     → unauthorised vectors are never scored
     → an OPTIMISATION and a first line of defence
                    │  chunk_ids + ranking
                    v
  ② RE-READ FROM THE GOVERNED VIEW, AS THE USER   — on-behalf-of-user
     → Unity Catalog applies the row filter and the column mask
     → THIS is the authoritative decision
```

> **The line to land:** *"Layer 1 makes retrieval cheap. Layer 2 makes it correct — and layer 2 isn't
> my code, it's Unity Catalog. The same engine that governs every dashboard in the company. The text
> that reaches the model is what came back from layer 2, never what the index returned."*

If you built the OSS version too, this is a strong comparison to draw:

> *"In my platform-agnostic build I wrote that post-check in Python and had to prove it correct with
> tests. Here I delete that code and the platform enforces it. That's the argument for building on
> Databricks rather than beside it."*

## 4B. The policy, in SQL

The same seven rules, but note *where* they hang. For the index source table the policy must be a
**view** (Fact 2 above); `SET ROW FILTER` is still the right call on any governed table that is *not*
an index source. Write this on the board — it's compact and it lands:

```sql
CREATE OR REPLACE FUNCTION security.chunk_row_filter(
  tenant_id STRING, sensitivity_lvl INT, region STRING,
  need_to_know STRING, valid_from DATE, valid_until DATE, source_system STRING)
RETURN is_account_group_member('kb_admins')
    OR EXISTS (SELECT 1 FROM security.user_entitlements e
               WHERE e.user_email = current_user()
                 AND tenant_id = 'meridian'                              -- tenant
                 AND sensitivity_lvl <= e.clearance_lvl                  -- clearance
                 AND (region = 'GLOBAL' OR region = e.region)            -- residency
                 AND (valid_from IS NULL OR valid_from <= current_date())-- embargo
                 AND (need_to_know IS NULL OR need_to_know = e.compartment)
                 AND (NOT e.is_external OR source_system NOT IN ('contract','pricing')));

-- on a table that is NOT a vector index source:
ALTER TABLE kb.chunks_governed SET ROW FILTER security.chunk_row_filter ON (...);

-- on the index source, the same predicate goes in a view instead:
CREATE OR REPLACE VIEW kb.chunks_secure AS
SELECT chunk_id, doc_id,
       CASE WHEN NOT contains_pii THEN content
            WHEN is_account_group_member('pii_readers') THEN content
            ELSE regexp_replace(content,'[\w.+-]+@[\w-]+\.[\w.-]+','[REDACTED_EMAIL]')
       END AS content
FROM kb.chunks c WHERE EXISTS ( ...the seven rules... );
```

> *"Seven policy rules in one object, and it governs **every** reader of it — the agent, a notebook,
> a dashboard, a SQL query. Not just callers who go through my application code."*

PII becomes a **column mask** (`is_account_group_member('pii_readers')`). Flag the distinction if they
know the platform: *"a UC column mask, not `ai_mask` — `ai_mask` is an AI transform, it's not an
access-control primitive and I'd never put it between a user and PII."*

**Live revocation, in one sentence:** *"`is_account_group_member()` reads SCIM-synced account groups,
so removing someone in Okta takes effect on their next query. No reindex, no cache bust, no code."*

## 4C. Encoding the ACL for the index filter

The gotcha, and it's a good one to volunteer:

> *"Vector Search filters work on scalar columns — there's no documented array-containment operator,
> so `allowed_groups ARRAY<STRING>` can't be filtered directly."*

Two encodings, and pick one out loud:

```
A. One BOOLEAN column per group  ← my default (bounded group set)
   "tenant_id='meridian' AND sensitivity_lvl<=2 AND region IN ('GLOBAL','EU')
    AND (grp_public=true OR grp_support_t3=true OR grp_engineering=true)"

B. Fan out one row per (chunk, group), filter group_id IN (...)
   unbounded groups, but multiplies VECTORS — the expensive thing
```

### ⭐ The war story to tell here

> *"One thing that bit me when I built this. On a **Standard** endpoint the filters are dictionaries,
> and the multi-column OR is **positional** — the value has to be an array with one element per OR
> clause, not a single scalar:*
>
> ```python
> {"grp_a OR grp_b": True}          # 400: "input must be an array"
> {"grp_a OR grp_b": [True]}        # 400: "length of value != number of clauses"
> {"grp_a OR grp_b": [True, True]}  # ✅  grp_a = true OR grp_b = true
> ```
>
> *So the array has to be regenerated whenever the caller's group count changes — I build the clause
> and its value array from the same list so they can't drift.*
>
> ***And it's another reason I'd pick Storage-Optimized: its filter is a SQL string, so
> `(grp_a = true OR grp_b = true)` means exactly what it looks like. No footgun."***

That's a detail you only have if you've run it, and it lands harder than any amount of architecture
diagramming.

**And the endpoint choice, justified:**

| | Standard | **Storage-Optimized** ← choose |
|---|---|---|
| latency | 20–50 ms | 300–500 ms |
| capacity | ~320M | 1B+ |
| cost | higher | **~7× lower** |
| filters | dictionary | **SQL string** |

> *"300–500ms of retrieval is invisible next to a 2-second generation, and I get SQL-string filters —
> which means my access predicate is reviewable by a security person. That's worth real money to me."*

## 4D. Retrieval — say what you *didn't* build

```python
index.similarity_search(
    query_text=q,
    query_type="HYBRID",              # dense + BM25, managed
    filters=acl_filter,               # ← layer 1, on every call
    reranker={"model": "databricks_reranker",
              "parameters": {"columns_to_rerank": ["title", "content"]}},
    num_results=20)
```

> *"Hybrid is one parameter. That replaces a BM25 index I'd otherwise hand-roll — and it kills the
> worst limitation of my OSS build, where I rebuilt the lexical index per request over the authorised
> pool. Reranking is another parameter: the managed reranker takes the top ~50 before returning my
> top-k."*

> *"Why hybrid at all: enterprise text is full of `MRD-4290`, `ws_vtx_eu_001`, `ING-2291`. Embeddings
> blur those together because they* look *alike. BM25 treats them as rare tokens and nails them.
> Dense finds what* means *the same; lexical finds what* says *the same."*

**What stays in agent code:** Multi-Query/RAG-Fusion, HyDE, decomposition, and the RRF across
generated queries. Those are orchestration patterns, not retrieval infrastructure.

---

# STEP 5 — Cross-cutting, failure, scale (40–55 min)

**Raise all of this unprompted.**

## Identity — the piece that makes layer 2 real

```
 user → App / Agent endpoint
    │ Databricks downscopes credentials to declared scopes,
    │ forwards them as  x-forwarded-access-token
    v
 get_user_workspace_client()   ← inside the request handler, never at startup
    v
 SQL warehouse → kb_chunks_secure → UC applies row filter + column mask
```

**Name the caveats yourself** — this is credibility, not weakness:
- OBO for agent endpoints is **public preview**; an admin has to enable it.
- Token refresh can lag **~5 minutes**.
- The token exists only at request time.

## Evaluation

```python
@scorer
def no_leak(inputs, outputs, expectations):
    leaked = set(expectations["forbidden_docs"]) & set(outputs["retrieved_doc_ids"])
    return {"value": 0.0 if leaked else 1.0}

mlflow.genai.evaluate(data=uc_dataset, predict_fn=ask_as_user,
                      scorers=[Correctness(), RetrievalGroundedness(), no_leak])
```

> *"Three families: retrieval, generation, and security. Security isn't a metric — it's a gate.
> A retrieval regression is a bug I fix next sprint; a leak is an incident."*

**Two hard-won points to make here:**

1. *"Never gate a release on an LLM judge. `Correctness` varies run to run; `no_leak` is set
   arithmetic and doesn't. Only the deterministic one blocks a deploy."* — *(If asked why you feel
   strongly: in my OSS build a security case flapped because the sufficiency verdict was an LLM
   judgement. Zero leaks either way, but a flaky alarm trains people to ignore the alarm.)*
2. **The Databricks superpower** — *"On this stack the leak test doesn't even need the agent. It's a
   SQL assertion against the governed view:*

   ```sql
   -- run as the Tier-1 agent's identity → must return 0
   SELECT count(*) FROM kb.chunks_secure WHERE doc_id = 'CT-VTX-001';
   ```

   *That's stronger than anything I can write in Python, because it tests the enforcement point
   itself rather than my code's use of it."*

Mention **MemAlign** (align a judge to SME labels via a UC labeling session) and `optimize_prompts()`
/ GEPA if they push on eval maturity.

## Observability — mostly free

| Question | Answered by |
|---|---|
| Why was this answer wrong? | MLflow Traces (spans, retrieved IDs, prompt version, tokens) |
| Did this user ever read that doc? | `system.access.audit` |
| Which tenant is burning budget? | `system.billing.usage` |
| What feeds this table? | `system.access.table_lineage` |

> **Volunteer the gap:** *"`system.access.audit` covers the Delta read. A Vector Search query isn't a
> UC table read, so it doesn't land there. Because layer 2 re-reads everything from the governed
> table, the audit trail is complete for anything the user actually saw — but I log the index's raw
> return separately, because **rows the index returned that the governed view then dropped** is my
> staleness signal. On Databricks that's a metric I can alert on."*

## Multi-tenancy

Catalog per tenant (hard boundary, natural unit for residency and CMEK) **plus** a `tenant_id`
predicate in the row filter. Defence in depth. Per-tenant **AI Gateway rate limits** for noisy
neighbours; tag endpoints and warehouses so billing attributes per tenant.

## Failure modes → degrade, don't break

| Fails | Behaviour |
|---|---|
| Model endpoint down | AI Gateway fallback to a secondary model; queue + backoff |
| VS endpoint down | fall back to keyword search over the governed view, **flag the answer as degraded** |
| Sync pipeline behind | serve from what's fresh, surface staleness; layer 2 keeps it *safe*, just less complete |
| Reranker unavailable | fall back to fusion order; trace records it |
| **SQL warehouse / UC unavailable** | **fail closed. Refuse.** Never fall back to the ungoverned index. |

That last row is the one to say slowly. **The failure mode you must never build is "layer 2 is down,
so serve layer 1's results".** That is a leak with a good excuse.

## Scale

- Delta Sync is incremental via **Change Data Feed** — only changed chunks re-embed.
- **Decouple ACL updates from content updates.** A permission change is a cheap column write; a
  content change means re-embedding. Conflating them makes every reorg expensive.
- Storage-Optimized scales past 1B vectors; index sync is ~20× faster than Standard.
- Cost shifts from per-token to **per-hour** — VS endpoints and warehouses bill while provisioned.
  At low volume that can cost *more* than a DIY stack; at enterprise volume it's dramatically cheaper.

---

# STEP 6 — Close deliberately (55–60 min)

### Three sentences

> *"Multi-source RAG on the Lakehouse, where Unity Catalog is the authority on access. A compiled ACL
> filter makes Vector Search cheap; an on-behalf-of-user re-read from the governed Delta view makes it
> correct. Hybrid retrieval and reranking are managed, the agent is MLflow-tracked and UC-registered,
> and every release is gated on a deterministic zero-leak assertion."*

### Top trade-offs, with what would change your mind

| Decision | Chose | Would revisit if |
|---|---|---|
| Two-layer enforcement | VS filter + OBO governed re-read | VS ships real row-level security → collapse to one layer |
| Storage-Optimized endpoint | yes — cost + SQL filters | a sub-100ms interactive SLA → Standard |
| Boolean-column-per-group | yes — bounded group set | thousands of groups → fan-out rows, or a per-request authz service |
| Catalog per tenant | yes | hundreds of small tenants → schema-per-tenant + row filter |

### The forward-deployed close — don't skip it

> *"Week one at a customer isn't this diagram. It's: get Unity Catalog and SCIM right, land **one**
> source, write the row filter, and prove the permission model for **three** personas with SQL
> assertions — before anyone argues about embedding models. If UC and SCIM aren't in place, that's the
> project, and I'd say so on day one rather than discovering it in week three."*

---

## Cheat sheet — the lines that carry this round

1. *"Vector Search does **not** enforce UC row filters — and it won't even build on a governed table. The index is a derived copy; the filter doesn't travel with the data."*
1b. *"So the base table stays ungoverned and locked to the pipeline SP, and humans read a governed view. Granting SELECT on that base table bypasses everything."*
2. *"Layer 1 makes retrieval cheap; layer 2 makes it correct — and layer 2 is Unity Catalog, not my code."*
3. *"The row filter protects the table for every reader, not just callers who go through my app."*
4. *"Live revocation is free: SCIM group change, next query, no reindex."*
5. *"Hybrid and reranking are one parameter each — I deleted a whole BM25 subsystem."*
6. *"Never gate a release on an LLM judge. The leak test is set arithmetic."*
7. *"On Databricks the leak test is a SQL assertion — it tests the enforcement point, not my code."*
8. *"Fail closed on authorisation. Never serve layer 1's results when layer 2 is down."*
9. *"Layer 1 overshooting is by design — embargo and need-to-know can't be pushed into the index. So the gate measures what reaches the model, not what the index proposed. Measuring the wrong layer gave me 6 false leaks the first time."*
9. *"A UC column mask, not `ai_mask` — one is governance, the other is a transform."*

## Questions to ask them

- Is Unity Catalog the governance boundary today, or is there still Hive metastore to migrate?
- Are account groups SCIM-synced, or managed in-workspace? *(Decides whether live revocation works.)*
- How faithfully do source-system permissions need to be mirrored per document?
- Where do you draw the line between platform-generic and customer-specific in a deployment?

## The one artefact to bring

A **persona × document visibility matrix**, generated by running the same
`SELECT count(*) FROM kb.chunks_secure` as each identity. Every cell decided by Unity Catalog, no LLM
involved, and one principal who sees nothing at all despite holding every group and the highest
clearance. It takes two seconds to run and it ends the access-control conversation.

---

## What I can say I actually ran

Useful to have straight, because "I designed this" and "I ran this" are different claims and an
interviewer will hear the difference.

**Executed against a live workspace** (Unity Catalog metastore, serverless SQL warehouse, an existing
Vector Search endpoint; all test objects dropped afterwards):

- **The whole notebook, end to end** — `notebooks/04-databricks-enterprise-rag.ipynb` runs to
  completion on serverless in ~12 minutes, builds the index, and passes its own leak gate.
- The **7-rule policy** — created and enforced. Tier-1 saw 2 of 8 rows; the contract, post-mortem,
  pricing policy and advisory all returned `count(*) = 0`.
- **The index/governance conflict** — confirmed by hitting it: a Delta Sync index refuses to build on
  a table carrying a row filter or column mask.
- **Clearance change with no DDL and no reindex** — the restricted rows appeared on the very next
  query. That's the live-revocation claim, demonstrated.
- **Embargo** — the advisory stayed hidden even at restricted clearance *with* the right compartment,
  because `current_date()` is evaluated per query.
- **External-principal rule** — commercial sources blocked despite maximum clearance.
- **Column mask** — same column, same query: redacted where `contains_pii = true`, untouched where
  false.
- **Vector Search ABAC filters** — 6 personas, 6 exact matches, including a cross-tenant principal
  with every group and top clearance returning **zero rows**.
- **Hybrid search**, and dict filter operators (`=`, `IN`, `>=`, `NOT`) — all confirmed. SQL-string
  filters correctly **rejected** on a Standard endpoint.

**What I could not verify end-to-end, and would say so:**

- The **managed reranker**. The API accepted the parameter shape, but the workspace returned *"a
  workspace-level configuration is preventing us from accessing the reranker model."* So I'd treat
  reranker availability as a per-workspace thing to confirm rather than assume — and I'd say that
  rather than implying I'd benchmarked it.
- **On-behalf-of-user auth**, which is public preview and needs an admin to enable it. The design
  depends on it; I've read the contract carefully but have not run it.

Being precise about that line is worth more than pretending the whole thing is battle-tested.

---

## Sources

- [Vector Search — row/column permissions not supported](https://docs.databricks.com/aws/en/generative-ai/vector-search)
- [Query an AI Search index — filters, hybrid, reranker](https://docs.databricks.com/aws/en/ai-search/query-ai-search)
- [Databricks Apps — on-behalf-of-user auth](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/auth)
- [Agent Framework — agent authentication](https://docs.databricks.com/aws/en/generative-ai/agent-framework/agent-authentication)
- [Unity Catalog — privileges and securable objects](https://docs.databricks.com/data-governance/unity-catalog/manage-privileges/privileges.html)
