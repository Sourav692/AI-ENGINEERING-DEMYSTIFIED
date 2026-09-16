# Observability for a Customer-Facing AI Application - Answer Key

This answer key is designed for interview preparation. It shows what a strong GenAI FDE candidate should ask, design, evaluate, secure, and communicate before moving from demo to production.

## Strong discovery questions
- What exactly counts as "slow" — which latency percentile, measured on which path, for which workflow?
- What counts as "wrong": an incorrect answer, an empty answer, a hallucinated fact, or a tool failure surfaced to the user?
- Which users and tenants are most affected, so instrumentation starts where the pain actually is?
- What is the team allowed to capture by default, and what is contractually or legally off limits?
- Who needs to diagnose a failure — support alone, or must engineering always be pulled in?
- What is the acceptable telemetry overhead before instrumentation starts distorting production behavior?
- What retention window applies to traces, and who may access them under which role?
- What does the executive sponsor need to see to believe quality is improving release over release?

## Strong functional requirements
- Support the core workflow: a support agent moves from a user complaint to the exact request family and explains the failure without seeing raw sensitive content.
- Attach a stable correlation ID to every request and propagate trace context across services, integrations, and queue boundaries.
- Capture per-hop timing across authentication, tenant resolution, retrieval, model call, tool use, post-processing, and delivery.
- Record retrieval evidence, model version, prompt template version, generation settings, and tool outcomes as structured attributes.
- Maintain separate views: an aggregate global dashboard for platform health and tenant-scoped views for customer debugging.
- Tag every request with a user-visible outcome — success, partial answer, or escalation — so complaints map to telemetry.

## Strong non-functional requirements
- Latency: instrumentation must not become the outage; telemetry overhead is a budgeted constraint, not an afterthought.
- Availability: telemetry export failure degrades diagnostics but never blocks the user request.
- Security: full prompts, raw customer documents, and secrets are never captured by default; sensitive fields are classified and hashed before storage.
- Compliance: audit logs answering who accessed what stay separate from debugging traces answering what failed where.
- Reliability: never let a single global sampling rule govern all error paths, or the rare failure that matters disappears.
- Cost: volume scales with request rate, trace rate, retention window, and sampling rate — so the first design decision is what not to collect.

## Architecture explanation
- The design is tracing-first: structured spans and selective redaction, with every request carrying a stable correlation ID from the edge inward.
- A trace collector attaches that ID and captures spans per hop, emitting structured attributes rather than raw text by default.
- A sensitivity classifier runs before durable storage, not after, tagging content and replacing it with a stable salted hash that preserves correlation without retaining the original.
- A retention-bounded trace store holds exported traces, where the retention window doubles as both a cost control and a privacy control.
- Two distinct consumers read that store: a cross-tenant global dashboard showing only aggregates, and tenant-scoped views for support triage.
- A support and access gateway enforces role-based, tenant-scoped access, so diagnosing one customer's incident never exposes another's.
- An audit and redaction pipeline enforces retention and redaction on export, giving defense in depth across code, collector, and review.
- Sampling is a control rather than a compromise: preferential retention for latency-heavy, error-heavy, and anomalous traces, with always-on exemplars.

## Data model / integration assumptions
- Request(tenant_id, prompt, user_id); ExportedTrace(correlation_id, tenant_id, prompt_class, query_hash, spans, result_status) — bounded structured attributes only, never raw prompts.
- Assume classification happens before attachment, tagging content sensitive or non-sensitive before it can ever reach a trace.
- Assume a salted HMAC-SHA256 hash preserves correlation and deduplication across requests without storing any original content.
- Assume telemetry attributes are schema-validated at ingestion, with unknown high-cardinality fields rejected or collapsed into a bounded bucket.
- Assume queue serialization contracts explicitly carry trace context, idempotency key, and tenant scope, or traces will silently break at async handoffs.

## Red-team risks
- sampling drops the only bad trace, high-cardinality tenant IDs, raw prompts in logs, trace context lost at queues, misleading quality metrics
- Uniform random sampling discarding the rare failure that matters most, leaving an incident with no evidence to reconstruct.
- A tenant-ID formatter bug exploding metric cardinality until the metrics backend itself becomes the incident.
- Raw prompts or documents reaching a log sink, turning the observability system into a new exposure surface.
- Trace context breaking at a queue boundary, producing orphan spans and requests that vanish after async handoff.
- Support tooling with weak least-privilege, where one misconfigured view spans every tenant instead of the one under investigation.

## Rollout plan
- Week 0-1: define user-facing SLOs first, with the customer stakeholder signing off on what "good enough" actually means.
- Week 1-2: translate "slow" and "wrong" into measurable definitions tied to a percentile, a path, and an outcome tag.
- Week 2-3: instrument one critical path end to end, proving trace propagation and redaction on a representative request.
- Week 3-4: verify no raw prompt, document, or secret appears in any exported trace through automated scanning.
- Week 5: add the trace-linked support workflow so an agent can move from alert to request family unaided.
- Week 6-8: introduce quality and cost signals with error-class sampling overrides and always-on exemplars.
- After pilot: widen instrumentation only while telemetry overhead and trace coverage both stay inside budget.

## Evaluation plan
| Metric | What it proves | Strong threshold | Dataset / method |
|---|---|---|---|
| Trace coverage | The bad request is actually represented in telemetry | High enough that complaints map to traces | Complaint intake compared with sampled traces |
| Mean time to diagnose | Support can explain a failure without escalating | Falling after the support workflow lands | Incident timeline from report to root cause |
| Redaction pass rate | Observability did not become an exposure surface | Zero raw prompts or secrets in any sink | Automated PII and secret scanners, red-team tests |
| Telemetry overhead | Instrumentation is not distorting production | Within the agreed overhead budget | Latency and cost with and without export |
| Retrieval and tool success | The likely causes of wrong answers are visible | Stable; regressions caught per release | Dependency spans by error class |
| Quality-event rate | User-visible failure is trending the right way | No rise after a release or config change | Escalations and human-reviewed bad outputs |

## Weak answer
I would add more logging across the services and build a dashboard. This is weak because volume is not visibility — it never defines what "slow" or "wrong" mean, has no correlation ID tying a complaint to a request, and makes the telemetry itself a new privacy and cost problem.

## Average answer
I would add distributed tracing with correlation IDs, capture latency per hop, redact sensitive fields, and sample traces to control cost. Support would get a dashboard. This is better, but still incomplete because uniform sampling can drop exactly the failure under investigation, and it does not separate audit access from debugging traces or cap attribute cardinality.

## Strong answer
I would refuse the vague complaint and split it into latency, correctness, and diagnosability. Then I would make the first design decision the unusual one: deciding what we will not collect. Full prompts, raw documents, secrets, and unbounded labels stay out; what goes in is a stable correlation ID, per-hop timing, retrieval evidence, model and prompt-template versions, tool outcomes, and an outcome tag. Classification and salted hashing happen before storage, so correlation survives without retaining content. Sampling is preferential rather than uniform, because the named failure is that sampling drops the only bad trace. The success test is operational: support moves from alert to request family and explains the failure without seeing sensitive content.

## Interviewer scorecard
| Area | 1 - Weak | 3 - Average | 5 - Strong |
|---|---|---|---|
| Problem framing | "Add more logs" | Names latency and errors | Splits slow, wrong, and diagnosable; defines each measurably before designing |
| Requirements | "Log everything" | Lists traces and metrics | Explicit capture and no-capture lists; non-goals; overhead as a constraint |
| Architecture | Logs plus a dashboard | Tracing with correlation IDs | Classifier before storage, bounded retention, global versus tenant views, access gateway |
| Data/integration | Mentions log fields | Names trace attributes | Bounded structured attributes, salted hashing, schema-validated cardinality, queue contracts |
| Evaluation | "We have dashboards" | Tracks latency and errors | Trace coverage, time to diagnose, redaction pass rate, telemetry overhead |
| Safety/security | "We redact PII" | Redacts in code | Defense in depth across code, collector, review; audit separated from debugging traces |
| Rollout | Instrument everything | Instrument then dashboard | SLOs first, one path, trace-linked support workflow, sampling overrides last |
| Communication | Shows the dashboard | Clear but generic | Leads with the dropped-trace failure, names what is not collected, closes with the support test |

## Final 2-minute spoken answer
I would not start with tooling. The customer says the AI is slow and sometimes wrong and they cannot tell why, and that single sentence is really three problems: is the request slow and where in the pipeline, is the answer wrong and is the fault retrieval or generation, and can anyone explain a failure without drowning in telemetry or exposing customer content. So my first two questions are what counts as slow — which percentile on which path — and what counts as wrong, meaning an incorrect answer, an empty one, a hallucinated fact, or a surfaced tool failure. Then I would make the design decision people usually skip: deciding what we will not collect. Full prompts, raw customer documents, secrets, and unbounded free-form labels stay out by default. What goes in is a stable correlation ID and tenant context, per-hop timing, retrieval evidence, model and prompt-template version, tool outcomes, and a user-visible outcome tag. A sensitivity classifier runs before durable storage and replaces content with a salted hash, so correlation survives without retention. The trace store is retention-bounded and feeds two separate consumers — an aggregate global dashboard and tenant-scoped support views behind a least-privilege gateway. The failure drill that anchors this chapter is that sampling drops the only bad trace, so sampling is preferential rather than uniform, with error-class overrides and always-on exemplars. The test of success is operational: support moves from an alert to the exact request family and explains the failure without seeing anything sensitive.
