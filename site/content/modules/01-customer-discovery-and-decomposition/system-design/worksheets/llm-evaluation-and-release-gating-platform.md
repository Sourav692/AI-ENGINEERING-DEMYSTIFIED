# LLM Evaluation and Release-Gating Platform - Case Study Worksheet

## 1. Interview prompt
Design a GenAI FDE solution for an **LLM Evaluation and Release-Gating Platform**: one system letting 30 AI applications decide whether a change is safe to release. A gate nobody trusts gets bypassed.

## 2. Clarify the customer problem
- What counts as a release, and what evidence must it pass?
- What is the highest-risk failure across quality, safety, latency, cost?
- Who may override a failed gate, and how is it recorded?
- Is evaluation data shared across apps, or isolated per tenant?
- What regression threshold is acceptable per application class?

## 3. Users and workflows
| User | Workflow | Current pain | AI assist opportunity | Human approval needed? |
|---|---|---|---|---|
| AI application engineer |  |  |  |  |
| Domain evaluator |  |  |  |  |
| Safety lead |  |  |  |  |
| Release manager |  |  |  |  |

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
- Artifact registry:
- Dataset store:
- Scheduling:
- Sandboxed runner:
- Grading and review:
- Policy engine:

## 7. Evaluation plan
| Metric | Good threshold | Bad threshold | Test dataset | Owner |
|---|---:|---:|---|---|
| Regression escape rate | < 5% / 30 days | Any severe escape | Incident tickets | Release manager |
| Human-grader agreement | >= 85% | Below app floor | Sampled human labels | Evaluation lead |
| Evaluation coverage | >= 95% | Below minimum sample | Dataset manifest | Platform ops |
| Flaky case rate | < 2% | > 5% per dimension | Repeated runs | Evaluation infra |

## 8. Failure modes
- Grader rewards verbosity over correctness
- Test set goes stale, stops discriminating
- Candidate overfits the benchmark
- Online sample contains PII
- Small sample creates false confidence
- Gate too slow; teams route around it

## 9. Rollout plan
1. Prove on one critical application.
2. Calibrate graders against human labels.
3. Keep gate advisory until agreement holds.
4. Add latency and cost gates.
5. Expand with app-specific rubrics.
6. Retire suites that stop discriminating.

## 10. Weak vs strong answer
**Weak:** "I'd build an eval dashboard with test runs and scorecards."

**Strong:** "I'd pin every candidate and baseline as immutable versioned artifacts, compute the delta against per-application thresholds, fail closed on missing evidence, hold rather than approve on a sample too small to decide, and calibrate graders against humans first."

## 11. Candidate scorecard
| Area | 1 | 3 | 5 | Score |
|---|---|---|---|---|
| Problem framing | Builds a dashboard | Some users/metrics | Controlled decision process |  |
| Architecture | Queue and workers | Scheduler and store | Control/data split, pinned artifacts |  |
| Evaluation | "Scores went up" | Pass rate tracked | Escape rate, agreement, flakiness |  |
| Production thinking | Demo only | Some monitoring | Fail closed, quotas, calibration gate |  |
| Communication | Reports metrics | Mostly clear | Decision and evidence first |  |
