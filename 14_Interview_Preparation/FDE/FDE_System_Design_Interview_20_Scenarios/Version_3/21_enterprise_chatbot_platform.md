# Enterprise Chatbot Platform - Case Study Worksheet

## 1. Interview prompt
Design a GenAI FDE solution for an **Enterprise Chatbot Platform** for 40,000 employees. The real driver is 6,400 staff already pasting company data into consumer AI tools.

## 2. Clarify the customer problem
- Commercial API, self-hosted, or hybrid by data class?
- General chat first, or grounding — and which systems?
- How long is retention, and who may read another's history?
- Can any employee publish an assistant, or is it reviewed?
- What rules out simply licensing a vendor's enterprise tier?

## 3. Users and workflows
| User | Workflow | Current pain | AI assist opportunity | Human approval needed? |
|---|---|---|---|---|
| Employee |  |  |  |  |
| Security / legal / compliance |  |  |  |  |
| Department admin |  |  |  |  |
| Platform operator |  |  |  |  |

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
- Session and identity:
- Context assembler:
- Retrieval ACLs:
- Policy and DLP:
- Model router:
- Audit:

## 7. Evaluation plan
| Metric | Good threshold | Bad threshold | Test dataset | Owner |
|---|---:|---:|---|---|
| Consumer-AI egress | Down 80% / 2 quarters | Flat or rising | Proxy log baseline | Security |
| Weekly active / eligible | >= 50% | Below 25% | Product telemetry | Product |
| Permission violations | 0 | Any nonzero | Contract tests, audit | Governance |
| Audit completeness | 100% | Below 100% | Turns recorded / served | Compliance |

## 8. Failure modes
- Over-scoped assistant launders access
- Stale ACL after a revocation
- Prompt injection via an uploaded document
- System prompt silently truncated
- Runaway scripted account burns budget
- Audit pipeline down; turns unrecorded

## 9. Rollout plan
1. Baseline egress from proxy logs.
2. General chat with SSO and audit.
3. Add grounding on one corpus.
4. Gate on zero permission violations.
5. Add attachments with scanning.
6. Add reviewed assistant publishing.

## 10. Weak vs strong answer
**Weak:** "I'd build a React frontend, a vector DB, and an LLM gateway."

**Strong:** "Identity is set at the session and re-checked every turn; nothing enters the context window without passing policy and being audited. Retrieval resolves live ACLs per chunk, an assistant's effective scope intersects the viewer's, and every layer fails closed."

## 11. Candidate scorecard
| Area | 1 | 3 | 5 | Score |
|---|---|---|---|---|
| Problem framing | ChatGPT clone | Governance named | Egress risk plus adoption |  |
| Architecture | UI and vector DB | ACL filtering added | Assembler, router, audit |  |
| Evaluation | "People like it" | Usage tracked | Egress, violations, audit |  |
| Production thinking | Launch to all | Pilot first | One risk class per phase |  |
| Communication | Technical only | Mostly clear | Board and on-call stories |  |
