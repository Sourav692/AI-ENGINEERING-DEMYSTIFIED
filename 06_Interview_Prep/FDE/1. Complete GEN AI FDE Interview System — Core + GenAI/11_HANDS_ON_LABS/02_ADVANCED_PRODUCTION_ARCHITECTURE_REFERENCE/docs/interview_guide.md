# Advanced Production Architecture Reference — Interview Guide

## Status and Purpose

**Status:** OPTIONAL REFERENCE  
**Implementation status:** PARTIALLY IMPLEMENTED  
**Required for the 30-day study track:** NO  
**Primary hands-on lab:** `../../01_CANONICAL_GENAI_FDE_INTERVIEW_LAB`  
**Primary purpose:** Advanced architecture discussion, production trade-off analysis, and interview extension exercises

This guide explains how to use the Advanced Production Architecture Reference during GenAI Forward Deployed Engineer interviews.

This repository is not the primary hands-on lab. It is an optional architecture reference designed to help candidates discuss how a GenAI system could evolve from an interview-ready prototype into a production-oriented enterprise platform.

Some components are fully implemented, while others are intentionally included as interfaces, reference structures, or candidate exercises. Do not claim that every component is production-ready or fully operational.

---

# 1. How to Position This Project in an Interview

Use the following positioning statement:

> This project is an advanced production-architecture reference for a multi-tenant GenAI application. It demonstrates how retrieval, model providers, tool execution, evaluation, audit logging, human review, observability, and deployment concerns can be separated into clear components. Some integrations are implemented, while others are intentionally represented as extension points for deeper engineering exercises.

Do not say:

- “This is a fully production-ready enterprise platform.”
- “Every integration works end to end.”
- “The infrastructure can be deployed directly without modification.”
- “The MCP tools are complete business-system integrations.”
- “The database and vector-store layers are fully implemented.”

Instead, say:

> The repository demonstrates production-oriented component boundaries and safety controls. Before real deployment, I would complete the database, provider, security, testing, infrastructure, and operational-hardening work described in the known limitations.

---

# 2. Recommended Interview Demonstration Order

Use this sequence during a 10–15 minute technical walkthrough.

## Step 1: Start with the customer problem

Explain the problem before discussing technology.

Example:

> The target use case is an enterprise GenAI assistant that retrieves permission-aware information, supports controlled tool execution, records audit events, and allows high-risk actions to be reviewed by a human.

Describe:

- Who the users are
- What business workflow is being improved
- What data sources are involved
- Which actions are read-only
- Which actions can change external systems
- What risks must be controlled
- How business value will be measured

## Step 2: Explain the system boundary

Identify the main system components:

- API or application layer
- Authentication and tenant context
- Retrieval layer
- Vector store
- Model-provider abstraction
- Prompt and orchestration layer
- MCP or tool-execution layer
- Human-review workflow
- Evaluation framework
- Audit logging
- Observability
- Database
- Deployment infrastructure

Explain which components are implemented and which are reference extensions.

## Step 3: Walk through one request

Use one concrete request.

Example:

> A support agent asks the assistant to find the relevant policy for a customer case and prepare a recommended response.

Describe the flow:

1. The request enters the API.
2. Authentication establishes the user and tenant context.
3. The system validates the request.
4. Retrieval is restricted to documents available to that tenant and user.
5. Relevant context is selected.
6. The model generates a grounded response.
7. Citations and safety checks are applied.
8. Audit information is recorded.
9. If the request includes a high-risk action, it is routed for approval.
10. Quality and latency metrics are emitted.

## Step 4: Explain failure handling

Discuss at least three realistic failures:

- Vector store unavailable
- Model provider timeout
- Stale or missing documents
- Permission mismatch
- Tool execution failure
- Prompt injection
- Evaluation regression
- Cost spike
- Audit-log failure
- Human-review backlog

For each failure, explain:

- Detection
- User-visible behaviour
- Retry policy
- Degraded mode
- Alerting
- Rollback
- Recovery
- Post-incident action

## Step 5: Explain production hardening

Finish by clearly describing what must be completed before production deployment.

---

# 3. Architecture Walkthrough

## API and application layer

The application layer should:

- Validate request schemas
- Establish authenticated user identity
- Establish tenant context
- Apply rate limits
- Enforce request-size limits
- Propagate trace identifiers
- Return safe errors
- Avoid exposing internal stack traces
- Record request metrics

Interview talking point:

> I would keep the API layer thin. Business rules, retrieval, provider calls, and tool execution should be implemented behind explicit interfaces so they can be tested and replaced independently.

## Tenant and permission context

Tenant isolation is a mandatory system property.

The tenant identifier should not be accepted blindly from an untrusted request body. It should be derived from authenticated identity, trusted claims, or a verified service-to-service context.

Controls should include:

- Tenant-aware database queries
- Tenant-aware vector retrieval
- Permission-aware filtering
- Tenant-scoped cache keys
- Tenant-scoped audit records
- Cross-tenant leakage tests
- Deny-by-default behaviour

Interview talking point:

> Tenant isolation must be enforced at more than one layer. I would enforce it in authentication, query construction, storage access, cache keys, retrieval filters, and automated leakage tests.

## Retrieval layer

The retrieval layer should support:

- Ingestion
- Chunking
- Metadata extraction
- Embedding generation
- Vector insertion
- Keyword or hybrid retrieval
- Metadata filtering
- Permission filtering
- Reranking
- Citation construction
- Retrieval evaluation

Discuss trade-offs among:

- Chunk size
- Chunk overlap
- Embedding model
- Vector database
- Hybrid search
- Reranking
- Freshness
- Cost
- Latency
- Recall
- Precision

Interview talking point:

> Retrieval quality is not measured only by whether relevant text appears somewhere in the result set. I would measure permission correctness, recall, precision, citation coverage, freshness, latency, and downstream answer groundedness.

## Model-provider abstraction

The provider layer should isolate:

- Model name
- Authentication
- Request format
- Timeout
- Retry policy
- Token limits
- Streaming
- Structured output
- Safety settings
- Usage accounting
- Error translation

Interview talking point:

> A provider abstraction is useful when the system may need model routing, fallback, regional providers, private models, or future migration. I would avoid hiding provider-specific capabilities behind an abstraction that is too generic.

## Tool and MCP layer

Tools should use explicit input and output contracts.

Every tool should define:

- Tool name
- Purpose
- Input schema
- Output schema
- Required authorization
- Tenant scope
- Read or write classification
- Idempotency behaviour
- Timeout
- Retry policy
- Audit requirements
- Human-approval requirements

High-risk write operations should not execute directly from unconstrained model output.

Interview talking point:

> I treat tool execution as a privileged boundary. The model may propose an action, but deterministic code validates authorization, schema, policy, and approval requirements before execution.

## Human-review workflow

Human review is appropriate when:

- Actions are irreversible
- Financial impact is significant
- Regulatory requirements apply
- The model has low confidence
- Policy is ambiguous
- Customer harm is possible
- The action changes an external system

A review record should contain:

- Original user request
- Proposed action
- Supporting evidence
- Model output
- Policy checks
- Risk classification
- Reviewer decision
- Reviewer identity
- Timestamp
- Final execution result

Interview talking point:

> Human-in-the-loop should not be added to every workflow. I use it selectively where the expected cost of an incorrect autonomous action is higher than the operational cost of review.

## Evaluation layer

The evaluation system should separate:

### Offline evaluation

- Retrieval relevance
- Permission leakage
- Groundedness
- Citation accuracy
- Tool-selection accuracy
- Structured-output validity
- Safety-policy adherence
- Regression testing

### Online evaluation

- User success
- Escalation rate
- Acceptance rate
- Correction rate
- Latency
- Cost per successful task
- Incident rate
- Business outcome

Interview talking point:

> I would not release a prompt, model, retrieval, or routing change based only on anecdotal examples. It should pass a versioned evaluation suite and controlled rollout.

## Audit logging

Audit logs should record:

- User identity
- Tenant identity
- Request identifier
- Model version
- Prompt version
- Retrieval identifiers
- Tool proposals
- Tool executions
- Approval decisions
- Policy decisions
- Errors
- Final outcome

Sensitive content should be minimized, redacted, encrypted, and retained according to policy.

Interview talking point:

> Auditability should be designed into the request lifecycle rather than added after an incident.

## Observability

Observe:

- Request count
- Error rate
- P50, P95, and P99 latency
- Provider latency
- Retrieval latency
- Tool latency
- Token usage
- Cost
- Cache hit rate
- Evaluation failures
- Permission denials
- Approval queue length
- Safety violations

Interview talking point:

> Technical health metrics are necessary but insufficient. I would also monitor user success, task completion, correction rate, escalation rate, and cost per successful outcome.

---

# 4. Implemented Components and Extension Points

Before an interview, update this table to reflect the exact current code status.

| Component | Current status | How to describe it |
|---|---|---|
| API structure | Verify before release | Implemented or partial application structure |
| Tenant-context handling | Verify before release | Demonstration of tenant-aware boundaries |
| In-memory retrieval | Verify before release | Local educational implementation |
| PostgreSQL models | Extension point | Requires completion |
| Database migrations | Reference placeholders | Not production-ready |
| pgvector integration | Extension point | Architecture and interface only unless completed |
| External model provider | Extension point | Requires SDK, credentials, retries, and tests |
| MCP tool definitions | Demonstration | Safety and schema examples |
| Tool business logic | Partial or placeholder | Requires real external integration |
| SQL safety | Reference design | Requires parser, allowlist, and policy enforcement |
| Human-review flow | Verify before release | Demonstration or partial implementation |
| Evaluation suite | Verify before release | Educational evaluation framework |
| Kubernetes manifests | Reference | Requires cluster-specific hardening |
| Terraform | Reference | Requires complete environment implementation |

Never describe an extension point as implemented.

---

# 5. Known Limitations

A strong interview answer includes limitations voluntarily.

Recommended limitations to discuss:

1. Some database models and migrations require completion.
2. The pgvector integration may be an extension interface rather than a complete adapter.
3. External model-provider integration requires configuration and testing.
4. MCP tools demonstrate safety boundaries but may not perform complete business operations.
5. Infrastructure files require environment-specific configuration.
6. Authentication and authorization require integration with a real identity provider.
7. Secrets management must be replaced with a production secret store.
8. Load, resilience, and penetration testing are required.
9. Data-retention and compliance rules must be defined for the target customer.
10. Evaluation datasets must be adapted to the customer domain.
11. Disaster-recovery procedures require validation.
12. Cost controls require real traffic measurements.

Suggested phrasing:

> The repository provides a strong architecture baseline, but I would not deploy it unchanged. My first production-hardening priorities would be identity integration, tenant-isolation testing, database completion, provider resilience, tool authorization, secret management, load testing, and operational runbooks.

---

# 6. Common Interview Questions

## Why did you separate the model provider from the application?

Strong answer:

> The abstraction reduces coupling between business logic and a specific provider. It supports testing with a mock provider, fallback between models, regional deployment, cost-based routing, and future migration. I would still expose provider-specific capabilities where they materially affect quality or latency instead of forcing every provider into an oversimplified interface.

## Why use RAG instead of fine-tuning?

Strong answer:

> The primary problem is access to current, private, permission-controlled enterprise knowledge. RAG supports freshness, citations, deletion, and permission-aware retrieval. Fine-tuning may help with style, task behaviour, or compact specialised knowledge, but it does not replace dynamic access control or current document retrieval.

## How would you prevent cross-tenant leakage?

Strong answer:

> I would derive tenant context from trusted authentication claims, enforce tenant filters in every storage and retrieval query, use tenant-scoped cache keys, prevent caller-controlled tenant overrides, record tenant context in audit logs, and run automated positive and negative leakage tests. For highly sensitive systems, I would also consider stronger physical or logical isolation.

## How would you make tool execution safe?

Strong answer:

> I would use schema validation, explicit authorization, allowlisted operations, bounded arguments, timeouts, idempotency keys, audit logging, and human approval for high-risk writes. The model proposes an action; deterministic code decides whether the action is allowed.

## What would happen if the model provider failed?

Strong answer:

> I would define timeouts, bounded retries, circuit breaking, fallback models where appropriate, degraded modes, user-visible error handling, and metrics. Read-only search may still work without generation, while write operations should fail safely rather than execute with incomplete reasoning.

## How would you evaluate the system?

Strong answer:

> I would maintain versioned offline datasets for retrieval, groundedness, permission leakage, tool selection, and safety. I would complement those with online measures such as task success, user acceptance, correction rate, escalation rate, latency, cost, and incident rate. Releases would require threshold checks and a controlled rollout.

## Why is human review needed?

Strong answer:

> Human review is justified where an incorrect action could create financial, legal, security, or customer harm. It should be risk-based, not universal. Low-risk read-only tasks can remain automated, while high-risk writes require approval.

## How would you scale retrieval?

Strong answer:

> I would first quantify document volume, query rate, update frequency, tenant count, and latency targets. Depending on those constraints, I would use sharding or partitioning, asynchronous ingestion, batch embedding, hybrid retrieval, caching, metadata indexes, reranking limits, and backpressure. I would also monitor freshness and permission-filter performance.

## What would you improve first?

Strong answer:

> I would prioritise the controls with the highest risk-reduction value: trusted identity integration, tenant isolation, complete database migrations, production provider handling, tool authorization, leakage testing, evaluation gates, and reproducible deployment. I would not begin by adding more models or more agent complexity.

---

# 7. Interview Whiteboard Structure

Use this order when drawing the architecture:

1. Users and external systems
2. Authentication and tenant context
3. API gateway or application service
4. Orchestration layer
5. Retrieval pipeline
6. Model-provider layer
7. Tool or MCP layer
8. Human-review queue
9. Data stores
10. Evaluation and observability
11. Audit logging
12. Deployment boundary

Mark:

- Trust boundaries
- Tenant context
- Read paths
- Write paths
- Approval points
- Failure points
- External services

Do not draw twenty components without explaining why they are needed.

---

# 8. Production-Hardening Plan

Use this phased plan when the interviewer asks how you would move the reference architecture toward production.

## Phase 1: Correctness and security

- Complete database models
- Complete migrations
- Implement trusted authentication
- Enforce tenant isolation
- Add authorization policies
- Complete provider integration
- Add secret management
- Add negative security tests
- Add permission-leakage tests

## Phase 2: Reliability

- Add timeouts
- Add bounded retries
- Add circuit breakers
- Add idempotency
- Add dead-letter handling
- Add backup and restore
- Add health and readiness probes
- Add disaster-recovery procedures

## Phase 3: Quality

- Create domain-specific evaluation datasets
- Add release thresholds
- Add prompt and model versioning
- Add retrieval regression tests
- Add safety regression tests
- Add canary deployment
- Add rollback automation

## Phase 4: Scale and cost

- Run load tests
- Measure model cost
- Add caching
- Add model routing
- Optimise chunking and reranking
- Batch embeddings
- Add quotas and rate limits
- Define capacity alerts

## Phase 5: Governance

- Define retention
- Define data residency
- Define incident ownership
- Define review policies
- Define model-risk controls
- Define audit access
- Create operational runbooks

---

# 9. Candidate Exercises

The following exercises are optional advanced work.

## Exercise 1: Complete the pgvector adapter

Implement:

- Tenant-aware insertion
- Similarity search
- Metadata filtering
- Permission filtering
- Index creation
- Integration tests
- Cross-tenant negative tests

## Exercise 2: Complete one model provider

Implement:

- Authentication
- Timeout
- Retry
- Structured output
- Token accounting
- Error mapping
- Mock tests
- Optional live integration test

## Exercise 3: Complete one MCP tool

Choose a realistic tool such as:

- Search customer tickets
- Retrieve account details
- Create a review request
- Execute a read-only SQL query

Add:

- Input schema
- Output schema
- Authorization
- Tenant isolation
- Audit logging
- Error handling
- Tests

## Exercise 4: Implement SQL safety

Add:

- Read-only enforcement
- Schema allowlist
- Table allowlist
- Column restrictions
- Row limit
- Timeout
- Query parser
- Audit logging
- Negative tests

## Exercise 5: Add a release gate

Create an automated workflow that:

1. Runs tests
2. Runs evaluation fixtures
3. Blocks leakage failures
4. Blocks unsafe tool behaviour
5. Produces a score report
6. Approves or rejects release

---

# 10. Ten-Minute Interview Script

## Minute 0–1: Customer problem

Explain the user, workflow, pain, risk, and measurable outcome.

## Minute 1–3: Architecture

Explain the main components and request flow.

## Minute 3–5: Retrieval and model use

Explain permission-aware retrieval, grounding, provider abstraction, and citations.

## Minute 5–7: Tools and safety

Explain deterministic validation, authorization, approval, and auditability.

## Minute 7–8: Evaluation and observability

Explain offline tests, online metrics, release gates, and monitoring.

## Minute 8–9: Failure handling

Explain provider failure, retrieval failure, permission risk, and rollback.

## Minute 9–10: Limitations and next steps

State what is incomplete and how you would harden it.

---

# 11. Candidate Self-Assessment

Before presenting this architecture, confirm that you can answer yes to each question.

- [ ] Can I explain the customer problem without mentioning technology first?
- [ ] Can I distinguish implemented components from extension points?
- [ ] Can I explain tenant isolation at multiple layers?
- [ ] Can I explain why RAG is appropriate?
- [ ] Can I explain when fine-tuning might still help?
- [ ] Can I describe safe tool execution?
- [ ] Can I explain human-review criteria?
- [ ] Can I define offline and online evaluation?
- [ ] Can I describe three failure modes?
- [ ] Can I explain cost and latency trade-offs?
- [ ] Can I state at least five known limitations?
- [ ] Can I propose a phased production-hardening plan?
- [ ] Can I complete the walkthrough within ten minutes?

---

# 12. Final Positioning Reminder

Use this project to demonstrate:

- Architecture judgment
- Production awareness
- Security thinking
- Evaluation discipline
- Failure handling
- Communication
- Honest technical self-assessment

Do not use it to imply that unfinished components are complete.

The strongest interview signal is not claiming that the system is perfect. The strongest signal is being able to explain:

- What works
- What does not yet work
- Why the architecture is structured this way
- Which risks matter most
- What you would implement next
- How you would verify that the system is ready
