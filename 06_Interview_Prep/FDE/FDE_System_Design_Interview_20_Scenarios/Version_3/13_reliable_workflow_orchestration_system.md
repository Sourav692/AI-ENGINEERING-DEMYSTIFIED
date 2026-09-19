# Reliable Workflow Orchestration System - Case Study Worksheet

## 1. Interview prompt
Design a GenAI FDE solution for a **Reliable Workflow Orchestration System**: coordinate approval, payment, email, and three internal systems when any step may fail or wait days. Exactly once means the business effect.

## 2. Clarify the customer problem
- What event means the workflow actually succeeded?
- Which failures need rollback, and which need compensation?
- Which steps may wait minutes, hours, or days?
- Who is authorized to resume, re-run, or override a case?
- Does the payment provider support idempotency keys?

## 3. Users and workflows
| User | Workflow | Current pain | AI assist opportunity | Human approval needed? |
|---|---|---|---|---|
| Workflow participant |  |  |  |  |
| Operations team |  |  |  |  |
| Application developer |  |  |  |  |
| Auditor |  |  |  |  |

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
- Durable state and history:
- Scheduling:
- Timers and signals:
- Activity workers:
- Compensation:
- Operator repair:

## 7. Evaluation plan
| Metric | Good threshold | Bad threshold | Test dataset | Owner |
|---|---:|---:|---|---|
| Duplicate effects | 0 | Any duplicate | Idempotency logs | Reliability |
| Replay determinism | Identical decisions | Any divergence | Replay test jobs | Runtime eng |
| Stuck workflow age | Within expected wait | Beyond threshold | Queue inspection | Operations |
| Manual repair count | Within tolerance | Above tolerance | Operator tickets | Support ops |

## 8. Failure modes
- Worker crashes after payment succeeds
- Email succeeds but CRM update fails
- Approval waits seven days
- Definition changes while instances run
- External API times out indefinitely
- Two workers advance the same instance

## 9. Rollout plan
1. One workflow, not a platform.
2. Gate on crash recovery.
3. Prove no duplicate effects.
4. Build operator visibility.
5. Rehearse resume and compensate.
6. Version instead of mutating.

## 10. Weak vs strong answer
**Weak:** "I'd build an orchestrator that calls each API in sequence with retries."

**Strong:** "I'd make it exactly once at the business-effect level: append-only history recording intent before execution, receipts keyed by idempotency key, waiting as a first-class timer state, compensation per step, and a pinned definition version per instance."

## 11. Candidate scorecard
| Area | 1 | 3 | 5 | Score |
|---|---|---|---|---|
| Problem framing | Needs an orchestrator | Names steps | Exactly once, business effect |  |
| Architecture | API chain | Durable state | Timers, signals, compensation |  |
| Evaluation | "It completed" | Failures tracked | Duplicates, replay determinism |  |
| Production thinking | Build platform | Pilot one process | Crash gate, operator repair |  |
| Communication | Describes engine | Mostly clear | Double-charge case first |  |
