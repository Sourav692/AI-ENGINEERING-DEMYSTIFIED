# G02 — Customer Support Automation: Cheat Sheet

Use the [Main guide](G02_Customer_Support_Automation_Main.md) for the spoken answer and the [Deep Dive](G02_Customer_Support_Automation_Deep_Dive.md) for technical follow-ups. The [source case](G02_Customer_Support_Automation.md) remains the full reference.

## One sentence

**A support assistant is a routed decision pipeline: the model suggests, the policy gateway decides, and uncertain or risky work reaches a human with context.**

## Say the flow

**Channel → Verify identity → Classify intent/risk → Fetch approved policy + live facts → Draft/propose → Deterministic policy gate → Answer / approval / handoff → Audit.**

**LLM/agent role:** Rules or a small model route; the LLM drafts; a bounded support-agent planner handles multi-system cases. The policy gateway decides whether any tool action runs.

## Five rules

1. Verify identity before account data or account tools.
2. Confidence is not permission; the gateway checks allowlist, threshold, freshness, and approval.
3. Billing, orders, CRM, and identity remain systems of record.
4. Every write is idempotent; reconcile an uncertain side effect before retry.
5. Optimize **safe resolution**, not raw deflection.

## Requirements to recall

**Functional:** route by intent and risk; retrieve grounded facts; draft; gate actions; hand off fully; audit outcomes.

**Non-functional:** routine p95 <3 s, ambiguous <8 s, high-risk handoff <15 s in the source example; secure account access; safe degradation; immutable audit; cost per resolved case.

**Illustrative load:** 2M tickets/month, 100 QPS peak, 20 languages. Under the source’s traffic and call-count assumptions: ~4.2M model calls/month and ~2.2M–2.4M retrieval calls/month.

## Action table

| Case | Default |
|---|---|
| FAQ | Approved, versioned evidence or safe cache; queue if weak. |
| Order status | Identity as needed, current order lookup. |
| Refund/address/payment change | Live facts + assurance + gateway; human approval over threshold. |
| Legal/safety/conflicting evidence | Human handoff. |
| Identity failure | No account tools. |
| Possible side effect + timeout | Pending reconciliation; never blind retry. |

## Handoff payload

Original message + identity status + intent/risk + evidence + policy checks + tool outputs/errors + attempted actions + **why automation stopped**.

## Failures to rehearse

- Wrong policy answer: stop delivery, preserve evidence and versions, hand off, add regression.
- Billing lookup timeout: block action, hand off with missing-fact reason.
- Refund timeout: inspect action record/ledger before doing anything again.
- Model or language route outage: narrow safe path or human queue.

## Release and rollout

**Gate:** representative QA, correct fallback, complete logging, stable retrieval, exercised rollback. Track safe automation, incorrect resolutions, first-contact resolution, repeat contact, CSAT, p95, and cost per resolved case.

**Sequence:** agent-assist → narrow reversible intents → one tool class at a time → canary and sample → kill switch per intent/tool.

## Variants

- **Multi-tenant:** tenant predicate on every retrieval and tool call; zero ACL red-team violations.
- **ServiceNow:** priority/assignment + approved KB/CMDB context; configuration changes through existing ITIL process.
- **Complex agent:** planner only for multi-system requests; direct path for simple lookups.

## Cost answer

**Measure by intent → route by risk → bound calls, steps, tokens, and retrieval → cache safe FAQ traffic.** Keep account facts live. Check `time saved − model/retrieval cost − wrong-resolution cost − recontact cost`.

## Interview triggers

| Asked | Answer |
|---|---|
| “The model is confident.” | Confidence never overrides policy or missing facts. |
| “80% autonomy?” | Define resolved-without-recontact; expand only where intent-level safety holds. |
| “Why a human?” | The handoff carries evidence, attempted actions, and the stop reason. |
| “What first?” | High-volume, low-harm, reversible intent. |

**Close:** Reduce handling time without increasing harmful mistakes; prove it with a gated rollout and customer outcomes.
