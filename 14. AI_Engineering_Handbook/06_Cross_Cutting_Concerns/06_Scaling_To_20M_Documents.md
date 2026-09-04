# Scaling to Twenty Million Documents

> **Level** 🟠 Scale, Security, Operations · **Module** 06 · **Doc** 6 of 7 · **Time** ~50 min
> **Prerequisites:** all of Module 04
> **Source material:** `3. AI_Engineer_Interview_Preparation/Enterprise RAG Platform/docs/Scale_Optimization.md`

## Why this matters

Module 04's corpus is 22 documents and 86 chunks in a single-process Chroma collection. That was deliberate: access control and security stay cheap to prove. Interviewers will still ask *"what if the customer has 20 million documents?"* This is the honest answer — what breaks first, what the fix is, and which fixes the codebase already proves the pattern for versus which are verbal-only because a laptop demo cannot honestly show them.

**This is not one scaling problem. It is three**, each needing a different fix: ingestion throughput, query-time latency, and per-tenant isolation overhead.

| Status | Meaning |
|---|---|
| **Proven** | The same mechanism exists in Module 04's code, at small scale |
| **Verbal** | Correct architecture; not an honest local demo |

## 1 · What breaks first

Assume ~4 chunks per document → **~80M chunks**. Walk the pipeline:

| Stage | Why it breaks | First symptom |
|---|---|---|
| **Ingestion** | Single-process embed loop | Days-long ingest; re-embedding unchanged docs |
| **Vector index** | In-process Chroma has no answer for 80M vectors | OOM, or an unusable index build |
| **ACL / ABAC** | Per-tenant scan + per-chunk check do not shard | Latency grows with *corpus* size, not *result* size |
| **BM25** | Built fresh over `fetch_all_allowed()` per query | O(allowed pool) per request — fine at 86 chunks, fatal at 80M |
| **Reranking** | `LLMReranker` is an LLM call per candidate set | 50 candidates × 20M-doc traffic = cost and latency |
| **Audit** | In-memory `RunTrace` | Trail not queryable; compliance risk |
| **Cost** | Uncached embed and generate billed per token | Linear growth with corpus size *and* query volume |

## 2 · Scaling ingestion

**Today:** one process, synchronous embed loop, content-hash incremental skip (**proven**).

At 20M:

1. **Parallelise embedding.** Fan documents out (`mapPartitions`, a job queue, Ray, a process pool). Embedding is embarrassingly parallel per document. The content-hash check that makes re-runs cheap must run *inside* workers, not in a serial loop.
2. **Batch embedding calls.** Hundreds of chunks per request; never one chunk per HTTP call.
3. **Split chunking from embedding.** Chunking is CPU-bound and cheap; embedding is API-bound and expensive. Over-provision chunk workers relative to embed workers.
4. **Idempotent, resumable jobs.** A 20M-doc run *will* be interrupted. Content-hash dedup plus a per-document ledger (`queued` / `embedded` / `indexed` / `failed`) means a restart finishes only what did not finish. Module 05's checkpoint idea, applied to a batch.
5. **Dead-letter poison pills.** Some fraction fails — corrupt PDF, bad encoding, empty file. Quarantine with the reason; do not stall the batch. Module 04's `record_rejection` is the small-scale version.
6. **On Databricks** — Auto Loader incrementally, a Spark UDF with batched foundation-model embeddings, Delta, then Vector Search sync. That is the production answer, not a bigger script (**verbal**; Module 08).

**Throughput math, said out loud.** At ~500 chunks/sec (batched API, reasonable parallelism): 80M chunks ≈ 160,000 s ≈ **~44 hours single-threaded**; **50-way parallelism → under an hour**. The point is *throughput per worker × worker count*, not "it will be slow".

## 3 · Scaling the vector index

**Today:** Chroma, one collection per tenant, in-process. Fine to roughly 10⁵–10⁶ vectors. At 80M it is the wrong tool.

| Option | When |
|---|---|
| **Databricks Vector Search** | UC-governed, Delta sync, hundreds of millions of vectors, ACL via UC row filters. Module 08's variant builds it |
| **Managed vector DB** (Pinecone, Weaviate, Milvus, Qdrant, sharded pgvector) | Not on Databricks; need native sharding, replica reads, metadata-filtered ANN |
| **Self-hosted sharded ANN** (FAISS/HNSW + a router) | Only with full control *and* the ops capacity. Rarely the right trade for an enterprise deployment |

Mechanisms any of them need:

1. **ANN, not exact search.** HNSW or IVF — a small recall hit for orders of magnitude of speed. Non-negotiable past ~1M vectors.
2. **Shard by tenant.** Module 04 already isolates tenants into separate collections, so sharding is easy: a request is always one tenant and never fans out. *Isolation model proven; sharding infrastructure verbal.*
3. **Push metadata filters into ANN, not after it.** Filtering *after* top-K silently loses recall — the true allowed hit may never have been in the top-K. That is Module 04's post-filter argument at scale. Production databases do filtered ANN; ask the vendor, do not build it.
4. **Replica reads.** Query load and index-build load scale independently.
5. **Hot/cold tiering.** Hot embeddings in the fast index; cold ones cheaper, rehydrated on demand (**verbal**).

## 4 · Scaling ACL/ABAC enforcement

This is where the design is actually strong. Be precise about what is free and what is new work:

| | What | Why |
|---|---|---|
| **Proven — free at scale** | Tenant isolation via separate collections | A query is one tenant's shard. More tenants → more shards, not more per-query work |
| **Proven — free at scale** | Post-retrieval re-check (`enforce`) | **O(candidates), not O(corpus).** Candidates are bounded by top-K |
| **Verbal — new work if the vendor cannot help** | ACL/ABAC *inside* ANN | If the index cannot filter in the search: over-fetch top-K·N and filter (wasteful, can still under-fill), or materialised per-attribute indexes (fast, expensive to maintain). Serious vector DBs support filtered search |
| **Proven mechanism, holds at 20M** | Live ACL without reindex | The catalog update takes effect with zero reindex because enforcement reads it at query time. Cost tracks candidate count, not corpus size — one of the few things that scales with no new engineering |

The line to say: **22 → 20M does not require re-architecting security — only swapping the storage and index layer underneath it.** The mechanisms that make 22 documents correct — tenant isolation, a policy catalog read at query time, candidate-bounded rerank — are the same mechanisms that scale.

## 5 · Latency

Attack each stage of the graph:

| Stage | Lever | Status |
|---|---|---|
| Rewrite / decompose / multi-query / HyDE | Small `fast_model`; the large model only for synthesis | **Proven** |
| Retrieval | ANN is sub-linear; keep top-K small into rerank | **Proven** at small scale, same principle at large |
| Rerank | A cheap reranker or cross-encoder — relevance, not reasoning | **Gap** — `LLMReranker` is a full LLM call; `CrossEncoderReranker` is the swap |
| Synthesis | This stage *should* use the strong model | Do not cheapen it |
| Repeat / near-duplicate questions | Cache embeddings *and* full responses | **Proven** — keyed on question + filter + exact context |
| LLM outage | Circuit breaker; fail fast | **Proven** |
| Round-trips | Batch embeds; parallelise independent LLM calls | **Partial** — check whether multi-query rewrites actually fan out concurrently |
| Cold start per tenant | Warm hot indexes; never lazy-load a tenant on first request | **Verbal** |

### Five levers for p95

1. **Route by difficulty.** Cheap model for rewrite, HyDE, grade, rerank; large model only for synthesis.
2. **Filter early.** ACL before the expensive rerank, so rerank sees a small authorised set. Bigger corpus → the filter does more of the work.
3. **Cache precisely.** Embeddings and full answers keyed on question + ACL filter + context. A hit is only for an identical, freshly re-enforced situation.
4. **Parallelise independent LLM work.** Multi-query, HyDE, per-tenant requests. Do not serialise what is independent.
5. **Filter in the index.** Filtered ANN is a latency win *and* a correctness win — no over-fetch-then-discard.

### p50 vs the tail

| Percentile | What dominates it |
|---|---|
| **p50** | Happy path: a cache hit, or fast dense retrieve + small-model rewrite + synthesis |
| **p95 / p99** | Cache miss on a cold query; multi-hop (extra LLM hops); rerank over a wide match set before ACL narrows it |
| **Circuit breaker** | A p99 tool. It bounds a dead dependency; it does not improve the typical case |

If asked "does caching fix tail latency?": **no.** Caching moves the **median**. Timeouts, circuit breakers and fallback to a smaller model move the **tail**.

## 6 · Cost

Same five levers: routing (proven), pre-filter before rerank (proven), embed and response cache (proven), tiered storage (verbal), a cheaper reranker (gap).

**One number to have ready.** A one-time embed of ~80M chunks at ~$0.0001 per 1K tokens with a small embedding model is real money but tractable — **low-to-mid four figures USD**, order of magnitude. **The ongoing cost that matters is query-time generation × query volume.** That is why the first three levers dominate the conversation, not the ingest bill.

## 7 · Chunking by document type

Module 04's chunker splits on markdown headings, packs to a target size with overlap, and prefixes title and section. Correct for a corpus that is already markdown. At 20M real enterprise documents the input is never uniform markdown — this is the first place ingest has to grow.

**The rule that generalises:** chunk on the format's **natural semantic unit**, not a fixed character count, and carry structure (heading, page, slide title, table caption) into the chunk. Fixed-size sliding windows are the fallback when there is no usable structure — never the default.

| Format | Natural split | Notes |
|---|---|---|
| Markdown / plain text | Headings, then pack paragraphs with overlap | Exactly Module 04 |
| DOCX | Paragraph + Word heading styles | Map heading-styled paragraphs to `#`/`##` and reuse the heading splitter. Never concatenate paragraphs and lose the styles. Strip track-changes first |
| PDF | Text vs scanned | Text: layout-aware extraction, reading order, font-size as heading signal. Scanned: OCR first. Multi-column reports need column-aware extraction or reading order silently breaks |
| HTML | `<h1>`–`<h6>`, `<section>`, `<article>`, `<table>`, `<li>` | Strip nav/footer/ads (readability-style), then the same chunker |
| Tables | One chunk per table, or per row-group if huge. **Never split mid-row** | Repeat header names on every chunk; small pricing/tier tables stay one atomic chunk — the service-credit failure from Module 01 |
| Excel / CSV | Logical row-groups (account, time window), not raw row count | Always carry headers; very wide tables flatten to sentences so relationships survive |
| Images | Not text until converted | OCR gated on confidence; multimodal embeddings when visual structure *is* the meaning (charts) |
| Code | Function/class boundaries (AST); never mid-function | Fallback: blank-line blocks with a cap |
| PowerPoint | One chunk per slide | Slide title as prefix; append speaker notes, do not orphan them |
| Email / chat / tickets | One turn, or question + resolving answer | A window that cuts a question from its answer is the worst failure for support RAG. Carry thread metadata |

Size still matters independent of format: format decides *where splits are allowed*; size and overlap decide *how big each piece is*. Too small loses context; too large kills precision and raises rerank and generation cost per chunk.

**Architecture: one pipeline, many parsers, one chunker.** Do not write six chunkers. Write per-format parsers that produce a common intermediate — text plus heading hierarchy, or explicit table/slide/message boundaries — then the same heading-aware packer. On Databricks that is `ai_parse_document` + `ai_prep_search`: parse is swappable; chunk-and-index is shared.

## 8 · Parent-child (small-to-big) chunking

**Today:** the retrieval unit *is* the generation unit. One flat chunk size is what gets embedded, what BM25 tokenises, and what the LLM sees verbatim. **Gap at 20M documents in many formats.**

**The conflict it solves.** Dense retrieval wants **small** chunks — one topic embeds sharply; three topics embed as a blur. Generation wants **enough context** — a small chunk in isolation is often missing the sentence that disambiguates it. Flat chunking forces one size to serve both. Parent-child breaks the coupling: **retrieve on the child, generate on the parent.**

1. **Child** — small (a paragraph, a table row-group, one slide, one email turn). This is what is embedded and tokenised. Retrieval precision lives here.
2. **Parent** — the container (section, full table, slide + notes, full thread). Never embedded or searched directly.
3. **At query time** — search returns child hits as usual; before building the prompt, resolve each surviving child to its parent and substitute the parent's text.
4. **Dedupe parents** — several child hits often resolve to the same parent; collapse before building context or the char budget double-pays.

Module 04's model already has the seam: `ResourceAttributes` describes itself as *"the attributes of a document (and, inherited, of each of its chunks)"*. ACL already flows parent → child. Add `parent_id` to `Chunk`, keep `attrs` on the parent, and only the context-building step changes. A policy change on the parent still needs zero reindex.

| | Flat (today) | Parent-child |
|---|---|---|
| Retrieval unit | = generation unit | Child (small, sharp) |
| Generation unit | = retrieval unit | Parent (section / table / slide / thread) |
| Cross-format tuning | One char target for every format | Child follows each format's natural unit; parent expansion is format-agnostic |
| ACL | Per chunk | Per parent, inherited — fewer places to drift |
| Cost | N children embedded | Same; plus a parent lookup and dedupe at context time |

**Status: verbal.** No parent/child relationship exists in the schema today. It is the next concrete extension, not a claimed capability.

## 9 · Other points to know cold

- **Multi-tenancy ≠ one big index + `tenant_id` filter.** A shared index means noisy-neighbour (one huge tenant's rebuild hurts everyone) and a filter that is easy to get wrong once and catastrophic if wrong. Per-tenant shards keep blast radius to one tenant.
- **Noisy-neighbour rate limits** already exist, checked before any LLM client is built — a limited request costs $0, not "error after you already paid".
- **Embedding-model or schema upgrades.** Re-embedding 20M docs is multi-day and multi-thousand dollars. **Blue/green index**: build beside the old one, cut traffic when backfilled. Never a big-bang in-place migration.
- **Backpressure, not unbounded queues.** An unbounded ingest queue OOMs the queue before the index. The per-run cost budget is the query-path version of the same instinct.
- **Observability must scale with the corpus, not only QPS.** `RunTrace` in memory becomes a queryable store (Delta, an APM) so "which tenant drives cost?" is not a log grep.
- **Drift detection.** A scheduled harness run diffing `leak_count`, `refusal_acc`, `groundedness` — at 20M docs and real traffic this is how you catch quality regressions before a customer does.
- **"Scales" ≠ "scales linearly."** ANN retrieval, post-retrieval ACL and per-tenant sharding are sub-linear or flat in corpus size. Say that explicitly.

## Interview lens

> *"Three problems, not one. Ingestion parallelises — it's throughput per worker times worker count, and content hashes make restarts cheap. The index swaps from Chroma to a filtered-ANN store sharded by tenant — the isolation model is already there. And access control is the part that's free at scale: the post-check is O(candidates), not O(corpus), and a policy change still needs zero reindex. Going from 22 documents to 20 million doesn't re-architect security — it swaps the storage layer underneath it."*

## Checkpoint

- Name the three scaling problems and the first symptom of each.
- Do the throughput arithmetic for 80M chunks at 500 chunks/s with 50 workers.
- Why is the post-retrieval ACL check "free at scale"? What is its complexity in?
- Why does caching not fix tail latency, and what does?
- Explain parent-child chunking: what conflict it solves and what changes in the code.
- What is the one number to have ready for embedding cost, and why does it not dominate the conversation?

**Next →** [Consolidated Quick Reference](07_Consolidated_Quick_Reference.md)
