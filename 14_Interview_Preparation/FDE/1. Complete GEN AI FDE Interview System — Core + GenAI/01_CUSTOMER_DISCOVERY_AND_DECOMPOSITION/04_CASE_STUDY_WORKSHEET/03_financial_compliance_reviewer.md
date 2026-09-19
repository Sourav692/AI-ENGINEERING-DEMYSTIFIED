# Financial Compliance Document Reviewer - Case Study Worksheet

## 1. Interview prompt
Design a GenAI FDE solution for **Financial Compliance Document Reviewer**. The customer has ambiguous requirements, sensitive data, and expects a production rollout, not a demo.

## 2. Clarify the customer problem
- What business process is broken today?
- Who are the users and what decisions do they make?
- What is the cost of delay, error, or manual work?
- What data is available, trusted, missing, or restricted?
- What does success mean in the first 30, 60, and 90 days?

## 3. Users and workflows
| User | Workflow | Current pain | AI assist opportunity | Human approval needed? |
|---|---|---|---|---|
| Primary operator |  |  |  |  |
| Manager/reviewer |  |  |  |  |
| Admin/security |  |  |  |  |

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
- Ingestion:
- Retrieval:
- Agent/tool use:
- Human approval:
- Evaluation:
- Monitoring:

## 7. Evaluation plan
| Metric | Good threshold | Bad threshold | Test dataset | Owner |
|---|---:|---:|---|---|
| Answer groundedness | >= 90% | < 80% | Golden Q&A | FDE/SME |
| Permission violations | 0 | > 0 | Red-team set | Security |
| Citation accuracy | >= 95% | < 85% | Sample docs | SME |
| Task completion | >= 80% | < 65% | Workflow tests | Product |

## 8. Failure modes
- Bad retrieval or missing context
- Hallucinated policy or procedure
- Cross-tenant or role-based data leakage
- Unsafe tool call or write-back action
- Stale documents or bad sync
- Cost/latency spike

## 9. Rollout plan
1. Offline prototype using historical cases.
2. SME review and evaluation set creation.
3. Read-only pilot with citations.
4. Human-approved actions.
5. Limited production canary.
6. Monitor, tune, and expand.

## 10. Weak vs strong answer
**Weak:** “I would use RAG with a vector database and ask GPT to answer.”

**Strong:** “I would first define the operational workflow and risk boundary, then design permission-aware retrieval with grounded citations, evals, red-team tests, human approval for risky actions, and production observability before rollout.”

## 11. Candidate scorecard
| Area | 1 | 3 | 5 | Score |
|---|---|---|---|---|
| Problem framing | Jumps to tools | Some users/metrics | Clear workflow and ROI |  |
| Architecture | Generic RAG | Reasonable components | Secure, observable, scalable |  |
| Evaluation | Vague accuracy | Basic metrics | Golden set + regression + red-team |  |
| Production thinking | Demo only | Some monitoring | SLOs, rollback, cost, incidents |  |
| Communication | Technical dump | Mostly clear | Executive + engineering clarity |  |
