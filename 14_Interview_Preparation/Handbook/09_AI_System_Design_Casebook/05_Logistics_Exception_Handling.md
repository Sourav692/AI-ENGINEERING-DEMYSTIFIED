# Case 5 — AI Logistics Exception-Handling Assistant (the FDE round)

> **Level** 🔴 Design Mastery · **Module** 09 · **Doc** 5 of 6 · **Time** ~35 min
> **Prerequisites:** Module 00 doc 3, Module 02 doc 5, Module 05, Module 06 doc 4
> **Source material:** `4. FDE_Related_Preparation/System_Design and Delivery/AI Logistics Exception-Handling Assistant Design.md`; `Mock - AI Exception-Handling Assistant.md`

## The prompt

You are the FDE embedded with a mid-size logistics customer. They want an AI exception-handling assistant that watches their shipment pipeline, detects disruptions — customs holds, missed carrier scans, weather delays — and either auto-resolves them or drafts a resolution for a human ops agent to approve, across multiple carriers and a mix of real-time and batch feeds.

This case is different from the previous four. It is framed as an **FDE round**, and it is worked in the order a real interview runs — clarifying questions first, with the *answers* recorded and each one's implication drawn out — because in this format the questions *are* the design.

## Step 1 — The four clarifying questions that decide the design

| Asked | Answer | Implication |
|---|---|---|
| **Data volume and freshness per carrier?** | Mixed. ~60% of carriers push real-time webhooks — scan events, status changes — ~200 events/s combined at peak. ~40%, mostly smaller regional carriers, provide batch file drops (CSV/EDI) every 2–6 hours, a few thousand records each | Ingestion needs **both** a streaming path and a scheduled batch path feeding the same pipeline — not a single uniform interface |
| **Who are the users, and what scale?** | Internal only — the customer's ops team. ~150 agents across three shifts, ~40 concurrent at peak during shift handoff, each handling 30–50 cases a day | **Low-DAU, high-stakes-per-interaction.** Scale pressure comes from event throughput, not concurrent users — a very different sizing profile from a consumer assistant |
| **What is the auto-resolve vs human-approval boundary?** | Value- and confidence-based: under $500 shipment value + high confidence → auto-resolve. **Customs/regulatory holds → always human, regardless of confidence.** Over $500, or below the confidence threshold → always human | **The core risk-boundary decision.** It defines a policy layer in front of every auto-resolution, with customs as a distinct always-gated path — not just a low-confidence case |
| **Regional or multi-tenant topology?** | One customer, one assistant experience, operating across US, EU and APAC with different carriers per region — and **EU data cannot leave the EU** | Rules out a single global deployment or data store. Regional data isolation behind one coherent experience |

Notice how each answer moved a box. That is the adaptation Module 00 called the signal.

**Functional:** ingest carrier events, real-time and batch; detect disruptions; classify by type, value, confidence; auto-resolve low-risk cases; draft a resolution for everything else and route to an agent; approve/edit/reject; full audit trail. **Non-functional:** EU residency; reliability (a missed exception is a stuck shipment); low latency from detection to draft; auditability; cost-efficient at a bounded scale; extensible to new carriers without redeploying the core.

## Step 2 — High-level architecture: two ingestion paths, one pipeline, a policy gate before anything acts

```
Carriers (60% real-time, 40% batch)
        │
   ┌────┴────┐
Webhook   Batch File
Ingest    Ingest (EDI/CSV, scheduled)
   │         │
   └────┬────┘
        │
Event Normalization & Stream
        │
Disruption Detection Service
   (customs hold · missed scan · weather delay)
        │
Resolution Agent
 (drafts action + confidence score)
        │
   Policy Gate
 (value + confidence + always-human customs rule)
   │            │
Auto-Resolve   Human Approval Queue
   │            │  (ops agent: approve / edit / reject)
   └─────┬──────┘
         │
   Carrier / Ops Systems (execute the resolution)
         │
   Audit Log (every decision, automated or human)
```

**The Policy Gate is drawn as a first-class component, not a side-check inside the Resolution Agent** — it is the one piece the customer said must never be bypassed for customs, so it must be independently testable and auditable. Module 05's guardrail engine, as a box.

## Step 3 — Deep dive A: ingestion, streaming and batch unified

Why not force everything onto one path? Forcing the 40% batch-only carriers onto a fake "real-time" interface means polling a file drop every few seconds for no benefit — the data gets no fresher, only the infrastructure gets more complex. Both paths converge *after* ingestion. Module 05's channel adapters, over carrier feeds.

- **Webhook ingest** — validated, deduplicated, pushed onto the stream immediately. The path detection must be genuinely low-latency on.
- **Batch ingest** — picked up on the carrier's schedule, parsed, **diffed against last known state per shipment so only changes enter the stream.** A missed scan on a batch carrier is inherently detected late — **surface that latency to agents rather than hide it**, because it changes how urgently they should act.

## Step 4 — Deep dive B: the Policy Gate

```
Resolution Agent output (action + confidence + shipment value + exception type)
            │
   Is exception type = customs/regulatory?
     │ Yes                    │ No
     ↓                        ↓
 Human Approval        value < $500 AND confidence ≥ threshold?
 Queue (always)          │ Yes                  │ No
                          ↓                      ↓
                     Auto-Resolve          Human Approval Queue
```

**The customs check runs first and short-circuits everything else.** This mirrors the customer's own framing: customs is a hard compliance boundary, not something that competes with a confidence score. Only after that gate does the value/confidence rule apply. **State the ordering out loud:** a candidate who checks confidence before the customs carve-out has built a system where, in principle, a high-confidence model could auto-resolve a customs hold — exactly what the customer ruled out. Same structure as Module 04's deny-rules-first, and Module 02's short-circuiting.

## Step 5 — Regional deployment for data residency

EU data cannot leave the EU, so a single global deployment is out. The pattern: a **shared control plane** — agent logic, model routing, policy definitions, UI — deployed identically in each region, paired with a **regional data plane** — event store, any vector store, audit log — that never replicates across regions.

```
        Shared Control Plane (logic, policy, UI — versioned identically)
              │                    │                    │
         US Region             EU Region             APAC Region
     (US carrier data,     (EU carrier data,     (APAC carrier data,
      US audit log)         EU audit log —        APAC audit log)
                             never leaves EU)
```

An agent in any region sees the same UI and the same policy; only storage is partitioned. Name the pattern — *shared logic, isolated data* — rather than just drawing three boxes. Module 06 doc 4's tenancy ladder, at the region level.

## Step 6 — Scaling and reliability

This system is not scale-constrained by users; it is constrained by **event throughput and correctness.**

- **Stateless** detection and resolution services behind a queue; state in the event store and audit log.
- **Queue-backed ingestion** — a regional weather event disrupting many shipments at once smooths into backlog instead of overwhelming detection.
- **Idempotency on auto-resolve actions** — rebooking a shipment must carry an idempotency key; a retry after a transient failure must never double-book or double-refund. Module 05 doc 4.
- **Circuit breakers on carrier APIs** — a flaky carrier should degrade to *"route to human"*, not pile up retries that delay every other exception behind it. Module 06 doc 2.
- **Batch-path latency, made visible** — track time-to-detect *separately* for real-time and batch carriers; averaging hides that a meaningful share are detected hours late by design.
- **Approval-queue SLAs** — with 40 concurrent agents, a queue that grows faster than agents clear it during shift handoff is a capacity problem the AI cannot solve. Alert on queue depth, not just event latency.

## Security and governance

- **Audit log as a first-class store** — every Policy Gate decision and every agent action, immutable, with the model's confidence and reasoning attached.
- **Least-privilege carrier credentials** — only the scopes needed to rebook or reschedule, never broad account credentials. Module 06 doc 1.
- **Regional access control** — an EU agent's session cannot query US data and vice versa by default, mirroring residency at the application layer too.
- **Explainability at the point of approval** — the drafted resolution must show *why* the model proposed it; an agent approving a black box under time pressure is how a wrong suggestion becomes a wrong human decision.

## Trade-offs

| Decision | Advantage | Trade-off |
|---|---|---|
| Unified stream (webhook + batch) | One detection code path; simpler to add carriers | Batch exceptions detected late by design — must be surfaced |
| Policy Gate as a separate component | Independently testable; customs rule cannot be bypassed by a confidence-score bug | Extra hop in the critical path |
| Regional data planes, shared control plane | Compliant by construction; consistent UX and policy | Cross-region reporting needs an aggregation layer that respects residency |
| Queue-backed ingestion | Absorbs bursts | Latency under normal load; backlog needs monitoring |
| Idempotent auto-resolve | Safe to retry | Every carrier integration must support idempotency keys — legacy ones may not, forcing some carriers to human-only |

## Summary

**The design centres on one non-negotiable: the Policy Gate. Everything else feeds it correctly and acts on its verdict safely.** Ingestion unifies two very different carrier shapes into one stream. The Resolution Agent proposes and never executes — that decision belongs to the gate, which enforces the customs rule ahead of the value/confidence threshold and is independently auditable because it is the boundary the customer will be held accountable for. Regional deployment shapes the architecture from the start. Reliability comes from treating batch latency as a surfaced fact, idempotent actions, and circuit-breaking flaky carriers down to a safe human fallback.

A modest-scale, high-stakes system — 150 users, not millions — where the engineering bar is correctness and auditability at one decision boundary.

## The mock transcript

The source folder includes a captured mock session that ran Stage 1 (the four questions above, with implications) and ended at the opening architecture prompt: *"Walk me through your high-level architecture. What are the major components, and how does an event — say, a missed carrier scan — flow through the system from ingestion to either auto-resolution or a human agent's queue?"* Use this document as the model answer, and practise picking up from exactly that prompt.

## Checkpoint

- For each of the four clarifying answers, name the box it moved.
- Why is the Policy Gate a separate component, and what is the ordering rule inside it?
- Explain the shared-control-plane / regional-data-plane pattern and what it costs.
- Why track time-to-detect separately for batch carriers?
- Which two Module 05 mechanisms appear here, and which Module 06 one?

**Next →** [The Agentic Coverage Map](06_Agentic_Coverage_Map.md)
