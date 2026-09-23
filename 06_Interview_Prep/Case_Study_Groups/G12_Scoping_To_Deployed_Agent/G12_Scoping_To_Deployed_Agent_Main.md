# G12 — Scoping to Deployed Agent: Main Interview Guide

> **Source:** [G12_Scoping_To_Deployed_Agent.md](G12_Scoping_To_Deployed_Agent.md). The [Deep Dive](G12_Scoping_To_Deployed_Agent_Deep_Dive.md) covers gate mechanics and limitations; the [Cheat Sheet](G12_Scoping_To_Deployed_Agent_Cheat_Sheet.md) is for rehearsal.

## The case in one sentence

Turn a customer request into a governed, two-week agent deployment with measurable value, named approvers, evidence-backed gates, a working rollback and a clear owner. The source demonstrates this with a Northwind support-triage agent; its day-14 numbers are scripted demo results, not live production evidence.

## Questions to ask the interviewer

| Ask | Design consequence |
|---|---|
| What customer outcome and baseline define success by week four? | Prevents a build with no measurable value. |
| Who is the sponsor, subject-matter expert and go/no-go owner? | Assigns approvals and escalation. |
| Which data sources, credentials and policies are available now? | Determines whether the two-week plan is feasible. |
| Which accelerator parts can be reused, and what is bespoke? | Controls delivery time and future maintenance. |
| What happens when a gate fails or an SME misses a deadline? | Defines no-go, escalation and schedule impact. |
| Which agent actions require human review, and how is rollback tested? | Sets production autonomy and containment. |

Do not start the engagement clock without measurable success metrics, a named SME and named sources. The source uses those as intake requirements.

## Requirements

**Functional delivery requirements:** intake and scope; evidence-backed security and data access; configured agent; signed golden set; baseline evaluation; shadow run; tested rollback; limited production; sponsor decision; runbook, dashboard and owner handover. Each stage advances only after its own gate, with authorized role and evidence recorded.

**Non-functional delivery requirements:** two-week target, auditability, separation of duties, reusable accelerators, tenant isolation, secure credentials, reliable escalations, rollback under two minutes in the demo, and measurable first value. A failed gate must stop advancement, not become an undocumented exception.

**Northwind agent requirements:** triage the top three Zendesk ticket categories, use Confluence knowledge and Salesforce read-only context, redact sensitive data, draft grounded replies, apply escalation rules, and keep people in control of sending while autonomy is earned. The demo target is first response under five minutes and at least 60% zero-edit sends by week four.

## Architecture: delivery gates and the deployed agent

The delivery state machine is deterministic; an LLM does not approve its own release. Within the delivered support agent, model calls can classify and draft replies. The latter architecture is a source-grounded design sketch, not a claim that every runtime component was implemented in the source demo.

```mermaid
flowchart TB
  subgraph Delivery[Two-week delivery control plane]
    I[Intake: outcome + SME + sources] --> S[Security review]
    S --> D[Data access]
    D --> C[Configure / signed golden set]
    C --> E[Baseline evaluation]
    E --> H[Shadow / rollback test]
    H --> L[Limited production / success metrics]
    L --> G[Sponsor go / no-go + handover]
  end
  subgraph Agent[Northwind support agent runtime]
    Z[Zendesk ticket] --> P[PII redaction]
    P --> T[LLM classification / top 3 routes]
    T --> R[Confluence KB + Salesforce read-only retrieval]
    R --> M[LLM grounded reply draft]
    M --> V[Grounding + escalation checks]
    V --> A[Human approval / Zendesk send]
    A --> O[Quality + latency telemetry]
  end
  E -. evaluates .-> Agent
  H -. shadows .-> Agent
  L -. controls rollout .-> Agent
```

### Step-by-step architecture

1. Intake records target outcome, baseline, sponsor, SME and data sources; incomplete intake does not start the delivery clock.
2. Security and data-access reviewers sign their own gates with evidence before the agent touches customer data.
3. The team pulls reusable connectors, prompts, evals and dashboards, then builds only the customer-specific escalation policy; the SME signs the golden set.
4. A baseline evaluation tests quality and safety. Shadow mode compares agent behavior without granting unrestricted sending, and the team proves rollback.
5. Limited production measures agreed success metrics. The sponsor makes the day-14 go/no-go decision; the team hands over a runbook, dashboard, owner and credentials plan.
6. At runtime, a Zendesk ticket is redacted, classified by a model, enriched with scoped KB/CRM context, drafted by an LLM, checked for grounding and escalation, and sent only under the chosen human approval policy.

## Gates, evidence and ownership

| Stage | Source gate | Signer |
|---|---|---|
| Scoping, days 1–2 | `security_review_passed` | Security reviewer |
| Data readiness, days 3–4 | `data_access_granted` | Customer SME; pending access escalates on day 3 |
| Configure, days 5–7 | `golden_set_signed_off` | Customer SME |
| Evaluate, days 8–9 | `eval_baseline_met` | FDE |
| Shadow, days 10–11 | `rollback_tested` | FDE |
| Limited production, days 12–13 | `success_metrics_met` | Sponsor |
| Day 14 | Go/no-go and handover | Named decision owner |

The gate API should reject wrong roles, missing evidence and skipped prior stages; deny decisions override optimistic state and every attempt is logged. Free-text evidence is weak: require structured checklist items and links to evaluation or rollback proof. A no-go is a valid outcome.

## Trade-offs, cost and honest limits

Northwind reuses five of six accelerator components (about 83%); the bespoke part is escalation policy. The demonstration reports 4m12s first response, 63% zero-edit sends, .83 evaluation score against .75 baseline, and rollback under two minutes. Week-four retention was not observed; `None` does not mean zero. The source's deterministic gate demo has 17 tests but does not implement full agent provisioning, eval-harness wiring, scope-change approval, versioned rollback or multi-engagement operations. State those gaps plainly in the interview.

For cost, agree on cost per resolved ticket at intake; bound model steps and tokens, reuse common connectors, and sample evaluation proportionally to risk. Keep customer credentials in a vault with scoped access and revoke or transfer them at handover. Record tenant boundaries and override rate. A low-cost pilot that fails its outcome metric is not success.

## Evaluation and rollout

Golden tickets must cover the top categories, retrieval misses, PII, policy escalations and cases where a draft should not be sent. Measure response time, zero-edit sends, groundedness, escalation correctness, human overrides, rollback time, cost per resolved ticket and week-four retention when it actually exists. Shadow before limited production; refuse broad rollout until sponsor-approved metrics and rollback evidence hold.

## Two-minute interview answer

“I start with a measurable business result, a named SME and real data sources; without those, the two-week clock is fiction. I run seven gated stages from scoping and security through data access, configuration, evaluation, shadow, limited production and sponsor go/no-go. Each gate needs evidence from the right owner and cannot be skipped. For the support-triage agent, a ticket is redacted, classified, enriched from read-only knowledge and CRM, drafted by an LLM, checked for grounding and escalation, then human-approved as needed. I reuse standard components, measure first response and zero-edit sends, prove rollback, and hand over ownership. If a gate fails, I stop or escalate rather than calling an unverified demo deployed.”
