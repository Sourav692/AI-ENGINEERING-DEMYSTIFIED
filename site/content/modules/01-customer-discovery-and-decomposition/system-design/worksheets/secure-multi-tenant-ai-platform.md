# Secure Multi-Tenant AI Platform - Case Study Worksheet

## 1. Interview prompt
Design a GenAI FDE solution for a **Secure Multi-Tenant AI Platform**: one application serving 500 enterprise tenants with isolation, predictable performance, and regional controls. The dangerous failure is a missing tenant predicate.

## 2. Clarify the customer problem
- Which data classes are in scope, and which are excluded?
- Are regional controls hard requirements or customer exceptions?
- Does "predictable performance" mean latency, throughput, or fairness?
- Which tenants may share infrastructure, and which need dedicated?
- What evidence do auditors need to prove isolation?

## 3. Users and workflows
| User | Workflow | Current pain | AI assist opportunity | Human approval needed? |
|---|---|---|---|---|
| Tenant end user |  |  |  |  |
| Tenant administrator |  |  |  |  |
| Platform operator |  |  |  |  |
| Security / compliance auditor |  |  |  |  |

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
- Identity and tenant context:
- Policy and region:
- Quota and admission:
- Partitioned storage:
- Audit:
- Monitoring:

## 7. Evaluation plan
| Metric | Good threshold | Bad threshold | Test dataset | Owner |
|---|---:|---:|---|---|
| Cross-tenant incidents | 0 | > 0 | Audit logs, incidents | Security |
| Isolation-test pass rate | Full pass | Any failure | Adversarial suite | Security eng |
| Per-tenant p95 latency | Within SLO | Sustained breach | Telemetry by tenant | SRE |
| Cost per tenant | Within band | Above band | Billing by usage | Finance/platform |

## 8. Failure modes
- Missing tenant predicate on a query
- Cache key omits tenant id
- Shared queue leaks payload metadata
- Vector index surfaces a neighbor
- One tenant exhausts shared quota
- Regional outage or misrouted traffic

## 9. Rollout plan
1. Internal test tenants only.
2. Adversarial isolation suite; failure halts.
3. Small shared tenants, tight quotas.
4. Validate latency, cost, support.
5. Dedicated tier on thresholds.
6. Monitor incidents and failover drills.

## 10. Weak vs strong answer
**Weak:** "I'd put tenant_id on every row and add row-level security."

**Strong:** "I'd derive immutable tenant context from verified identity, split control plane from data plane, enforce isolation independently at row, object, cache, queue, log, vector and key layers, fail closed on a missing predicate, and gate rollout on an adversarial isolation suite."

## 11. Candidate scorecard
| Area | 1 | 3 | 5 | Score |
|---|---|---|---|---|
| Problem framing | Jumps to tools | Some tenants/metrics | Shared default, exception path |  |
| Architecture | Generic services | Reasonable components | Control/data split, fail-closed |  |
| Evaluation | Vague isolation | Basic tests | Adversarial suite as gate |  |
| Production thinking | Demo only | Some monitoring | Blast radius, rollback, drills |  |
| Communication | Technical dump | Mostly clear | Outcome and risk first |  |
