# Scale and latency — from a 22-doc demo to 20M documents

This repo’s flagship corpus is **22 docs / 86 chunks** in a single-process Chroma collection. That
is deliberate: ACL and security stay cheap to prove. Interviewers will still ask *“what if the
customer has 20M documents?”*

This note is the honest answer: **what breaks first, what the fix is, and which fixes this codebase
already proves the pattern for** (even at toy scale) versus which answers are verbal-only because a
laptop demo cannot honestly show them.

**This is not one scaling problem.** It is three, and each needs a different fix:

1. Ingestion throughput
2. Query-time retrieval latency
3. Per-tenant isolation overhead

| Status           | Meaning                                          |
| ---------------- | ------------------------------------------------ |
| **Proven** | Same mechanism exists in this repo (small scale) |
| **Verbal** | Correct architecture; not an honest local demo   |
| **N/A**    | Does not apply here                              |

**Related:** [pipeline](06-architecture-end-to-end.md) · [coverage map §4.6](07-system-design-coverage-map.md)
(short 10M-chunk cost answer this file expands) · [Databricks / Lakehouse twin](03-theory-databricks.md)
(Vector Search + Unity Catalog — the real 20M-doc answer, not Chroma).

---

## Contents

1. [What breaks first](#1-what-breaks-first-at-20m-documents)
2. [Ingestion](#2-scaling-ingestion-to-20m-documents)
3. [Vector index](#3-scaling-the-vector-index)
4. [ACL / ABAC](#4-scaling-aclabac-enforcement)
5. [Latency](#5-latency-optimization)
6. [Cost](#6-cost-at-20m-documents)
7. [Chunking by document type](#7-chunking-strategy-by-document-type)
8. [Parent-child (small-to-big) chunking](#8-parent-child-small-to-big-chunking)
9. [Other interview points](#9-other-scale-points-worth-knowing-cold)

---

## 1. What breaks first at 20M documents

Assume ~4 chunks/doc → **~80M chunks**. Walk the pipeline and ask *what falls over here first*.

| Stage                  | Why it breaks                                                                | First symptom                                                                                |
| ---------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **Ingestion**    | Single-process embed loop; no volume-scale incremental sync                  | Days-long ingest; re-embedding unchanged docs                                                |
| **Vector index** | In-process Chroma has no answer for 80M vectors                              | OOM, or an unusable index build                                                              |
| **ACL / ABAC**   | Per-tenant scan + per-chunk attribute check do not shard                     | Latency grows with*corpus* size, not *result* size                                       |
| **BM25**         | Built fresh over`fetch_all_allowed()` per query (`retrieval/lexical.py`) | Rebuilding a keyword index per request is O(allowed pool) — fine at 86 chunks, fatal at 80M |
| **Reranking**    | `LLMReranker.rerank()` calls an LLM per candidate                          | 50 candidates × 20M-doc traffic = cost and latency                                          |
| **Audit**        | In-memory`RunTrace` / audit events                                         | Trail is not queryable; compliance risk                                                      |
| **Cost**         | Uncached embed/generate billed per token                                     | Linear growth with corpus size*and* query volume                                           |

---

## 2. Scaling ingestion to 20M documents

**Today:** `scripts/ingest.py` — one process, synchronous embed loop, content-hash incremental skip
(`demo_incremental_sync.py`, **proven**).

### What changes at 20M

1. **Parallelize embedding.** Fan out documents (`mapPartitions`, a job queue, Ray, a process pool).
   Embedding is embarrassingly parallel per document. **Proven pattern:** the content-hash check is
   the mechanism that makes re-runs cheap; it needs to run *inside* workers, not a serial `for`
   loop.
2. **Batch embedding API calls.** Hundreds of chunks per request. Never one chunk per HTTP call.
3. **Split chunking from embedding.** Chunking is CPU-bound and cheap; embedding is API-bound and
   expensive. Over-provision chunk workers relative to embed workers.
4. **Idempotent, resumable jobs.** A 20M-doc run *will* be interrupted. Content-hash dedup (already
   here) plus a per-document ledger (`queued` / `embedded` / `indexed` / `failed`) means a restart
   only finishes what did not finish.
5. **Dead-letter poison pills.** Some fraction will fail (corrupt PDF, bad encoding, empty file).
   Quarantine with the error reason; do not stall the batch on one bad doc.
6. **On Databricks** ([03-theory-databricks.md](03-theory-databricks.md)): Lakeflow pipeline — Auto
   Loader incrementally, Spark UDF (batched `ai_query` / foundation-model embeddings), Delta, then
   Vector Search sync. That is the production answer, not a bigger Chroma script. **Verbal.**

### Throughput math (say this out loud)

If embedding is ~**500 chunks/sec** (batched API, reasonable parallelism):

- 80M chunks ≈ 160,000 seconds ≈ **~44 hours** single-threaded-equivalent
- **50-way** parallelism → **under an hour**

The point is *throughput per worker × worker count*, not “it will be slow.”

---

## 3. Scaling the vector index

**Today:** Chroma, one collection per tenant, in-process / on-disk. Fine to roughly **10⁵–10⁶**
vectors.

**At ~80M vectors, this Chroma setup is the wrong tool.** Pick a real index:

| Option                                                                                    | When to pick it                                                                                                                                                                                    |
| ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Databricks Vector Search**                                                        | UC-governed, Delta sync, hundreds of millions of vectors, ACL via UC row filters. This is what`docs/03` and `notebooks/04` build. Natural fit because this repo already has a Databricks twin. |
| **Managed vector DB** (Pinecone, Weaviate, Milvus/Zilliz, Qdrant, sharded pgvector) | Not on Databricks. Need native sharding, replica reads, metadata-filtered ANN.                                                                                                                     |
| **Self-hosted sharded ANN** (FAISS/HNSW + a router)                                 | Only if you need full control*and* have the ops capacity. Rarely the right tradeoff for a 20M-doc *enterprise* deploy.                                                                         |

### Mechanisms any of those need

1. **ANN, not exact search.** HNSW or IVF: a small recall hit for orders-of-magnitude speed. Non-negotiable past ~1M vectors.
2. **Shard by tenant (or tenant-hash).** This repo already isolates tenants into separate collections
   (`tenant_isolation` in [docs/07](07-system-design-coverage-map.md)). That is why horizontal
   sharding is easy: a request is always one tenant, so queries never fan out across tenants.
   **Isolation model: proven. Sharding infra: verbal.**
3. **Push metadata filters into ANN**, not after it. Filter *after* top-K is how you silently lose
   recall (the true allowed hit may never have been in that top-K). Production DBs do filtered ANN
   (filter-then-search or search-with-filter). Call this out even at demo scale if asked.
4. **Replica reads.** Query load and index-build load scale independently. Writes go to a primary.
5. **Hot / cold tiering.** Recent or hot embeddings stay in the fast index; cold vectors go cheaper
   and rehydrate on demand. **Verbal** (also in [docs/07](07-system-design-coverage-map.md) §4.6).

---

## 4. Scaling ACL/ABAC enforcement

This is where the repo is actually strong. Be precise about what is free vs what is new work.

|                                                        | What                                                | Why                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------ | --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Proven — free at scale**                      | Tenant isolation via separate collections / indexes | A query is always one tenant’s shard. More tenants → more shards, not more per-query work.                                                                                                                                                                                                                     |
| **Proven — free at scale**                      | Post-retrieval re-check (`nodes.enforce()`)       | **O(candidates)**, not O(corpus). Candidates are already bounded by top-K.                                                                                                                                                                                                                                 |
| **Verbal — new work if the vendor cannot help** | ACL/ABAC *inside* ANN                            | If the index cannot filter in the search: (a) over-fetch top-K·N and filter (wasteful, can still under-fill) or (b) materialized per-principal / per-attribute indexes (fast, expensive to maintain). Databricks Vector Search and serious vector DBs support filtered search. Ask the vendor; do not build it. |
| **Proven mechanism, still holds at 20M**         | Live ACL without reindex                            | `demo_acl_catalog_update.py`: policy-table update takes effect with **zero reindex** because enforcement reads the catalog at **query** time. Cost still tracks candidate count, not corpus size. One of the few things that scales without new engineering.                                       |

---

## 5. Latency optimization

The customer-facing number. Attack each LangGraph stage ([docs/06](06-architecture-end-to-end.md) §3).

| Stage                                              | Lever                                                                             | Here                                                                                                                                             |
| -------------------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Rewrite / decompose / multi-query / HyDE** | Small`fast_model`, never the large model except final synthesis (`config.py`) | **Proven**                                                                                                                                 |
| **Retrieval (dense / BM25 / hybrid)**        | ANN is sub-linear; keep top-K small into rerank                                   | **Proven** (Chroma HNSW at small scale; same principle at large)                                                                           |
| **Rerank**                                   | Cheap reranker or cross-encoder — relevance, not reasoning                       | **Gap** — `LLMReranker` is a full LLM call                                                                                              |
| **Synthesis**                                | This stage*should* use the strong model                                         | Do not cheapen it                                                                                                                                |
| **Repeat / near-dup questions**              | Cache embeddings*and* full responses                                            | **Proven** — `llm/client.py::embed()`; `graph/nodes.py::generate()` keyed on `(question, ACL filter, exact context, coverage note)` |
| **LLM outage**                               | Circuit breaker / timeout; fail fast                                              | **Proven** — `_CircuitBreaker`, 3 failures, 30s cooldown, half-open trial                                                               |
| **Round-trips**                              | Batch embeds; parallelize independent LLM calls (multi-query rephrases)           | **Partial** — check whether `generate_multi_queries()` actually fans out concurrently                                                   |
| **Cold start per tenant**                    | Warm hot indexes; do not lazy-load a tenant only on first request                 | **Verbal** — warmup / pooling is a real prod concern                                                                                      |

### Five levers for p95 (interview-ready)

1. **Route by difficulty.** Cheap model for rewrite, HyDE, grade, rerank. Large model only for
   synthesis. Already `fast_model` / `synthesis_model`.
2. **Filter early.** ACL / tenant / ABAC before expensive rerank, so rerank only sees a small
   authorized set. Bigger corpus → this filter does more of the work.
3. **Cache precisely.** Embeddings and full answers keyed on question + ACL filter + context. A hit
   is only for an identical, freshly re-enforced situation.
4. **Parallelize independent LLM work.** Multi-query, HyDE, per-tenant requests. Do not serialize
   what is independent.
5. **Filter in the index.** Filtered ANN (section 3, item 3) is a latency win *and* a correctness
   win — no over-fetch-then-discard.

### p50 / p95 / p99

Interviewers want **tail**, not average.

| Percentile                | What dominates it                                                                                          |
| ------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **p50**             | Happy path: cache hit, or fast dense retrieve + small-model rewrite + synthesis                            |
| **p95 / p99**       | Cache miss on a cold query; multi-hop (extra LLM hops); rerank over a wide match set before ACL narrows it |
| **Circuit breaker** | A**p99** tool. It bounds a dead dependency. It does not improve the typical case.                    |

If asked “does caching fix tail latency?”: **no.** Caching moves the **median**. Timeouts, circuit
breakers, and fallback to a smaller model move the **tail**.

---

## 6. Cost at 20M documents

Same five levers as [docs/07](07-system-design-coverage-map.md) §4.6, restated:

1. Model routing by difficulty — **proven**
2. Prefilter before expensive rerank — **proven**
3. Embed + response cache; never pay twice — **proven**
4. Tiered storage (hot vs cold embeddings) — **verbal**
5. Cheaper reranker (every request, only a relevance score) — **gap** (see §5)

**One number to have ready.** One-time embed of ~80M chunks at ~$0.0001 / 1K tokens (small embedding
models) is real money but tractable — **low-to-mid four figures USD**, order of magnitude.

**Ongoing cost that actually matters** is query-time generation × query volume. That is why levers
1–3 dominate the conversation, not the one-time ingest bill.

---

## 7. Chunking strategy by document type

**Today:** `ingest/chunker.py` splits on markdown `#` / `##` / `###`, packs paragraphs to
`chunk_target_chars` with a trailing-tail overlap, and prefixes every chunk with `doc.title` +
section. Correct for this corpus: every source is already markdown. **Proven, single format.**
`Document.text` arrives clean. At 20M real enterprise docs, input is never uniform markdown — this
is the first place ingest has to grow.

The **chunking policy** below still applies once each format is text. Only “raw bytes → text +
structure” changes.

**Rule that generalizes:** chunk on the format’s **natural semantic unit**, not a fixed character
count. Carry structure (heading, page, slide title, table caption) into the chunk the same way this
repo prefixes `doc.title - section`. Fixed-size sliding windows are the **fallback** when there is
no usable structure — not the default.

| Format                                                       | Natural split                                                                | Notes                                                                                                                                                                                                                                                                                                            |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Markdown / plain text**                              | Headings, then pack paragraphs with overlap                                  | **Exactly this repo.** Overlap must keep a fact that straddles a boundary recoverable (`_pack()` `tail = current[-overlap:]`).                                                                                                                                                                         |
| **DOCX**                                               | Paragraph + Word Heading 1/2/3                                               | `python-docx`. Do **not** concatenate paragraphs and re-run the markdown chunker — you throw away heading styles. Map heading-styled paragraphs to `#` / `##`, then reuse `_split_by_heading()`. Tables: see Tables. Strip track-changes/comments first.                                          |
| **PDF**                                                | Text PDF vs scanned PDF                                                      | **Text:** layout-aware extract (`pdfplumber`, `PyMuPDF`) — reading order + font-size as heading signal. Rebuild hierarchy from font-size deltas, then heading-split-and-pack. **Scanned:** OCR first (Images). Multi-column reports need column-aware extract or reading order silently breaks. |
| **HTML**                                               | `<h1>`–`<h6>`, `<section>`, `<article>`, `<table>`, `<li>`      | Strip nav/footer/ads (readability-style, not raw`get_text()`). Same heading-to-marker conversion as DOCX, then the existing chunker.                                                                                                                                                                           |
| **Tables** (DOCX / PDF / HTML / Excel)                 | One chunk per table, or per row-group if huge.**Never split mid-row.** | Same failure`chunker.py` warns about (service-credit tiers). Large tables: (a) repeat header column names on every chunk; (b) small pricing/tier tables stay **one atomic chunk**.                                                                                                                       |
| **Excel / CSV**                                        | Logical row-groups (account, time window), not raw row count                 | 500-row slices have no topic for embedding. Prefer semantic groups. Always carry headers. Very wide tables (100+ cols): flatten to sentences (`For account X, revenue Q1 was Y…`) so the model sees relationships a raw grid hides.                                                                           |
| **Images** (scans, screenshots, diagrams, whiteboards) | Not text until converted                                                     | (1)**OCR** then chunk like text — gate on confidence; do not silently index garbage. (2) **Multimodal embeddings** (CLIP-style) when visual structure *is* the meaning (charts). Enterprise default is usually (1); mention (2) for diagrams.                                                     |
| **Code**                                               | Function/class boundaries (AST / tree-sitter). Never mid-function.           | Fallback: blank-line blocks + a hard cap — closer to`_pack()` than to headings.                                                                                                                                                                                                                               |
| **PowerPoint**                                         | One chunk per slide (or a few adjacent sparse slides)                        | Slide title = header prefix, like`doc.title - section`. Append speaker notes to that slide’s chunk; do not orphan them.                                                                                                                                                                                       |
| **Email / chat / tickets**                             | One turn, or question + resolving answer — not a character window           | A window that cuts a question from its answer is close to the worst failure for support RAG. Carry thread metadata (participants, time, resolution) the way`attrs` already rides on chunks — filtering *and* citations.                                                                                     |

### Size still matters, independent of format

After extract, the same `chunk_target_chars` / `chunk_overlap_chars` apply. Format decides **where
splits are allowed**. Size/overlap decide **how big each piece is**.

- Too small → lost context (row without header, sentence without the qualifier).
- Too large → precision dies (one chunk “answers” many questions equally badly) and rerank/generate
  cost per chunk goes up.

### Architecture: one pipeline, many parsers, one chunker

Do not write six chunkers. Write **per-format parsers** that turn raw bytes into a common
intermediate (text + heading hierarchy, or explicit table / slide / message boundaries), then the
**same** heading-aware pack this repo already has.

That is also `ai_parse_document` + `ai_prep_search` on Databricks
([03-theory-databricks.md](03-theory-databricks.md)): parse is a swappable step; chunk-and-index is
shared.

---

## 8. Parent-child (small-to-big) chunking

**Today:** this repo's retrieval unit *is* the generation unit. `ingest/chunker.py` produces one flat
chunk size (`chunk_target_chars`), that chunk is what gets embedded, what BM25 tokenizes, and what
`_format_context()` (`graph/nodes.py`) hands to the LLM verbatim. Fine at 86 chunks, single format.
**Gap at 20M docs, many formats.**

### The conflict this solves

Dense retrieval wants **small** chunks — a chunk that talks about one thing embeds sharply; a chunk
that drifts across three topics embeds as a blur and loses precision. Generation wants **enough
context** — a small chunk handed to the LLM in isolation is often missing the sentence that
disambiguates it (which plan, which region, which effective date). Flat chunking forces one size to
serve both jobs. Parent-child breaks that coupling: **retrieve on the child, generate on the parent.**

### Mechanism

1. **Child chunk** — small (sentence/paragraph-ish, or per §7's natural unit: a table row-group, one
   slide, one email turn). This is what gets embedded and what BM25 tokenizes. Retrieval precision
   lives here.
2. **Parent chunk** — the container the child came from (its section, its full table, its whole
   slide + notes, the full email thread). Never embedded or searched directly.
3. **At query time:** dense/BM25/hybrid search returns child hits as usual (unchanged retrieval
   code path — `strategies.py`, `fusion.py`). Before `_format_context()` builds the LLM prompt,
   resolve each surviving child to its parent and substitute the parent's text. The LLM sees full
   context; the ranking that got it there was scored on the sharp, narrow child.
4. **Dedup parents.** Multiple child hits from RRF/fusion often resolve to the same parent (e.g. two
   sentences from the same section both matched) — collapse to one parent block before building
   context, or `_format_context()`'s char budget silently double-pays for the same text.

### Why this repo's model already has the seam for it

`ResourceAttributes`' own docstring says it: *"The ABAC attributes of a document (and, inherited, of
each of its chunks)."* ACL/ABAC already flows parent → children conceptually — this is the same
inheritance pattern, just for chunk text instead of security attributes. Concretely:

- Add `parent_id` (and, for the parent's own record, `parent_text`) to `Chunk` in `models.py`.
- `attrs: ResourceAttributes` stays on the **parent** and is inherited by every child — no per-child
  duplication, and a policy change on the parent still needs zero reindex (same mechanism as
  `demo_acl_catalog_update.py`, §4).
- `ingest/store.py::dense_search()` and `retrieval/lexical.py::BM25Index` keep operating on child
  text unchanged; only `_format_context()` gains a parent-resolution step.

### Why multi-format makes this matter more, not less

Flat, uniform `chunk_target_chars` packing already fights §7's per-format table (a PPTX slide, a
table row-group, and an email turn are not the same natural size). Parent-child removes the pressure
to compromise on one global char target across formats: each format's **child** granularity can stay
true to its natural unit (one slide, one row-group, one turn) while the **parent** — section, full
table, full thread — is what supplies context, uniformly, regardless of format.

|                     | Flat chunking (today)                   | Parent-child                                                                                                                 |
| ------------------- | --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Retrieval unit      | = generation unit                       | Child (small, sharp)                                                                                                         |
| Generation unit     | = retrieval unit                        | Parent (section/table/slide/thread)                                                                                          |
| Cross-format tuning | One char target must serve every format | Child size follows each format's natural unit (§7); parent expansion is format-agnostic                                     |
| ACL/ABAC            | Per-chunk (already works)               | Per-parent, inherited — fewer places policy can drift                                                                       |
| Cost                | N chunks embedded and searched          | Same embed/search cost (children are still what's indexed); extra cost is only a parent lookup + dedup at context-build time |

**Status: verbal.** No parent/child relationship exists in this repo's schema today — this is the
next concrete extension, not a claimed capability.

---

## 9. Other scale points worth knowing cold

**Multi-tenancy ≠ one big index + `tenant_id` filter.** This repo already does separate collections
per tenant. Say *why*: a shared index means noisy-neighbor (one huge tenant’s rebuild/query load
hurts everyone) and a filter that is easy to get wrong once and catastrophic if wrong. Per-tenant
shards keep blast radius to **one tenant**.

**Noisy-neighbor rate limits already exist** (`authz/rate_limit.py`). Fixed-window per-tenant
counter **before** any LLM client is built, so a limited request costs **$0**, not “error after you
already paid.”

**Embedding-model / schema upgrades.** Re-embedding 20M docs is multi-day and multi-thousand
dollars. **Blue/green index:** build beside the old one, cut traffic when backfilled. Never a
big-bang in-place migration.

**Backpressure, not unbounded queues.** An unbounded ingest queue OOMs the queue before the index.
Per-run token/cost budget (`max_cost_per_run_usd`, **proven**) is the query-path version of the same
instinct: halt and escalate instead of unbounded spend.

**Observability must scale with the corpus, not only QPS.** `RunTrace` is in-memory per run. At
scale it belongs in a queryable store (Delta, APM) so “which tenant is driving cost/latency?” is
not a log grep.

**Drift detection.** [docs/07](07-system-design-coverage-map.md) flags this as an open gap: scheduled
eval harness, diff `leak_count` / `refusal_acc` / `groundedness`, alert on regression. At 20M docs
and real traffic this is how you catch retrieval quality before a customer does.

**“Scales” ≠ “scales linearly.”** ANN retrieval, post-retrieval ACL, and per-tenant sharding are
**sub-linear or flat** in corpus size. Say that explicitly. The mechanisms that make 22 docs
correct (tenant isolation, policy catalog at query time, candidate-bounded rerank) are the **same**
mechanisms that scale. 22 → 20M does **not** require re-architecting security — only swapping the
storage/index layer underneath it.
