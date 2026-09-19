# Tool-Using AI Agent with Safety Controls - Answer Key

This answer key is designed for interview preparation. It shows what a strong GenAI FDE candidate should ask, design, evaluate, secure, and communicate before moving from demo to production.

## Strong discovery questions
- Which actions are reversible and which are not, and exactly where does the money boundary sit?
- Does the agent act as the user, a service account, or a delegated actor with a narrow role?
- What exact work should be automated first, and what must stay human-owned?
- Which systems are the source of truth for identity, customer state, and financial actions?
- What makes an action safe to execute automatically rather than requiring approval?
- What is the rollback path when the agent makes a bad call, and who executes it?
- What evidence must be recorded for audit, support, and dispute resolution?
- Is success fewer handling minutes, higher resolution rate, lower error rate, or better satisfaction?

## Strong functional requirements
- Support the core workflow: interpret incoming work, propose a bounded next action, pass it through deterministic policy, and execute only what is permitted.
- Let the planner propose but never execute; the model interprets while deterministic systems decide who may act and what may change.
- Declare every tool in a registry with its schema and data class, so tool use is governable rather than ad hoc.
- Require explicit approval for irreversible or financial actions above a threshold, captured as a first-class record.
- Execute through an idempotent gateway so a retry or replay can never produce a second side effect.
- Provide a tested kill switch that halts autonomous execution paths without a deploy.

## Strong non-functional requirements
- Latency: budget model-planning time separately from tool time; p95 completion under about 15 seconds for low-risk tasks.
- Availability: at 50,000 users and 20 QPS peak, 10 actions per task means roughly 200 tool actions per second — reads parallelize, writes do not.
- Security: short-lived, narrowly scoped credentials minted per workflow; the model never holds a reusable API key or admin token.
- Compliance: a tamper-evident ledger recording intent, policy decision, approval, and outcome for every action.
- Reliability: fail closed for writes when the credential broker or policy engine is unavailable; degrade only the lowest-risk reads.
- Cost: hard ceilings on tool calls per task, per-task spend, refund amount, and allowable destinations — guardrails, not tuning knobs.

## Architecture explanation
- The control plane decides what may happen; the data plane performs it. The model sits entirely inside the control plane's proposal step.
- The agent planner proposes one bounded next action at a time and is explicitly forbidden from executing anything directly.
- The task state store tracks workflow progress and intermediate results, and is never treated as the business source of truth.
- The tool registry declares allowed tools, argument schemas, and data-class metadata, so an undeclared tool simply cannot be called.
- The policy decision point deterministically returns allow, block, or needs-approval, with the granted scopes and a reason string.
- The credential broker mints short-lived capability tokens bound to one tenant, one workflow, one action type, and one expiry.
- The approval service captures human sign-off for irreversible actions, and the idempotent execution gateway ensures a given proposal executes exactly once.
- The audit ledger records intent, decision, approval, and outcome; a kill switch halts autonomous paths and is tested before launch.

## Data model / integration assumptions
- AgentTask(id, actor, goal, state, step_budget); ToolDefinition(name, schema, data_class, scopes); ActionProposal(id, task_id, tool, args_hash, policy_decision); PolicyDecision(proposal_id, verdict, scopes, reason); ActionReceipt(proposal_id, idempotency_key, outcome).
- Assume the proposal is the model's recommendation and the receipt is the only proof a side effect occurred, so the two are never conflated.
- Assume arguments are canonicalized before hashing, so the same logical input always yields the same idempotency seed.
- Assume a repeated idempotency key returns the stored receipt rather than calling the tool again, which is what makes retries safe.
- Assume schema validation runs before policy evaluation, so malformed arguments are rejected before any authorization logic executes.

## Red-team risks
- prompt injection requesting an unauthorized tool, lost tool responses, stale approvals, action loops, credential broker outage
- Indirect prompt injection inside a CRM record, ticket thread, database row, or fetched page; tool observations are untrusted data, never commands.
- Over-broad credentials, where a long-lived token turns one manipulated plan into fleet-wide access rather than a single bounded workflow.
- Unvalidated proposals, such as a confident "refund $5,000" against a $500 task limit, which validation must reject regardless of model certainty.
- Lost responses after a tool succeeded, where a naive retry issues a second refund unless the gateway is genuinely idempotent.
- Stale approvals and action loops, where an aged sign-off authorizes the wrong state or an unbounded agent retries itself into a bill.

## Rollout plan
- Week 0-1: classify every action by reversibility and financial impact, and name the approver for each risky class.
- Week 1-2: launch the smallest safe slice — read-only triage and drafting, with no write path enabled at all.
- Week 2-3: prove reversibility on a narrow set of CRM writes before any write path is widened.
- Week 3-4: add write paths only where rollback is demonstrated, keeping every financial action behind a human.
- Week 5: red-team the prompt with hostile tool observations before granting the agent any additional power.
- Week 6-8: canary a small representative traffic slice, watching policy denials, duplicate effects, approval delay, and override rate.
- After pilot: expand autonomy only where unsafe-action count stays at zero and duplicate effects never appear.

## Evaluation plan
| Metric | What it proves | Strong threshold | Dataset / method |
|---|---|---|---|
| Unsafe action count | The control boundary actually held | Zero in any sensitive workflow | Audit review, incident tickets, rule checks |
| Duplicate-effect count | Retries and replays cannot double-charge | Zero; any occurrence alerts immediately | Idempotency logs and reconciliation reports |
| Policy denial rate | Denials reflect real policy, not a broken prompt | Stable against baseline; spikes investigated | Policy engine logs |
| Approval rate and delay | Human gates protect without stalling the workflow | Delay within SLO; rate stable | Approval service logs |
| Task completion rate | Automation finishes work without manual rescue | Holds or improves after each expansion | Workflow state machine and case closures |
| Human override rate | The agent is earning its place in the queue | Low enough to justify the automation | Review UI and post-action edits |

## Weak answer
I would build an assistant that connects to email and CRM and issues refunds when it decides the customer deserves one. This is weak because it makes the model the authority, handing it credentials rather than scoped capabilities, with no deterministic policy gate and no defense against instructions hidden in a ticket.

## Average answer
I would have the agent plan tool calls, check permissions before each one, require approval for large refunds, and log everything. I would add retries for reliability. This is better, but still incomplete because it does not treat tool output as untrusted, does not bound loops or spend, and adds retries without idempotency — which is how one refund quietly becomes two.

## Strong answer
I would frame the outcome as enabling useful automation while deterministic controls govern identity, permissions, risk, and irreversible effects, because the model must never be the authority. The planner proposes one bounded action; a typed schema validates it; a deterministic policy engine returns allow, block, or needs-approval; a credential broker mints a short-lived token scoped to that single action; and an idempotent gateway guarantees the effect happens exactly once. Tool observations are untrusted data, never instructions, so injection fails at the policy gate rather than relying on model judgment. Loops, spend, refund amounts, and destinations all have hard ceilings. I would start read-only, prove reversibility before enabling writes, keep money behind a human, and red-team the prompt before granting more power.

## Interviewer scorecard
| Area | 1 - Weak | 3 - Average | 5 - Strong |
|---|---|---|---|
| Problem framing | "Build an agent that does refunds" | Names automation and approvals | Outcome as controlled automation; model proposes, deterministic systems decide |
| Requirements | "It should be safe" | Lists permissions and logging | Reversibility classes, money boundary, delegation model, explicit step budget |
| Architecture | Model calls tools directly | Adds a permission check | Planner, registry, policy point, credential broker, approval, idempotent gateway, kill switch |
| Data/integration | Mentions logs | Names tasks and tool calls | Proposal vs. receipt separated, canonical args hash, validation before policy |
| Evaluation | "It works" | Tracks success rate | Unsafe actions, duplicate effects, denial rate, approval delay, override rate |
| Safety/security | "The model will refuse" | Adds scoped tokens | Untrusted observations, short-lived capabilities, output validation, bounded loops and spend |
| Rollout | Enable all tools | Pilot with approvals | Read-only first, reversibility proven, money behind a human, prompt red-team, canary |
| Communication | Describes the agent | Clear but generic | Leads with the hostile case, names what fails closed, closes with the autonomy gate |

## Final 2-minute spoken answer
I would not start with the model. The customer asks for an agent that reads email, queries internal systems, updates CRM records, and issues refunds, and everyone nods at the feature list before disagreeing completely — operations wants speed, security wants hard gates, finance fears irreversible money movement. That disagreement is the design problem. So I would restate the outcome as enabling useful automation while deterministic controls govern identity, permissions, risk, and irreversible effects. The crucial consequence is that the model is not the authority: it can interpret and propose, but deterministic systems decide who may act, what may change, and whether an action can be reversed. Concretely, the planner proposes one bounded action, a typed schema validates the arguments before policy even runs, a deterministic policy engine returns allow, block, or needs-approval with the scopes it grants, a credential broker mints a short-lived token tied to one workflow and one action type, and an idempotent execution gateway guarantees exactly one side effect no matter how many retries occur. Tool observations are untrusted data, never commands, so a prompt injection hidden in a ticket fails at the policy gate rather than depending on the model to notice it. Loops, per-task spend, refund amounts, and destinations all carry hard ceilings. I would roll out read-only first, prove reversibility before enabling any write path, keep money behind a human, and red-team the prompt before granting more autonomy. Success is fewer handling minutes with zero unauthorized or unreviewed irreversible changes.
