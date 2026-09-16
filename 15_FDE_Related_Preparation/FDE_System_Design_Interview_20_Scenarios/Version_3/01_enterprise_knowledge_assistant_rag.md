# Enterprise Knowledge Assistant with RAG - Case Study Worksheet

## 1. Interview prompt
Design a GenAI FDE solution for an **Enterprise Knowledge Assistant with RAG**. Employees ask questions across Drive, SharePoint, Slack, wikis, and tickets; the dangerous constraint is permission fidelity, not retrieval quality.

## 2. Clarify the customer problem
- Which source is authoritative, and what happens when sources conflict?
- Must source permissions be inherited live, or is periodic sync acceptable?
- How fresh must answers be, and how fast must deletions leave retrieval?
- Who diagnoses a wrong answer, and who owns the leakage risk?
- What happens when evidence is weak: refuse, label, or escalate?

## 3. Users and workflows
| User | Workflow | Current pain | AI assist opportunity | Human approval needed? |
|---|---|---|---|---|
| End user (employee) |  |  |  |  |
| Operator / support |  |  |  |  |
| Security owner |  |  |  |  |
| Executive sponsor |  |  |  |  |

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
- Ingestion and ACL:
- Permission-filtered retrieval:
- Reranking and budget:
- Citations:
- Evaluation:
- Monitoring:

## 7. Evaluation plan
| Metric | Good threshold | Bad threshold | Test dataset | Owner |
|---|---:|---:|---|---|
| Permission leakage | 0 | > 0 | ACL red-team suite | Security |
| Grounded answer rate | >= baseline | > 5 pts below | Silent-mode labeled set | ML/eval |
| Citation precision | >= agreed bar | > 5 pts decline | SME-reviewed sample | Evaluation |
| Freshness lag | Within SLO | Exceeds SLO | Connector vs. index stamps | Ingestion |

## 8. Failure modes
- Missed deletion leaves stale content retrievable
- Stale ACL cache serves a revoked user
- Similar but irrelevant passages retrieved
- Fabricated citation
- Prompt injection in a ticket or wiki
- Provider outage or peak cost spike

## 9. Rollout plan
1. One low-risk corpus, no write-back.
2. Access-leakage suite; exposure blocks release.
3. Silent evaluation on real questions.
4. Read-only pilot with citations.
5. Source-by-source expansion.
6. Monitor, reconcile, widen on gates.

## 10. Weak vs strong answer
**Weak:** "I'd embed the documents in a vector DB and let an LLM answer."

**Strong:** "I'd name permission fidelity as the load-bearing constraint, normalize source ACLs at ingestion, filter by effective permissions before generation, verify citations, abstain on weak evidence, and gate rollout on a leakage suite."

## 11. Candidate scorecard
| Area | 1 | 3 | 5 | Score |
|---|---|---|---|---|
| Problem framing | Jumps to tools | Some users/metrics | Names the dangerous constraint |  |
| Architecture | Generic RAG | Reasonable components | Permission-filtered, observable |  |
| Evaluation | Vague accuracy | Basic metrics | Leakage suite + groundedness |  |
| Production thinking | Demo only | Some monitoring | Fail-closed, rollback, drills |  |
| Communication | Technical dump | Mostly clear | Outcome and risk first |  |
