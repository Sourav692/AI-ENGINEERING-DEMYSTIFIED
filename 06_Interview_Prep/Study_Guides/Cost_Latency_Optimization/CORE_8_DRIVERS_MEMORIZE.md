# The 8 Drivers to Actually Memorize

**Source:** `03_GenAI_FDE_Cost_Latency_Optimization_Playbook.pdf` — §2 (cost drivers), §3 (latency drivers), §4 (trade-offs), §15 (incidents). Every field below is the playbook's own content. Nothing invented.
**Purpose:** the open-tab reference during the interview. The other 27 drivers are recognition-only — see `CRAM_SHEET_FULL_PLAYBOOK.md`.

---

## Why these 8

The playbook lists 18 cost drivers and 17 latency drivers. Seven of them appear on **both** lists — those are the ones worth real memory, because a single answer serves "why is it expensive?" *and* "why is it slow?". The eighth (batch/eval jobs) is cost-only, but the playbook singles it out as the spend that runs silently in the background.

**Memorize them in request-path order, not as a list.** Recite the path and the drivers fall out of it:

```
prompt/context in → retrieval → rerank → agent steps & tools → generation out
                                                    ↑                ↓
                                                 retries         logging
                              (and, off the request path entirely: batch & eval jobs)
```

That ordering is just the playbook's own latency equation with the cost drivers hung on it. If you can draw it, you can derive all 8 live — which is what the interviewer is actually scoring.

---

## 1 · Input tokens & long context

| | |
|---|---|
| **What causes it** | Long prompts, retrieved context, chat history, tool results. Large documents, full chat history, large policy manuals. |
| **Why underestimated** | Teams count the user's question but ignore the system prompt, RAG chunks and hidden history. Large context *feels* safe but is expensive and slower. |
| **Production signal** | The bill increases even when user traffic is flat. Cost rises **and** answer quality degrades from distraction. |
| **Metrics to pull** | Input tokens, prompt version, first-token latency, prompt build time, payload size, answer accuracy, citation precision. |
| **Fix** | Trim prompts, compress context, summarize history, cache static prompt parts. Retrieve only relevant sections, deduplicate, hierarchical summaries. Precompute and cache static parts of the prompt. |
| **Trade-off / risk** | Less context reduces accuracy **if retrieval quality is weak**. Requires better ingestion and retrieval design to be safe. |
| **Latency face** | First-token latency (UI appears frozen before streaming) and large prompt construction (backend slow *before* the model call). Prevention: monitor first-token separately from total latency; version prompt templates. |
| **§4 decision** | *More retrieval context vs less* — use less for narrow evidence needs, avoid for broad legal/policy synthesis. |
| **Say** | "More context is not always better; irrelevant context increases cost and can reduce answer quality." |
| **Appears as** | §15 #10 prompt update increased tokens · §15 #14 long context caused poor performance |

---

## 2 · Output tokens

| | |
|---|---|
| **What causes it** | Verbose answers, uncontrolled generation, reasoning-heavy tasks. |
| **Why underestimated** | Teams measure *requests*, not *generated tokens*. |
| **Production signal** | Long answers dominate per-request cost. Streaming starts but completion drags. |
| **Metrics to pull** | Output tokens, tokens/sec, total generation time, end-to-end duration. |
| **Fix** | Set max tokens, concise templates, structured output, summarize only when needed. Short answer defaults with progressive detail. |
| **Trade-off / risk** | Too aggressive limits produce **incomplete answers**. |
| **Latency face** | Long output generation and total response time. Prevention: concise answer defaults; allow expansion on demand. |
| **§4 decision** | *Streaming vs non-streaming* — streaming improves perceived latency but does **not** reduce total compute cost. |
| **Say** | "Streaming is UX optimization, not a substitute for backend optimization." |
| **Appears as** | §15 #1 cost 5× after rollout (output verbosity is a listed cause) |

---

## 3 · RAG retrieval & vector search

| | |
|---|---|
| **What causes it** | Vector search, metadata filtering, query rewriting, hybrid search. High-dimensional vectors, replicas, large metadata, high top-k. |
| **Why underestimated** | Retrieval seems cheap until request volume and tenant count rise. Storage and query units scale with corpus **and tenants**. |
| **Production signal** | Vector DB cost, latency and infra load increase. Search latency and DB bill rise after adding documents. |
| **Metrics to pull** | Retrieval duration, vector DB P95, top-k, filter selectivity, index memory, shard load, corpus size, DB CPU, QPS. |
| **Fix** | Filter **before** vector search, tune top-k, batch reads, optimize the index, cache retrieval results. Dimension choice, sharding, dedupe, lifecycle policies, quantization, metadata pruning. |
| **Trade-off / risk** | Too few chunks reduce answer completeness. Over-tuning the index reduces recall. |
| **Latency face** | Retrieval latency (slow before the model call) and vector search latency (worsens as documents grow). Prevention: pre-test retrieval at the *target* corpus size; separate hot and warm corpora. |
| **§4 decision** | *More chunks vs fewer* — calibrated top-k by query type; use for known-document lookup, avoid for ambiguous exploratory queries. |
| **Say** | "I would evaluate recall and answer faithfulness while reducing top-k." |
| **Appears as** | §15 #3 RAG slow after adding docs · §15 #8 vector DB latency increased |

---

## 4 · Reranking

| | |
|---|---|
| **What causes it** | Cross-encoder rerankers, LLM-based relevance scoring. |
| **Why underestimated** | The quality win hides a latency **and** cost multiplier. |
| **Production signal** | One request triggers many reranker scores. Good answers but a slow pipeline. |
| **Metrics to pull** | Reranker latency, candidate count, quality lift **by segment**. |
| **Fix** | Rerank only ambiguous or high-stakes queries; reduce the candidate count; use a lighter reranker. |
| **Trade-off / risk** | Less reranking lowers precision. |
| **Latency face** | Reranker latency. Prevention: gate reranking by query ambiguity; monitor quality lift **per millisecond added**. |
| **§4 decision** | *Reranking vs direct retrieval* — rerank only when retrieval confidence is low. Use for ambiguous, high-value enterprise search; avoid on very low-latency chat paths. |
| **Say** | "Reranking should be a gated quality tool, not an unconditional tax." · "If it improves only 20% of queries, do not tax 100% of traffic." |
| **Appears as** | §15 #9 reranker improved quality but doubled latency |

---

## 5 · Agent steps & tool calls

| | |
|---|---|
| **What causes it** | Planning, retrieval, CRM calls, web/API calls, reflection. Plus third-party APIs: search, CRM, OCR, document parsing, rerank APIs. |
| **Why underestimated** | **One user request becomes 5–20 sub-requests.** The LLM is not the only bill. |
| **Production signal** | Cost per request varies wildly by agent path. External API fees scale with tool use. The agent appears to think forever. |
| **Metrics to pull** | Agent step count, tool count, repeated tool args, per-tool latency, timeout rate, parse failures, dependency SLA, trace length. |
| **Fix** | Max steps, tool budgets, allowlists, deterministic routing, cached tool results, smaller planning model, summarized intermediate state, parallelize safe read-only calls. |
| **Trade-off / risk** | Too strict limits may **block complex workflows**. Never parallelize side-effecting actions blindly. Caching tool results introduces freshness and security issues. |
| **Latency face** | Agent planning loops and tool/API latency. Prevention: **every agent path needs a budget**; budget tool calls per workflow. |
| **§4 decision** | *Agentic vs deterministic workflow* — deterministic routing for common paths, agent only for open-ended tasks. |
| **Say** | "I would not use an agent where a workflow engine or router is enough." · "I would treat the agent as an execution graph with budgets, not an open-ended reasoning loop." |
| **Appears as** | §15 #4 agent keeps calling tools repeatedly · §15 #15 tool-calling workflow times out · §16 Case 3 (45s → 8s, €1.20 → €0.18) |

---

## 6 · Retries

| | |
|---|---|
| **What causes it** | Timeouts, parsing failures, provider errors, safety re-prompts. |
| **Why underestimated** | **Retries are invisible to product metrics unless traced.** |
| **Production signal** | Cost spikes during incidents. |
| **Metrics to pull** | Retry count, timeout rate, parse errors, provider error codes, fallback rate. |
| **Fix** | Idempotency, retry budgets, backoff, schema validation, fallback models. |
| **Trade-off / risk** | Too few retries **reduce availability**. |
| **Latency face** | Synchronous external calls and timeouts on the critical path — queue async jobs, callbacks, optimistic UI. |
| **§4 decision** | Structured output helps here, but the playbook warns: avoid schemas so complex they *cause* retries. |
| **Say** | "The increase is likely from request shape, not just user count. I would isolate token growth, retries, agent steps, and batch jobs before changing the model." |
| **Appears as** | §15 #1 cost 5× after rollout · §15 #11 provider latency unstable |

---

## 7 · Logging, tracing & observability overhead

| | |
|---|---|
| **What causes it** | Full prompts, completions, embeddings, traces. Synchronous telemetry writes. |
| **Why underestimated** | Necessary for debugging, so nobody questions it — but storage costs grow and it sits on the hot path. |
| **Production signal** | Observability bill **and privacy risk** increase. Tracing/logging slows the hot path. |
| **Metrics to pull** | Telemetry duration, log volume. |
| **Fix** | Sample, redact, TTL policies, structured metrics over raw payloads. Async logging. |
| **Trade-off / risk** | Less detail **slows incident analysis** — keep enough detail for incidents. |
| **Latency face** | Observability overhead is its own row in §3: synchronous logging is a listed cause of a post-deploy latency jump. |
| **§12 link** | Log cost and latency per request path *without* storing unnecessary sensitive payloads; use sampling where full tracing is too expensive. |
| **Say** | (Pair it with the caching-security framing: observability and caching are the two places where a cost optimization becomes a **privacy** decision.) |
| **Appears as** | §15 #2 latency jumped 2s → 20s (synchronous logging is a listed cause) |

---

## 8 · Batch jobs & evaluation pipelines *(cost-only, but the classic surprise)*

| | |
|---|---|
| **What causes it** | Summarization, enrichment, embedding, migration. Regression tests, synthetic queries, judge models. |
| **Why underestimated** | Batch work is **not visible to interactive users**, and offline evals call expensive models repeatedly. |
| **Production signal** | The monthly bill spikes after a data refresh. CI/CD or nightly jobs become large hidden spend. |
| **Metrics to pull** | Embeddings generated vs documents *changed*, duplicate rate, job retries, queue depth, eval/batch spend, model version. |
| **Fix** | Queue budgets, incremental processing, off-peak scheduling, rate limits. Sampled/stratified eval sets, cheaper judge models, run deltas only. Content-hash embedding cache and change detection. |
| **Trade-off / risk** | Longer processing windows. **Weak eval coverage misses quality regressions.** |
| **§4 decision** | *Batch vs live inference* — batch for ingestion, enrichment and evals; avoid for interactive support/chat. |
| **Say** | "Batching is ideal when user value does not require an immediate response." · "Embedding should be incremental. Re-embedding unchanged documents is usually a pipeline design issue." |
| **Appears as** | §15 #13 batch embedding job became too expensive · §16 Case 5 (nightly PDFs) |

---

## The two latency-only add-ons

Name these when the question is purely about latency, because they have **no cost analogue** and candidates routinely miss them:

| Driver | Symptom | Fix | Trade-off |
|---|---|---|---|
| **Cold starts** | The first request after idle is slow | Min replicas, warmers, keep-alive, provisioned concurrency | Costs more idle capacity — balance idle cost against latency |
| **Sequential workflow design** | Each step waits for the previous one unnecessarily | Parallelize independent calls, prefetch, async non-critical work | Do **not** parallelize unsafe side effects |

(Both are the actual cause behind §15 #6 "executive demo is too slow" and §16 Case 6 "sub-3-second sales assistant".)

---

## If they push past the 8

Name the rest without detail — that alone signals coverage. From §2: embedding generation, multi-step reasoning, streaming, fine-tuning, GPU/inference hosting, human review. From §3: model inference time, network latency, database latency, auth and permission checks.

Then hand the question back to method:

> "I would not rank these from memory. I would attribute spend by tenant, feature, model, prompt version and request path, build a latency waterfall from traces, and let the measurement pick the driver."

---

## The 60-second recital

1. **Decompose, don't list.** "Latency is auth, routing, retrieval, reranking, prompt construction, queue time, inference, tool calls, post-processing, network return. Cost is input tokens, output tokens, embeddings and retrieval, reranking, tools, infra, and logging and evaluation overhead."
2. **Name the hidden multipliers.** "The ones that surprise teams are retries, agent loops, long outputs, repeated retrieval, and eval and batch jobs running in the background."
3. **Point at the measurement.** "I would break spend down by tenant, feature, model and prompt version, and build a trace waterfall — then optimize the largest measured driver."
4. **State the constraint.** "And I would check what the fix costs: less context hurts accuracy if retrieval is weak, fewer chunks hurt recall, less reranking hurts precision, tighter agent budgets block complex workflows, and fewer retries hurt availability."

Step 4 is the one most candidates skip, and it is the whole point of §2's and §4's trade-off columns.
