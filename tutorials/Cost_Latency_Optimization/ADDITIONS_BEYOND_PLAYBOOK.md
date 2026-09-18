# Beyond the Playbook — what §15/§16 leave out

**Companion to** `CRAM_SHEET_S15_S16.md`. Nothing here is in the PDF. This is the layer an interviewer reaches for when they push past "I'd cap top-k and route to a smaller model" and ask *how*, *by how much*, or *prove it*.

Anthropic figures below are current as of the `claude-api` skill's cached table (2026-06-24). Numbers for other providers change constantly — state the *mechanism* in an interview, and say "I'd check current pricing" for the digits.

---

## A. Provider mechanics the playbook never names

The playbook says "cache static prompt parts" and "trim prompts". These are the actual controls.

### A1. Prompt caching is a **prefix match**, and that explains scenario 12

- Cache matching is byte-exact on the **prefix**, rendered in the order `tools` → `system` → `messages`. One changed byte anywhere in the prefix invalidates everything after it.
- **Therefore:** stable content first (frozen system prompt, deterministically-ordered tool list), volatile content (timestamps, request IDs, the user's question) *after* the last cache breakpoint.
- **Silent invalidators** — the real root causes behind "cache hit rate dropped suddenly" (§15 #12): a `datetime.now()` in the system prompt, unsorted JSON keys, a tool list whose order varies, a prompt-version bump, a model swap (caches are **model-scoped**), or a mid-conversation `effort` change.
- **Prove it, don't guess:** `usage.cache_read_input_tokens`. Zero across repeated identical requests = a silent invalidator, full stop. (Anthropic also ships a cache-diagnosis beta that reports *why* a turn missed.)
- Limits worth knowing: max 4 cache breakpoints per request; the minimum cacheable prefix is model-dependent (roughly 512–4096 tokens) — shorter prefixes silently don't cache at all, which looks like "caching doesn't work here."
- **Cascades forfeit cache.** This is the sharp trade-off the playbook's §5 "cheap→medium→premium" pattern hides: each model has its own cache namespace, so a 3-model cascade means 3 cold prefixes. Measure *one strong model at lower effort* before you build the cascade.
- Anthropic-specific escape hatch: **mid-conversation system messages** (append `{"role":"system"}` into `messages[]` instead of editing top-level `system`) change operator instructions without invalidating the cached history prefix.

### A2. Current Claude price/latency tiers (the "which model" answer, with digits)

| Model | Input $/MTok | Output $/MTok | Context |
|---|---|---|---|
| Claude Opus 5 (`claude-opus-5`) | $5.00 | $25.00 | 1M |
| Claude Sonnet 5 (`claude-sonnet-5`) | $2.00 | $10.00 | 1M |
| Claude Haiku 4.5 (`claude-haiku-4-5`) | $1.00 | $5.00 | 200K |
| Claude Fable 5.1 (`claude-fable-5-1`) | $10.00 | $50.00 | 1M |

Two things to say out loud with this table: **output is ~5× input**, so output-token discipline outranks prompt trimming on chatty workloads; and a router that moves 80% of traffic from Opus 5 to Haiku 4.5 is a ~5× unit-cost cut on that slice — *that's* what "model routing" is worth, quantified.

### A3. Levers the playbook has no equivalent for

| Lever | What it does | Maps to §15/§16 |
|---|---|---|
| **Batch API** | Async processing at **50% of standard cost** | Case 5 (nightly PDFs) — the playbook says "batch"; this is the actual discount |
| **Effort control** (`output_config.effort`: low→max) | Trades thinking depth for tokens *within one model* | §4 trade-offs — a cheaper knob than swapping models, and it keeps one cache namespace |
| **Task budgets** | Advisory token ceiling the model *sees*, so it paces itself and lands gracefully (min 20K) | §15 #4, Case 3 — softer than a hard max-step cut-off, no truncated work |
| **Context editing** (`clear_tool_uses`) | Clears old tool results / thinking from history before the model sees it | §8 "agent memory growth increases prompt cost every turn" |
| **Compaction** | Server-side summarization when history nears a threshold | §15 #14 long-context |
| **Tool search + `defer_loading`** | Tool *definitions* stop being resident prompt tokens; the model searches for them | Big agent-cost driver the playbook omits entirely |
| **`strict: true` / structured outputs** | Schema-valid tool args and responses → fewer parse-failure retries | §2 "retries are invisible unless traced" |
| **`count_tokens` endpoint** | Exact token counts for CI regression checks | §15 #10 "prompt CI checks for token budget" — this is how you implement it |
| **Fast mode** (Opus 5/4.8) | Same model, up to **2.5× output tokens/sec**, at premium pricing ($10/$50) | §15 #6 exec demo: buy latency with money for one high-stakes path |
| **Admin usage/cost API** | Org-level spend attribution | §15 #1/#5/#7 — "cost attribution by request path" needs a data source |

---

## B. Latency physics the playbook waves at

### B1. Prefill vs decode — why input and output hurt in *different* places

Inference has two phases, and conflating them is the most common junior mistake:

- **Prefill** processes the whole prompt in parallel → it sets **time-to-first-token**. TTFT scales with *input* tokens.
- **Decode** generates one token at a time → it sets **tokens/sec** and total time. That scales with *output* tokens.

So: a bloated prompt is a **first-token** problem (and a cost problem); a verbose answer is a **completion-time** problem. "The UI feels frozen" → look at prompt size, retrieval and queueing. "It starts fast then drags" → look at output length. The playbook lists both symptoms (§3) but never gives the reason they're separate.

### B2. Tail latency compounds in multi-step agents

If one step is p95 = 1s, five sequential steps are **not** p95 = 5s — they're worse, because you need all five to be fast simultaneously. Roughly, for independent steps, end-to-end p95 degrades toward the sum of higher percentiles. Practical consequences:
- A 6-step agent with a "fine" per-call p95 can have an awful end-to-end p95.
- Parallelizing read-only calls doesn't just save the sum — it collapses the tail.
- This is the quantitative argument for §8's step budgets and Case 3's "bounded execution graph".

### B3. Little's Law for capacity planning

`concurrency = throughput × latency`. At 10 req/s with 4s average latency you need ~40 in-flight slots. Halving latency halves the concurrency you must provision — which is why latency work is also a *capacity cost* win, not only a UX win. Useful when an interviewer asks "how many replicas / what rate limit?"

### B4. Cost per *successful task*, not per request

A cheaper model that needs two turns, a retry, or a human correction is not cheaper. Always quote **cost per resolved ticket / per accepted suggestion / per processed document** (the playbook's Case 2 gets to "cost/resolved ticket" but never generalizes the rule).

---

## C. RAG and vector specifics the playbook keeps abstract

- **The real top-k latency knob is the index parameter, not top-k.** HNSW `ef_search` (and IVF `nprobe`) controls the recall/latency curve far more directly than k. "Tune the index" in §15 #3/#8 means these.
- **Quantization is the storage lever**: scalar/product quantization or binary embeddings with a rescoring pass cut memory and search time by large factors at modest recall loss. Pairs with the playbook's "dimension choice".
- **Dimension truncation:** several modern embedding models are Matryoshka-trained, so you can truncate the vector (e.g. 1536→512) and re-evaluate recall instead of re-embedding with a different model. Verify per model.
- **Reranker cost is candidates × document length**, because a cross-encoder runs a forward pass per pair. The fix in §15 #9 ("reduce candidates") is doing real work: 50→10 candidates is ~5× less reranker compute. Also truncate the passage, not just the list.
- **Retrieval metrics the playbook omits:** nDCG@k (rank-aware, unlike Recall@k), context precision and context recall (RAGAS), and answer-level faithfulness. Recall@k alone will happily bless a retriever that buries the right chunk at position 9.
- **Hybrid search fusion needs a weight** — RRF (reciprocal rank fusion) is the usual default and it's a tunable, not a constant.

---

## D. Metrics the playbook's §12 list is missing

- **TTFT vs TPOT vs total** as three separate SLOs (the playbook has first-token and total, not inter-token).
- **Goodput** — successful requests/sec under SLO, not raw throughput. A system doing 100 req/s where 30% blow the latency budget is doing 70 goodput.
- **Cache hit rate split by cache type** *and* **token-weighted** — a 60% hit rate on tiny requests saves nothing.
- **Queue wait vs service time**, separately. Conflating them makes an overloaded system look like a slow model.
- **Saturation/utilization** alongside latency — latency curves knee sharply past ~70–80% utilization, so a rising p99 with flat p50 usually means queueing, not a slower model.
- **Escalation rate and human-override rate** as *cost* metrics, not just quality metrics.

---

## E. Three scenarios an interviewer may add that §15 doesn't cover

| Scenario | The senior answer |
|---|---|
| **"Rate limits are throttling us at peak"** | Separate provider 429s from your own gateway limits. Short term: retry with jitter + a fallback model/region, shed non-interactive traffic to batch. Long term: capacity commitments, tenant-aware quotas, and queue non-urgent work rather than retrying into the same wall. |
| **"Costs are fine but the eval bill tripled"** | LLM-as-judge is inference too. Stratified sample instead of full-set, use a cheaper judge with a periodic strong-judge audit, run deltas only on changed prompts/models, and cache judge calls on unchanged pairs. |
| **"Streaming works but users abandon mid-answer"** | Measure abandonment against first-token time and answer length, and **cancel the stream + any in-flight tool calls on abandon** — otherwise you pay for tokens nobody read. The playbook mentions cancellation as UX; it's also a cost control. |

---

## F. If the interviewer pushes for specifics you're unsure of

Say the mechanism and name the measurement, don't invent a number:

> "I'd expect prompt caching to cut input cost on the repeated prefix by roughly an order of magnitude and remove most of the prefill time, but I'd confirm against the current pricing page and the cache-read token counter in our own traces before committing to a figure in a customer deck."

That answer scores higher than a confidently wrong percentage — and it *demonstrates* the playbook's own thesis: measure, then claim.
