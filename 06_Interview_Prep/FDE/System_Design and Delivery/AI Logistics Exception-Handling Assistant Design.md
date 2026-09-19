# AI Logistics Exception-Handling Assistant Design

*System Design & Delivery Interviews — Full Worked Tutorial (FDE Round)*

The interview question: you're the FDE embedded with a mid-size logistics customer. They want an AI-powered exception-handling assistant that watches their shipment pipeline, detects disruptions (customs holds, missed carrier scans, weather delays), and either auto-resolves them or drafts a resolution for a human ops agent to approve — across multiple carriers and a mix of real-time and batch data feeds.

This tutorial walks the **full FDE loop end-to-end**, in the order a real interview runs: clarifying questions first, then requirements, capacity, architecture, deep dives, tradeoffs, and a final summary — with a model answer at every stage.

`200 events/sec real-time` · `150 ops agents, 40 concurrent` · `US/EU/APAC` · `EU data residency`

---

## 1 · Define the problem space

**A strong candidate clarifies before proposing an architecture — these four questions decide most of the design below.**

> **Data volume & freshness per carrier?** Mixed. ~60% of carriers push real-time events (webhooks — scan events, status changes), ~200 events/sec combined at peak. The remaining ~40%, mostly smaller regional carriers, only provide batch file drops (CSV/EDI) every 2–6 hours, a few thousand records per drop. → the ingestion layer needs both a streaming path and a scheduled batch path feeding the same pipeline.
>
> **Who are the users, and what's the scale?** Internal only — the customer's own ops team, not their end customers. ~150 ops agents across three shifts, ~40 concurrent at peak during shift handoff, each handling ~30–50 exception cases/day. → low-DAU, high-stakes-per-interaction system; scale pressure comes from event throughput, not concurrent users.
>
> **What's the auto-resolution vs. human-approval boundary?** Value- and confidence-based: under $500 shipment value + high model confidence → auto-resolve. Customs/regulatory holds → always human, no exceptions, regardless of confidence. Over $500 value, or confidence below threshold → always human. → this is the core risk-boundary decision; it defines a policy/guardrail layer that gates every auto-resolution action, with customs treated as a distinct always-gated path rather than just a low-confidence case.
>
> **Regional or multi-tenant topology?** One customer, one assistant experience, but operations span US, EU, and APAC with different carrier sets per region — and EU shipment/customer data cannot leave the EU. → rules out a single global deployment/data store; needs regional data isolation (at minimum for EU) behind one coherent assistant experience.

**✅ Functional** — what the assistant must do:

- Ingest shipment events from carriers, real-time and batch
- Detect disruptions: customs holds, missed scans, weather delays
- Classify each exception by type, value, and confidence
- Auto-resolve low-risk, low-value, high-confidence cases
- Draft a proposed resolution for everything else and route it to a human ops agent
- Let an ops agent approve, edit, or reject a drafted resolution
- Maintain a full audit trail of every decision, automated or human

**⚙️ Non-functional** — the qualities that make it production-grade:

- Regional data residency (EU data never leaves the EU)
- High reliability — a missed exception is a real shipment sitting stuck
- Low latency from disruption detection to draft resolution (ops agents work in near real time during a shift)
- Auditable and compliant — every auto-resolution and every human decision must be traceable
- Cost-efficient at a modest, bounded user scale (150 agents, not millions of consumers)
- Extensible to new carriers without a redeploy of the core pipeline

---

## 2 · High-level architecture

**Two ingestion paths, one exception pipeline, a policy gate before anything acts.**

Carrier data arrives through two paths — real-time webhooks and scheduled batch drops — and both normalize into the same event stream. A Disruption Detection service classifies each event; anything that looks like an exception goes to a Resolution Agent, which drafts an action and a confidence score. A Policy Gate — the auto-resolve vs. human-approval boundary from Section 1 — decides whether that action executes automatically or lands in an ops agent's approval queue. Every path, automated or human, writes to an audit log.

```
Carriers (60% real-time, 40% batch)
        │
   ┌────┴────┐
Webhook   Batch File
Ingest    Ingest (EDI/CSV,
(events)  scheduled)
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
   │            │
   └─────┬──────┘
         │
   Carrier / Ops Systems
   (execute the resolution)
         │
   Audit Log (every decision, automated or human)
```

The Policy Gate is drawn as a first-class component, not a side-check inside the Resolution Agent — it's the one piece the customer explicitly said must never be bypassed for customs cases, so it needs to be independently testable and auditable.

---

## 3 · Ingestion: streaming vs. batch, unified

**Why not force everything onto one path?**

Forcing the 40% batch-only carriers onto a fake "real-time" interface just means polling a file drop every few seconds for no benefit — the data doesn't get fresher, only the infrastructure gets more complex. Instead, both paths converge *after* ingestion, not before.

**🔌 Webhook ingest** — Real-time carriers push scan/status events directly; validated, deduplicated, and pushed onto the event stream immediately. This is the path exception detection needs to be genuinely low-latency on.

**📦 Batch ingest** — Regional carriers' file drops are picked up on their delivery schedule (every 2–6 hours), parsed, and diffed against the last known state per shipment so only *changes* enter the same event stream. A missed scan on a batch carrier is inherently detected late — the design should surface that latency to ops agents rather than hide it, since it changes how urgently they should act on it.

Both paths write to the same normalized event schema, so Disruption Detection never needs to know which path an event came from.

---

## 4 · The Policy Gate — auto-resolve vs. human approval

**The one component the customer explicitly said must never be bypassed.**

```
Resolution Agent output
(action + confidence + shipment value + exception type)
            │
   Is exception type = customs/regulatory?
     │ Yes                    │ No
     ↓                        ↓
 Human Approval        value < $500 AND confidence ≥ threshold?
 Queue (always)          │ Yes                  │ No
                          ↓                      ↓
                     Auto-Resolve          Human Approval Queue
```

The customs check runs *first* and short-circuits everything else — this mirrors the customer's own framing: customs is a hard compliance boundary, not something that should ever compete with a confidence score. Only after that gate does the value/confidence rule apply. This ordering is deliberate and worth stating out loud in an interview: a candidate who checks confidence before the customs carve-out has built a system where, in principle, a high-confidence model could still auto-resolve a customs hold — exactly what the customer ruled out.

---

## 5 · Regional deployment for data residency

**One assistant experience, three isolated data planes.**

EU shipment and customer data cannot leave the EU, so the architecture can't be a single global deployment. The pattern: a shared control plane (agent logic, model routing, policy definitions, UI) deployed identically in each region, paired with a **regional data plane** — event store, vector/embedding store if used for similarity lookups, and audit log — that never replicates data across regions.

```
        Shared Control Plane (logic, policy, UI — versioned identically)
              │                    │                    │
         US Region             EU Region             APAC Region
     (US carrier data,     (EU carrier data,     (APAC carrier data,
      US audit log)         EU audit log —        APAC audit log)
                             never leaves EU)
```

An ops agent in any region sees the same assistant UI and the same policy rules — only the underlying data storage is partitioned. This is the same "shared logic, isolated data" pattern used for any multi-region compliance boundary, and it's worth naming explicitly rather than just drawing three boxes.

---

## 6 · Scaling and reliability

**This system is not scale-constrained by users — it's constrained by event throughput and correctness.**

**🧩 Stateless services** — Detection and Resolution Agent services are stateless, horizontally scalable behind a queue; state lives in the event store and audit log, not in the service instances.

**📬 Event-driven, queue-backed** — Webhook events land on a queue before Disruption Detection consumes them, so a burst of carrier events (e.g. a regional weather event disrupting many shipments at once) smooths into backlog instead of overwhelming the detection service.

**🔁 Idempotency on auto-resolve actions** — Any auto-resolved action (e.g. rebooking a shipment) must be idempotent and carry an idempotency key, since retries after a transient failure must never double-book or double-refund.

**🛑 Circuit breakers on carrier APIs** — When an auto-resolution needs to call a carrier's API to execute an action, wrap that call in a circuit breaker — a flaky carrier API should degrade to "route to human" rather than let retries pile up and delay every other exception behind it.

**🗄️ Batch-path latency budget, made visible** — Because 40% of carriers only report every 2–6 hours, the system's own "time to detect" metric should be tracked separately for real-time vs. batch carriers — averaging them together would hide the fact that a meaningful share of exceptions are detected hours late by design, not by failure.

**⏱️ Human approval queue SLAs** — With only 150 agents and 40 concurrent at peak, the approval queue itself needs monitoring — a queue that grows faster than agents can clear it during shift handoff is a capacity problem the AI layer can't solve by itself, and the design should alert on queue depth, not just on individual event latency.

---

## 7 · Security & governance

**Every auto-resolved action and every human decision must be traceable — this customer's compliance posture depends on it.**

- **Audit log as a first-class store, not a side effect** — every Policy Gate decision (customs → human, value/confidence → auto or human) and every ops agent action (approve/edit/reject) is written immutably, with the model's confidence score and reasoning trace attached.
- **Least-privilege carrier API credentials** — the Resolution Agent's execution path holds only the specific carrier API scopes needed to rebook/reschedule, never broad account-level carrier credentials.
- **Regional access control** — an EU ops agent's session should not be able to query US shipment data and vice versa by default, mirroring the data-residency boundary at the application layer, not just the storage layer.
- **Explainability at the point of human approval** — the drafted resolution shown to an ops agent must include *why* the model proposed it (which signals, which confidence), since an agent approving a black-box suggestion under time pressure is exactly how a wrong auto-suggestion turns into a wrong human decision too.

---

## 8 · Tradeoffs

| Decision                                   | Best use                                                  | Advantages                                                                                          | Tradeoffs                                                                                                                                                                                    |
| ------------------------------------------ | --------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Unified stream (webhook + batch merge)     | Single detection pipeline regardless of carrier feed type | One code path for Disruption Detection; simpler to extend to new carriers                           | Batch-sourced exceptions are detected late by design — must be surfaced, not hidden                                                                                                         |
| Policy Gate as separate component          | Enforcing the customs-always-human rule                   | Independently testable/auditable; customs rule can't be silently bypassed by a confidence-score bug | Extra hop in the critical path vs. embedding the check in the Resolution Agent                                                                                                               |
| Regional data planes, shared control plane | EU data residency + one consistent assistant experience   | Compliant by construction; consistent UX and policy logic everywhere                                | Cross-region reporting/analytics requires an aggregation layer that respects residency (e.g. aggregated metrics only, no raw EU data leaving)                                                |
| Queue-backed ingestion                     | Absorbing bursty carrier event spikes                     | Smooths load spikes into backlog instead of dropping/overwhelming detection                         | Adds latency under normal load; needs monitoring so backlog doesn't silently grow                                                                                                            |
| Idempotent auto-resolve actions            | Any action that touches a carrier booking/refund          | Safe to retry after transient failures                                                              | Requires every downstream carrier integration to support idempotency keys — not all legacy carrier APIs do, which may force some carriers into human-only handling regardless of confidence |

---

## 9 · Final design summary

**The design centers on one non-negotiable: the Policy Gate, everything else is built to feed it correctly and act on its verdict safely.**

Ingestion unifies two very different carrier data shapes — real-time webhooks and multi-hour batch drops — into one event stream, so Disruption Detection has a single interface regardless of carrier maturity. The Resolution Agent proposes an action and a confidence score, but never executes anything directly — that decision belongs to the Policy Gate, which enforces the customer's explicit compliance rule (customs is always human) ahead of the general value/confidence threshold, and which is designed as an independently auditable component precisely because it's the boundary the customer cares about most.

Regional deployment isn't an afterthought bolted on for compliance — EU data residency shapes the architecture from the start, via a shared control plane paired with isolated regional data planes, so the assistant behaves identically for every ops agent while data never crosses a boundary it isn't allowed to. Reliability comes from treating the batch-ingestion path's inherent latency as a first-class, surfaced fact rather than noise to average away, from idempotent auto-resolve actions, and from circuit-breaking flaky carrier APIs down to a safe human-approval fallback rather than letting retries cascade.

> This is a modest-scale, high-stakes system — 150 users, not millions — where the engineering bar isn't raw throughput, it's correctness and auditability at the one decision boundary (auto vs. human) the customer will actually be held accountable for.

---

*Companion mock-interview transcript: [Mock - AI Exception-Handling Assistant.md](<Mock%20-%20AI%20Exception-Handling%20Assistant.md>)*
