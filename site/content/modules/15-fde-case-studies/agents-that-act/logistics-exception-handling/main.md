# G17 — Logistics Exception Handling: Main Interview Guide

**Exception handling** is: a shipment should have moved, it didn’t, ops must tell the customer or the carrier. Customs is not a chatbot decision.

**G17 covers one slice:** watch feeds, detect a hold/miss/weather, draft or auto-resolve only what policy allows. Humans always own customs.

End to end, as a missed scan in Frankfurt:

1. **Carrier webhook or batch file** becomes one event.
2. **We detect the exception** and pull shipment value, route, freeze rules.
3. **Policy gate:** weather delay with a known playbook might auto-message; **customs always queues a human.**
4. **Ops sees a draft** — next scan, customer text, proposed carrier call — not a silent write.
5. **Allowed auto-resolve runs once** through a gateway with an audit row.
6. **SAP/weather variants** add more signals; the gate does not get looser.

That’s it: **feed → detect → policy → draft or narrow auto → audit.** “Just ping the carrier for every blip” stays out.

> **Source:** [G17_Logistics_Exception_Handling.md](/modules/15-fde-case-studies/agents-that-act/logistics-exception-handling#full-pack), especially §§1–10. Use the [Deep Dive](/modules/15-fde-case-studies/agents-that-act/logistics-exception-handling#deep-dive) for gate, reliability and evaluation detail and the [Cheat Sheet](/modules/15-fde-case-studies/agents-that-act/logistics-exception-handling#cheat-sheet) for rehearsal.

## Anchor and related case

This is a modest-user, high-stakes exception system. It watches carrier feeds, detects customs holds, missed scans and weather delays, then either drafts for an ops agent or auto-resolves a narrowly allowed case. **Customs and regulatory holds always go to a human.**

| Case | Shared foundation | What changes |
|---|---|---|
| #5 Logistics exception assistant (anchor) | Two feed types, one detection path, resolution draft, independent policy gate | 150 ops agents; value/confidence boundary; EU residency. |
| #66 Shipment rerouting over SAP and weather | Same event normalization, gate, action and audit pattern | SAP becomes source and target, weather adds a predictive signal, 500 regional managers expand the approval surface. |

## Questions to ask the interviewer

| Ask | Design consequence |
|---|---|
| How fresh is each carrier feed and at what peak rate? | Webhook and batch ingestion need different adapters and latency promises. |
| Who acts on a draft, and how many cases arrive per shift? | Sizes the human queue and its SLA. |
| Which cases may auto-resolve, and which are always human? | Defines the policy gate before any carrier write. |
| What are the shipment-value and confidence rules? | Sets the narrow auto path and calibration work. |
| Which regions may store or access shipment data? | Determines regional data planes and application access. |

## Requirements: Functional + Non-Functional

The easiest way to frame requirements in an interview is:

> **Functional = what the system does. Non-functional = how well it does it and what constraints it must satisfy.**

### Functional requirements — what the system must do

1. **Ingest webhooks and CSV/EDI drops.**
2. **Normalize and deduplicate.**
3. **Detect disruptions.**
4. **Propose a resolution** with signals and confidence.
5. **Enforce customs-first, value, and confidence policy.**
6. **Auto-execute only eligible actions**, idempotently.
7. **Let agents approve / edit / reject** all others.
8. **Audit every verdict and action.** New carriers are adapters, not core rewrites.

### Non-functional requirements — how well / under what constraints

| Requirement | Example target / constraint |
|---|---|
| **Safety** | Zero customs holds auto-resolved; missing type/value/confidence → human. |
| **Residency** | EU data stays in EU. |
| **Reliability** | No silently lost exception or double action. |
| **Freshness** | Separate metrics for real-time vs batch feeds. |
| **Latency / cost** | Low time-to-draft; cost per resolved exception. |
| **Security** | Least-privilege carrier credentials. |
| **Load (illustrative)** | ~60% carriers webhooks, ~**200 events/s** combined peak; 40% files every 2–6 h. ~150 agents, ~40 concurrent, 30–50 cases/day. Upper bound ~17.3M events/day vs ~4,500–7,500 human cases/day. Detect cheaply on all events; model only exceptions. |

### Interview shortcut

If asked **“What are the requirements?”**, say:

> **“Functionally, ingest feeds, detect, draft, then a policy gate — customs always human. Non-functionally, no double actions, EU stays in EU, and we don’t call the model on every webhook.”**

## Architecture

The resolution **agent/model drafts** an action and confidence; a separate deterministic policy gate decides whether execution is permitted. Shared versioned logic is deployed into US, EU and APAC regional data planes. EU records and audit data do not replicate out of the EU.

```mermaid
flowchart TB
  W[Carrier webhooks: validate / dedupe] --> N[Normalize event]
  B[Carrier CSV / EDI: parse / diff] --> N
  N --> Q[(Regional durable queue)]
  Q --> D[Disruption detection: rules / classifier]
  D -->|routine| S[Update shipment state]
  D -->|exception| A[Resolution agent: draft + confidence + reasons]
  A --> C{Customs or regulatory hold?}
  C -->|yes or unknown| H[Regional human approval queue]
  C -->|no| V{Value below $500 and confidence high?}
  V -->|no or missing| H
  V -->|yes| E[Idempotent scoped executor]
  H -->|approve or edit| E
  H -->|reject| L[(Regional immutable audit)]
  E -->|carrier circuit open| H
  E --> X[Carrier / ops system]
  C --> L
  V --> L
  H --> L
  E --> L
  P[Shared versioned policy and prompts] -. deployed per region .-> A
  P -.-> C
  P -.-> V
```

### Step-by-step architecture

- Validate and deduplicate webhook events; parse scheduled files and emit only shipment-state differences. Both paths become one regional event schema, with batch detection lag visible.
- Queue normalized events to absorb storms, then use rules or a small classifier to find customs, missed-scan and weather exceptions. Routine scans only update state.
- Send exceptions to the resolution agent for an action draft, confidence and supporting signals. The agent cannot call carrier write APIs directly.
- The independent gate checks customs/regulatory status **first**, using detection's type rather than the agent's label. Any customs or unknown case goes to a human.
- For non-customs cases, only shipment value under $500 and confidence above the agreed threshold may auto-resolve; all others enter the regional approval queue.
- An approved or eligible action uses scoped carrier credentials, an idempotency key and a circuit breaker. A flaky or non-idempotent carrier falls back to human handling.
- Log every verdict, draft, approval/edit/rejection and execution in the regional audit store; keep EU data and access within the EU.

## Decisions, failures and evaluation

**Customs is an invariant, not a threshold.** A high-confidence model cannot override it. A missing field fails to the human queue, and an unavailable audit store blocks action. A legacy carrier that cannot honor an idempotency key may need human-only handling because a timeout can otherwise cause double booking. A circuit breaker moves carrier failures to human review rather than retrying into a storm.

**Two feed clocks:** polling a batch-only carrier every few seconds cannot make its 2–6-hour file arrive sooner. Keep separate time-to-detect p50/p95 for webhook and batch feeds. Show lateness on the draft. Queue depth and approval age are separate operational SLOs.

**Release evidence:** replay labeled historical exceptions for recall and precision per type; adversarial customs cases must produce **zero auto-resolutions**; calibrate confidence above the auto threshold; test duplicate execution, EU-to-US access denial and audit completeness. Start offline, then shadow with all human actions, then one region/one integrated carrier for known-route missed scans. For rerouting benefit, use a matched holdout: the route not taken is not directly observable.

**Cost and latency:** keep model calls behind detection; template common missed-scan rebooks; cap agent steps, carrier calls and retries; route difficult human-read drafts to a stronger model only when useful. Cost scales with exceptions, not routine scan volume. During a weather burst, prioritize backlog by value and deadline and scale stateless detection; the human approval queue may become the real bottleneck.

## Two-minute interview answer

“I would ask about feed freshness, the human boundary, shipment value rules and regional residency first. Webhook and batch carriers get different adapters but converge on one normalized, regional queue; batch changes are diffed and their lateness is surfaced. Cheap detection finds exceptions, and only then does a resolution agent draft an action with confidence and reasons. An independent gate checks customs first and always sends it to a human. For other cases, only under-$500, high-confidence actions may auto-resolve. Execution is idempotent, scoped and circuit-broken, with every verdict and action audited in-region. I would prove the customs invariant offline, shadow all actions, then enable one narrow auto-resolve cohort while watching outcome, delay and reversal rates.”
