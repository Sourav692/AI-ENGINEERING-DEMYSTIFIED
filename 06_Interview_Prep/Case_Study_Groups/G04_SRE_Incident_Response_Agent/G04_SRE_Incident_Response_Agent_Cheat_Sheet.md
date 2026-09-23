# G04 — SRE Incident Response Agent: Cheat Sheet

Use the [Main guide](G04_SRE_Incident_Response_Agent_Main.md) to practice speaking and the [Deep Dive](G04_SRE_Incident_Response_Agent_Deep_Dive.md) for technical follow-ups. The [source](G04_SRE_Incident_Response_Agent.md) is the full reference.

## One sentence

**Query anything authorized, change nothing autonomously; dedupe first, show evidence and source gaps, stage mitigation for human approval.**

## Flow

**Alerts → dedupe/correlate → cap per-service investigations → parallel read-only telemetry → typed coverage → ranked hypothesis + evidence → proposal → owner/commander approval → gateway → verify effect/timeline.**

**LLM/agent role:** Rules or a small model dedupe alerts; the strong LLM synthesizes hypotheses. The incident agent proposes mitigation, and humans approve production writes.

## Ask first

Which alert class? Who approves? Which sources and owners? What is read-only? Burst and first-output target? Required evidence/simulation? Pilot oracle? Audit and rollback?

## Source planning numbers

**1,200 alerts/day average; 400 alerts/90 s burst; <30 s first useful summary; 3–8 s interactive follow-up.** A ~10-second human approval can be acceptable mid-incident.

## Five tool states

`SUCCESS` data · `EMPTY` searched, no match · `UNAVAILABLE` source did not answer · `DENIED` no permission · `INVALID` bad arguments.

**EMPTY ≠ UNAVAILABLE.** Every summary reports source coverage. Do not explain a denial to the model.

## Three boundaries

1. Dedupe before any model call.
2. Read-only investigation before human approval.
3. One gateway for every approved write; run outside affected blast radius.

## Proposal must include

Exact command + computed blast radius + evidence + runbook + change-freeze check + simulation/dry run + rollback path. Missing approval, permission, or required simulation means no execution.

## Failure card

Telemetry down → report `UNAVAILABLE` and lower confidence. Alert storm → attach to cluster, visible queue. Stale runbook → warn/block proposal. Injection in logs → data, not instructions. Approval/policy down → fail closed on writes.

## Release and rollout

**Hypothesis precision from post-incident review** is the falsifying metric. Track <30 s under burst, coverage on every run, reversal rate, citations, zero unauthorized tools/permission violations. Historical golden set → shadow → live read-only → approved low-risk actions.

## Latency answer

Send less raw telemetry: pre-aggregate, cap lookback, parallelize reads, stream ranked hypotheses, reserve the strong model for synthesis. At 10×, telemetry quotas and provider limits bind before average daily alert count.

## Interview close

“The agent buys responders a fast, evidence-backed first view while the observability stack may be failing. It suggests the next safe check or mitigation; humans approve production changes.”
