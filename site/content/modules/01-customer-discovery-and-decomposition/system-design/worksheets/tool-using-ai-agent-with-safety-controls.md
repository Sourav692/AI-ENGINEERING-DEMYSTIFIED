# Tool-Using AI Agent with Safety Controls - Case Study Worksheet

## 1. Interview prompt
Design a GenAI FDE solution for a **Tool-Using AI Agent with Safety Controls**: it reads email, queries systems, updates CRM, and issues refunds — without unchecked authority. The model proposes; it never decides.

## 2. Clarify the customer problem
- Which actions are reversible, and where is the money boundary?
- Does the agent act as the user, a service account, or delegated?
- What makes an action safe to run without approval?
- What is the rollback path for a bad call, and who runs it?
- What evidence must exist for audit and dispute resolution?

## 3. Users and workflows
| User | Workflow | Current pain | AI assist opportunity | Human approval needed? |
|---|---|---|---|---|
| Business user |  |  |  |  |
| Approver |  |  |  |  |
| Security owner |  |  |  |  |
| Tool / data owner |  |  |  |  |

## 4. Requirements
### Functional
-
-
-

### Non-functional
- Latency target:
- Availability target:
- Cost budget:
- Security/privacy constraints:
- Audit/compliance requirement:

## 5. Data and integration map
| Data source | Format | Owner | Freshness | Permission model | Risk |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

## 6. Proposed architecture
Use one of the rendered diagrams as a base, then customize:
- Planner and proposals:
- Tool registry:
- Policy decision point:
- Credential broker:
- Approval service:
- Idempotent execution:

## 7. Evaluation plan
| Metric | Good threshold | Bad threshold | Test dataset | Owner |
|---|---:|---:|---|---|
| Unsafe action count | 0 | Any nonzero | Audit review | Trust and safety |
| Duplicate effects | 0 | Any occurrence | Idempotency logs | Reliability |
| Policy denial rate | Stable baseline | Sudden spike | Policy engine logs | Platform |
| Human override rate | Low and falling | Rising | Review UI edits | Operations |

## 8. Failure modes
- Prompt injection requests an unauthorized tool
- Tool succeeds but the response is lost
- Approval becomes stale before execution
- Agent loops on the same action
- Credential broker is unavailable
- Proposal exceeds the task's refund limit

## 9. Rollout plan
1. Read-only triage and drafting.
2. Prove reversibility on narrow writes.
3. Enable writes where rollback works.
4. Keep money behind a human.
5. Red-team the prompt.
6. Canary, then widen autonomy.

## 10. Weak vs strong answer
**Weak:** "I'd connect the agent to email and CRM and let it issue refunds."

**Strong:** "The model proposes one bounded action; a typed schema validates it, a deterministic policy engine allows or blocks it, a broker mints a short-lived scoped credential, and an idempotent gateway guarantees exactly one effect. Tool output is untrusted data, never instructions."

## 11. Candidate scorecard
| Area | 1 | 3 | 5 | Score |
|---|---|---|---|---|
| Problem framing | Feature list | Some approvals | Model proposes, policy decides |  |
| Architecture | Model calls tools | Permission check added | Broker, gateway, kill switch |  |
| Evaluation | "It works" | Success rate | Unsafe actions, duplicate effects |  |
| Production thinking | Enable all tools | Pilot first | Read-only first, bounded spend |  |
| Communication | Describes agent | Mostly clear | Hostile case first |  |
