# Meridian Assist — Enterprise RAG with Attribute-Based Access Control

An enterprise RAG platform built around the problem that actually makes enterprise RAG hard: **not
everyone is allowed to read everything, so the same question has different correct answers for
different people.**

Built with **LangGraph** (orchestration), **ChromaDB** (vectors), and **OpenAI** (embeddings +
generation).

---

## The business case

**Meridian Cloud** is a B2B SaaS observability company. Support engineers, account managers and
security staff all need answers from the same knowledge base — help-centre docs, engineering
runbooks, support tickets, incident post-mortems, customer contracts, pricing policy and security
advisories.

They cannot all see the same things:

> *"Why did Vertex Financial lose data in March, and do they get service credits?"*

| Who asks | What they should get |
|---|---|
| Tier-1 support agent | Platform-side backlog; credits are an account-manager conversation |
| Tier-3 engineer | The engineering root cause; the account is credit-eligible |
| Account manager | The contractual credit tiers — but not the engineering root cause |
| External contractor | Nothing — blocked by data residency and the external-source rule |
| Anyone in another tenant | Nothing at all, regardless of their groups or clearance |

Getting that right — **provably**, not by prompting the model nicely — is what this project is about.

---

## Quick start

```bash
# 1. OPENAI_API_KEY must be in the repo-root .env (it already is)
# 2. Build the index (~$0.0001, a few seconds)
python scripts/ingest.py

# 3. Ask something
python scripts/ask.py --user u_marco_t3 "Why did EU ingest degrade on 14 March?"
python scripts/ask.py --list-users

# 4. The access-control demo — the one to run in front of an interviewer
python scripts/demo_access_control.py --matrix    # policy only, no LLM cost
python scripts/demo_access_control.py             # full demo

# 5. Evaluation
python scripts/evaluate.py --kinds security       # the release gate
python scripts/evaluate.py                        # the full golden set
python scripts/evaluate.py --compare dense bm25 hybrid multi_query hyde enterprise
python scripts/calibrate_judge.py                 # LLM-judge vs. hand-labeled cases

# 5b. The moderate-effort additions from docs/07's punch list
python scripts/demo_second_connector.py           # a JSON connector into its own tenant
python scripts/demo_incremental_sync.py           # content-hash sync skips unchanged docs
python scripts/demo_acl_catalog_update.py         # live ACL change, no reindex

# 6. Tests
python -m pytest -m "not llm"    # 62 fast tests, no API calls
python -m pytest                 # + 6 live integration tests
python tests/verify_security_reference.py   # asserts docs/04 matches the running policy
```

---

## Documentation

| File | What it is |
|---|---|
| **`docs/01-theory.md`** | The concepts, in plain language with diagrams. Read first. |
| **`notebooks/02-hands-on.ipynb`** | Builds and runs every component, step by step. |
| **`INTERVIEW_SCRIPT.md`** | How to present this on a whiteboard in 60 minutes (the 6-step framework). |
| **`docs/04-security-checks-reference.md`** | **Every field and every check, with a worked example each.** The doc to revise from before an interview. |
| **`docs/03-theory-databricks.md`** | The same system rebuilt on the Lakehouse — UC governance, Vector Search, Agent Framework, MLflow. |
| **`notebooks/04-databricks-enterprise-rag.ipynb`** | **Runs in a Databricks notebook.** Builds the whole Lakehouse version and attacks it. |
| **`INTERVIEW_SCRIPT_DATABRICKS.md`** | The Databricks-native whiteboard script (6 steps), for a Databricks-stack audience. |
| **`databricks/`** | Standalone validation scripts (run locally against a workspace over REST). |
| **`docs/Scale_Optimization.md`** | Scaling this platform to 20M documents, latency optimization, and cost — what breaks first, what the fix is, and interview-ready answers. |

### Which notebook do I run where?

| Notebook | Runs on | Needs |
|---|---|---|
| `notebooks/02-hands-on.ipynb` | **Your laptop** | `OPENAI_API_KEY` in `.env`; ChromaDB |
| `notebooks/04-databricks-enterprise-rag.ipynb` | **A Databricks workspace** (serverless is fine) | A Vector Search endpoint; nothing else — auth is notebook-native |

Import the Databricks one with:

```bash
databricks workspace import /Users/<you>/enterprise_rag/04-databricks-enterprise-rag \
  --file notebooks/04-databricks-enterprise-rag.ipynb \
  --format JUPYTER --language PYTHON --overwrite --profile DEFAULT
```

Set `VS_ENDPOINT` in the config cell to an endpoint you already have, or flip `CREATE_ENDPOINT = True`.
The last cell drops everything it created.

### Two versions, on purpose

`01` / `INTERVIEW_SCRIPT.md` are **platform-agnostic** — ChromaDB, OpenAI, a hand-written policy
engine. Everything runs and is tested.

`03` / `INTERVIEW_SCRIPT_DATABRICKS.md` are the **Lakehouse design**, where most of that hand-written
machinery becomes a platform primitive — and where one specific gap decides the architecture:

> **Databricks Vector Search does not enforce Unity Catalog row filters or column masks.** The index
> is a derived copy; the filter does not travel with the data. The answer is two enforcement layers —
> a compiled ACL filter on the index, then an authoritative re-read from the governed Delta view
> *on behalf of the user*, where UC itself does the enforcing.

Being able to present both — and explain why the second is better — is the point.

---

## Architecture

```
START -> authorize -> plan -> retrieve -> enforce -> grade -+-> generate -> verify -> END
                                                            +-> refuse ------------> END
```

`authorize` runs **first**; `enforce` runs **before the model sees anything**. That ordering is
expressed in the graph's edges rather than left to a code convention.

| Node | Does |
|---|---|
| `authorize` | Resolves the principal, compiles the ABAC policy into a Chroma `where` filter |
| `plan` | Detects multi-hop questions and decomposes them |
| `retrieve` | Runs the chosen strategy — every store call carries the ACL filter |
| `enforce` | **Authoritative** policy re-check + PII redaction + audit events |
| `rerank` | LLM reranker, 20 candidates → 6 (runs *after* enforcement) |
| `grade` | Sufficiency gate: sufficient / partial / insufficient |
| `generate` | Synthesis with inline citations |
| `verify` | Citation validity + ACL re-check + groundedness score |
| `refuse` | Clean no-answer path with escalation |

### Access control: two layers

```
LAYER 1  pre-filter   (cheap, approximate — an OPTIMISATION)
         compiled into the vector search: tenant, clearance, region, group overlap

LAYER 2  post-check   (authoritative — THE ACTUAL DECISION)
         full policy on fresh attributes: embargo, need-to-know, live revocation, obligations
```

**The filter makes retrieval cheap. The post-check makes it correct.** When layer 2 denies something
layer 1 should have caught, that is logged as a **security event** — the index is stale or the filter
is broken.

Plus physical isolation: **one Chroma collection per tenant**, so a bug in the metadata filter still
cannot cross a tenant boundary.

### The policy (deny overrides allow)

| # | Rule | Denies when |
|---|---|---|
| 1 | `tenant_isolation` | different tenant — nothing crosses this |
| 2 | `clearance` | document outranks the principal's clearance |
| 3 | `data_residency` | document is region-locked, principal is elsewhere |
| 4 | `embargo` | before publication or after expiry |
| 5 | `need_to_know` | principal isn't in the document's compartment |
| 6 | `external_restriction` | contractors can't read commercial sources |
| 7 | `default_deny` | nothing granted it |

Plus **obligations** on an allow: `redact_pii`, `audit_access`.

### Retrieval strategies

All swappable and benchmarked against the same golden set:

| Strategy | What it does |
|---|---|
| `dense` | Vector search only (baseline) |
| `bm25` | Keyword only — error codes, ticket IDs, SKUs |
| `hybrid` | Dense + BM25 fused with Reciprocal Rank Fusion |
| `multi_query` | N LLM rewrites → retrieve each → RRF (**= RAG-Fusion**) |
| `hyde` | Hypothetical answer embedded as the search probe |
| `enterprise` | All of the above + decomposition + reranking (**production default**) |

---

## Layout

```
enterprise_rag_platform/
├── data/
│   ├── corpus/              22 documents with ACL frontmatter
│   ├── identities.json      9 personas, each exercising a different policy rule
│   └── golden_set.json      22 eval cases (quality / security / behaviour)
├── docs/01-theory.md
├── notebooks/02-hands-on.ipynb
├── scripts/                 ingest, ask, demo_access_control, evaluate, generate_corpus
├── src/enterprise_rag/
│   ├── authz/               policy.py (the rules) + enforcement.py (the backstop)
│   ├── ingest/              loader, chunker, store, pipeline
│   ├── retrieval/           strategies, fusion, lexical, expansion, rerank
│   ├── graph/               LangGraph nodes, state, versioned prompts
│   ├── evaluation/          the golden-set harness
│   └── observability/       run tracing
├── tests/                   68 tests (62 fast, 6 live)
└── INTERVIEW_SCRIPT.md
```

---

## Verified results

Everything below was produced by running this code against live OpenAI. **The full-corpus table below
predates the retrieval-pool sizing change** (`dense_k`/`bm25_k`/`fusion_k` were raised from 12/12/20
to 40/40/50 per `docs/07`'s punch list, closer to the prep doc's "top 50-100 before reranking"
reference) **and the nDCG metric** — a spot-check 10-case run after both changes still shows 100%
pass rate, recall@k 1.00, nDCG 0.96, at a comparable per-case cost, but the full 22-case × 6-strategy
comparison hasn't been re-run since (it's a real-money, multi-minute operation each time).

**Golden set, `enterprise` strategy — 22/22 pass**

```
recall@k     1.00      refusal accuracy  100%       LEAKS   0   (gate: must be 0)
MRR          1.00      distractions      0          p50     10.7 s
groundedness 1.00      refusal advisories none      cost    $0.0196
```

**Strategy comparison** — same golden set, all six strategies:

| strategy | recall@k | MRR | grounded | refusal_acc | **leaks** | distract | p50 ms | cost |
|---|---|---|---|---|---|---|---|---|
| dense | 1.00 | 0.958 | 1.00 | 0.917 | **0** | 0 | 6259 | $0.0133 |
| bm25 | 1.00 | 0.944 | 1.00 | 1.000 | **0** | 1 | 5200 | $0.0157 |
| hybrid | 1.00 | 0.958 | 1.00 | 0.917 | **0** | 0 | 7339 | $0.0153 |
| multi_query | 1.00 | 0.958 | 1.00 | 1.000 | **0** | 0 | 8313 | $0.0153 |
| hyde | 1.00 | **1.000** | 0.929 | 0.917 | **0** | 0 | 8850 | $0.0163 |
| enterprise | 1.00 | 0.958 | 1.00 | 0.917 | **0** | 0 | 10908 | $0.0200 |

**Tests** — 62 fast (policy, fusion, chunking, enforcement, golden-set integrity) + 6 live
integration, all passing.

### Read these numbers honestly

**The corpus is 22 documents.** Retrieval is easy at that size, so every strategy scores near
perfectly on quality and the differences are noise. Do **not** read this table as proof that HyDE or
multi-query earn their keep — `enterprise` is simply the slowest and most expensive here, and `dense`
would be the right production choice *for this corpus*. The value is that the harness **exists and
gates the release**: on a 200,000-document corpus the same table is what tells you whether HyDE earns
its latency. The number that matters here is the **zero leak column**.

**Three things the eval caught during development**, all of which are in the git history rather than
quietly fixed:

1. **A false security alarm.** `bm25` was reported as leaking `CT-VTX-001` to the account manager —
   but she is *permitted* to read it; it was simply the wrong document for a pricing question. I had
   conflated "unauthorised" with "irrelevant" in one field. Split into `forbidden_docs` (gates the
   release) and `distractor_docs` (a precision metric), with `tests/test_golden_set.py` asserting
   every `forbidden_docs` entry is genuinely policy-denied so the labels cannot drift again. A false
   security alarm is worse than no alarm — it trains people to ignore the real one.
2. **A shadowed policy rule.** A coverage test showed no security case actually exercised
   `external_restriction`: for the contractor persona, `clearance` denied first every time. Added a
   high-clearance external consultant (`u_dana_ext`) and case `S09`, where that rule is the *only*
   thing standing between her and the contracts.
3. **A flaky gate.** Case `S05` refuses on most runs and occasionally answers thinly from public
   help-centre docs, because the sufficiency verdict is an LLM judgement. Zero leaks either way. So
   security cases now gate **only** on the deterministic property (leaks, decided by the policy
   engine with no model involved); the refusal expectation is recorded as a non-gating advisory.
   Security must never hinge on a coin flip.

**Two more, caught while adding the moderate-effort items from `docs/07`'s punch list** — full
detail there, short version here:

4. **An unscoped reset cross-contaminated tenants.** Ingesting a brand-new `acme_helpdesk` tenant
   with `reset=True` silently wiped the unrelated, already-indexed `meridian` corpus, because
   `store.reset_store()`/`catalog.reset_catalog()` deleted the whole Chroma directory / whole SQLite
   file regardless of which tenant was being ingested. Fixed: both now accept a `tenant_id` and scope
   the reset to just that tenant; `pipeline.ingest()` passes its own through by default.
5. **A stored content hash survived a reset it shouldn't have.** Combining `reset=True` with
   `incremental=True` skipped re-embedding 21 of 22 documents into a *freshly-emptied* index, because
   their hashes matched records from before the reset — a near-empty index reporting success. Fixed:
   incremental skipping now only applies when `reset=False`.

---

## What this deliberately does *not* do

Named because an architect should know where the demo ends:

- **BM25 index is rebuilt per request** over the authorised pool. Correct, and wrong at scale — the
  production answer is a lexical store with native document-level security (Elasticsearch/OpenSearch
  DLS) or a cached per-group shard.
- **Identity is a JSON file**, not a live OIDC/SCIM integration.
- **Ingestion is still batch, not streaming CDC** — but it's no longer full-refresh-only: content-hash
  incremental sync (`ingest(incremental=True)`) skips re-embedding unchanged documents, and per-source
  last-sync freshness plus a persisted rejected-docs record exist (`ingest/freshness.py`).
- **Only two connectors exist** (markdown+frontmatter, and a JSON ticket export) — enough to prove the
  pipeline is format-agnostic, not a real Confluence/Zendesk/SharePoint integration.
- **Rate limiting and the circuit breaker are in-process, single-instance state** — correct logic, not
  backed by anything shared across workers or that survives a restart; same caveat as the caches below.
- **PII redaction is regex-based** — production wants Presidio or a cloud DLP service.
- **Reranking uses an LLM.** A cross-encoder is cheaper and faster at scale; `CrossEncoderReranker`
  is implemented behind the same interface as a one-line swap.
- **Caching is in-process only.** An embedding cache (`llm/client.py`) and a response cache
  (`graph/nodes.py::generate()`) now exist, both process-lifetime dicts — real infrastructure needs a
  shared store (Redis, etc.) with an eviction policy, not a dict that resets on restart. The response
  cache does respect the lesson from `SA-2026-05`'s war story about permission-epoch staleness: its
  key is derived from the *already-enforced* context (the chunk ids that survived Layer 2 this
  request), not from principal identity alone, so a revoked or newly-granted document changes the
  context and therefore the key — a stale cache entry is structurally not reachable, not just avoided
  by convention.
