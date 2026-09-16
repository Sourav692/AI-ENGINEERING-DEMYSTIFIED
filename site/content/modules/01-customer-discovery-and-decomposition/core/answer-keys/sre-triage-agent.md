# SRE Incident Triage Agent - Answer Key

This answer key is designed for interview preparation. It shows what a strong GenAI FDE candidate should ask, design, evaluate, secure, and communicate before moving from demo to production.

## Strong discovery questions
- What exact production incident response workflow is slow, risky, or inconsistent today, and what decision does the user need to make at the end of the workflow?
- Who is the primary user, who reviews the output, and who owns the operational risk if the assistant is wrong?
- Which tasks are read-only assistance, which are draft-only, and which actions require explicit human approval before write-back?
- What systems contain the trusted source of truth, and how do their permissions, freshness, and ownership differ?
- What are the top 5 recurring cases by volume and the top 5 highest-risk cases by business impact?
- What does a successful 30-day pilot prove: reduced handling time, higher accuracy, better compliance, lower escalations, or improved user satisfaction?
- What answer must the assistant refuse or escalate instead of generating?
- What audit evidence must be stored so security, legal, or management can reconstruct why the system answered a certain way?

## Strong functional requirements
- Support the core workflow: alert fires, agent correlates logs/metrics/traces/deployments/runbooks, proposes likely cause and next steps, drafts incident timeline, and only executes safe read-only diagnostics unless approved.
- Return grounded answers with citations to approved source systems; do not answer unsupported claims confidently.
- Apply user, role, tenant, region, and sensitivity permissions before retrieval and before final response generation.
- Show confidence, missing evidence, and escalation reason when the system is uncertain or policy risk is high.
- Collect user feedback and reviewer corrections for evaluation, not direct model training without governance.
- Provide admin controls for source inclusion, document freshness, policy rules, blocked actions, and audit export.

## Strong non-functional requirements
- Latency: interactive answers should target 3-8 seconds for normal questions; longer workflows should be asynchronous with progress state.
- Availability: design for business-critical support hours with graceful degradation if LLM, vector DB, or source system is down.
- Security: SSO, RBAC/ABAC, source-level ACLs, encryption in transit and at rest, secrets management, and no training on customer data unless contractually allowed.
- Compliance: immutable audit logs for queries, retrieved evidence, model version, policy decisions, approvals, and final output.
- Reliability: fail closed on permission uncertainty, stale data, missing citations, or high-risk write actions.
- Cost: enforce token budgets, caching for stable documents, retrieval pruning, smaller models for classification, and model routing for expensive reasoning only.

## Architecture explanation
- User enters a question or workflow request through the product UI, chat surface, or embedded workflow panel.
- Request gateway authenticates the user, loads role/tenant/context, classifies intent, sensitivity, and whether the request is read-only, draft-only, or action-taking.
- Connectors ingest and normalize data from Prometheus/Grafana, Datadog/New Relic, logs, traces, Kubernetes, CI/CD, feature flags, incident management, runbook repository; ingestion preserves metadata, document version, source owner, freshness, and ACLs.
- Hybrid retrieval combines keyword search, vector search, metadata filters, and permission filters. Retrieval happens only after policy checks, not after generation.
- A reasoning layer builds an answer from retrieved evidence, structured records, and approved playbooks. It must cite sources and expose missing evidence.
- Tool-use layer is allowlisted. Read tools can run automatically; write tools require policy checks, idempotency keys, preview mode, and human approval for risky actions.
- Evaluation service runs offline golden tests, regression tests, red-team tests, and live shadow-mode scoring before and after deployment.
- Observability captures latency, cost, retrieval quality, refusal rate, escalation rate, user feedback, source freshness, and policy violations.

## Data model / integration assumptions
- Alert(id, service, severity, labels, start_time); Signal(id, alert_id, source, metric/log/trace, timestamp, value); Deployment(id, service, version, commit, deploy_time); Runbook(id, service, symptom, steps, risk_level); ActionProposal(id, action_type, blast_radius, approval_status); IncidentTimeline(event_id, incident_id, timestamp, source).
- Assume all source records have stable IDs, owner metadata, last-updated timestamps, and access-control metadata. If a source lacks ACL metadata, it is excluded from production retrieval until mapped.
- Assume embeddings are not the authority for permissions; permissions are checked through metadata filters and, for sensitive records, source-system authorization checks.
- Assume source freshness varies by system. The answer should display stale-source warnings when documents or records are older than approved thresholds.
- Assume user feedback is stored separately from ground truth; SME-reviewed corrections become evaluation data only after approval.

## Red-team risks
- unsafe remediation command, wrong root cause, leaking secrets from logs, alert fatigue, prompt injection in logs/runbooks
- Indirect prompt injection hidden in documents, tickets, comments, transcripts, or uploaded files that instructs the model to ignore policy.
- Permission-boundary tests where the same question is asked by users with different roles, tenants, regions, and entitlements.
- Data exfiltration attempts such as summarizing all confidential records, exposing hidden metadata, or revealing system prompts/tool schemas.
- Unsafe automation attempts such as closing, approving, refunding, emailing externally, changing priority, or executing commands without approval.
- Staleness and conflict attacks where old documents contradict new policy; system must surface conflict and prefer approved current sources.

## Rollout plan
- Week 0-1: define workflow, risk boundary, success metrics, source owners, approval rules, and non-goals.
- Week 1-2: ingest a limited approved corpus; build offline prototype with no write-back and no external communication.
- Week 2-3: create golden dataset from historical cases and SME-approved answers; add red-team and permission tests.
- Week 3-4: run shadow mode against historical/live cases; compare against human decisions without showing output to end users.
- Week 5: launch read-only pilot with citations, confidence, feedback capture, and escalation path.
- Week 6-8: enable draft-only workflow actions behind human approval; keep all high-risk actions gated.
- After pilot: expand sources and users only if eval metrics, incident rate, latency, and cost stay within thresholds; maintain rollback plan.

## Evaluation plan
| Metric | What it proves | Strong threshold | Dataset / method |
|---|---|---|---|
| Groundedness | Answer claims are supported by retrieved evidence | >= 90% supported claims | Golden Q&A + SME review |
| Citation accuracy | Citations point to the exact source/section used | >= 95% correct citations | Source-span audit |
| Permission safety | No answer uses sources the user cannot access | 0 violations | ACL red-team suite |
| Task completion | User can complete the target workflow with less manual effort | >= 80% successful task completion | Workflow replay tests |
| Escalation quality | High-risk/uncertain cases are routed to humans | >= 95% correct escalation on high-risk cases | Risk-labeled scenarios |
| Latency/cost | System meets interaction budget | p95 within target; cost per workflow below budget | Load test + production telemetry |

## Weak answer
I would connect the documents to a vector database, use an LLM to answer questions, and maybe add a chatbot UI. This is weak because it ignores the real production incident response workflow, permission boundaries, source freshness, evaluation, human approval, and production monitoring.

## Average answer
I would build a RAG system over the relevant company data, add citations, and test it with sample questions. I would also monitor accuracy and latency. This is better, but still incomplete because it does not clearly separate low-risk assistance from high-risk actions, does not define the data model or permission checks, and does not explain rollout gates.

## Strong answer
I would start by mapping the user workflow and risk boundary, then design a permission-aware system for production incident response. The system would ingest approved sources with metadata, freshness, and ACLs; use hybrid retrieval with pre-generation permission filtering; generate cited answers; expose uncertainty and missing evidence; and route risky actions to human approval. I would validate it with golden cases, permission red-team tests, groundedness/citation metrics, latency and cost budgets, and a staged rollout from offline prototype to shadow mode to read-only pilot to approved write-back. The key is not just using GenAI, but proving the system is trustworthy, auditable, and operationally safe.

## Interviewer scorecard
| Area | 1 - Weak | 3 - Average | 5 - Strong |
|---|---|---|---|
| Problem framing | Jumps to chatbot/RAG without asking business workflow questions | Identifies users and basic success metric | Defines user workflow, decision owner, risk boundary, and ROI |
| Requirements | Generic functional requirements | Some functional/non-functional requirements | Clear functional, non-functional, security, audit, cost, and failure requirements |
| Architecture | LLM + vector DB only | Reasonable RAG components | Permission-aware retrieval, tool policy, human approval, observability, rollback |
| Data/integration | Mentions sources vaguely | Lists main sources | Defines source of truth, metadata, ACL, freshness, schema assumptions, and integration risks |
| Evaluation | Says 'test accuracy' | Uses a small test set | Golden set, regression, red-team, offline + online metrics, SME review |
| Safety/security | Mentions privacy generally | Adds RBAC and logging | Threat models prompt injection, leakage, stale data, unsafe actions, and fail-closed behavior |
| Rollout | Deploys directly | Pilot after testing | Shadow mode, read-only pilot, gated write-back, canary, monitoring, rollback |
| Communication | Overly technical or vague | Clear but generic | Executive-friendly, structured, practical, and production-oriented |

## Final 2-minute spoken answer
I would not start with the model. I would start by clarifying the broken production incident response workflow, who uses the system, what decision they need to make, and what risk we cannot automate. For SRE Incident Triage Agent, I would design a permission-aware assistant around the workflow: alert fires, agent correlates logs/metrics/traces/deployments/runbooks, proposes likely cause and next steps, drafts incident timeline, and only executes safe read-only diagnostics unless approved. The architecture would ingest approved sources from systems like Prometheus/Grafana, Datadog/New Relic, logs, traces, Kubernetes, CI/CD, feature flags, incident management, runbook repository, preserve metadata, freshness, and ACLs, then use hybrid retrieval with permission filtering before generation. The LLM would produce cited answers, show uncertainty, and escalate when evidence is missing or risk is high. Tool use would be allowlisted: read-only tools can run automatically, but any write-back or externally visible action needs preview and human approval. I would evaluate with SME-approved golden cases, citation accuracy, groundedness, permission red-team tests, task completion, latency, and cost. Rollout would be staged: offline prototype, shadow mode, read-only pilot, then limited approved actions with monitoring and rollback. The production goal is not a flashy demo; it is a trusted workflow assistant that is secure, auditable, and measurably improves the business process.
