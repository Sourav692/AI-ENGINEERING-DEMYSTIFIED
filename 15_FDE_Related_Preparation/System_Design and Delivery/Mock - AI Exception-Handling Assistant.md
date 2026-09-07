# Mock Interview — AI Logistics Exception-Handling Assistant

*FDE System Design mock session, captured from `fde-system-design-mock`.*

## Use Case

You're the FDE embedded with a mid-size logistics customer. They want an AI-powered
exception-handling assistant that watches their shipment pipeline, detects disruptions
(customs holds, missed carrier scans, weather delays), and either auto-resolves them or
drafts a resolution for a human ops agent to approve — across multiple carriers and a mix
of real-time and batch data feeds.

---

## Stage 1 — Clarifying Questions (Requirements Gathering)

### Q1 · Data volume & freshness per carrier

**Asked:** What is the data size we get from each carrier, and is it real-time, batch, or a
mix of both?

**Answer:** Mixed. ~60% of carriers push real-time events (webhooks — scan events, status
changes), roughly 200 events/sec combined at peak. The remaining ~40%, mostly smaller
regional carriers, only provide batch file drops (CSV/EDI) every 2–6 hours, a few thousand
records per drop.

**Implication:** ingestion layer needs to support both a streaming path and a scheduled
batch-ingest path feeding the same downstream pipeline — not a single uniform interface.

### Q2 · Who are the users, and what's the scale?

**Asked:** Who are the end users — internal team or external customers — and what's the
expected DAU/MAU?

**Answer:** Internal only — the customer's own ops team, not their end customers. ~150 ops
agents total across three shifts, ~40 concurrent at peak during shift handoff. Each agent
handles ~30–50 exception cases/day through the assistant.

**Implication:** low-DAU, high-stakes-per-interaction system. Scale pressure comes from
event/data throughput, not from concurrent human users — very different sizing profile from
a consumer-facing assistant.

### Q3 · Auto-resolution vs. human-approval boundary

**Asked:** What are the criteria that decide between auto-resolution and routing to a human
for approval?

**Answer:** Value-based and confidence-based split:
- Under $500 shipment value + high model confidence → auto-resolve (e.g. rebooking a missed
  scan on a known route).
- Customs/regulatory holds → **always** human, regardless of confidence — hard no on
  automation given compliance risk.
- Over $500 value, or confidence below threshold → always human.

**Implication:** this is the core risk-boundary decision for the whole system — it defines a
policy/guardrail layer that has to sit in front of any auto-resolution action, and customs
handling needs to be treated as a distinct, always-gated code path rather than just another
low-confidence case.

### Q4 · Regional / multi-tenant topology

**Asked:** Does this serve across different regions, or does every region get its own AI
assistant?

**Answer:** One customer, one AI assistant *experience*, but they operate across US, EU, and
APAC with different carrier sets per region. Critically: **EU data residency** — shipment
and customer data from EU flows cannot leave the EU.

**Implication:** can't be a single global deployment/data store. Needs regional data
isolation (at minimum for EU) while still presenting one coherent assistant to ops agents —
likely a regional-deployment pattern with a shared control plane, not shared data plane.

---

## Stage 2 — High-Level Architecture

*Not completed.* The candidate ended the mock session right after the interviewer's opening
prompt for this stage (event flow from ingestion — e.g. a missed carrier scan — through to
auto-resolution or the human approval queue) and before giving an answer. No architecture
content to record yet.

**Open prompt that was on the table when the session ended:**
> Walk me through your high-level architecture. What are the major components, and how does
> an event — say, a missed carrier scan — flow through the system from ingestion to either
> auto-resolution or a human agent's queue?

---

## Stages Not Reached

Deep dive & tradeoffs, mid-session curveball, wrap-up, and final scorecard were not run —
the session was exited before the high-level architecture stage was answered.

---

*Resume this scenario later by starting a new `fde-system-design-mock` session and pasting
this doc's use case + Q1–Q4 back in as context, or by picking up directly at the open
architecture prompt above.*
