# G03 — Tool-Using Agent with Safety Controls: Cheat Sheet

Use the [Main guide](/modules/15-fde-case-studies/agents-that-act/tool-using-agent-with-safety-controls#main) to practice speaking and the [Deep Dive](/modules/15-fde-case-studies/agents-that-act/tool-using-agent-with-safety-controls#deep-dive) for mechanisms. The [source](/modules/15-fde-case-studies/agents-that-act/tool-using-agent-with-safety-controls#full-pack) is the full reference.

## One sentence

**The model proposes; deterministic systems decide; the idempotent gateway executes once and records a receipt.**

## Flow

**Authenticate → bounded proposal → registered typed tool → validate → policy: allow/block/approve → scoped token → idempotent gateway → system of record → receipt/audit → continue or stop.**

**LLM/agent role:** The agent's LLM planner proposes one bounded tool call; policy, approval, and the gateway control execution.

## Ask first

Actions reversible? Money boundary? Delegated identity? What needs approval? Systems of record? Audit/retention? How to stop in-flight work? Peak task and tool load?

## Six must-haves

1. Planning separated from execution.
2. Tool, arguments, identity, and policy validated.
3. Narrow short-lived credentials.
4. Human approval for high-risk effects.
5. Idempotent, auditable writes.
6. Safe stop on uncertainty.

## Four security controls

**Untrusted tool observations · no broad credentials · validated proposals · hard ceilings on steps, spend, amount, destination, and concurrency.**

**Proposal ≠ receipt. Confidence ≠ permission. Approval binds to payload + record version + expiry.**

## Failure triggers

| Trigger | Default |
|---|---|
| Policy or broker down | Writes fail closed. |
| Injection in email/tool output | Data, not instructions; policy blocks scope change. |
| Lost tool response | Reconcile by idempotency key; no blind write retry. |
| Approval stale | Re-request against current snapshot. |
| Tool loop | Step cap, result cache, breaker, escalate. |
| Over-limit refund | Validate and reject before policy. |

## Source planning numbers

**50k users · 20 QPS peak · 10 actions/task → ~200 tool actions/s.** Iterative planning may mean 40–60 model calls/s. Qualitative risk aid: **impact × likelihood × irreversibility**.

## Release and rollout

**Zero unsafe actions; zero duplicate effects.** Read-only → reversible writes with revert/idempotency → financial actions behind approval → red-team → canary. Kill switch halts new calls, queued work, and in-flight authority.

## Cost answer

Trace model steps and tool latency; route common tasks deterministically; cap steps/retries; cache safe read results; run slow side effects asynchronously. Measure cost and steps per task.

## Near-miss card

Planner proposed **18 refunds**; six blocked, 12 allowed; **€740** exceeded **€250** no-approval threshold. Gateway prevented unauthorized transfer, but planner bulk-action behavior failed. Disable bulk path, audit allowed calls, add risk-aware schemas and simulation, keep gateway enforcement.

## Interview close

“I would let the model interpret and propose, keep authority in policy and approval, execute only through a scoped idempotent gateway, and expand autonomy only when unsafe and duplicate effects stay at zero.”
