# Cost & Latency Playbook — §15 + §16 Cram Sheet

**Source:** `03_GenAI_FDE_Cost_Latency_Optimization_Playbook.pdf` (Tobias Weissmann), §15 Production Troubleshooting Scenarios (15 scenarios) + §16 Interview Case Studies (7 cases).
**Fidelity:** strictly the playbook's own content, condensed. Nothing added. Anything beyond the PDF lives in `ADDITIONS_BEYOND_PLAYBOOK.md`.

---

## 0. The two shapes you actually memorize

Everything in §15 and §16 is these two templates filled in with different nouns. Learn the templates, and you can reconstruct any scenario live.

### Shape A — the §15 incident playbook (9 rows, same 9 every time)

```
Symptoms → Clarifying questions → Probable causes → Metrics to check
        → Debugging steps → Immediate fix → Long-term fix → Prevention
        → Customer communication → Interview-ready answer
```

The doc's own framing: *"the goal is not to memorize fixes, but to demonstrate a senior debugging sequence: clarify, measure, isolate, mitigate, prevent, and communicate."*

**Free marks:** the *Customer communication* row is byte-identical in all 15 scenarios —
> "Acknowledge impact, show measured cause, provide immediate mitigation, then explain long-term prevention and success metric."

Memorize that one sentence and you have 1/9 of every scenario for free.

### Shape B — the §16 case-study answer (7 rows, same 7 every time)

```
Interviewer prompt → Clarifying questions → Weak answer → Strong answer
        → Architecture reasoning → Cost/latency trade-offs
        → Metrics to monitor → Final recommendation
```

**The weak answer is always the same move:** *change one knob without measuring* — bigger model, longer context, faster model, global limit, browser cache, premium model on everything. **The strong answer is always the same move:** *route by risk/intent, bound the workflow, cache with permissions, measure per path.*

---

## 1. §15 — The 15 production scenarios

> Drill order below = the doc's order. `Ask` = clarifying questions, `Now` = immediate fix, `Later` = long-term fix, `Say` = the interview-ready line.

### 1. LLM cost increased 5× after rollout
- **Symptom:** daily spend jumped sharply; active users grew only modestly.
- **Ask:** which tenant, feature, prompt version, model route, retry path, batch job or agent workflow changed?
- **Causes:** longer prompts, new RAG context, agent loop, eval job, retries, output verbosity, provider price-tier change.
- **Metrics:** cost/request, tokens/request, requests by feature, retry count, model distribution, output tokens, eval + batch spend.
- **Debug:** break spend by tenant / feature / model / prompt version; compare before vs after rollout; inspect high-cost traces.
- **Now:** cap max output length, pause expensive batch/eval jobs, route simple tasks to smaller model, cap agent steps.
- **Later:** budgeting, anomaly alerts, prompt-token regression tests, request-path cost dashboard.
- **Prevent:** pre-rollout cost simulation + per-tenant budget alerts.
- **Say:** *"The increase is likely from request shape, not just user count. I would isolate token growth, retries, agent steps, and batch jobs before changing the model."*

### 2. Latency jumped from 2 seconds to 20 seconds
- **Symptom:** assistant unusably slow right after a deployment.
- **Ask:** did retrieval, reranker, prompt version, model, provider, tool dependency or region change?
- **Causes:** new reranker, larger context, provider latency incident, cold starts, tool timeout, synchronous logging.
- **Metrics:** P95/P99, first-token, retrieval, rerank, model latency, tool latency, timeout + retry rate.
- **Debug:** trace waterfall; compare component timing before vs after deploy.
- **Now:** roll back prompt/reranker change, disable optional tool, reduce top-k, activate fallback provider.
- **Later:** per-component latency budgets, canary deploys, provider health monitoring.
- **Prevent:** performance tests with realistic payload and corpus size.
- **Say:** *"I would not guess. I would use traces to see whether the 18-second increase is retrieval, model, tool calls, or infrastructure."*

### 3. RAG retrieval became slow after adding more documents
- **Symptom:** vector search latency grows after corpus expansion.
- **Ask:** how many documents, chunks, dimensions, tenants, filters and replicas changed?
- **Causes:** untuned index, too many chunks, missing metadata filters, high top-k, hot shard.
- **Metrics:** vector DB P95, top-k, filter selectivity, index memory, shard load, corpus size.
- **Debug:** replay representative queries; compare index/filter behaviour.
- **Now:** reduce top-k, add metadata filters, tune index, scale vector DB, deduplicate chunks.
- **Later:** capacity planning by corpus size and tenant; ingestion quality gates.
- **Prevent:** benchmark retrieval at *projected* production corpus size.
- **Say:** *"Adding documents changes retrieval economics. I would filter earlier, tune index settings, and remove duplicate chunks before simply scaling hardware."*

### 4. Agent keeps calling tools repeatedly
- **Symptom:** agent repeats CRM lookup / retrieval / calculator calls and times out.
- **Ask:** which tool repeats, what observation triggers it, and is state preserved?
- **Causes:** poor stopping condition, ambiguous tool descriptions, missing memory, failed parse, no result cache.
- **Metrics:** agent steps, tool count, repeated tool args, parse failures, timeout rate.
- **Debug:** inspect trace; identify loop trigger and the missing state transition.
- **Now:** set max steps, cache tool result, improve tool schema, add deterministic route.
- **Later:** agent budget tests + trace-based loop detection.
- **Prevent:** unit tests for tool selection and loop prevention.
- **Say:** *"I would treat this as a control-loop bug. The fix is step budgets, better tool routing, cached results, and explicit stopping criteria."*

### 5. One tenant has unusually high usage
- **Symptom:** one customer consumes far more tokens/requests than comparable tenants.
- **Ask:** is this legitimate adoption, abuse, a loop, a batch job or an integration bug?
- **Causes:** automated integration loop, heavy document processing, power-user workflow, missing quota.
- **Metrics:** cost/tenant, cost/user, request source, tokens/request, batch jobs, agent steps.
- **Debug:** segment usage by API key, user, feature, time of day, prompt version.
- **Now:** tenant rate limit, contact the customer, pause the suspicious workflow if necessary.
- **Later:** tenant budgets, usage dashboard, anomaly alerts, integration safeguards.
- **Prevent:** contract-aligned quotas and notifications.
- **Say:** *"I would first distinguish healthy adoption from runaway automation. The response differs: support scale-up for healthy usage, throttle loops or abuse."*

### 6. Executive demo is too slow
- **Symptom:** demo answer takes too long in front of stakeholders.
- **Ask:** is the demo path hitting cold starts, large documents, a slow provider or live tools?
- **Causes:** unwarmed services, live external dependencies, over-large prompt, no streaming, poor network.
- **Metrics:** first-token latency, retrieval latency, model latency, tool calls, cold-start count.
- **Debug:** run rehearsal traces; identify the demo-specific critical path.
- **Now:** warm services, pre-index documents, stream output, use a stable demo dataset, shorten the answer.
- **Later:** demo-readiness checklist with latency rehearsal and a fallback path.
- **Prevent:** separate the demo environment from production claims.
- **Say:** *"For an executive demo, I would reduce live uncertainty while staying honest about production architecture and limitations."*

### 7. Customer complains the AI is too expensive
- **Symptom:** customer questions the invoice or the projected budget.
- **Ask:** which workflows drive cost, and what business value do they produce?
- **Causes:** premium-model overuse, verbose answers, no quotas, heavy batch jobs, low-value workflows.
- **Metrics:** cost by feature, active users, cost/outcome, model distribution, tokens/request.
- **Debug:** build a cost-attribution report; identify low-value high-cost paths.
- **Now:** route simple tasks to a cheaper model, add quotas, trim prompts, cache safe repeated results.
- **Later:** ROI dashboard and budget policies.
- **Prevent:** cost review before expansion.
- **Say:** *"I would not defend the bill generically. I would show cost by workflow and propose concrete reductions that preserve value."*

### 8. Vector database query latency increased
- **Symptom:** RAG latency rises while model latency is unchanged.
- **Ask:** did index size, metadata filters, shard distribution or traffic change?
- **Causes:** index fragmentation, hot tenant, inefficient filters, under-provisioned replicas.
- **Metrics:** query latency, filter selectivity, QPS, shard CPU/memory, cache hit rate.
- **Debug:** compare slow vs fast queries; inspect filters and index statistics.
- **Now:** add selective filters, scale replicas, tune index, reduce dimensions/top-k.
- **Later:** vector DB capacity planning and index maintenance.
- **Prevent:** load-test with a realistic tenant distribution.
- **Say:** *"When vector DB latency rises, I check corpus growth, filter selectivity, top-k, shard load, and tenant hot spots."*

### 9. Reranker improved quality but doubled latency
- **Symptom:** answer quality improved, user experience got worse.
- **Ask:** which queries truly need reranking, and how many candidates are scored?
- **Causes:** reranking every query, too many candidates, heavy reranker model.
- **Metrics:** reranker latency, candidate count, quality lift **by segment**.
- **Debug:** ablation by query type — no rerank vs rerank top 10 vs top 50.
- **Now:** gate reranking to ambiguous/high-value queries; reduce candidates.
- **Later:** quality-latency policy and retrieval-confidence thresholds.
- **Prevent:** monitor **quality lift per millisecond added**.
- **Say:** *"Reranking should be conditional. If it improves only 20% of queries, do not tax 100% of traffic."*

### 10. Prompt update increased token usage
- **Symptom:** cost and first-token latency rise after a prompt release.
- **Ask:** what changed in system prompt, few-shot examples, context packing or output format?
- **Causes:** verbose instructions, duplicated rules, added examples, longer default output.
- **Metrics:** input tokens, output tokens, prompt version, parse errors, retry count.
- **Debug:** diff prompt templates; compare token metrics by version.
- **Now:** roll back or trim the prompt; reduce examples; enforce output max.
- **Later:** prompt CI checks for token budget and quality regression.
- **Prevent:** every prompt rollout ships a cost-impact report.
- **Say:** *"Prompt changes are production changes. I would version them and compare token usage and latency before rollout."*

### 11. Model provider latency became unstable
- **Symptom:** intermittent latency spikes with no application deploy.
- **Ask:** is the instability model-specific, region-specific or provider-wide?
- **Causes:** provider incident, regional queueing, rate limiting, network issue.
- **Metrics:** provider latency by model/region, fallback rate, error codes, queue time.
- **Debug:** compare providers/models and application traces during the spike windows.
- **Now:** activate fallback model/provider, reduce concurrency, degrade optional features.
- **Later:** provider health dashboard + multi-provider fallback strategy.
- **Prevent:** test fallback prompts and schema compatibility.
- **Say:** *"I would isolate provider latency from our own pipeline and use routing/fallback rules rather than waiting blindly."*

### 12. Cache hit rate dropped suddenly
- **Symptom:** latency and cost rise because fewer requests hit cache.
- **Ask:** did cache key, TTL, prompt version, document version or traffic mix change?
- **Causes:** new prompt version invalidated the cache, TTL too short, normalization changed, document churn.
- **Metrics:** cache hit rate by type, invalidations, TTL, key cardinality, traffic mix.
- **Debug:** compare cache keys before vs after deploy; inspect invalidation events.
- **Now:** roll back the key change, adjust TTL, normalize queries, pre-warm safe cache.
- **Later:** cache observability + deployment checks.
- **Prevent:** cache changes require a performance **and security** review.
- **Say:** *"A cache hit drop is usually a keying, versioning, traffic, or invalidation issue; I would inspect those before scaling."*

### 13. Batch embedding job became too expensive
- **Symptom:** nightly embedding bill spikes after a document refresh.
- **Ask:** are all documents re-embedded, or only changed content?
- **Causes:** full re-indexing, duplicate docs, no content hash, larger embedding model.
- **Metrics:** embeddings generated, documents changed, duplicate rate, model version, job retries.
- **Debug:** compare **changed** document count with **embedded** document count.
- **Now:** pause the full job; switch to incremental indexing; deduplicate.
- **Later:** content-hash-based embedding cache and change detection.
- **Prevent:** indexing budget + anomaly alerts.
- **Say:** *"Embedding should be incremental. Re-embedding unchanged documents is usually a pipeline design issue."*

### 14. Long context window caused poor performance
- **Symptom:** cost and latency high; answers become less focused.
- **Ask:** why is long context used — broad synthesis, weak retrieval, or convenience?
- **Causes:** too much irrelevant context, chat-history bloat, full documents in the prompt.
- **Metrics:** input tokens, answer accuracy, citation precision, first-token latency.
- **Debug:** compare long-context answer vs compressed-RAG answer on an eval set.
- **Now:** use retrieval, summarization, context compression, history summarization.
- **Later:** context-budget policies per workflow.
- **Prevent:** treat context size as a **quality** variable, not only a cost variable.
- **Say:** *"Long context is a tool, not a strategy. I would test whether smaller evidence improves both speed and faithfulness."*

### 15. Tool-calling workflow times out
- **Symptom:** LLM response fails because the external workflow exceeds the timeout.
- **Ask:** which tool is slow, can it be async, and is the result required immediately?
- **Causes:** slow external API, serial calls, no timeout budget, synchronous side effects.
- **Metrics:** tool latency, timeout rate, dependency errors, step count, retries.
- **Debug:** trace tool calls; identify the critical-path dependency.
- **Now:** set tool timeouts, parallelize read-only calls, return a partial answer or an async job.
- **Later:** dependency SLAs and circuit breakers.
- **Prevent:** workflow design review before adding tools.
- **Say:** *"A tool timeout is not always an LLM issue. I would redesign slow side effects as async and keep the user informed."*

---

## 2. §15 one-liners — the highest-yield page

| # | Symptom | The one line to say |
|---|---------|---------------------|
| 1 | Cost 5× after rollout | Request **shape**, not user count — isolate tokens, retries, agent steps, batch jobs before touching the model. |
| 2 | 2s → 20s after deploy | Don't guess — traces tell you if the 18s is retrieval, model, tools or infra. |
| 3 | RAG slow after more docs | Adding documents changes retrieval **economics** — filter earlier, tune the index, dedupe before scaling hardware. |
| 4 | Agent loops on tools | It's a **control-loop bug**: step budgets, tool routing, cached results, explicit stopping criteria. |
| 5 | One tenant over-using | Separate healthy adoption from runaway automation — scale up one, throttle the other. |
| 6 | Exec demo slow | Reduce live uncertainty while staying **honest** about production architecture. |
| 7 | "Too expensive" | Don't defend the bill — show cost **by workflow** and propose reductions that preserve value. |
| 8 | Vector DB latency up | Check corpus growth, filter selectivity, top-k, shard load, tenant hot spots. |
| 9 | Reranker doubled latency | Reranking is **conditional** — if it helps 20% of queries, don't tax 100% of traffic. |
| 10 | Prompt update raised tokens | Prompt changes are **production changes** — version them, compare tokens and latency pre-rollout. |
| 11 | Provider latency unstable | Isolate provider latency from our pipeline; use routing/fallback rules, don't wait blindly. |
| 12 | Cache hit rate dropped | Usually keying, versioning, traffic mix or invalidation — inspect those before scaling. |
| 13 | Batch embedding too costly | Embedding should be **incremental**; re-embedding unchanged docs is a pipeline design issue. |
| 14 | Long context hurt quality | Long context is a tool, not a strategy — test whether **smaller** evidence is faster *and* more faithful. |
| 15 | Tool workflow times out | A tool timeout is not always an LLM issue — make slow side effects async and keep the user informed. |

---

## 3. §16 — The 7 interview case studies

### Case 1 — Enterprise legal RAG assistant under strict cost limits
- **Prompt:** legal team wants RAG over contracts and policies. Strict budget, answers must cite sources, latency target < 8s.
- **Ask:** Who are the users (lawyers, sales, procurement, execs)? Which documents are authoritative and how are permissions represented? Acceptable risk level for legal interpretation? Are the latency and cost ceilings contractual? Is human review required for external-facing language?
- **Weak:** strongest model + all documents in a long context window for every request.
- **Strong:** permission-aware RAG with metadata filters, calibrated top-k, citation enforcement, model routing. Simple clause lookup → mid-tier model; high-risk synthesis escalates. Rerank only ambiguous queries.
- **Architecture:** auth → tenant/ACL filters → hybrid retrieval → optional rerank → compressed evidence → answer with citations → audit log.
- **Trade-offs:** cost limit forces top-k tuning + routing; legal quality forces citations + escalation; the latency target rules out unconditional heavy reranking.
- **Metrics:** Recall@k, citation correctness, cost/request, retrieval latency, model latency, human escalation rate.
- **Recommendation:** pilot with a limited document set, define high-risk categories, instrument cost and latency from day one.

### Case 2 — Support chatbot with 10,000 daily users
- **Prompt:** volume growing, monthly LLM spend rising faster than ticket deflection.
- **Ask:** Which intents dominate traffic? What % are repeated FAQs? Target cost per resolved issue? Can answers be cached? Which answers need live account data?
- **Weak:** keep the same model and hope browser-layer caching helps.
- **Strong:** intent router, cached safe FAQ answers, small model for classification, RAG for knowledge answers, tool calls only for account-specific requests, concise response defaults.
- **Architecture:** gateway → intent classifier → FAQ semantic cache → RAG/tool path → model route → streaming answer.
- **Trade-offs:** caching cuts cost but must be permission-aware; small model handles simple traffic; live account data can't be broadly cached.
- **Metrics:** cost/resolved ticket, deflection rate, cache hit rate, P95 latency, tool latency, CSAT.
- **Recommendation:** reduce cost **by workflow**, not across the board; protect high-value paths.

### Case 3 — Reduce latency for an agentic CRM assistant
- **Prompt:** sales users complain account prep takes 30–45 seconds.
- **Ask:** Which tools are called? Serial or parallel? How many agent steps? Which data is required synchronously? Can account snapshots be precomputed?
- **Weak:** switch to a faster model without inspecting agent traces.
- **Strong:** trace the agent, cap steps, cache account data, parallelize read-only calls, precompute account summaries, route common requests to deterministic workflows.
- **Architecture:** user → deterministic intent route → account cache → parallel CRM/tool calls → summarization → optional agent for ambiguous next steps.
- **Trade-offs:** agent flexibility is useful, but common CRM operations should be deterministic and cache-backed.
- **Metrics:** agent step count, tool latency, cache hit rate, timeout rate, cost/request.
- **Recommendation:** replace the open-ended agent loop with a **bounded execution graph**.

### Case 4 — Multi-tenant GenAI platform with per-customer budgets
- **Prompt:** SaaS company wants GenAI features across customers with strict tenant isolation and budget controls.
- **Ask:** How are tenants isolated today? Which budgets are contractual? Can tenants choose model tiers? What data retention and audit policies apply? How is billing reported?
- **Weak:** add a global token limit and a shared cache.
- **Strong:** tenant-aware gateway, per-tenant budgets, permission-aware cache, tenant-specific observability, model-routing policy, quota alerts, isolation tests.
- **Architecture:** tenant gateway → auth → budget check → cache/model route → tenant-scoped data plane → cost attribution → dashboards.
- **Trade-offs:** caching and routing are powerful but dangerous without tenant keys and budget ownership.
- **Metrics:** cost/tenant, quota usage, cross-tenant access tests, cache hit rate by tenant, P95 latency.
- **Recommendation:** make `tenant_id` and `permission_signature` **first-class across every service**.

### Case 5 — Document summarization pipeline for batch processing
- **Prompt:** thousands of PDFs processed nightly; cost too high.
- **Ask:** Are documents new or changed? Is full summarization required every time? What is the SLA? Can work be batched off-peak? What quality checks are needed?
- **Weak:** run all PDFs through the premium model every night.
- **Strong:** content hashing, incremental processing, document dedupe, cheaper summarization model, batch inference, queue budgets, sampled evaluation.
- **Architecture:** ingest → hash/dedupe → parse → changed-only queue → batch summarization → quality sample → publish.
- **Trade-offs:** batch optimizes throughput, not interactive latency; quality is checked by sampling + strong-model audits.
- **Metrics:** documents processed, changed ratio, cost/document, queue depth, failure rate, eval score.
- **Recommendation:** never reprocess unchanged documents without a reason.

### Case 6 — Real-time sales assistant, sub-3-second response
- **Prompt:** sales team wants real-time answer suggestions during calls, sub-3s target.
- **Ask:** What must complete within 3 seconds? Can data be precomputed before calls? Is streaming acceptable? Which facts must be current? What happens on timeout?
- **Weak:** large model with a live CRM lookup on each request.
- **Strong:** precompute account context, keep the prompt small, mid/small model for suggestions, stream quick bullets, run enrichment asynchronously, fall back gracefully.
- **Architecture:** before call → precompute context. During call → small prompt → fast model → streamed suggestion. After call → async summary + CRM update.
- **Trade-offs:** a sub-3s target is a **workflow design** problem, not only a model choice.
- **Metrics:** first-token latency, total latency, cache/precompute hit rate, user accept rate, timeout rate.
- **Recommendation:** separate real-time suggestions from slower enrichment.

### Case 7 — Incident: LLM costs exploded after launch
- **Prompt:** new GenAI feature launched yesterday; spending exceeded the weekly budget in one day.
- **Ask:** What changed at launch? Which tenant/feature dominates spend? Are retries or agents involved? Are eval or batch jobs running? Is there abuse or an integration loop?
- **Weak:** disable the entire AI feature without diagnosis.
- **Strong:** activate the spend circuit breaker, identify top spend paths, cap output, pause batch/eval jobs, reduce premium routing, apply tenant quotas — **then** run root-cause analysis.
- **Architecture:** incident dashboard → cost attribution → mitigation controls → customer communication → permanent guardrails.
- **Trade-offs:** business continuity vs spend control — keep low-cost safe paths online while disabling runaway paths.
- **Metrics:** cost/minute, tokens/request, model distribution, retry count, agent steps, tenant usage.
- **Recommendation:** budget guardrails must exist **before** launch.

---

## 4. §16 pattern recognition — weak vs strong, at a glance

| Case | The weak move | The strong move |
|------|---------------|-----------------|
| Legal RAG | Strongest model + everything in long context | Permission-aware RAG, calibrated top-k, citations, routing, gated rerank |
| Support chatbot | Same model + browser caching | Intent router + FAQ semantic cache + small model + tools only for account data |
| Agentic CRM | Faster model, no trace inspection | Trace → cap steps → cache → parallelize → precompute → deterministic routes |
| Multi-tenant | Global token limit + shared cache | Per-tenant budgets, permission-aware cache, tenant observability, isolation tests |
| Batch PDFs | Premium model on every PDF nightly | Hash + change detection + dedupe + cheaper model + batch + sampled eval |
| Real-time sales | Large model + live CRM lookup per request | Precompute before, small prompt + stream during, enrich async after |
| Cost explosion | Kill the whole feature | Circuit breaker → attribute → cap/pause/route/quota → *then* RCA |

**The four verbs that generate every strong answer:** **measure** (trace/attribute first) → **route** (match model and path to risk) → **bound** (steps, tokens, top-k, timeouts, budgets) → **cache safely** (tenant + permission + version in the key).

---

## 5. Delivery — the 60-second structure the doc wants (§18, reused for §15/§16)

1. **Frame the problem** — business impact, treated as a measured workflow-optimization problem.
2. **Decompose the path** — retrieval, reranking, model inference, tool calls, retries, caching, post-processing.
3. **Identify the driver** — name the *largest measured* driver (often repeated retrieval + agent loops, not the base model).
4. **Fix safely** — step limits, in-request caching, route simple tasks down, cap output.
5. **Prove improvement** — P95 latency, cost/request, quality evals, cache hit rate, user success rate, before vs after.
6. **Prevent recurrence** — budgets, alerting, prompt/token regression checks, incident dashboard by tenant and feature.

---

## 6. Self-test before you close the file

Cover the answers and produce, from memory:
- [ ] The 9 rows of the §15 playbook, in order.
- [ ] The one customer-communication sentence used by all 15 scenarios.
- [ ] All 15 symptoms, and the first metric you'd pull for each.
- [ ] The 7 rows of the §16 case answer, in order.
- [ ] For each of the 7 cases: 3 clarifying questions and the one-sentence strong answer.
- [ ] The four verbs: measure → route → bound → cache safely.
- [ ] Your own incident, told in the 6-step 60-second structure.

---

*Drill this interactively:* https://claude.ai/artifact/2A3WKQifWFfeywuEscAsv5 (4 modes — symptom→playbook recall, weak-vs-strong picker, clarifying-questions drill, metrics recall).
*Beyond the playbook:* `ADDITIONS_BEYOND_PLAYBOOK.md`.
