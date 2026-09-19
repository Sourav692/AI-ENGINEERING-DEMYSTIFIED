# Cost & Latency Optimization Playbook — Full Cram Sheet (§1–§18)

**Source:** `03_GenAI_FDE_Cost_Latency_Optimization_Playbook.pdf` (Tobias Weissmann), 32 pages, 18 sections.
**Fidelity:** strictly the playbook's own content, compressed to recall-sized lines. Anything beyond it is in `ADDITIONS_BEYOND_PLAYBOOK.md`.
**Start here if you are short on time:** `CORE_8_DRIVERS_MEMORIZE.md` — the 8 drivers worth real memory; §2 and §3 below are recognition-only.
**Companions:** `CRAM_SHEET_S15_S16.md` (the 15 incidents + 7 cases expanded in full) · `Cost_Latency_Drills_FULL_PLAYBOOK.html` (258-card offline drill) · https://claude.ai/artifact/2A3WKQifWFfeywuEscAsv5

---

## 0. The spine — learn this and you can regenerate most of the book

```
End-to-end latency = auth + request routing + retrieval + reranking + prompt construction
                   + model queue time + inference + tool/API calls + post-processing + network return

Cost per request   = input tokens + output tokens + embedding/retrieval + reranking
                   + tool/API + infra allocation + logging/evaluation overhead
```

> **Senior FDE principle:** never optimize the model in isolation. Break the workflow into measured components, then remove the largest bottleneck first.

Sections §2–§13 are each one term of those two equations, expanded into a levers table. §15–§16 replay the same levers as incidents and interview cases.

---

## §1 — Why cost and latency matter

**Why demos die in production:** demos hide *traffic shape* (one user, warm cache, clean data), *tail latency* (P95/P99, not the average), *usage expansion* (longer questions, bigger uploads — tokens grow faster than request count), and *governance cost* (security review, audit logging, evaluation, human review, support).

**Why cost explodes after rollout:** a real request is rarely one model call — routing, query rewriting, retrieval, reranking, generation, evaluation, summarization, safety checks and tool execution can all fire for one user action.

**Why latency kills adoption:** users tolerate latency for complex, infrequent, high-value tasks; they reject it for conversational, repetitive, operational work. And a slow pilot creates *political* risk — stakeholders conclude GenAI isn't ready even when quality is strong.

| Executive concern | What they really ask | FDE translation |
|---|---|---|
| ROI | Does the value justify the spend? | Cost per resolved ticket / per document, hours saved, deflection rate, revenue & risk impact |
| Predictability | Can we budget this safely? | Per-tenant budgets, token limits, quotas, anomaly alerts, routing rules |
| Adoption | Will employees actually use it? | Perceived latency, workflow fit, reliability, explainability |
| Risk | Will this leak data or create compliance issues? | Permission-aware retrieval, audit logs, caching controls, human approval |
| Scalability | Can this work beyond the pilot? | Load-test realistic traffic, measure P95/P99, define cost curves before rollout |

**Prototype vs production:** dataset (curated/static → large, messy, multi-tenant, churning) · security (mocked → OAuth/OIDC/SAML, RBAC/ABAC, permission filtering, audit) · load (one user → concurrency, spikes, batch, retries) · observability (console logs → traces, token metrics, cost dashboards, alerts) · latency (one happy path → tail latency, queueing, cold starts) · cost (small bill → budget ownership, allocation, anomaly detection, procurement).

---

## §2 — Core cost drivers (18)

> **Do not memorize this table.** Memorize the 8 in `CORE_8_DRIVERS_MEMORIZE.md` and derive the rest from the cost equation. This is for coverage and lookup.

> The dangerous ones are the hidden multipliers: retries, long prompts, long outputs, agent loops, repeated retrieval, large context, and eval pipelines running silently.

| Driver | Production signal | Reduce it by | It costs you |
|---|---|---|---|
| Input tokens | Bill rises while traffic is flat | Trim prompts, compress context, summarize history, cache static parts | Less context hurts accuracy if retrieval is weak |
| Output tokens | Long answers dominate per-request cost | Max tokens, concise templates, structured output | Aggressive limits truncate answers |
| Long context windows | Cost rises, quality degrades from distraction | Retrieve relevant sections, compress, dedupe, hierarchical summaries | Needs better ingestion and retrieval |
| RAG retrieval | Vector DB cost, latency and infra load climb | Filter first, tune top-k, batch reads, optimize index, cache results | Too few chunks reduce completeness |
| Embedding generation | Batch jobs expensive overnight | Incremental indexing, change detection, embedding cache, cheaper model | Stale embeddings hurt freshness |
| Vector DB storage/search | Latency and bill rise after adding documents | Dimension choice, sharding, filters, index tuning, dedupe, lifecycle | Over-tuning reduces recall |
| Reranking models | One request triggers many reranker scores | Rerank only ambiguous/high-stakes; fewer candidates; lighter model | Less reranking lowers precision |
| Agent tool calls | Cost per request varies wildly by path | Max steps, tool budgets, allowlists, deterministic routing, cached tools | Strict limits block complex workflows |
| Multi-step reasoning | High output tokens, long traces | Only for complex/high-risk; route simple tasks to direct answers | May reduce reliability on hard tasks |
| Model retries | Cost spikes during incidents | Idempotency, retry budgets, backoff, schema validation, fallback models | Too few retries reduce availability |
| Streaming responses | Users follow up before completion; infra holds connections | Stream only long user-visible generation; cancel unused streams | Streaming hides cost, doesn't remove it |
| Logging and tracing | Observability bill and privacy risk grow | Sample, redact, TTL, structured metrics over raw payloads | Less detail slows incident analysis |
| Evaluation pipelines | CI/nightly jobs become large hidden spend | Sampled/stratified eval, cheaper judges, run deltas only | Weak coverage misses regressions |
| Batch jobs | Monthly bill spikes after a data refresh | Queue budgets, incremental processing, off-peak, rate limits | Longer processing windows |
| Fine-tuning | Extra model-version operations and evals | Use when behaviour repeats and prompts are large; compare vs RAG/prompting | Provider lock-in, stale behaviour |
| GPU/inference hosting | Low utilization, expensive standby | Autoscaling, batching, quantization, right-size, managed API at low volume | Operational complexity |
| Third-party APIs | External fees scale with agent/tool use | Cache, batch, negotiate limits, deterministic pre-filtering | Freshness and security issues |
| Human review | Support teams become the bottleneck | Risk-based routing, active learning, better UI, policy automation | Automation must not bypass controls |

> **Field note:** when cost rises, don't ask "which model is expensive?" Ask which *features, tenants, prompts, tools, retries, eval jobs and batch workflows* are consuming the budget. Cost allocation by request path is the difference between guessing and engineering.

---

## §3 — Core latency drivers (17)

> Same rule as §2 — recognition, not recall.

> Latency is a chain. Improving one link doesn't help if another dominates.

| Driver | Symptom | Fix | Prevention |
|---|---|---|---|
| Model inference time | Long wait before/during generation | Compare tiers, cut prompt/output, route simple tasks down | Model routing; never default to the largest |
| First-token latency | UI looks frozen before streaming | Lean prompt, reuse connections, stream, warm paths | Monitor first-token separately from total |
| Total response time | Answer finishes too slowly | Limit output, parallelize safe work, async background | Concise answer defaults |
| Retrieval latency | Slow before the model call | Filter before vector search, tune index, cache, cut top-k | Pre-test at target corpus size |
| Vector search latency | Worsens as documents grow | Index tuning, sharding, quantization, metadata pruning | Separate hot/warm corpora |
| Reranker latency | Good answers, slow pipeline | Fewer docs, only when needed, lighter reranker | Gate by query ambiguity |
| Tool/API latency | Agent waits on CRM, ERP, search | Parallelize, cache, timeouts, degrade gracefully | Budget tool calls per workflow |
| Agent planning loops | Agent "thinks forever" | Max steps, deterministic routers, smaller planning model | Every agent path needs a budget |
| Cold starts | First request after idle is slow | Min replicas, warmers, keep-alive, provisioned concurrency | Balance idle cost vs latency |
| Network latency | Regional users slower | Regional deployment, connection pooling, colocation | Data residency may constrain regions |
| Database latency | Permission/metadata lookups slow | Indexes, denormalized read models, async writes | Never bypass auth for speed |
| Large prompt construction | Backend slow *before* the model call | Precompute, cache static parts, compress context | Version prompt templates |
| Long output generation | Streams, then drags | Short defaults, progressive detail, max output | Allow expansion on demand |
| Sequential workflow design | Each step waits unnecessarily | Parallelize independent calls, prefetch, async non-critical | Don't parallelize unsafe side effects |
| Synchronous external calls | Request times out on a dependency | Queue async jobs, callbacks, optimistic UI | Async for non-immediate tasks |
| Auth and permission checks | Secure retrieval is slow | Precompute ACL metadata, filter before search, cache carefully | Never leak data for speed |
| Observability overhead | Tracing slows the hot path | Async logging, sampling, redaction, metrics over traces | Keep enough detail for incidents |

**Method:** build a latency waterfall from distributed tracing — mark auth, retrieval, reranking, prompt build, first-token, generation, tool calls, post-processing, logging, network return. Optimize the slowest component, judged on **P95/P99, not averages**.

---

## §4 — Cost vs latency vs quality (13 decisions + the exact sentence)

> The goal is the minimum-cost, minimum-latency design that still meets quality, safety, security and UX requirements.

| Decision | Use when | Avoid when | Say |
|---|---|---|---|
| Smaller vs larger model | Classification, extraction, routing, simple summaries | High-risk legal/financial/medical/security reasoning | "I would match model strength to task risk and complexity instead of using the premium model for every request." |
| Fast vs accurate answer | Operational chat, support triage, guidance | Regulated or irreversible decisions | "I would separate perceived latency from final confidence and make high-risk paths slower but safer." |
| More vs less retrieval context | Narrow evidence needs | Broad legal/policy synthesis | "More context is not always better; irrelevant context increases cost and can reduce answer quality." |
| More vs fewer chunks | Known-document lookup | Ambiguous exploratory queries | "I would evaluate recall and answer faithfulness while reducing top-k." |
| Reranking vs direct retrieval | Ambiguous, high-value enterprise search | Very low-latency chat paths | "Reranking should be a gated quality tool, not an unconditional tax." |
| Agentic vs deterministic | Ambiguous multi-step problems | Known workflows with stable tools | "I would not use an agent where a workflow engine or router is enough." |
| Real-time vs async | Bulk summarization, embedding, reports | Live conversation | "Not every AI workflow should be synchronous." |
| Streaming vs not | Narrative answers, copilots | Short classification/extraction | "Streaming is UX optimization, not a substitute for backend optimization." |
| Fine-tune vs prompt | Repeated structured tasks, stable style | Fast-changing knowledge or permissions | "I would compare fine-tuning against RAG and prompt compression using production traffic." |
| Caching vs freshness | FAQs, embeddings, tool results with TTL | User-specific sensitive answers, changing permissions | "Caching must be permission-aware; speed is not worth cross-tenant leakage." |
| Batch vs live | Ingestion, enrichment, evals | Interactive support/chat | "Batching is ideal when user value does not require an immediate response." |
| Self-hosted vs managed | Predictable high volume, strict data controls | Low/variable traffic, small team | "I would compare total cost of ownership, not only token or GPU price." |

---

## §5 — Model selection

> The senior question is not "what is the best model?" but **"what is the weakest *reliable* model for this task, risk level, latency target and budget?"**

**Model roles:** routing (intent/complexity/policy detection — cheap model decides if premium is needed) · extraction (small model or constrained parser; validate with schema) · summarization (cheaper model when factuality risk is moderate and the source stays available; cite chunks) · reasoning (only for multi-step judgement; gate by risk, audit traces) · embedding (choose by domain recall, dimension, latency, storage) · reranker (precision without sending all context to the generator) · multimodal (expensive — try OCR/parsing first; route pages, not whole files).

**Cascades:** cheap → medium → premium · rules before LLM · retrieval-confidence gate · cheap draft + strong verify · provider fallback (keep prompts and schemas portable).

**Context window:** useful when the question genuinely needs broad evidence; dangerous as a substitute for retrieval quality. The target is **minimum sufficient context**, not maximum context.

---

## §6 — Prompt optimization

Prompts are production artifacts. Prompt bloat is one of the most common hidden causes of cost increase and first-token latency.

**Principles:** separate static instructions from dynamic content (so static parts can be cached/versioned) · remove instructions repeated across system/developer/user layers · few-shot only where it measurably improves accuracy · structured output when downstream systems consume it, but not so complex it causes retries · limit output length with expansion-on-demand · compress retrieved context with source identifiers · track template version, token usage, error rate and quality impact before rollout.

| Change | Effect |
|---|---|
| Remove repeated style instructions | Fewer input tokens, less instruction conflict |
| Reduce few-shot examples | Smaller prompt; keep only examples that move the eval score |
| Compress context | Lower cost, faster first token |
| Output limit | Lower output-token cost, faster completion |
| Structured fields | Easier downstream parsing and observability |

**Rollout discipline:** regression-eval before production · compare token usage before/after · measure first-token latency, total latency, parse failures, retries, user correction rate · version every template and link incidents to versions · keep a rollback path.

---

## §7 — RAG cost and latency

> Not vector-DB tuning — a full pipeline problem: parsing, chunking, metadata, permissions, embedding, indexing, query rewriting, retrieval, reranking, context packing, generation, evaluation.

| Lever | Guidance |
|---|---|
| Chunk size | Tune by document type and question type; evaluate faithfulness and recall |
| Chunk overlap | Minimal overlap; avoid blind 20% on every corpus |
| Metadata filtering | Apply **before** vector search where possible — shrinks the search space and prevents leakage |
| Permission-aware retrieval | Precompute ACL metadata; never filter only after generation |
| Hybrid search | For enterprise terms, acronyms, IDs, product names, legal clauses |
| Query rewriting | Gate it — rewriting every query adds latency and cost |
| Top-k tuning | Measure quality as top-k drops; top-k 20 may not beat top-k 5 |
| Context compression | Summarize/extract relevant lines; must preserve citations |
| Deduplication | Cuts storage, retrieval noise, token cost and hallucination risk |
| Embedding freshness | Incremental indexing and content hashes |
| Vector DB tuning | Tune on production-like corpus size and tenant filters |
| Retrieval evaluation | Recall@k, MRR, faithfulness, citation correctness — don't tune top-k blindly |

**Memorize the two paths:**
- **Ingestion:** parse → normalize → deduplicate → chunk → classify metadata → compute permissions → embed → index → validate retrieval.
- **Query:** authenticate → infer intent → apply tenant/ACL filters → retrieve → optional rerank → compress context → generate → cite → log metrics.

> **Senior position:** the best RAG optimization is usually *not* a faster vector database. It is cleaner documents, better metadata, permission filters before search, fewer duplicate chunks, calibrated top-k, and a generator prompt that receives only the minimum evidence needed.

---

## §8 — Agent cost and latency

**Why agents blow up:** too many planning steps before useful action · tool loops from ambiguous descriptions or missing state · reflection on simple tasks · unbounded retries · large intermediate context carried every step · repeated instead of cached retrieval · serial execution of parallelizable calls · external API delays without timeout budgets · memory growth inflating prompt cost every turn.

| Control | Risk control |
|---|---|
| Hard max step limits | Escalate to human / ask clarification at the limit |
| Tool allowlists by intent | Route by intent first |
| Tool call + cost budgets | Record budget exhaustion as a trace event |
| Parallel read-only tool calls | Never parallelize side-effecting actions blindly |
| Cached tool results (request/session) | TTL + permission checks |
| Deterministic routing for common paths | Fall back to the agent for ambiguous tasks |
| Smaller planning model | Escalate if confidence is low |
| Summarized intermediate state | Keep the audit log outside the prompt |
| Human approval for expensive/sensitive actions | Thresholds + clear user explanation |
| Trace analysis for loops | Add tests for repeated failure paths |

**The worked number:** agentic CRM assistant at 45s / €1.20 per request → trace showed 9 model calls, 7 retrievals, 4 CRM calls and large intermediate context → max 4 steps + in-request caching + smaller routing model → **8s / €0.18**. Long-term: deterministic routes for account lookup, ticket summary and next-best-action; agent only for ambiguous multi-step requests.

> **Say:** "I would treat the agent as an execution graph with budgets, not an open-ended reasoning loop."

---

## §9 — Caching (this is a *security* section)

Enterprise caching must be **tenant-aware, permission-aware, version-aware and freshness-aware.**

| Cache type | Security / freshness rule |
|---|---|
| Prompt caching | Don't cache user-specific sensitive context across users |
| Semantic caching | A poor similarity threshold returns stale or mismatched answers |
| Response caching | Key must include tenant, user permission, document version, prompt version |
| Embedding caching | Key on content hash + embedding model version |
| Retrieval result caching | Invalidate on document, ACL or metadata changes |
| Tool result caching | Don't cache sensitive dynamic data broadly |
| Session-level caching | Clear at logout / session expiry |
| Tenant-level caching | Never mix tenant keys |
| CDN / API gateway caching | Static resources only — never dynamic personalized responses |

**Safe to cache:** public or tenant-approved static docs with version keys · embeddings keyed by content hash + model version · prompt templates keyed by version · low-risk tool results with short TTL and permission-bound keys · retrieval results *only* when tenant, permissions, document versions and filters are in the key.

**Never casually:** cross-tenant responses without isolation · sensitive user-specific answers without permission-bound keys · results behind fast-changing permissions without strong invalidation · regulated data where retention policy forbids storing derived outputs · tool responses containing secrets, tokens, credentials or private notes.

**The cache key rule (quote it):**
```
tenant_id + user_id or permission_signature + document_version
+ prompt_version + model_version + request_normalized_hash + tool_state_version
```
> If that feels too heavy, that is a sign the answer may not be safe to cache broadly.

---

## §10 — Streaming and UX

Streaming improves *perceived* latency. It does not reduce total latency or cost.

| Concept | Tactic |
|---|---|
| First-token latency | Stream early, shrink prompt, warm connections |
| Total latency | Limit output, parallelize safe steps, fewer tool calls |
| Perceived latency | Streaming, progress states, partial results, skeleton UI |
| Progressive disclosure | Concise default + "show details" |
| Async job handling | Job status, notification, downloadable result |
| Cancellation | Cancel the stream *and* tool execution; log cancelled cost |
| Retry UX | Retry safely, give a partial answer and a next step |
| Timeout handling | Per-component and global timeout budgets |

**Streaming is hiding a real problem when:** retrieval/tools take 10s before any token · the answer is simply too verbose · agent loops keep running after the user stopped needing the result · the UI streams low-confidence content before verification.

---

## §11 — Infrastructure and deployment

> Infrastructure optimization is about controlling the **critical path**.

API gateway (don't hide per-tenant cost attribution) · connection pooling (pool exhaustion → latency spikes) · HTTP keep-alive · async queues (users need job status) · worker scaling by queue depth (avoid uncontrolled batch spend) · horizontal scaling (provider latency may still dominate) · tenant-aware rate limits · backpressure (graceful degradation over cascading failure) · autoscaling (LLM load may not correlate with CPU) · cold-start reduction (costs idle capacity) · regional deployment (data residency constrains you) · GPU batching/quantization (low utilization can beat managed API on price — the wrong way) · serverless vs containers · Kubernetes tuning · batch inference · observability overhead.

**Six architecture patterns:** real-time GenAI API (short critical path, routing, streaming, caching, strict timeouts) · async document pipeline (queue, batch, worker autoscaling, budgets, retries) · RAG ingestion pipeline (dedupe, incremental indexing, ACL metadata, embedding cache) · multi-tenant platform (tenant budgets, isolation, per-tenant metrics, permission-aware cache) · agent execution service (step limits, tool budgets, trace store, deterministic routes) · evaluation pipeline (sampled evals, cheaper judges, scheduled offline runs).

---

## §12 — Observability

> A production GenAI system without cost and latency observability is **financially unsafe**.

**17 metrics:** request latency · first-token latency · total generation time · input/output tokens · cost per request · cost per tenant/feature/user · retrieval & reranker latency · tool call latency · agent step count · cache hit rate · retry/timeout rate · P95/P99 · provider/model latency · vector DB latency · queue depth · GPU utilization · customer ROI metrics.

**Five dashboards:** executive cost (CFO/sponsor) · engineering latency (P50/95/99 by component) · tenant usage (CS/account team) · incident (on-call/SRE/FDE) · model performance (AI engineers/product).

**Every trace event should carry:** `tenant_id, feature, prompt_version, model, input_tokens, output_tokens, estimated_cost, latency breakdown, retrieval top-k, reranker used, cache status, tool calls, retries, timeout status, final outcome` — with sensitive payloads redacted and a retention policy applied.

---

## §13 — Budgeting and guardrails

> Treat budget as a first-class engineering constraint, not a monthly surprise.

Per-user budget · per-tenant budget · per-feature budget · per-request token limit · max agent steps/tool calls · tenant-aware rate limits and quotas · spend anomaly detection · expensive-query detection (long context, repeated retries, high tool usage) · model fallback rules · human approval for high-cost/high-risk actions.

**Five policies:** free tier (small model default, strict daily quota, no long-context agent workflows) · enterprise tenant (contract budget, quota alerts, premium only for approved workflows, monthly report) · internal employee assistant (department budgets, approval for sensitive workflows, retention limits) · high-risk workflow (strong model, citations, human approval, full audit trace, **no broad cache**) · demo environment (warm paths, seeded cache, capped traffic, fixed dataset, budget alert).

---

## §14 — Enterprise customer communication (memorize the wording)

| Situation | Say |
|---|---|
| High latency | "I would not frame this as simply a model problem. I would break the latency into retrieval time, model inference time, tool-call time, and post-processing time. That lets us optimize the real bottleneck instead of guessing." |
| Cost increase | "The increase appears to be driven less by user count and more by request shape: longer prompts, more retrieved context, additional tool calls, and retries. I would separate these drivers so we can reduce spend without reducing useful quality." |
| Executive trade-off | "We can make this faster and cheaper, but we need to decide which quality bar must remain fixed. For low-risk requests we can route to a smaller model. For high-risk workflows I recommend keeping the stronger model and optimizing retrieval and prompt size first." |
| Model downgrade | "This is not a downgrade of the product experience. It is a routing strategy: use the premium model where it changes the outcome, and use a faster model where the task is simple and measurable." |
| Why caching helps | "Many requests repeat the same stable context. A permission-aware cache can reduce latency and cost while preserving tenant isolation and freshness rules." |
| Why not always the best model | "The best model is not always the best system choice. The right system uses the cheapest reliable model for the task and escalates only when complexity or risk requires it." |
| Optimization roadmap | "I would propose a three-step roadmap: first instrument the bottlenecks, then apply safe quick wins like prompt trimming and top-k tuning, and finally redesign heavy workflows with routing, caching, and async processing." |
| Handling complaints | "Your concern is valid. I would separate whether the issue is answer quality, latency, cost predictability, or workflow fit. Each has a different fix, and treating everything as a model problem would be too imprecise." |
| Pilot failed on latency | "The pilot showed useful quality but the workflow latency was not production-ready. I would treat this as an engineering optimization issue, not a failure of the entire AI use case." |
| CFO / procurement | "We can provide per-tenant budgets, cost ceilings, usage dashboards, and model-routing rules so spend is predictable rather than open-ended." |
| Security concern on caching | "Caching is only acceptable when the cache key includes tenant and permission boundaries, and when invalidation respects document and access changes. We should not cache sensitive cross-user answers broadly." |

**The 6-step customer narrative:** acknowledge the business concern → decompose into measurable components → identify quick wins that don't compromise security or quality → explain trade-offs as options, not absolutes → connect every optimization to adoption / ROI / budget predictability / risk reduction → commit to measured follow-up with dashboards, thresholds and before/after numbers.

---

## §15 + §16 — Incidents and cases

**Full expansion lives in `CRAM_SHEET_S15_S16.md`.** The 9-row incident shape is: Symptoms → Clarifying questions → Probable causes → Metrics → Debugging steps → Immediate fix → Long-term fix → Prevention → Customer communication → Interview line. The customer-communication row is identical in all 15:

> "Acknowledge impact, show measured cause, provide immediate mitigation, then explain long-term prevention and success metric."

**The 15 incidents:** cost 5× after rollout · 2s→20s after deploy · RAG slow after adding docs · agent loops on tools · one tenant over-using · exec demo slow · "too expensive" complaint · vector DB latency up · reranker doubled latency · prompt update raised tokens · provider latency unstable · cache hit rate dropped · batch embedding too costly · long context hurt quality · tool workflow times out.

**The 7 cases:** legal RAG under cost limits · support chatbot at 10k DAU · agentic CRM latency · multi-tenant platform with budgets · nightly PDF batch · sub-3s real-time sales assistant · post-launch cost explosion.

**The four verbs that generate every strong answer:** **measure → route → bound → cache safely.**

---

## §17 — The ten checklists

**Cost:** break cost down by tenant/feature/model/prompt version/request path/batch job · measure input & output tokens, retries, agent steps, tool calls, embeddings, reranking, logging · find low-value high-cost workflows before cutting quality globally · max output length + per-request token budgets · route simple tasks down · dedupe documents, don't re-embed unchanged content · gate reranking and query rewriting · safe caching with tenant/permission keys · spend anomaly alerts **before launch** · include eval and batch jobs in spend analysis.

**Latency:** measure first-token, total, retrieval, reranker, model, tool, DB, auth, post-processing · inspect P95/P99, not averages · trace waterfall for slow requests · reduce prompt size and output length · parallelize independent read-only calls · move long work async · timeout budgets per dependency · warm cold paths · regional deployment + connection pooling · monitor provider latency separately.

**RAG:** evaluate chunk size/overlap on real docs and real queries · filter (tenant, ACL, type, date) before vector search · tune top-k with retrieval evals and faithfulness · remove duplicates and boilerplate · hybrid search for acronyms/IDs/exact terms · gate reranking · compress context while preserving source IDs · incremental indexing + content-hash embedding cache · measure vector DB P95 and filter selectivity · track citation correctness and recall.

**Agents:** max steps, max tool calls, max cost, global timeout · tool allowlists by intent · cache retrieval and tool results per request/session · deterministic workflows for common tasks · smaller planning model · summarize intermediate state · parallelize safe read-only calls · human approval for expensive/sensitive actions · track step count and repeated tool patterns · test loop and timeout scenarios.

**Prompts:** remove repeated instructions and unused examples · separate static/dynamic · output length defaults + expansion on demand · structured output only as complex as necessary · compress context and summarize history · track template version in every trace · token budget tests in CI · compare quality, retries, parse errors and tokens before rollout · avoid hidden bloat from conversation memory · keep a rollback path.

**Caching:** define the type · tenant and permission boundaries in keys · document/prompt/model/tool-state versions · TTLs by freshness and risk · never cache secrets, tokens or broad sensitive answers · measure hit rate, miss reason, stale incidents, invalidations · prewarm safe high-frequency entries · audit isolation for cross-tenant leakage · document when caching is forbidden · review with security and compliance.

**Observability:** log cost and latency per request path without unnecessary sensitive payloads · token usage by prompt version and model · latency broken down by component · cache hit rate and invalidation events · retries, timeouts, provider errors, fallback usage · agent step/tool counts and repeats · five dashboards · alerts for spend anomalies and P95/P99 regressions · retention per privacy policy · sampling where full tracing is too expensive.

**Customer communication:** acknowledge business impact first · separate quality/cost/latency/security/workflow-fit · trade-offs as options, not excuses · don't blame the provider without evidence · show measured bottlenecks and before/after targets · connect to ROI, adoption, predictability · document mitigation and prevention · plain language for executives, traces for engineers · set expectations for high-risk workflows · be transparent about caching, retention and tenant isolation.

**Pre-production readiness:** load test realistic traffic/documents/tenants/prompt sizes · latency and cost SLOs by workflow · budgets, quotas, rate limits, token limits, agent limits · validate permission-aware retrieval and cache isolation · prompt/model regression evals · review dashboards and alerts · test provider fallback and graceful degradation · test batch budgets and retry behaviour · incident runbooks + customer comms templates · security/compliance review for logging, caching, retention.

**Executive demo readiness:** stable dataset matching the business scenario · warm services and caches · rehearse with production-like network · measure latency for every demo path · fallback path for provider/network delays · concise defaults and streaming · no uncontrolled live agent workflows unless tested · ROI and trade-off explanation ready · don't overclaim production readiness · capture feedback as measurable next steps.

---

## §18 — The senior mental model

1. **Measure before changing** — traces, cost attribution, token metrics, P95/P99.
2. **Break latency into components** — auth, retrieval, reranking, prompt construction, first-token, generation, tool calls, post-processing, network.
3. **Break cost into drivers** — input, output, embeddings, reranking, retries, agent steps, tools, logging, evals, batch, infra.
4. **Optimize workflow before model** — routing, async design, caching, removing steps.
5. **Use smaller models where possible** — match strength to complexity, risk, quality bar.
6. **Cache carefully** — without tenant and permission safety it becomes a security incident.
7. **Control agent behaviour** — step limits, tool budgets, traces, deterministic routes, stopping rules.
8. **Set budgets and guardrails** — predictable by tenant, feature, user, request path.
9. **Communicate trade-offs clearly** — options with benefits, risks, business impact.
10. **Connect optimization to business value** — adoption, ROI, reliability, security, sustainable scale.

### One-page field summary

| Question | Senior answer |
|---|---|
| Where is the latency? | Trace the full path: auth, retrieval, rerank, model, tools, post-processing, network. |
| Where is the cost? | Attribute by tokens, model, retries, agent steps, embeddings, tools, evals, infra, tenant. |
| What to optimize first? | The largest measured bottleneck improvable without breaking quality or security. |
| Use a smaller model? | Yes for simple low-risk tasks if evals confirm quality; escalate for complex/high-risk. |
| Should we cache? | Only with tenant, permission, freshness and retention controls. |
| Should we use agents? | Only when deterministic workflows are insufficient; budgeted and traced. |
| How to convince executives? | Cost predictability, latency targets, adoption impact, ROI metrics. |

### The 60-second answer structure (practise one real incident in this shape)

1. **Frame** — the system was useful, but cost and latency were not production-ready; a measured workflow-optimization problem.
2. **Decompose** — retrieval, reranking, model inference, tool calls, retries, caching, post-processing.
3. **Identify the driver** — the largest was repeated retrieval and agent tool loops, not the base model.
4. **Fix safely** — step limits, in-request retrieval caching, routed simple tasks to a smaller model, capped output.
5. **Prove it** — P95 latency, cost/request, quality evals, cache hit rate, user success rate, before vs after.
6. **Prevent recurrence** — budgets, alerting, prompt/token regression checks, incident dashboard by tenant and feature.

### Closing principle

> Premium GenAI engineering is not about using the most powerful model everywhere. It is about building a measured, secure, cost-aware, latency-aware system that customers can trust, afford, adopt and scale.
