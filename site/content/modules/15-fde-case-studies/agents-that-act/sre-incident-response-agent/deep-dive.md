# G04 — SRE Incident Response Agent: Deep Dive

The [Main guide](/modules/15-fde-case-studies/agents-that-act/sre-incident-response-agent#main) is the spoken answer. This is its technical backup; the unchanged [source case](/modules/15-fde-case-studies/agents-that-act/sre-incident-response-agent#full-pack) has the complete reference and interview scripts.

**Model and agent roles:** Rules or a small model collapse alerts before the strong LLM synthesizes ranked hypotheses from bounded, read-only telemetry. The incident agent may propose a mitigation, but only human approval plus the gateway permits a write.

## 1. Telemetry map and dependency inversion

| Source | Useful facts | Likely incident failure |
|---|---|---|
| Prometheus/Grafana | Metrics and alert rules | Query storm as the metrics store struggles. |
| Datadog/New Relic | APM, metrics, logs | Rate limits and ingestion lag. |
| Application/infra logs | Error signatures and event detail | PII/secrets and context overflow. |
| Distributed traces | Failing call path | Sampling omits failing request; backend degraded. |
| Kubernetes | Pod events, rollout state | Read credentials too close to write scope. |
| CI/CD and deploy metadata | Recent version/commit/deploy | Mid-flight deploy or missing metadata. |
| Feature flags | Flag flip history | Change masquerades as code regression. |
| PagerDuty/Jira and incident history | Alerts, prior response | Duplicate incidents, stale owner. |
| Runbooks | Approved checks and mitigations | Stale step or injection in text. |

The agent runs outside the affected blast radius and assumes any telemetry source may be partially unavailable. Every record needs stable ID, owner, updated time, and ACL metadata; exclude an unmapped source. Redact sensitive log fields before context assembly. Feedback stays separate from ground truth until SME/post-incident approval.

Core records: `Alert`, `Signal`, `Deployment`, `Runbook`, `ActionProposal`, `IncidentTimeline`, and `SourceCoverage(investigation_id, source, status)`. Source coverage is part of the answer, not just operational telemetry.

## 2. Intake, correlation, and context budget

The source’s 1,200 alerts/day average is less important than **400 in 90 s**. Group by service and time window; attach new alerts to an active cluster; cap concurrent investigations per service. Rules or a small model do this before any strong-model call. One good investigation per correlated incident beats hundreds of shallow ones and protects the telemetry backend.

Pre-aggregate before prompting: bucket metrics, count log signatures, sample traces, diff deployments, cap lookback. Keep raw slices available through read tools when a hypothesis needs them. The strong model synthesizes ranked causes from a bounded evidence set, with citations and missing-source disclosure. A citation-free cause is a refusal or a low-confidence hypothesis, not a finding.

## 3. Tool result contract and gateway

Use five typed states: `SUCCESS` (data), `EMPTY` (query succeeded, no match), `UNAVAILABLE` (source did not answer), `DENIED` (caller lacks authority), `INVALID` (bad arguments). A string result hides the difference. `EMPTY` versus `UNAVAILABLE` prevents false confidence and retry storms. `DENIED` must not reveal a workaround; log the human-readable reason outside model context.

An approved write takes one route: **authorize → validate → execute with timeout and idempotency key → classify → trim to declared fields → log**. Authorization comes first to avoid revealing a protected schema to a denied caller. An example idempotency seed is a hash of run ID, tool name, and canonical arguments. Read tools use scoped read-only credentials. Write tools appear only for the current rollout stage and remain behind approval.

## 4. Proposal and human boundary

An action proposal contains exact command, service/owner, computed blast radius, supporting signals, runbook, change-freeze status, simulation or dry-run result, rollback path, and expiry. A missing blast radius or required simulation blocks the proposal. Service owner and incident commander review; approval and decision time are logged. A freeze owner must approve work during a declared freeze. The model may recommend; the gateway and approvers decide.

The agent’s timeline records alert IDs, queried signals, reached/missed sources, hypotheses, confidence, proposals, approvals, executed command, outcome, model/prompt version, and policy state. That supports post-incident review of both correct and wrong calls.

## 5. Latency arithmetic and 10× growth

First useful output target is **under 30 s** from alert receipt; interactive follow-up **3–8 s**. Example slices from the source: dedupe/correlation <1 s, context ~1–2 s, parallel queries ~5–10 s for the slowest source, strong synthesis ~10–15 s with streaming. Pre-aggregation runs as results arrive. Citation verification stays inline for proposals; explanatory text can use an async check if policy allows it.

For a slow prototype, trace auth, retrieval, rerank, model, tools, verification. Parallelize independent reads, cache versioned catalog/deploy context, reduce candidate count, stream useful partials, and remove diagnostics that do not change the hypothesis. Avoid serial reasoning loops in a live incident. At 10× alert volume, correlation load rises but strong-model calls should follow incident clusters, not raw alert count. Provider quota and telemetry rate limits likely bind; source coverage exposes degradation early.

## 6. Failure ladder

| Source/guard failure | Visible behavior |
|---|---|
| Metrics down | `UNAVAILABLE` by deadline, metrics omitted from evidence, lower confidence. |
| Logs rate-limited | Sampled signatures, logs marked partial. |
| Traces degraded | Use metrics/deploy diff without waiting. |
| Deploy context missing | Say deploy correlation was unavailable. |
| Runbook stale | Warning and lower-confidence/blocked proposal. |
| Model down | Bounded secondary provider route; investigation stays read-only. |
| Approval/policy/credential service down | No execution; proposal waits or expires. |
| Injection in runbook/log | Content remains data, flagged chunk excluded; no new tool authority. |

Choose the degradation rung by a deterministic health snapshot, disclose it to the responder, and emit it as a trace attribute. Trip a source breaker on windowed failure rate with minimum sample size; consecutive-failure triggers misbehave under bursty incident traffic. Permission uncertainty and writes fail closed. Telemetry gaps degrade visibly.

## 7. Evaluation, red team, and rollout

The oracle is post-incident review. **Hypothesis precision** is the falsifying metric: low precision makes responders ignore the assistant. Also track first useful output, coverage on every run, approval time, later reversal rate, groundedness, citations, task completion, permission violations, unsafe tool calls, and cost/investigation. Example source targets include ≥90% grounded claims, ≥95% citations, ≥95% correct high-risk escalation, ≥80% task completion, and zero permission or unapproved-write violations; agree per-class thresholds before launch.

Red-team wrong-service commands, unsupported causes, leaked secrets/PII, alert noise, injected runbooks/logs, different user roles on the same alert, freezes, and stale contradictory runbooks. Offline cases cannot detect every small regression: shadow live alerts, pin model versions, canary changes, and roll back on disagreement or a harmful proposal.

Week one: one alert class, named source owners, historical incidents and SME labels, no write path. Then shadow summaries, live read-only with citations/coverage, draft timelines or approved low-risk actions, and expansion only while precision, latency, and safety hold. A responder ignoring output is a rollback signal, not merely an adoption metric.

## 8. Interview pivots

- **“Should it restart production?”** Read-only investigation → proposed remediation → approved execution → limited autonomous low-risk reversible actions after proof. Never start with auto rollback.
- **“What breaks first?”** Example: metrics returns `EMPTY` during a partial outage, assistant infers “nothing wrong” and cites nothing. Distinguish `EMPTY` from `UNAVAILABLE`; track citation-free hypothesis rate.
- **“18-second prototype?”** Decompose the stack, parallelize independent telemetry, pre-aggregate and stream; keep verification for proposals.
- **“Too expensive?”** Rules/small model for correlation, one strong synthesis, bounded lookback, cached versioned catalog/runbooks. Track cost per resolved investigation.
- **“Wrong citation?”** Verify against the actual retrieved signal/runbook span; reject or repair before a proposal.

The [source](/modules/15-fde-case-studies/agents-that-act/sre-incident-response-agent#full-pack) retains the full diagrams, 45-minute script, leveling rubric, recovery moves, and references.
