# AI System for an Air-Gapped Environment - Case Study Worksheet

## 1. Interview prompt
Design a GenAI FDE solution for an **Air-Gapped Environment**: AI capability inside a network that cannot reach the internet. The boundary is not a constraint on the design — it is the design.

## 2. Clarify the customer problem
- What classification level applies, and what handling rules follow?
- What hardware is available locally, and is it fixed?
- How do artifacts enter: scanned, approved, signed, rolled in?
- What identity, storage, and directory services exist inside?
- What are the logging, retention, and recovery limits?

## 3. Users and workflows
| User | Workflow | Current pain | AI assist opportunity | Human approval needed? |
|---|---|---|---|---|
| Analyst (end user) |  |  |  |  |
| Operations / IT admin |  |  |  |  |
| Security / compliance officer |  |  |  |  |
| Program sponsor |  |  |  |  |

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
- Build and signing:
- Transfer inspection:
- Offline registry:
- Orchestration:
- Document pipeline:
- Local telemetry:

## 7. Evaluation plan
| Metric | Good threshold | Bad threshold | Test dataset | Owner |
|---|---:|---:|---|---|
| Signature verifications | 0 failures admitted | Any admitted | Transfer-hop logs | Security |
| Offline install success | Consistently clean | Any outside reach | Staging installs | Platform eng |
| Capacity saturation | Below threshold | Sustained above | GPU and queue telemetry | Operations |
| Analyst time per case | Improves vs. baseline | Flat or worse | Local case timings | Sponsor |

## 8. Failure modes
- Missing transitive package blocks install
- Artifact corrupted during transfer
- Model exceeds available GPU memory
- Local certificate expires
- Update breaks stored-index compatibility
- Library assumes telemetry egress

## 9. Rollout plan
1. Staging mirrors production exactly.
2. Rehearse the transfer drill.
3. Document the handoff repeatably.
4. Single-node canary on real traffic.
5. Prepare and test rollback bundle.
6. Expand while gates hold.

## 10. Weak vs strong answer
**Weak:** "I'd run the model on-premises behind a firewall."

**Strong:** "I'd treat the offline release pipeline as a high-trust control plane: pin and attest every dependency, verify signatures against offline trust roots, keep telemetry local, fail closed on an incomplete bundle, and prepare rollback as a tested artifact."

## 11. Candidate scorecard
| Area | 1 | 3 | 5 | Score |
|---|---|---|---|---|
| Problem framing | Air gap as firewall | Offline deployment | Boundary is the design |  |
| Architecture | One container | Registry and mirror | Build/offline split, canary |  |
| Evaluation | "It works offline" | Install checks | Signatures, saturation, time saved |  |
| Production thinking | Install and leave | Some monitoring | Tested rollback, fail-closed policy |  |
| Communication | Vendor-centric | Mostly clear | Failure and gate first |  |
