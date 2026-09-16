# AI System for an Air-Gapped Environment - Answer Key

This answer key is designed for interview preparation. It shows what a strong GenAI FDE candidate should ask, design, evaluate, secure, and communicate before moving from demo to production.

## Strong discovery questions
- What classification level is the data, and what handling rules govern storing text, retaining prompts, or caching outputs?
- What hardware is available locally, since that decides whether a larger model, a smaller one, or a retrieval-heavy workflow is feasible?
- What quality target and latency does the human workflow need — assist tool, batch analyst, or near-interactive copilot?
- How are artifacts imported, approved, scanned, signed, and rolled in, because that governs how fast a vulnerability can be patched?
- What identity system exists locally, and which storage or directory services can the application rely on?
- What are the logging, retention, backup, and disaster-recovery limits inside the network?
- Which business outcome can the customer verify locally without trusting a vendor-reported number?
- Who operates this at 2 a.m. without the build team, and what must they be able to fix alone?

## Strong functional requirements
- Support the core workflow: an analyst submits a document inside the enclave and receives classification, extraction, or redaction with no runtime internet dependency.
- Package the model and service offline, so the full runtime deploys from one bundle without reaching outside.
- Sign and version every artifact, so each model, container, and dependency traces to an approved release.
- Run a local registry and dependency mirror, so installs and redeploys never leave the enclave.
- Integrate local identity, so access control follows the customer's approved accounts and groups.
- Provide an auditable update and rollback ceremony, so every promotion can be reviewed and reversed.

## Strong non-functional requirements
- Latency: budget end to end across upload, preprocessing, retrieval, inference, validation, and rendering; if inference dominates, shrink the model or context.
- Availability: elasticity is limited or absent, so capacity must be right up front — size against the 20 QPS peak, not the average.
- Security: pin and attest every dependency, verify signatures against offline trust roots, and separate privileged administration from normal user workflow.
- Compliance: append-only audit answering who did what, to which artifact hash, and when, retained to local policy.
- Reliability: fail closed on incomplete or corrupted bundles and keep the current release running rather than improvising.
- Cost: `Replicas = ⌈(QPS × Tokens_request) / (TokensPerSecond_replica × UtilizationTarget)⌉` — when the answer exceeds the fixed pool, change the workload, not the hardware ask.

## Architecture explanation
- The design is two worlds joined by one controlled path; the trust boundary runs between the connected build environment and everything else.
- The connected build environment assembles source, pinned dependencies, and model artifacts into a reproducible bundle before export.
- An artifact signing service produces verifiable attestations and signatures for whatever crosses the boundary.
- A transfer staging zone quarantines and inspects the bundle for integrity, policy conformance, and chain of custody before admission.
- Inside, signatures are verified against offline trust roots and approved content lands in a local registry and package mirror, the offline source of truth.
- A local orchestrator schedules services, enforces deployment policy, and manages canary rollout against a limited slice of traffic.
- The model server and document pipeline do the work — ingestion, OCR and parsing, chunking, retrieval, scoring, redaction, result assembly.
- A local identity provider and local telemetry stack complete the enclave; nothing exports externally, and a cache must never outrank the registry as truth.

## Data model / integration assumptions
- ReleaseManifest(version, artifact_hashes, signatures, dependencies); ModelDeployment(model_id, version, hardware, status); OfflineAuditEvent(actor, action, artifact_hash, time).
- Assume ownership splits cleanly: the build team owns signed release material until handoff, the offline runtime owns deployment state, security owns the audit trail.
- Assume deployment history is retained long enough to answer "what was running when this document was analyzed?"
- Assume OfflineAuditEvent is append-only and never edited in place, since it is the only way to reconstruct an incident without a vendor console.
- Assume promotion uses optimistic concurrency with a revision token, so two operators cannot promote incompatible releases at once.

## Red-team risks
- missing transitive package, artifact corrupted in transfer, telemetry quietly phoning home, expired local certificate, index-model incompatibility
- A missing transitive dependency tempting someone to reach outside the boundary; the system must fail closed and block promotion instead.
- Artifact corruption between hops, so hashes and signatures are verified after every transfer, not only at the source.
- Libraries assuming telemetry egress, where crash reporting or cloud diagnostics quietly violate the boundary while looking like monitoring.
- Privileged administration treated as routine, when key rotation, trust-root updates, index rebuilds, and rollback promotion all need explicit audited approval.
- A "temporary" workaround becoming permanent — the failure the security officer fears most, and the one accreditation review will find.

## Rollout plan
- Week 0-1: fix scope and non-goals — no live internet calls, no ad hoc dependency fetching, no self-updating agents, no cloud observability.
- Week 1-2: build a staging environment that matches production node class, storage layout, GPU profile, OS image, and trust roots.
- Week 2-3: rehearse the transfer and import drill end to end, verifying signatures offline and installing without reaching outside.
- Week 3-4: document the handoff so it is repeatable and auditable, because "someone will hand-carry it" is not a process.
- Week 5: run a single-node canary that serves real traffic and meets agreed health thresholds across a defined observation window.
- Week 6-8: prepare the rollback bundle as an artifact — previous known-good release, signatures, operator checklist, escalation path — and test it.
- After pilot: expand nodes only while install success, signature verification, and capacity saturation hold, keeping release age monitored.

## Evaluation plan
| Metric | What it proves | Strong threshold | Dataset / method |
|---|---|---|---|
| Offline install success rate | A bundle installs cleanly with no outside reach | Consistently clean on representative staging | Repeated installs on production-matched nodes |
| Signature verification failures | Nothing unverified entered the enclave | Zero admitted; every failure quarantined | Verification logs at each transfer hop |
| Model throughput and latency | The fixed GPU pool actually meets the workflow | Within the interactive or batch SLO | Load test at the 20 QPS peak |
| Capacity saturation | Headroom survives a large document or burst | Below the admission threshold | GPU and queue telemetry |
| Release age and MTTR | The enclave can still be patched and repaired | Within agreed patch and recovery windows | Release ledger and incident records |
| Analyst time saved per case | The workflow improved in terms the customer verifies | Measurable local reduction versus baseline | Local case-turnaround measurement |

## Weak answer
I would deploy the model on-premises behind a firewall and serve documents locally. This is weak because it treats the air gap as a network setting rather than the organizing constraint, saying nothing about how artifacts legally enter, how dependencies are attested, or how updates roll back.

## Average answer
I would package the model and service into a container, sign it, move it across the boundary, and run it locally with a package mirror and local identity. I would keep logs on-premises. This is better, but still incomplete because it does not define what fails closed, how a bad release is reverted under approval delay, or how capacity is sized against a fixed GPU pool.

## Strong answer
I would treat the boundary as the system design, anchored to one sentence: maintainable local AI capability without violating network, artifact, identity, or audit boundaries. That makes the offline release pipeline a high-trust control plane — every dependency pinned and attested, signatures verified against offline trust roots, telemetry local-first, privileged administration separated from normal use. The riskiest failure is an incomplete or corrupted bundle, so the system fails closed, preserves evidence, and keeps the current release intact. I would size honestly against the fixed GPU pool and change the workload shape rather than ask for hardware that cannot arrive. The first gate: if a bundle cannot prove integrity, completeness, and compatibility offline, it does not enter.

## Interviewer scorecard
| Area | 1 - Weak | 3 - Average | 5 - Strong |
|---|---|---|---|
| Problem framing | Treats air gap as a firewall setting | Names offline deployment and local identity | Boundary is the design; outcome stated in terms the customer verifies locally |
| Requirements | "Run it on-premises" | Lists offline packaging and signing | Must-have list, explicit exclusions, constraints separated from preferences |
| Architecture | One container on a server | Registry, orchestrator, model server | Nine components in dependency order across the build/offline split with trust boundaries |
| Data/integration | Mentions versions | Names manifest and deployment | ReleaseManifest, ModelDeployment, append-only audit, ownership boundaries, optimistic concurrency |
| Evaluation | "It works offline" | Install and latency checks | Install success, signature failures, saturation, release age, analyst time saved |
| Safety/security | "It is air-gapped, so it is safe" | Adds signing and local logs | Pinned attested dependencies, no egress assumptions, privileged admin as a high-risk interface |
| Rollout | Install and hand over | Stage then deploy | Production-matched staging, rehearsed transfer drill, single-node canary, tested rollback bundle |
| Communication | Vendor-centric | Clear but generic | Leads with the failure, names fail-closed policy, closes with the admission gate |

## Final 2-minute spoken answer
I would not start with the model. In an air-gapped environment the boundary is not a limitation layered on top of an otherwise normal AI system — it is the system design, so every decision gets argued against it rather than around it. I would restate the outcome as providing maintainable local AI capability without violating network, artifact, identity, or audit boundaries, then test every later choice against that sentence. Architecturally there are two worlds joined by one controlled path. On the connected side, a build environment assembles pinned dependencies and model artifacts, and a signing service attests whatever will cross. A transfer staging zone quarantines and inspects the bundle. Inside the enclave, signatures are verified against offline trust roots, approved content lands in a local registry and package mirror that is the source of truth, an orchestrator deploys a canary, acceptance tests run, and only then does it promote or roll back. Identity and telemetry stay local; nothing phones home. The named drill is a missing transitive package: the system fails closed, blocks promotion, keeps the current release running, and quarantines the bundle rather than improvising a reach outside. On capacity I would be honest — with a fixed GPU pool the sizing formula quickly produces an uncomfortable replica count, and the right response is to challenge the request profile and move work offline, not to ask for hardware that cannot arrive. The first production gate is that a bundle proves integrity, completeness, and compatibility offline, or it does not enter.
