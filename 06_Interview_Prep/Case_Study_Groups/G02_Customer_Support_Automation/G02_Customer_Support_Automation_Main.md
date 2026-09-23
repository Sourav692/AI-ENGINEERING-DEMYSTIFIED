# G02 — Customer Support Automation: Main Interview Guide

> **Core idea:** Build a routed decision pipeline that knows when to answer, when to ask for approval, and when to hand off. The model can draft and recommend; verified identity and a deterministic policy gateway decide whether an account action may happen.

The unchanged [source case](G02_Customer_Support_Automation.md) is the full reference. Use this guide for the spoken design, the [Deep Dive](G02_Customer_Support_Automation_Deep_Dive.md) for follow-ups, and the [Cheat Sheet](G02_Customer_Support_Automation_Cheat_Sheet.md) for last-minute recall.

## 1. Open with the risk

> “I want to reduce handling time and cost without increasing incorrect or harmful resolutions. I’ll identify which requests can be answered, which need approval, and which need a human. Then I’ll design the identity, policy, action, and handoff boundaries around those decisions.”

Use a double-charge request as the running example. A fluent reply is not enough: the system must verify the customer, check live billing facts, apply the refund policy, avoid a duplicate refund, and hand off cleanly if anything is uncertain.

Ask early about six areas: **channels and peak volume; permitted actions and approval thresholds; identity and sensitive data; source freshness; human escalation; languages.** Ask which legal, financial, or safety categories remain human-reviewed. If the interviewer gives no numbers, state assumptions and keep money-moving and account-changing actions gated.

### G02 is the anchor for its support-automation variants

Learn the shared decision pipeline here, then change the boundary that dominates each variant.

| Related case | What changes from G02 |
|---|---|
| Customer Support Assistant at 1M conversations/day | Planner only for multi-system requests; three distinct memory layers; model routing and large-scale serving. |
| Multi-Tenant SaaS Support Assistant | Add a tenant predicate to every retrieval and tool call; test for cross-tenant leakage. |
| ServiceNow Ticket Automation Agent | Classify, prioritize, assign, and request missing details; obey the existing ITIL change process. |
| Agentic Support Workflow / customer-support interview mocks | Probe handoff quality, wrong refunds, stale facts, confidence, rollout, and the requested automation target. |
| Study-guide implementations | Show how branches, interrupts, retrieval, durable state, and specialist tools implement the same control boundaries. |

## 2. Requirements and scope

### Functional requirements — what it must do

1. Normalize chat, email, web, or voice transcripts into one case envelope.
2. Classify the request by intent and risk before choosing an answer or action path.
3. Verify identity before accessing account data or invoking account tools.
4. Retrieve approved policy and current customer/order facts; draft an evidence-backed response.
5. Run proposed actions through authorization, validation, freshness, threshold, and approval checks.
6. Escalate with the full conversation, evidence, attempted actions, and the reason automation stopped.
7. Record decisions, tool calls, human overrides, and outcomes for audit and learning.

### Non-functional requirements — how well it must do it

| Constraint | Example from the source case |
|---|---|
| Latency | Routine p95 <3 s; ambiguous p95 <8 s; high-risk handoff bundle p95 <15 s. The high-risk final decision remains human. |
| Availability | At the illustrative 2M tickets/month and 100 QPS peak, routing and escalation keep accepting work while optional enrichment is shed. |
| Security | Customer text stays untrusted; tools are scoped per workflow; identity is checked before account access. |
| Reliability | Timeouts and incomplete facts lead to a safe handoff; possible side effects are reconciled before retry. |
| Auditability | Preserve actor, model/tool/policy versions, validated fields, decision, and override in an immutable trail. |
| Cost and outcome | Optimize net value per resolved case, including wrong resolutions and repeat contacts, rather than raw deflection. |

**First-release exclusions:** autonomous legal complaints, open-ended negotiation, unsupervised refunds or cancellations, cross-system repair without review, and ambiguous proactive outreach.

## 3. Architecture you can draw

```text
Channel gateway → Identity/assurance → Intent + risk router
             → Approved policy + live account facts → Draft / proposed action
             → Deterministic tool policy gateway → Decision
                                                ├─ Answer / safe auto-resolve
                                                ├─ Human approval → scoped action tool
                                                └─ Handoff with context + reason

Control plane: risk tags, thresholds, tool allowlists, policy/model versions,
               routing rules, per-intent and per-tool kill switches.
Every stage: trace, outcome, latency, cost, audit event.
```

**Three boundaries to point at:**

- **Identity:** pre-auth FAQ can use a limited generic mode; account tools require verified assurance.
- **Authorization:** the model proposes; the tool policy gateway checks identity, allowed action, thresholds, freshness, and human approval. Confidence never grants permission.
- **Sync/async:** accept and route promptly; run permitted longer actions in the background with status and reconciliation.

The automation layer owns the **case workflow and evidence of its decisions**. CRM, identity, order, and billing systems remain authoritative for customer facts and money. Policy articles are versioned; live account or billing state is fetched before an action.

## 4. Decide what can happen

| Request | Path |
|---|---|
| Public FAQ | Retrieve approved policy or use a safe versioned cache; answer or queue if evidence is weak. |
| Order status | Verify identity if account-specific; fetch current order status; answer only from the returned facts. |
| Refund, cancellation, address or payment change | Check live facts and assurance; gateway applies allowlist and threshold; require approval where policy says so. |
| Legal/safety issue, unclear language, conflicting evidence | Escalate with reason codes and context. |
| Tool timeout after an action may have executed | Mark pending, inspect action record or ledger, then confirm, continue waiting, or escalate. Never blindly repeat it. |

Use a planner only when the request truly spans systems, such as refunding an order, cancelling a warranty, notifying shipping, and creating a ticket. A simple “track my order” request should take the direct lookup path. Keep session context, cross-session customer history, and enterprise knowledge as separate memory layers; they have different freshness and privacy rules.

## 5. Make actions and handoffs reliable

Keep a versioned `Case`, an immutable `ProposedAction`, and a `Handoff`. Every write boundary needs an idempotency key; the action record can use an argument hash to recognize a duplicate without storing raw sensitive arguments. Check `Case.version` so automation cannot overwrite a human’s newer decision. A duplicate customer message should return the existing case, not create a second one.

A useful handoff contains: original message; identity status; parsed intent and risk; retrieved evidence; policy checks; tool outputs and error codes; attempted or pending actions; and the exact reason automation stopped. Prioritize the human queue by risk and impact. A transcript alone makes the agent repeat work and hides the failed control.

## 6. Failure playbook

- **Identity unavailable:** account tools fail closed; offer only limited generic help or escalate.
- **Policy retrieval unavailable or stale:** do not present a superseded rule as current; withhold the commitment and hand off.
- **Billing lookup times out:** block the refund because facts are incomplete; attach the failure and conversation to the handoff.
- **Refund response times out:** treat execution as uncertain; reconcile against the ledger/action record before any retry.
- **Model endpoint fails:** circuit-break, queue eligible work, and route risky cases to humans.
- **Language detection fails:** use a language-neutral intake and escalate when uncertain.
- **Confident but wrong policy answer:** stop automated delivery, preserve prompt/output/policy version, hand off, and add a regression case.

Retries are bounded and jittered, failed jobs remain inspectable, and timeouts never convert a blocked action into an allowed one.

## 7. Scale, latency, and cost

The source’s sizing exercise assumes **2M tickets/month, 100 QPS peak, and 20 languages**. With an illustrative 70% routine / 20% ambiguous / 10% escalated mix and 2 / 3 / 1 model calls respectively, that is about **4.2M model calls/month**, before retries and moderation. The same assumptions imply roughly **2.2M–2.4M retrieval calls/month**. Treat these as interview assumptions, not measured production demand.

| Pressure | Design response |
|---|---|
| Peak QPS or incident burst | Stateless gateway/router, ordered queues by customer or case, rate limits per user/tenant/tool, circuit breakers, shed optional enrichment. |
| Latency | Budget by risk tier; direct lookup for simple work, bounded retrieval/context, selective reasoning, streaming for perceived speed, background actions where allowed. |
| Freshness | Cache approved policy by version and safe FAQ answers by tenant/permission/version; fetch live identity, money, account status, and authorization. |
| Cost | Trace spend by intent; use rules or a small model for classification/FAQ, a stronger model for ambiguous or high-risk synthesis, and a planner only for multi-system work. |
| Growth toward 10M conversations/day | Partition retrieval by product/region/language/business unit, isolate escalation and offline work, regionalize for residency, and scale stateless services independently. |

The business check is **NetValue = time saved − model/retrieval cost − wrong-resolution cost − repeat-contact cost**. Lower model spend is not a win if it creates expensive recontacts.

## 8. Evaluation and release

**Safe automation rate** means automated cases resolved without correction, complaint, or harmful escalation divided by automated cases. Read it beside incorrect-resolution rate, first-contact resolution, repeat contact, CSAT, handling time, and cost per resolved case. Deflection alone only tells you that work moved.

Use four views: technical health (latency, tools, queues, fallback); model quality (grounding, retrieval, escalation correctness, unsupported answers); adoption (agent use, acceptance, overrides); business outcome (resolution, CSAT, recontact, cost). Segment by intent, language, and customer group. A falling handle time with rising repeat contact signals rework, not improvement.

Before launch, require stable retrieval on target intents, representative human QA approval, correct fallbacks, complete logging, and an exercised rollback path. Support operations owns escalation and adoption; engineering owns reliability and guardrails; product owns the gate; security/legal own access and action permissions.

## 9. Roll out by intent and tool class

1. **Agent-assist:** draft and summarize; a human sends every reply.
2. **Prove the controls:** use real traffic and historical tickets to validate retrieval, risk routing, handoff completeness, and audit.
3. **Narrow automation:** enable high-volume, low-harm, reversible intents such as order status or shipping ETA.
4. **Add one tool class at a time:** ticket tagging, read-only lookup, then increasingly sensitive actions with explicit approval gates.
5. **Canary and review:** sample automated outcomes; keep a kill switch per intent and per tool; roll back the drifting slice.

When asked for “80% autonomy in six months,” first ask **80% of what**—tickets, intents, or cases resolved without recontact? Let safe automation and repeat-contact results determine expansion, especially for money-moving and legal requests.

## 10. Variants and implementation hooks

- **Multi-tenant SaaS:** carry tenant identity through retrieval, tools, cache, and logs; test the same question as users from different tenants. Release gate: zero permission violations in the tenant ACL red-team suite.
- **ServiceNow/ITSM:** classify priority and assignment from ticket, asset/CMDB, and approved knowledge data. Propose configuration changes through the customer’s ITIL change process; do not bypass it.
- **Multilingual:** language detection needs a default path; do not silently drop an unknown language.
- **Framework details:** durable approval interrupts belong at the risky tool, not the start of the turn; bounded retries and agent steps prevent loops; hybrid retrieval and source-specific indexes protect exact IDs and error codes. See the Deep Dive for the source’s six concrete mock designs.

## 11. Interview delivery

Spend the hour roughly as follows: opening and requirements (10 min), architecture and control boundaries (15), action safety/handoff/failure drill (15), evaluation and rollout (10), scale/cost/variants and close (10).

**90-second answer:**

> “I would design support automation as a routed decision pipeline. The gateway normalizes the message, identity verification establishes what account data and tools are available, and an intent router tags risk. Approved policy and current account facts ground a draft or proposed action. A deterministic gateway checks authorization, freshness, thresholds, and whether a human must approve; the model cannot grant itself permission. Simple, low-risk requests can be answered quickly. Money-moving or ambiguous cases go to an agent with evidence, attempted actions, and a reason. Every write is idempotent, and an uncertain side effect is reconciled before retry. I’d launch in agent-assist, then automate narrow reversible intents, adding tools one class at a time with per-intent rollback. I’d judge it by safe automation, incorrect resolutions, repeat contact, CSAT, latency, and cost per resolved case.”

### Interviewer trigger → short answer

| Asked | Say |
|---|---|
| Why not a general chatbot? | It must decide whether to answer, approve, act, or hand off. |
| Model is confident? | Confidence helps routing; the gateway still enforces action permission. |
| Duplicate refund? | Idempotency, immutable action record, ledger reconciliation after timeout. |
| Human takeover? | Structured handoff with evidence, attempted actions, and reason. |
| What to automate first? | High-volume, low-harm, stable, reversible intents. |
| What proves success? | Safe automation and customer outcomes, not deflection alone. |
| Cost spike? | Measure by intent, route, bound work, cache safe FAQ answers. |

**Final mental model:** Verify → Classify risk → Fetch authoritative facts → Draft → Policy gate → Answer / approve / hand off → Audit and learn.
