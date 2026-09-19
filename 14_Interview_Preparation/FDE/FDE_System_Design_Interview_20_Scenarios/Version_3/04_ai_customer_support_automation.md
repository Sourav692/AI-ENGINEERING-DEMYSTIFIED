# AI Customer-Support Automation - Case Study Worksheet

## 1. Interview prompt
Design a GenAI FDE solution for **AI Customer-Support Automation**: automate routine requests, escalate risky ones to a human with full context. The danger is an unauthorized action or a confidently wrong answer.

## 2. Clarify the customer problem
- Which channels are in scope, and at what volume and peak?
- Which actions are autonomous, and which need approval?
- How is the customer authenticated before account tools run?
- What must a human see at handoff, and how fast?
- How many languages, and what happens when detection fails?

## 3. Users and workflows
| User | Workflow | Current pain | AI assist opportunity | Human approval needed? |
|---|---|---|---|---|
| Customer |  |  |  |  |
| Support agent |  |  |  |  |
| Support operations lead |  |  |  |  |
| Security / legal reviewer |  |  |  |  |

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
- Identity verification:
- Intent and risk routing:
- Grounded retrieval:
- Tool policy gateway:
- Escalation:
- Monitoring:

## 7. Evaluation plan
| Metric | Good threshold | Bad threshold | Test dataset | Owner |
|---|---:|---:|---|---|
| Safe automation rate | Stable per intent | Any intent drop | QA review labels | Support ops |
| Incorrect resolutions | <= baseline | Above baseline | Reopen events | Support QA |
| Repeat-contact rate | Flat or down | Rises post-change | CRM correlation | Support analytics |
| Cost per resolved case | Improves | Offset by rework | Finance reporting | Finance ops |

## 8. Failure modes
- Confidently wrong policy answer
- Prompt injection in customer text
- Action taken before identity verified
- Refund executes, response times out
- Stale account state drives a commitment
- Handoff omits context; agent repeats work

## 9. Rollout plan
1. Agent-assist only; human sends.
2. Automate low-risk reversible intents.
3. Add one tool class at a time.
4. Sample-review automated cases.
5. Kill switch per intent.
6. Roll back by intent.

## 10. Weak vs strong answer
**Weak:** "I'd send each message to an LLM and let it resolve the ticket."

**Strong:** "I'd build a routed decision pipeline: verify identity before account tools, tag intent and risk, ground the draft in approved policy, and let a deterministic policy gateway — not the model — decide whether to auto-resolve, seek approval, or escalate."

## 11. Candidate scorecard
| Area | 1 | 3 | 5 | Score |
|---|---|---|---|---|
| Problem framing | Builds a chatbot | Some routing | Routed decision pipeline |  |
| Architecture | LLM replies | Retrieval plus escalation | Identity gate, policy gateway |  |
| Evaluation | Vague accuracy | Deflection and CSAT | Safe automation, repeat contact |  |
| Production thinking | Demo only | Some monitoring | Per-intent kill switch, rollback |  |
| Communication | Technical dump | Mostly clear | Harm case first |  |
