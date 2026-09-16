# High-Volume Batch Inference System - Case Study Worksheet

## 1. Interview prompt
Design a GenAI FDE solution for a **High-Volume Batch Inference System**: classify 100 million records nightly before 6:00 a.m. under rate and cost limits. The real target is replayability and recovery when behind.

## 2. Clarify the customer problem
- Who consumes the output, and what breaks if it is late?
- Can the batch be partial, or must it be all-or-nothing?
- What happens when the job is behind at 4 a.m.?
- What capacity can the downstream consumer actually absorb?
- Is there a hard cost ceiling, and which degraded mode is preferred?

## 3. Users and workflows
| User | Workflow | Current pain | AI assist opportunity | Human approval needed? |
|---|---|---|---|---|
| Morning operations team |  |  |  |  |
| On-call platform engineer |  |  |  |  |
| Model owner |  |  |  |  |
| Business sponsor |  |  |  |  |

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
- Snapshot and planning:
- Partitioning:
- Leasing and workers:
- Rate-limit coordination:
- Checkpoint and sink:
- Contingency:

## 7. Evaluation plan
| Metric | Good threshold | Bad threshold | Test dataset | Owner |
|---|---:|---:|---|---|
| Completion forecast | Beats deadline | Crosses, no contingency | Progress telemetry | Operations |
| Duplicate logical results | Within replay window | Beyond window | Logical-key comparison | Data engineering |
| Straggler age | Within recovery budget | Oldest exceeds budget | Partition histograms | Batch platform |
| Cost per million records | Within envelope | Trends outside | Billing + usage logs | Finance/platform |

## 8. Failure modes
- Behind schedule with no path to deadline
- Provider cuts quota mid-run
- Hot partition produces stragglers
- Worker crashes after the model call
- Result sink throttles writes
- Corrupted checkpoint or snapshot hash

## 9. Rollout plan
1. Benchmark representative token distribution.
2. Load test at 1%.
3. Load test at 10%.
4. Practice failures on purpose.
5. Agree contingency modes and owners.
6. Run full scale with forecasting.

## 10. Weak vs strong answer
**Weak:** "I'd build a batch classifier with workers and a scheduler."

**Strong:** "I'd freeze an immutable snapshot, split it into partitions balanced by processing cost, lease them durably, hold backpressure in a rate-limit coordinator, checkpoint for bounded replay, upsert by record key, and agree contingency modes before the run is ever late."

## 11. Candidate scorecard
| Area | 1 | 3 | 5 | Score |
|---|---|---|---|---|
| Problem framing | Throughput only | Names the deadline | Replayable, recovery decisions |  |
| Architecture | Queue and workers | Adds checkpointing | Snapshot, leases, backpressure |  |
| Evaluation | "Job finished" | Throughput tracked | Forecast, duplicates, stragglers |  |
| Production thinking | Run it live | Some alerting | Failure drills, contingency owners |  |
| Communication | Quotes throughput | Mostly clear | 4 a.m. decision first |  |
