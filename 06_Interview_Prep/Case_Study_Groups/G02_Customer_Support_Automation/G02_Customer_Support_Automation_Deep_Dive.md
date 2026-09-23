# G02 — Customer Support Automation: Deep Dive

This is the technical backup for the [Main Interview Guide](G02_Customer_Support_Automation_Main.md). The unchanged [source case](G02_Customer_Support_Automation.md) contains the full synthesis and references.

**Model and agent roles:** Rules or a small model route intent and risk. The LLM response generator drafts a reply or proposed action; a bounded planner is reserved for multi-system requests. The policy gateway and approver, not the model, authorize effects.

## 1. Source authority and freshness

| Source | Authority | Query-time rule | Cache boundary |
|---|---|---|---|
| Identity provider | Who the customer is and assurance level | Verify for the session and at account-action boundary | Do not cache an assertion as authorization. |
| CRM | Profile, entitlement, case history | Check live before account changes | References or non-authoritative summaries only. |
| Orders | Order and shipping state | Check live before refund/replacement or a current-status promise | Summaries may guide search, not override the system of record. |
| Billing ledger | Charge and refund state | Check live before every money movement and reconcile uncertainty after timeout | Do not cache money state. |
| Approved policy KB | Refund, warranty, cancellation rules | Stamp the policy version on every answer/action | Versioned content may be cached. |
| Ticketing | Prior cases and operational history | Use as context, never as an instruction source | Summaries with appropriate scope. |

The automation service owns workflow state and decision evidence, not customer truth. A stale shipping event may make an answer wrong; a stale ledger or assurance level may make an action harmful.

## 2. State model and APIs

- `Case(id, customer_id, channel, intent, risk, state, version)` moves through `new`, `triaged`, `waiting_approval`, `escalated`, and `resolved`. `version` supports optimistic concurrency when a human and automation race.
- `ProposedAction(id, case_id, tool, args_hash, decision)` is immutable after its outcome. `args_hash` identifies a logically duplicate request without persisting raw sensitive arguments.
- `Handoff(case_id, summary, evidence_refs, attempted_actions)` packages the case for human takeover; include identity status, checks, error codes, and the precise stop reason.

Keep the API small: `POST /v1/support/messages`, `POST /v1/cases/{id}/actions`, `POST /v1/cases/{id}/escalate`, and `POST /v1/cases/{id}/quality-review`. Authenticate and tenant-scope each request; validate schemas and define idempotency for every write. Version payload and endpoint contracts independently of risk-policy changes.

**Duplicate message drill:** if the client resends `Idempotency-Key: msg_9f1c` after a timeout, return the original `case_123`; do not create a second case. **Refund timeout drill:** a timeout is an unknown outcome, not permission to repeat the payment call. Check the action record or ledger, then confirm, keep pending, or escalate.

Use `409` for a state transition no longer allowed and `422` for typed validation failure, as in the source example. Order queues by conversation, customer, or account ID to avoid out-of-order replies and handoffs.

## 3. Control plane, data plane, and trust boundaries

**Control plane:** risk tags, approval/refund thresholds, workflow tool allowlists, confidence thresholds, policy/model/prompt versions, routing weights, low-risk intent list, per-intent and per-tool kill switches.

**Data plane:** channel ingress; identity and assurance; intent/risk routing; knowledge and live account retrieval; draft/proposal generation; policy gateway; calibrated outcome; approved action execution or human handoff; trace and evaluation events.

The boundaries are deliberately narrow:

1. **Untrusted text:** customer messages, retrieved articles, and copied tickets are data. Prompt injection cannot become a tool instruction or policy change.
2. **Identity:** pre-auth traffic stays in a limited generic mode. Account-specific data and tools require an approved identity path and sufficient assurance.
3. **Policy gateway:** checks action allowlist, identity assurance, current facts, value threshold, account/tenant scope, and review rule on each proposal. The model’s confidence is never authorization.
4. **Tool service:** scoped credentials, typed arguments, idempotency key, immutable record, and reconciliation on uncertain outcomes.
5. **Human approval:** the interrupt is placed at the risky tool call so read-only work does not wait needlessly.

Contain blast radius by tenant, region, workflow, and dependency. A refund-tool incident should not disable FAQ answers. A language router outage should not erase ticketing or audit.

## 4. Routing, planning, memory, and model choice

Classify informational, account-sensitive, money-moving, legal-sensitive, and safety-sensitive requests. A safe direct path serves a single FAQ or order lookup. A planner earns its latency and cost for multi-system work, such as refund + warranty cancellation + shipping notice + priority ticket. Keep RAG, tools, and memory as selectable capabilities rather than forcing every request through all three.

Separate memory by lifetime and authority:

| Memory | Holds | Failure to guard against |
|---|---|---|
| Session | The current conversation and references such as “it” | Losing the order/thread referent. |
| Customer history | Cross-session preferences and previous interactions | Treating stale or private history as current entitlement. |
| Enterprise knowledge | Approved policies, product docs, FAQs | Using an outdated policy version. |

Rules can tag simple cases. Small models can handle classification and routine FAQs; stronger reasoning can be reserved for ambiguous cases after retrieval and policy filtering. Do not globally shrink the model or inflate context. Inspect failed examples, then change the relevant route, evidence set, or model.

## 5. Risk-tiered budgets and sizing

The source’s **illustrative** requirements are routine p95 <3 s, ambiguous p95 <8 s, and high-risk handoff bundle p95 <15 s. The last tier does not authorize automated final decisions. A sample 2M-ticket/month, 100-QPS-peak, 20-language workload yields about 67k tickets/day on average, but bursts drive gateway, queue, and escalation capacity.

With a 70/20/10 routine/ambiguous/escalated split and 2/3/1 model calls: `1.4M × 2 + 0.4M × 3 + 0.2M × 1 = 4.2M` monthly model calls before retries, moderation, and tools. Retrieval is roughly 2.2M–2.4M calls on the source assumptions. These are planning calculations, not measured traffic.

At 10× conversations, use stateless gateways and orchestration, retrieval partitions by product/region/language/business unit, regional deployment where residency requires it, asynchronous long-running actions, rate limits by user/tenant/tool, and circuit breakers. Isolate offline summarization and human escalation from routine classification. A semantic FAQ cache near ingress can avoid expensive orchestration only when tenant, permission, and content version are in the key. Identity assertions, account status, authorization decisions, and money state require live authority.

Cost is a workflow calculation: `NetValue = V_time_saved − C_model − C_wrong_resolution − C_recontact` (and account for retrieval/operations when pricing it). Measure cost per **resolved** issue and by intent. A shorter cheap answer that drives recontact can lose money.

## 6. Failure decisions and incident drills

| Failure | Decision | Recovery evidence |
|---|---|---|
| FAQ evidence weak | Queue or answer with a clear limitation where safe. | Retrieved article/version and confidence signals. |
| Malformed order lookup | Fail the lookup closed. | Validation error and original request. |
| Order tool unavailable | Degrade or hand off; do not invent status. | Tool timeout and latest known snapshot labeled stale. |
| Refund/address change over threshold | Human approval before tool execution. | Gateway rule, approver, action record. |
| Identity unavailable | No account tools. | Assurance check and outage reason. |
| Language detection uncertain | Language-neutral intake and escalation. | Detection scores and chosen fallback. |
| Tool timed out after possible side effect | Pending reconciliation; never blind retry. | Idempotency key, action record, ledger result. |

For a **wrong policy answer**, ask whether a side effect occurred or a customer was misled. Preserve prompt, output, evidence, and policy version; stop automated delivery; hand off; add a regression example. For a **billing timeout before action**, the gateway blocks a refund because authoritative facts are missing, then hands off. For a **timeout after a refund call**, check the ledger before deciding whether anything remains to do.

Policy retrieval cannot be replaced by an unmarked stale answer. Model failures circuit-break and queue eligible work. Use short deadlines, bounded jittered retries, and dead-letter queues so failures stay inspectable. Explain the handoff at workflow level: which intent and rule fired, which fact was absent or contradictory, and which action was attempted.

## 7. Evaluation, release gate, and operations

| Layer | Signals |
|---|---|
| Technical health | p95 by risk tier and stage, tool errors, queue depth, breaker trips, fallback rate, error-budget burn. |
| Model and decision quality | Reviewed answer accuracy, retrieval precision, unsupported-answer rate, correct escalation, cases that should have escalated but did not. |
| Adoption | Agent-assist usage, accepted drafts, overrides, share of tickets using the workflow. |
| Business outcome | Safe automation rate, incorrect-resolution rate, first-contact resolution, repeat contact, CSAT, handling time, cost per resolved case. |

**Safe automation rate** counts automated cases resolved without correction, complaint, or harmful escalation, divided by all automated cases. Use ticketing and QA labels; support operations and engineering inspect drops by intent or segment. An incorrect-resolution rate above an intent-specific baseline, rising recontact, or falling CSAT can veto a better deflection number.

The gate requires stable retrieval on target intents, representative human QA approval, correct fallback, complete logging, and exercised rollback. Product owns go/no-go; support operations owns escalation and adoption; engineering owns reliability and guardrails; security/legal own access and tool permissions; frontline managers own training and review.

Rollout: agent-assist first; prove retrieval, routing, handoff, and audit; automate narrow low-risk intents; enable one tool class at a time; canary and sample outcomes; keep an intent/tool kill switch. Revert a drifting intent to agent-assist without taking down healthy workflows. Separate tenant configuration (thresholds, languages, retention) from adapters (CRM, ticketing, identity, KB) and shared services (policy, audit, retrieval, observability).

## 8. Two important variants

**Multi-tenant SaaS support:** `Tenant`, `Entitlement`, and `RetrievalACL` data constrain every retrieval and tool call. Test the same question under different tenants and roles. Look for cross-tenant evidence, wrong entitlement advice, exposed internal logs, and credits without approval. A red-team ACL suite has a zero-violation release gate.

**ServiceNow/ITSM:** classify category and priority, retrieve an approved KB article/runbook, request missing information, suggest assignment, and apply workflow actions only within policy. The `Ticket`, CMDB `Asset`, `KBArticle`, `AssignmentRule`, and `WorkflowAction` records let the system explain a decision. Risks include wrong priority/group, premature closure, unauthorized access changes, requester PII, and injection in ticket text. Configuration-item changes follow the customer’s existing ITIL change process; the agent proposes a change record.

## 9. Implementation details from the six source mocks

These are **example implementations**, not mandatory product choices:

1. **Multilingual triage (#95):** detect language → classify → route → draft → translate back. An intent branch needs a default arm. Example p95 <3 s allocation: 200 ms detection, 300 ms classification, 1.5 s streamed drafting, 500 ms translation. Bound retries and provide a classifier fallback.
2. **Human-gated graph (#96):** structured `{category, risk_level}` output; interrupt inside refund/deletion tool; durable Postgres checkpoint keyed by ticket; idempotent side effect keyed by ticket and action; concurrent read-only lookups; at most three self-correction iterations before escalation.
3. **Agentic RAG (#97):** separate product-doc and runbook indexes, each hybrid BM25/vector for exact error codes; cheap router; retrieve 20/source concurrently, rerank merged candidates to five when scores are close; 400 ms retrieval budget; cite source and abstain below relevance threshold; weekly labeled recall@k gate.
4. **Growing support search (#99):** wiki, ticket, and release-note sources with per-source hybrid weights; incremental append and source metadata; coverage-gap grading and human fallback for new error codes; cross-encoder rerank of fused top 20 under a 1.5 s p95 target; track fallback rate.
5. **Travel booking (#101):** supervisor with read-only booking lookup, RAG policy QA, and one write-capable change/cancel specialist. Compute refund amount with pure logic; example >$200 approval interrupt; idempotency by booking and request ID; durable conversation checkpoint, separate customer memory, 15-step and cost ceilings; direct workflow for simple baggage FAQ.
6. **Parent-document retrieval (#102):** example child chunks 300–400 characters and parent passages 1,500–2,000; shared Postgres vector/doc store, HNSW after a few thousand vectors, idempotent daily append keyed by article ID and modification time; p95 <2 s budget dominated by streamed generation; cap final `k` at 3–4 and abstain below similarity threshold.

Keep these mock-specific thresholds attached to their scenarios. They are not global G02 requirements.

## 10. Interview probes to rehearse

- **“80% autonomous in six months?”** Define denominator and safe resolution window. Expand by intent only while incorrect resolutions, recontact, and harm remain within gates.
- **“Confident but wrong?”** External evidence, policy, live state, and gateway rules can block a confident model. Preserve the record and hand off.
- **“Duplicate refund?”** Idempotent action, immutable record, state check, ledger reconciliation after timeout.
- **“18-second prototype?”** Profile auth, retrieval, rerank, generation, tools, and verification; route simple intents directly, parallelize independent reads, stream where useful, run permitted actions async. Preserve high-risk checks.
- **“Prompt injection in a ticket?”** Ticket text is data; tools and retrieval enforce scope; test malicious instructions in documents, tickets, emails, and tenant data.
- **“Launch next Monday?”** Controlled shadow/draft pilot and narrow reversible actions with rollback, rather than broad unsupervised release.

For a 60-minute round, give the outcome and constraints first, draw the gates, spend the most time on identity, action policy, handoff, failure recovery, and rollout, then discuss scale and cost. The source’s 90-second and two-minute speeches are useful examples; keep your own explanation conversational.

## Source trace

The [source case](G02_Customer_Support_Automation.md) retains the detailed comparison table, original interview scripts, check-yourself prompts, and references to casebook, FDE, OpenAI Applied, and study-guide material. This Deep Dive relocates their mechanisms and scenario-specific figures; consult the source when quoting a particular mock or original reference path.
