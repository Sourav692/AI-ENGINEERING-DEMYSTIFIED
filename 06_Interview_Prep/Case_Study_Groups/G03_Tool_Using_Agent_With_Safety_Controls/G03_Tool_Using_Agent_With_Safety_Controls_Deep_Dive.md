# G03 — Tool-Using Agent with Safety Controls: Deep Dive

The [Main guide](G03_Tool_Using_Agent_With_Safety_Controls_Main.md) is the spoken design. This is its technical backup; the unchanged [source case](G03_Tool_Using_Agent_With_Safety_Controls.md) keeps the complete synthesis and references.

## 1. Policy, state, and execution records

`AgentTask(id, actor, goal, state, step_budget)` tracks the workflow, not customer or financial truth. `ToolDefinition(name, schema, data_class, scopes)` limits the legal tool space. `ActionProposal(id, task_id, tool, args_hash, policy_decision)` is the model’s recommendation. `PolicyDecision(proposal_id, verdict, scopes, reason)` is the deterministic verdict. `ActionReceipt(proposal_id, idempotency_key, outcome)` is proof of the side effect. Canonicalize arguments before hashing, and return the stored receipt when the same business action is retried.

Keep the order explicit: authenticate → propose → resolve registered tool → validate typed arguments/data class/limits → evaluate policy → obtain approval if required → mint scoped credential → execute through the gateway → persist receipt → decide whether to continue. In this case, validation runs before policy so malformed or over-limit proposals never enter authorization. If the policy or broker cannot be reached, a write cannot proceed.

An approval is a durable record of reviewer, time, rationale, exact payload, tenant, record version, amount, and expiry. A later state change invalidates it. The gateway, not the planner, owns exactly-once effect semantics within the idempotency contract. A lost response is an unknown outcome that needs reconciliation; neither a prompt nor a generic retry makes it safe.

## 2. Nine components and their failure behavior

| Component | Control it owns | If unavailable |
|---|---|
| Planner | Next bounded proposal, stop condition, step budget | Pause and escalate. |
| Task state store | Durable workflow progress | Stop writes; no untracked continuation. |
| Tool registry | Declared schemas, data class, risk label | Undeclared tool cannot run. |
| Policy decision point | Allow, block, or approval with reason/scope | Writes fail closed. |
| Approval service | Payload-bound human decision | Wait, expire, or re-request. |
| Credential broker | Short-lived capability for one action | Writes fail closed; no broad-secret fallback. |
| Execution gateway | Scoped, validated, idempotent effect | Reconcile uncertain writes. |
| Audit ledger | Intent, proposal, verdict, approval, receipt | Stop if evidence cannot be made durable. |
| Kill switch | Stop autonomous paths and revoke authority | Tested before launch. |

The user boundary ends at authentication, planner boundary at proposal, policy boundary at verdict, and execution boundary at the downstream side effect. CRM, email, internal data, and refund systems remain systems of record. A cache may speed safe reads but never becomes authority for permissions or refunds.

## 3. Risk and sizing

Use `Impact × Likelihood × Irreversibility` as a qualitative risk aid, not a numeric proof. A public FAQ read may be autonomous; a CRM update may need preconditions; a refund may need human approval; some exports or permission changes are blocked. Refund reversibility in software does not erase customer, finance, or abuse costs.

The source’s planning anchor is **50k users, 20 QPS peak, 10 actions/task**: roughly 200 tool actions/s. Iterative plans may reach 40–60 model calls/s. With about 1 s of planner compute/task, the planner needs roughly 20 core-seconds per second at peak, plus slack for tails. Illustrative 5 KB decision + 20 KB audit/task gives about 100–400 KB/s and 8.6–34.6 GB/day raw before indexing/replication. At 10× peak, ask what saturates first: planner, approval queue, adapter, ledger, or refund service. At 10× lower load, simplify deployment but keep the same safety boundary.

Cap concurrency by user, tool, and globally; also cap value and destination. Partition ordered work by account or workflow so conflicting writes do not race. Reads can run in parallel; writes and approvals must follow state transitions. Long workflows return a job ID and continue asynchronously.

## 4. Integrations at enterprise scale

The layers have different jobs: **REST/SOAP/SQL execute; function calling lets a model select a tool; MCP advertises tools/resources; an agent framework coordinates multi-step work.** MCP does not replace the underlying API. Direct REST is enough for a fixed deterministic workflow, while a planner earns its overhead only when a request spans systems.

Putting 1,500 functions from 100 applications into every prompt makes selection and schema maintenance brittle. A registry loads only task-relevant tool descriptions and carries typed arguments, data class, risk, and scopes. At 500+ applications/200k employees, scale stateless planner/gateway services, use per-user and per-app quotas, keep long work async, and place region-local gateways/tool servers where data residency requires it.

The model never receives a broad API key. A trusted service propagates enterprise identity and attaches a narrow OAuth/RBAC/ABAC capability to the approved call. Every downstream application evaluates that identity. Task state and audit are separate from cross-session business truth.

## 5. Security and failure drills

The four controls are a set: untrusted tool observations, no broad long-lived credentials, validation of proposals, and ceilings on steps/spend/amount/destinations. Add defense in depth: policy, broker, idempotent gateway, ledger, and kill switch. Scope failures by tenant, region, workflow, and dependency.

| Drill | Expected behavior |
|---|---|
| Injection hidden in email or CRM row | Treat content as data; policy rejects requested scope change; preserve evidence; quarantine or hand off. |
| Tool succeeded, response lost | Check idempotency key/transaction record; return stored receipt or mark uncertain for reconciliation. Never blindly repeat a write. |
| Approval aged out | Compare payload, tenant, record version, amount, expiry; re-request on mismatch. |
| Agent repeats a call | Attempt counter, cached result, backoff, breaker, explicit stop and escalation. |
| Broker or policy down | Writes fail closed. Only explicitly allowed, non-sensitive cached reads may degrade. |
| Amount/destination outside limit | Reject before policy evaluation regardless of confidence. |

The runbook must locate prompts, versions, proposal/validation/policy records, approval artifact, token scope, calls, and receipts. The kill switch must halt new calls, cancel queued work, revoke/expire delegated tokens, and make downstream reject in-flight completions. A read-only replay can be safe; a write replay needs its receipt/idempotency contract.

## 6. Release and operational metrics

Zero unsafe actions and zero duplicate effects gate expansion. Track policy denial rate, approval rate/delay, tool success, task completion, override rate, p95, step count, retry count, and cost per task. A denial spike can mean an attack or a broken schema; an override spike can mean model quality or policy calibration. Inspect examples before changing the gate.

The red-team set covers indirect injection in tool output; over-broad credentials; over-limit or malformed proposals; response-loss retries; stale approvals; tool loops; cross-tenant requests. A passing demo is not evidence that these paths are safe.

Rollout: read-only triage/draft → narrow reversible CRM writes with owner/revert plan → money behind a human → injection tests → small canary → expansion if gates hold. Shared product services are policy, broker, approval, execution, and ledger; customer wiring remains configuration and adapters. Train users on refusals, approvals, escalation, and recovery.

## 7. Cost and latency pivot

Agent steps and tool calls, including retries after rejected or failed actions, are the common cost driver. Profile model planning versus downstream tool wait versus approval. If planner-heavy, route common intents deterministically and combine safe reads; if tool-heavy, cache safe reads in-request and prefetch; if approval-heavy, improve proposal clarity and risk classification, never bypass approval.

For a **tool loop**, inspect the trace for repeated tool/observation pairs and missing state transitions, then impose max steps, result cache, clear stopping criteria, and tool-selection tests. For a **tool timeout**, find the critical path, parallelize independent reads, set per-tool deadlines, and move slow side effects to an async job with status. Measure steps, tool latency, retries, timeouts, and cost before and after.

## 8. Refund near miss: planner failure, gateway success

The source incident’s support agent asked to handle delayed VIP shipments. The planner selected `refund_customer` for 18 orders. A €740 request exceeded a €250 no-approval threshold; six calls were blocked, 12 allowed, and no unauthorized money moved. A planner prompt designed to be “more action-oriented” omitted bulk approval boundaries. The unchanged gateway policy blocked the high-value actions.

Contain by disabling bulk refund planning, forcing VIP refunds into review-ticket mode, adding user confirmation, and auditing the 12 allowed actions. Prevent with threshold-aware schemas, policy simulation, a separate action-risk check, better planner examples, and non-bypassable gateway enforcement. Treat it as a near miss even though the money gate held; the proposal distribution deteriorated.

## 9. Interview trade-offs

| Trade-off | Decision |
|---|---|
| Flexible agent vs deterministic workflow | Flexible interpretation, deterministic action control. |
| Fine scopes vs integration effort | Scope irreversible effects first; reuse shared auth wrappers. |
| Auto execution vs approval delay | Low-risk auto, medium conditional/reviewed, high-risk explicit approval or block. |
| Central gateway vs direct write integrations | Centralize auth, validation, audit, and idempotency in one write path. |

The [source](G03_Tool_Using_Agent_With_Safety_Controls.md) retains the original 50-minute script, full diagrams, trace excerpt, and reference table.
