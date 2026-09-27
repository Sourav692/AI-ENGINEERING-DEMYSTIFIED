# FDE Interview — Trigger → Concept Cheat Sheet

Use this to recognize what an interviewer is testing and decide your next move. A trigger suggests a question or requirement; it does not automatically justify a component.

```text
HEAR THE TRIGGER → RECALL THE CONCEPT
                           ↓
        CLARIFY → REQUIREMENT → CHOICE → TRADE-OFF
```

**Answer pattern:** “That suggests ___. I’d clarify ___ before choosing ___. The main trade-off is ___.”

## 1. Discovery and Requirements — Modules 1–3

| Hear… | Think… | Ask / say next | Module |
|---|---|---|---|
| “We need an AI agent” | Proposed solution vs business problem | “What outcome matters, and what is painful today?” | 1 |
| “People waste time on this” | Current workflow and bottleneck | “Walk me through the steps and where time is spent.” | 1 |
| “What should the system do?” | Functional requirements | Summarize capabilities, actions, approvals, and failures | 2 |
| “Follow-up questions” | Relevant context | What must persist across turns or tasks? | 2 |
| “Recommend the next action” | Reason, not necessarily act | Who decides and who executes? | 2 |
| “Fast, reliable, cheap” | Measurable NFRs | Workload, metric, target, window, quality floor | 3 |
| “100K users” | Workload discovery | Active users, peak rates, concurrency, task duration | 1, 3, 9 |
| “Reduce support cost” | Business outcome | Baseline, resolved cases, quality and customer experience | 1, 3, 11 |
| “Trustworthy answers” | AI quality | Correctness, claim support, relevant evaluation cases | 3, 13 |

**Recall discovery:** WHY → TODAY → WHO/HOW MUCH → WHAT → HOW FAR → BOUNDARIES.

## 2. Architecture Responsibilities — Module 4

| Hear… | Think… | Ask / say next | Module |
|---|---|---|---|
| “User identity, tenant quotas, request validation” | API Gateway | Application-entry controls; downstream access still checked | 4 |
| “Several model providers, fallback, token tracking” | Model Gateway | Compatible model-call controls and provider limits | 4 |
| “Several request categories” | Router | Choose capability; separate agents are not implied | 2, 4 |
| “Branches, tools, retries, approvals” | Orchestrator | Coordinate steps and state transitions | 4 |
| “Resume tomorrow / after a crash” | Durable state | Persist progress, approval, and action status | 4, 6, 12 |
| “Repeated eligible lookup” | Cache | Freshness, tenant/access scope, invalidation | 4, 11 |
| “Long task / temporary burst” | Queue | Bounded wait, job status, processing capacity | 4, 9, 10 |
| “Several consumers react to a refund” | Event distribution | Delivery, duplicate handling, independent consumers | 4 |

```text
API Gateway   = User → Application control
Model Gateway = Application → Model control

Router: Which capability?
Orchestrator: Which step / transition next?
State store: Where did the task stop?
```

## 3. RAG and Enterprise Data — Module 5

| Hear… | Think… | Ask / say next | Module |
|---|---|---|---|
| “Company policies / manuals” | RAG knowledge | Approved sources, ingestion, freshness, access | 5 |
| “Current order or refund status” | Live API/tool | Query the system of record within authorized scope | 5, 7 |
| “Correct document never appears” | Recall / ingestion | Does it exist, parse correctly, pass filters, and get retrieved? | 5 |
| “Too many unrelated chunks” | Precision / ranking | Search signals, chunking, reranking, final context | 5 |
| “Exact product code” | Keyword / hybrid matching | Compare exact-term and meaning-based retrieval | 5 |
| “Old policy answer” | Freshness and version | Update pipeline, metadata, applicability | 5 |
| “Right evidence, wrong answer” | Context use / generation | Was evidence retained, and do claims follow it? | 5, 13 |
| “Includes citations” | Evidence support | Do sources actually support the important claims? | 5, 13 |
| “Different document permissions” | Authorized retrieval | Enforce before context; update permissions and cache scope | 5, 16 |

```text
Debug RAG:
Source → Parse/index → Access/version filters
       → Retrieve/rank → Final context → Supported answer
```

RAG = retrieval-augmented generation. Recall concerns finding relevant evidence; precision concerns how much retrieved evidence is relevant. Groundedness concerns support, not whether the source is current and correct for the case.

## 4. Agents, Tools, Actions, and Approval — Modules 6–8

| Hear… | Think… | Ask / say next | Module |
|---|---|---|---|
| “Same steps every time” | Workflow/code | Keep defined rules and branches deterministic | 6 |
| “Next steps depend on findings” | Bounded agent | Which decisions need flexible reasoning? | 6 |
| “Separate agent for every feature” | Complexity justification | What specialization/parallel benefit exceeds coordination cost? | 6, 17 |
| “Twenty calls for a simple task” | Bounds / no progress | Shared step/tool/token/time/cost/retry budget | 6, 11 |
| “Access production CRM/ERP” | Controlled tool layer | Specific operations, validated inputs, scoped credentials | 7 |
| “Issue refund / cancel order” | Write action | Authorization, policy, safe execution, confirmation | 7, 8 |
| “Amount threshold” | Deterministic policy | Exact boundaries, trusted facts, rule ownership/version | 8 |
| “Manager must approve” | HITL | Action/evidence packet, authorized reviewer, durable state | 8 |
| “Approval takes hours” | Durable approval workflow | Persist, expire/reject, resume and revalidate | 8 |
| “Action changes after approval” | Approval binding | Check policy and obtain fresh approval where required | 8 |
| “Policy service unavailable” | Fail-closed sensitive writes | Stop/defer action; safe unaffected assistance may continue | 8 |
| “Disable refunds now” | Kill switch | Execution boundary, queued/in-flight work, actual outcomes | 8, 14 |

```text
Agent recommends → Policy decides → Executor acts
                          ↓
                 Approval if required
```

HITL = human-in-the-loop. High model confidence is not permission to act. Approval does not grant unrelated access or reverse completed transactions.

## 5. Scale, Latency, and Cost — Modules 9–11

| Hear… | Think… | Ask / say next | Module |
|---|---|---|---|
| “One tenant hurts everyone” | Noisy neighbor / fairness | Tenant concurrency, quotas, weighted scheduling | 9 |
| “Within quota, but system full” | Admission control | Can this task be accepted within capacity now? | 9 |
| “Queue grows continuously” | Sustained overload | Arrival vs completion rate; capacity or reduced intake | 9 |
| “More workers did not help” | Shared/external bottleneck | Model quota, tool API, retrieval, state-store saturation | 9 |
| “Average 3s, P99 25s” | Tail latency | Slow traces by workload, tenant, and release | 10 |
| “Model fast, task slow” | Critical path | Queue, retrieval, tools, repeated hops, network | 10 |
| “Independent reads are sequential” | Parallelism | Overlap only when inputs, limits, and correctness allow | 10 |
| “Long silence before output” | First useful output / streaming | Separate first output from final completion | 10 |
| “Five-minute research” | Async interaction | Task ID, durable state, progress, results | 10 |
| “Bill doubled” | Attribution | Volume, task mix, model/tokens, calls, retries, rework | 11 |
| “History grows forever” | Context optimization | Relevant turns/evidence, summaries, authoritative state | 11 |
| “Five model calls every time” | Call reduction | What reasoning does each call add? | 10, 11 |
| “Same strong model for all tasks” | Evaluated model routing | Cheapest capable path at required quality | 11 |
| “Background work can wait” | Batch eligibility | Deadline and measured billing/processing benefit | 11 |
| “Cheap requests, many failed tasks” | Cost per successful task | Include retries, escalation, and relevant rework | 11 |

```text
Rate limit: May this tenant send this much work?
Admission:  Can the system accept it now?
Queue:      Where can accepted work wait within limits?

Latency: Trace → Critical path → Optimize → Recheck quality
Cost: Total cost across attempts ÷ successful tasks
```

Streaming does not necessarily reduce computation. Async does not automatically shorten completion. A queue does not create capacity. TTFT means time to first token; useful user output and confirmed action completion are separate measurements.

## 6. Failure and Recovery — Module 12

| Hear… | Think… | Ask / say next | Module |
|---|---|---|---|
| “Write timed out” | Unknown outcome | Query status/reconcile before another write | 7, 12 |
| “Repeated request / message” | Idempotency | Stable identifier for the same logical action | 7, 12 |
| “Intermittent service errors” | Bounded retry | Transient/safe? Backoff, jitter, deadline | 12 |
| “Retries worsen outage” | Retry amplification | Shared budgets, circuit breaker, capacity protection | 12 |
| “Provider unavailable” | Compatible fallback | Capability, quality, permissions, residency | 12 |
| “Crash after some steps” | Durable recovery | Known checkpoints plus uncertain-action reconciliation | 12 |
| “Message fails repeatedly” | DLQ | Dead-letter queue owner, diagnosis, safe replay | 12 |
| “Optional feature breaks everything” | Blast radius / degradation | Keep safe independent capabilities available | 12 |

**Rule:** timeout ≠ confirmed failure; checkpoint ≠ exactly-once external effect; DLQ ≠ completion. Never generate a fresh logical action key simply because the previous attempt timed out.

## 7. Evaluate, Release, and Operate — Modules 13–15

| Hear… | Think… | Ask / say next | Module |
|---|---|---|---|
| “Says cancelled, order still active” | Task success | Verify confirmed downstream state | 13 |
| “Wrong tool arguments” | Deterministic assertions | Schema, permitted values, intended resource/action | 13 |
| “Helpful / complete / grounded?” | Semantic rubric | Calibrate human/model judges against expert cases | 13 |
| “Ratings high, tickets reopen” | Online outcomes | Delayed results and actual resolution | 13 |
| “New prompt better on 20 cases” | Coverage and release evidence | Held-out segments, failures, baseline, gates | 13, 14 |
| “Compare without affecting users” | Shadow | Candidate isolated from production writes | 14 |
| “Only two tenants first” | Scoped canary/flag | Cohort, stable assignment, stop criteria | 14 |
| “Regression after release” | Rollback / kill switch | Known compatible baseline, active tasks/actions | 14 |
| “Old tasks remain pending” | Version compatibility | State schema, policy, approval/action meaning | 14 |
| “Slow request yesterday” | Distributed trace | Task/trace ID, critical spans, queue, retries | 15 |
| “Widespread slowdown” | Metrics | Scope, saturation, workload/version patterns | 15 |
| “Exact error?” | Structured logs | Correlated event and error category | 15 |
| “Why was this refund issued?” | Business audit | Identity, evidence, policy, approval, action result | 15 |
| “Did we meet the promised service?” | SLI / SLO / SLA | Measured indicator / target / agreed commitment | 15 |

```text
Good wording ≠ completed task
Offline evaluation ≠ real production outcome
Shadow ≠ canary
Rollback ≠ undo completed payment

Logs: Specific events
Metrics: Aggregate patterns
Traces: Correlated path
Audit: Business decision/action trail
```

Observe tool operations, state transitions, decision summaries, and evidence; private model chain-of-thought is not required. Shadow candidates must not duplicate real actions. Keep telemetry access and retention appropriate to sensitive data.

## 8. Enterprise Security — Module 16

| Hear… | Think… | Ask / say next | Module |
|---|---|---|---|
| “Logged-in user” | Authentication, then authorization | Which resource/operation is permitted? | 16 |
| “Roles differ” | RBAC + resource scope | Role-based access plus ownership and tenant checks | 16 |
| “Filter secrets after generation” | Weak boundary | Restricted evidence must stay out of context | 16 |
| “Agent needs credentials” | Least privilege / secrets | Trusted executor uses scoped secrets outside model context | 16 |
| “Shared enterprise platform” | End-to-end tenant isolation | Data, index, cache, state, jobs, logs, tools, results | 16 |
| “Data cannot leave this region” | Residency | Models, telemetry, backups, failover, tools | 16 |
| “Document/tool says ignore checks” | Untrusted data | Text cannot change authority | 16 |

**Distinguish:** authentication = who; authorization = allowed resource/operation; business policy = whether this action meets the rule; tenant fairness = shared-capacity allocation.

## 9. Trade-Offs and Interview Execution — Modules 17–18

| Hear… | Think… | Ask / say next | Module |
|---|---|---|---|
| “Critic adds latency and cost” | Marginal benefit | Critical-case improvement vs targets and simpler baseline | 17 |
| “Maximum recall, minimum latency” | Evidence/processing trade-off | Required quality, search/rerank, candidate budget | 17 |
| “Remove approvals for speed” | Hard constraint | Confirm customer policy; do not silently drop controls | 17 |
| “Why not something simpler?” | Requirement-based justification | Which gap needs this complexity, and what evidence supports it? | 17 |
| “Customer priority changed” | Revisit decision | New constraint, options, validation | 17 |
| “Design the whole system” | End-to-end execution | Discover → require → design → stress-test → ship/operate | 18 |
| “Walk one request” | Concrete flow | Identity, evidence, live data, state, authority, outcome | 18 |
| “What next?” | Validation plan | Open assumptions, success evidence, next measurement | 18 |

> “I’m choosing X because of requirement Y. The trade-off is Z. I’d verify it using W.”

## 10. Final 60-Second Recall

```text
Need AI?       → WHY + TODAY
What must do?  → FRs
How well?     → NFRs
Documents?    → Authorized RAG
Live state?   → API/tool
Dynamic steps?→ Bounded agent; otherwise workflow
Business write?→ Policy + approval if required + executor
More users?   → Workload + bottleneck + capacity/fairness
Slow?         → Critical-path trace
Expensive?    → Cost per successful task
Timeout write?→ Reconcile; preserve action identifier
Ready to ship?→ Evaluate + version + gate + scoped rollout
Why happened? → Observability or audit?
Restricted data?→ Enforce resource/tenant boundaries
Why this choice?→ Requirement + trade-off + verification
```

**Closing check:** every important box should have a customer requirement, a failure behavior, and a way to verify that it worked.
