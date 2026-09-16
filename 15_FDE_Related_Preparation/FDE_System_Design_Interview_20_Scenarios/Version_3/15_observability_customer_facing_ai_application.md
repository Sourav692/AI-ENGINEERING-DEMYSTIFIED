# Observability for a Customer-Facing AI Application - Case Study Worksheet

## 1. Interview prompt
Design a GenAI FDE solution for **Observability of a Customer-Facing AI Application**. The customer says the AI is slow and sometimes wrong and nobody knows why. First decide what not to collect.

## 2. Clarify the customer problem
- What counts as slow: which percentile, on which path?
- What counts as wrong: incorrect, empty, hallucinated, or tool failure?
- Which tenants and workflows are most affected?
- What are we allowed to capture by default?
- Who must diagnose a failure without escalating?

## 3. Users and workflows
| User | Workflow | Current pain | AI assist opportunity | Human approval needed? |
|---|---|---|---|---|
| Support agent |  |  |  |  |
| Engineer on call |  |  |  |  |
| Security reviewer |  |  |  |  |
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
- Correlation and spans:
- Sensitivity classifier:
- Trace store:
- Sampling policy:
- Support access:
- Dashboards:

## 7. Evaluation plan
| Metric | Good threshold | Bad threshold | Test dataset | Owner |
|---|---:|---:|---|---|
| Redaction pass rate | 0 raw prompts | Any leak | PII/secret scanners | Security |
| Trace coverage | Complaints map to traces | Gaps on failures | Complaint vs. trace volume | Platform |
| Mean time to diagnose | Falling | Rising | Incident timelines | Support eng |
| Telemetry overhead | Within budget | Distorts production | Latency with/without export | Observability owner |

## 8. Failure modes
- Sampling drops the only bad trace
- Tenant ID explodes metric cardinality
- Logs capture a raw prompt
- Trace context breaks at a queue
- Quality metric improves while adoption falls
- Telemetry export becomes the outage

## 9. Rollout plan
1. Define user-facing SLOs first.
2. Make slow and wrong measurable.
3. Instrument one critical path.
4. Scan exports for raw content.
5. Add trace-linked support workflow.
6. Add quality and cost sampling.

## 10. Weak vs strong answer
**Weak:** "I'd add more logging and build a dashboard."

**Strong:** "I'd decide what not to collect first, attach a stable correlation ID per request, classify and salt-hash sensitive fields before storage, sample preferentially toward errors and latency outliers, and test success by whether support can explain a failure unaided."

## 11. Candidate scorecard
| Area | 1 | 3 | 5 | Score |
|---|---|---|---|---|
| Problem framing | Add more logs | Names latency | Splits slow, wrong, diagnosable |  |
| Architecture | Logs and dashboard | Tracing added | Classifier before storage |  |
| Evaluation | "We have dashboards" | Latency tracked | Coverage, MTTD, redaction |  |
| Production thinking | Instrument all | Some sampling | Overhead budget, error overrides |  |
| Communication | Shows dashboard | Mostly clear | Dropped-trace failure first |  |
