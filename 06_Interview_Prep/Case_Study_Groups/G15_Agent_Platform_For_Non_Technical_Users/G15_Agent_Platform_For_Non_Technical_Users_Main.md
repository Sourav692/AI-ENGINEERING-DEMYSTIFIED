# G15 — Agent Platform for Non-Technical Users: Main Interview Guide

> **Full source:** [G15_Agent_Platform_For_Non_Technical_Users.md](G15_Agent_Platform_For_Non_Technical_Users.md), especially §§1–12 for the anchor and §13 for Cascade Robotics. Use the [Deep Dive](G15_Agent_Platform_For_Non_Technical_Users_Deep_Dive.md) for guardrail and recovery mechanics and the [Cheat Sheet](G15_Agent_Platform_For_Non_Technical_Users_Cheat_Sheet.md) for rehearsal.

## The anchor and its related case

The anchor asks for a multi-tenant platform where non-technical users configure workflows across channels that may reply, tag, escalate or issue a refund. The hard part is ensuring a real action is authorized, executed once and recoverable after a crash.

| Case | Shared foundation | What changes |
|---|---|---|
| #8 Agent platform whiteboard anchor | Canonical events, declarative specs, deterministic guardrails and durable runs | Explain the platform design and negative cases in 60 minutes. |
| #64 Cascade Robotics handbook/project | Same workflow engine and safety controls | Shows the $500 refund against a $50 cap, conflicting workflows, a runnable demo and implementation gaps. |

## Questions to ask the interviewer

| Ask | Design consequence |
|---|---|
| How non-technical is the author: forms, templates or plain-English creation? | Determines authoring surface and reviewable spec. |
| Which channels and who owns their integrations? | Defines adapters, threading and dedup behavior. |
| Are actions read-only, reversible or destructive? | Defines approval, spend and audit policy. |
| What is the blast radius of a bad workflow? | Sets default budgets and rollout gates. |
| Is multi-tenancy required from day one? | Makes tenant identity part of every event, spec, lock and policy. |

## Requirements and the $500 refund

**Functional:** normalize channels into a canonical event; choose one live workflow or a named non-selection; store versioned declarative workflows; validate typed tool arguments; checkpoint every step; deduplicate side effects; apply per-step guardrails; require role-checked promotion through draft, testing, shadow, live and autonomous stages.

**Non-functional:** tenant isolation, no unauthorized destructive action, actual-dollar spend caps, max steps and cost, crash recovery, idempotency under redelivery, one active run per target entity, audit of every allow/deny, and separation between author and approver. The source's deterministic demo has 21 tests and no LLM; it establishes the safety engine's behavior, not the safety of a future LLM planner.

Cascade Robotics wants small refunds without bothering a human. A **$500 refund** on a tenant with a **$50 cap** is refused, never clamped to $50. Even autonomous status cannot bypass that cap; `issue_refund` also needs a tenant allow-list entry or human approval. A retry cannot refund a second time.

## Architecture

The runtime is a fixed, versioned step list in the demonstrated system. A future LLM may propose a typed value or a draft workflow spec, but code controls routing, argument schema, policy, approval, execution and resumption. An LLM is not present in the source's runnable demo.

```mermaid
flowchart TB
  C[Email / Slack / chat / form / webhook] --> A[Channel adapters: canonical Event + tenant ID]
  A --> R[Route: live trigger + priority]
  R -->|no match| N[Named no-match reason]
  R --> L[Entity lock]
  L -->|held| H[entity_locked]
  L --> O[Checkpointed orchestrator: pinned spec]
  O --> V[Resolve + validate typed arguments]
  V -->|invalid| X[Halt with reason]
  V --> I[Action idempotency check]
  I -->|already applied| K[Checkpoint next step]
  I --> G[Deterministic guardrail: budget, cap, stage, allow-list / approval]
  G -->|deny| X
  G -->|approval needed| P[Pause for authorized human]
  P --> O
  G -->|allow| T[Scoped tool action]
  T --> K
  K -->|more steps| O
  K -->|done| D[Completed + run trace]
  W[Versioned workflow store / promotion] --> R
  Q[Tenant policy] --> G
```

### Step-by-step architecture

- Each channel adapter translates a payload once into an event carrying channel, type, tenant, target entity, payload and raw reference.
- Routing matches only that tenant's live workflow, chooses highest priority and returns a named reason if none matches; an entity lock prevents concurrent mutations of the same ticket.
- The orchestrator pins the workflow version and resumes at `next_step_index`, using the same loop for fresh and restarted runs.
- Before a step runs, it resolves values and validates the tool's typed schema. A model may supply proposed values, but cannot change the spec or tool signature in the demo.
- An action-level idempotency key is checked **before** authorization so a replayed side effect is a no-op and is not charged again.
- The guardrail checks the tighter workflow/tenant step and spend caps, shadow/live stage and destructive-tool allow-list or human approval. Deny wins; approval pauses safely.
- Only an allowed step calls the scoped tool. The orchestrator records the outcome, checkpoints, logs every decision and continues or finishes.

## Decisions an interviewer will probe

**Priority versus lock:** priority chooses which workflow *should* run; the lock prevents two from acting at once. They solve different problems. A draft workflow never matches a live event.

**Dollars versus compute cost:** a refund tool must check its real `amount_usd`, not the tiny operational fee for calling the tool. One source bug let $500 pass a $5 cap because it checked the wrong quantity. Another bug charged the cap again on replay even though the refund was deduplicated; moving the idempotency check before authorization fixed it.

**Ordered denial:** step budget → spend cap → shadow mode → not live → human approval if the destructive tool is not tenant-allow-listed. Workflow limits may tighten tenant policy but never loosen it. `AUTONOMOUS` raises which actions can skip approval; it never removes caps.

**Promotion:** `DRAFT → TESTING → SHADOW → LIVE → AUTONOMOUS`, one step at a time. An author cannot sign off their own workflow. Shadow mocks writes; live still needs human approval for actions that have not earned autonomous permission.

**Runaway cost:** measure cost per run and tenant, cap steps and model tokens, add tenant budgets and circuit breakers. Idempotency covers action effects *and* billing. Route deterministic events through rules and use a model only where judgment adds value.

## Rollout, scale and honest gaps

Start with one channel and one non-destructive workflow, then prove negative guardrail cases and staged promotion before enabling refunds. The demo's in-process locks and idempotency dicts are not shared across workers; production needs a distributed lock or database uniqueness and a durable shared idempotency store. The source also lacks a visual builder, natural-language-to-spec compiler, real LLM planner, automatic retry wrapper, secret vault integration, output PII redaction and gradual version migration. A compiled natural-language spec should land in `DRAFT` for review, never straight in `LIVE`.

## Two-minute interview answer

“I would separate what a non-technical user intends from what may safely execute. Each channel becomes one canonical, tenant-scoped event. Routing chooses the highest-priority live workflow, while an entity lock prevents concurrent actions. A versioned declarative spec drives one checkpointed execution loop. Arguments are typed and validated; action-level idempotency is checked before charging or authorization; then deterministic guardrails enforce step limits, the real dollar spend cap, rollout stage and human approval or a tenant allow-list. Only an allowed tool call runs, and every decision is logged. I would prove the $500 refund is refused under a $50 cap, a replay cannot refund twice, and a crash resumes from its checkpoint. The source demo does this without an LLM; a future planner would remain inside these same boundaries.”
