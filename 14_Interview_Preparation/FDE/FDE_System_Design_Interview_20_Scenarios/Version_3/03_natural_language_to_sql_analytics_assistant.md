# Natural-Language-to-SQL Analytics Assistant - Case Study Worksheet

## 1. Interview prompt
Design a GenAI FDE solution for a **Natural-Language-to-SQL Analytics Assistant**. Executives ask the same questions weekly and analysts hand-translate them. The dangerous failure is valid SQL answering the wrong business question.

## 2. Clarify the customer problem
- Who owns each metric definition, and how often do they change?
- Does a semantic layer exist, or must this system build one?
- Which dialects and warehouses are in scope?
- Does the warehouse already enforce row and column security?
- What happens when the question is ambiguous: ask, refuse, or escalate?

## 3. Users and workflows
| User | Workflow | Current pain | AI assist opportunity | Human approval needed? |
|---|---|---|---|---|
| Executive |  |  |  |  |
| Analyst |  |  |  |  |
| Data / platform engineer |  |  |  |  |
| Metric owner |  |  |  |  |

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
- Metric registry:
- Schema retrieval:
- Ambiguity check:
- AST and policy validation:
- Read-only execution:
- Monitoring:

## 7. Evaluation plan
| Metric | Good threshold | Bad threshold | Test dataset | Owner |
|---|---:|---:|---|---|
| Semantic correctness | Matches analyst | Any silent mismatch | Golden question/SQL cases | Analytics lead |
| Policy violations | 0 escaped | > 0 escaped | Query-run audit | Security |
| Bytes scanned per answer | Within baseline | > 20% above | Warehouse telemetry | Data platform |
| User trust score | >= launch target | Two-period decline | In-product feedback | Product |

## 8. Failure modes
- Valid SQL, wrong business question
- Stale schema invalidates a template
- Join fan-out inflates totals
- Query scans excessive data
- Summary contradicts the table
- Policy blocks frustrate users

## 9. Rollout plan
1. Ten governed metrics, named owners.
2. Golden question/SQL/result cases.
3. Replay golden set per change.
4. Shadow analysts; analyst stays truth.
5. Executive release once matched.
6. Expand domain by domain.

## 10. Weak vs strong answer
**Weak:** "I'd let an LLM write SQL from the schema and run it."

**Strong:** "I'd anchor every question on a governed metric before touching tables, ask rather than guess when ambiguous, validate SQL as an AST against policy and a scan budget, execute read-only, and prove it on ten metrics with golden cases."

## 11. Candidate scorecard
| Area | 1 | 3 | 5 | Score |
|---|---|---|---|---|
| Problem framing | Jumps to text-to-SQL | Some users/metrics | Governed decision support |  |
| Architecture | LLM plus warehouse | Semantic layer added | Registry first, AST policy gate |  |
| Evaluation | Vague accuracy | Some test queries | Golden cases, semantic correctness |  |
| Production thinking | Demo only | Some monitoring | Scan budgets, rollback, owners |  |
| Communication | Technical dump | Mostly clear | Wrong-answer risk first |  |
