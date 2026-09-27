# FDE AI System Design — Rapid Revision Guide

> **Purpose:** Last-day revision for an AI/Agentic FDE problem-decomposition interview.
>
> Don't memorize architectures. Memorize the **decision process**.

---

# 1. The Master Interview Flow

Whenever you get a vague prompt:

```text
Customer Problem
      ↓
Discovery
      ↓
Functional Requirements
      ↓
Non-Functional Requirements
      ↓
Happy-Path Architecture
      ↓
Data / RAG
      ↓
Agent / Tools / Actions
      ↓
Policy / HITL
      ↓
Scale
      ↓
Latency + Cost
      ↓
Reliability
      ↓
Evaluation + Release
      ↓
Observability + Security
      ↓
Trade-offs
```

### Opening line

> "Before jumping into architecture, I'd first understand the business outcome and current workflow, then clarify users and scale, data and integrations, how much autonomy the AI should have, success criteria, and production constraints."

---

# 2. Discovery — What Should I Ask?

Remember:

```text
WHY
TODAY
WHO
SCALE
DATA
ACTION
SUCCESS
BOUNDARIES
```

### WHY

> What business problem are we solving and what outcome matters?

### TODAY

> How does this process work today and where are the biggest pain points?

### WHO + SCALE

> Who uses the system, how many users do we expect, and what are peak volume and concurrency?

### DATA

> What data does the system need, where does it live, and how fresh must it be?

### ACTION

> Does AI only answer/recommend, or can it take actions?

> Which actions require human approval?

### SUCCESS

> How will we measure success?

Think:

```text
Business KPI
AI Quality
Task Success
Latency
Reliability
Cost
```

### BOUNDARIES

Ask about:

```text
Security
Privacy
Compliance
Latency
Availability
Cost
Integrations
```

---

# 3. Functional Requirements

Think:

```text
Understand
    ↓
Retrieve
    ↓
Route
    ↓
Reason
    ↓
Tool
    ↓
Act
    ↓
Escalate
    ↓
Audit
```

Typical requirements:

- Accept and understand requests
- Maintain relevant context
- Retrieve enterprise knowledge
- Respect user permissions
- Route to correct capability
- Call enterprise tools/APIs
- Execute approved actions
- Escalate risky/uncertain cases
- Handle failures
- Maintain audit trail
- Capture feedback

---

# 4. Non-Functional Requirements

Remember:

```text
SCALE
LATENCY
RELIABILITY
QUALITY
SECURITY
SAFETY
COST
OBSERVABILITY
AUDIT
```

Don't invent numbers.

Ask the customer and turn requirements into measurable SLOs.

Example (the 5 seconds is a placeholder — confirm the real number with the customer):

```text
Bad:
"The system must be fast."

Better:
"P95 response latency < 5 seconds
for interactive requests."
```

---

# 5. Core Architecture Components

## API Gateway

```text
User
 ↓
API Gateway
 ↓
AI Application
```

Handles:

```text
Authentication
Authorization
Tenant Context
User Rate Limits
Quota
Request Validation
```

Think:

> **User → Application control**

---

## Model Gateway

```text
AI Application
      ↓
Model Gateway
      ↓
Model A / B / C
```

Handles:

```text
Model Routing
Provider Abstraction
Fallback
Retry
Provider Limits
Tokens
Cost
```

Think:

> **Application → Model control**

---

## Router

Determines:

```text
What capability should handle this request?
```

Use deterministic rules/classifiers where possible.

---

## Orchestrator

Controls:

```text
Workflow
State
Branching
Agents
Tools
Retries
Checkpoints
```

---

## State Store

Stores durable:

```text
Session
Workflow
Agent
Approval State
```

---

## Queue

Use when:

```text
Long-running work
Traffic bursts
Async processing
Background jobs
```

---

## Cache

Use for repeated safe work.

Remember:

```text
Cache
 ↓
Latency ↓
Cost ↓

BUT

Freshness risk ↑
```

---

# 6. RAG — Rapid Version

## Ingestion

```text
Documents
 ↓
Parse
 ↓
Chunk
 ↓
Embed
 ↓
Index
```

## Query

```text
Question
 ↓
Permission / Metadata Filter
 ↓
Retrieve
 ↓
Rerank
 ↓
Context
 ↓
LLM
```

Remember:

### Recall

> Did I retrieve the relevant information?

### Precision

> How much retrieved information is actually relevant?

### Groundedness

> Is the answer supported by retrieved evidence?

### Static vs Live

```text
"What is the refund policy?"
        ↓
       RAG

"Where is my refund?"
        ↓
     Live API
```

### Security rule

> Apply permissions during retrieval. Don't retrieve everything and ask the LLM not to expose unauthorized information.

---

# 7. Agentic Systems — Rapid Version

First ask:

> **Do I actually need an agent?**

```text
Deterministic problem
       ↓
Workflow / Code

Dynamic reasoning
       ↓
Agent
```

Then ask:

> **Do I actually need multiple agents?**

Don't create multi-agent architecture without a reason.

### Agent loop

```text
Reason
 ↓
Tool
 ↓
Observe
 ↓
Reason
 ↓
Action
```

### Always bound agents

```text
Max Steps
Max Tools
Max Tokens
Max Retries
Max Time
Max Cost
```

---

# 8. Tools & Actions

Prefer:

```text
Agent
 ↓
Controlled Tool
 ↓
Enterprise System
```

rather than unrestricted production access.

For business actions:

```text
Agent
 ↓
Recommendation
 ↓
Policy
 ↓
Executor
 ↓
Enterprise System
```

### Critical term: Idempotency

```text
Refund
 ↓
Timeout
 ↓
Retry

Must NOT
 ↓
Refund twice
```

Use an idempotency key that the execution path actually honours.

---

# 9. Guardrails & Human Approval

Remember:

```text
Agent recommends
      ↓
Policy decides
      ↓
Executor acts
```

Do not use the LLM as the final authority for deterministic business rules.

Example (illustrative thresholds — the customer sets the real ones, including the middle band):

```text
Refund < $100
      ↓
Auto

Refund $100–500
      ↓
Policy checks

Refund > $500
      ↓
Human Approval
```

Other terms:

```text
Least Privilege
Fail-Closed
Kill Switch
Defense in Depth
```

---

# 10. Scaling — Rapid Version

Interviewer says:

> "Now scale this to 100K users."

Think:

```text
Stateless Workers
Horizontal Scaling
Rate Limits
Admission Control
Queue
Backpressure
Fairness
Tenant Isolation
Caching
Autoscaling
```

### Rate Limit

> May this user/tenant send this much traffic?

### Admission Control

> Does the system currently have capacity to accept this work?

### Backpressure

> What happens when incoming work exceeds processing capacity?

### Fair Queue

Prevent:

```text
Tenant A ███████████████████

Tenant B █

Tenant C █
```

### Noisy Neighbor

One tenant consumes shared resources and hurts others.

---

# 11. Latency — Rapid Version

First decompose:

```text
Total Latency
     │
     ├── Queue
     ├── Retrieval
     ├── LLM
     ├── Agent
     ├── Tool
     └── Network
```

Then optimize.

Remember:

```text
MEASURE
   ↓
SLO
   ↓
STREAM
   ↓
PARALLELIZE
   ↓
REDUCE MODEL HOPS
   ↓
OPTIMIZE RETRIEVAL
   ↓
OPTIMIZE TOOLS
   ↓
CONTROL QUEUE
   ↓
ASYNC LONG TASKS
```

Track:

```text
P50
P95
P99
TTFT
```

Don't optimize only average latency.

---

# 12. Cost — Rapid Version

Break cost down:

```text
Model
Tokens
Retrieval
Tools
Compute
Retries
```

Then:

```text
MODEL
 ↓
CONTEXT
 ↓
CACHE
 ↓
CALLS
 ↓
BOUNDS
 ↓
BATCH
 ↓
MEASURE
```

### Questions to ask

Can a smaller model handle this?

Can I reduce context?

Can I cache it?

Do I need this LLM call?

Can deterministic code handle it?

Is the agent making unnecessary calls?

### Best metric

```text
Cost
 ÷
Successful Tasks
```

> **Cost per successful task** — the one I'd lead with, because it counts retries and failed attempts.

---

# 13. Reliability — Rapid Version

When something fails:

```text
Failure
 ↓
Timeout?
 ↓
Retry?
 ↓
Fallback?
 ↓
Degrade?
 ↓
Recover?
 ↓
Escalate?
```

Know these:

### Timeout

Don't wait forever.

### Retry

Retry transient failures.

### Exponential Backoff + Jitter

Don't hammer a failing dependency.

### Circuit Breaker

```text
Repeated failures
       ↓
Stop calling temporarily
```

### Graceful Degradation

One non-critical service failing shouldn't necessarily kill everything.

### DLQ

```text
Fail
 ↓
Retry
 ↓
Retry
 ↓
DLQ
```

### Checkpoint

Resume long-running workflows after failure.

### Blast Radius

> If this fails, how much of the system is affected?

---

# 14. Evaluation — Rapid Version

## RAG

Evaluate:

```text
Retrieval
Groundedness
Answer Quality
```

## Agents

Evaluate:

```text
Routing
Tool Selection
Tool Arguments
Trajectory
Task Success
```

### Deterministic

```text
Correct schema?
Correct tool?
Correct arguments?
Latency threshold?
Required citation?
```

### Non-Deterministic

```text
Helpful?
Relevant?
Grounded?
High-quality?
```

Use human/LLM judges.

### Offline

Before release.

### Online

Production traces + outcomes + feedback.

Remember:

```text
Beautiful Answer
      ≠
Successful Task
```

---

# 15. Release — Rapid Version

Avoid:

```text
New Prompt
   ↓
100% Production
```

Prefer:

```text
Change
 ↓
Offline Evaluation
 ↓
Release Gate
 ↓
Shadow / Canary
 ↓
Online Evaluation
 ↓
Full Production
```

### Shadow

```text
Request
 ├→ Current → User
 └→ Candidate → Evaluate only
```

### Canary

```text
Candidate
 ↓
Small % Users
 ↓
Observe
 ↓
Expand / Rollback
```

Also know:

```text
Versioning
Feature Flags
Rollback
Kill Switch
```

---

# 16. Observability — Rapid Version

Trace the entire request:

```text
Request
 ↓
Router
 ↓
Agent
 ↓
Retriever
 ↓
LLM
 ↓
Tool
 ↓
Response
```

Capture:

```text
Latency
Tokens
Cost
Model
Agent Steps
Retrieved Docs
Tool Calls
Errors
Outcome
```

### Observability vs Audit

**Observability**

> Why is my system behaving badly?

**Audit**

> Why did my system take this business action?

---

# 17. Security — Rapid Version

### Authentication

> Who are you?

### Authorization

> What are you allowed to do?

Then:

```text
Identity
 ↓
Authorization
 ↓
Data Permissions
 ↓
Tool Permissions
 ↓
Policy
 ↓
Human Approval
 ↓
Audit
```

Remember:

```text
Least Privilege
Tenant Isolation
Permission-Aware RAG
Secrets Management
PII
Data Residency
Defense in Depth
```

---

# 18. Trade-Offs — Rapid Version

Almost every decision should have:

```text
Decision
 ↓
Why?
 ↓
Trade-off?
```

### Main triangle

```text
             QUALITY
              /   \
             /     \
          COST ─── LATENCY
```

Examples:

```text
Stronger Model
→ Quality ↑
→ Cost ↑
→ Latency ↑
```

```text
More Retrieval
→ Recall potentially ↑
→ Tokens ↑
→ Cost ↑
→ Latency ↑
```

```text
Cache
→ Cost ↓
→ Latency ↓
→ Freshness Risk ↑
```

```text
More Agents
→ Potential capability ↑
→ Cost ↑
→ Latency ↑
→ Complexity ↑
→ Failure Points ↑
```

### Strong interview sentence

> "I'm choosing X because of requirement Y. The trade-off is Z."

---

# 🔥 Trigger → Concept Cheat Sheet

This is the section to revise immediately before the interview.

| Interviewer Says                      | Think                                         |
| ------------------------------------- | --------------------------------------------- |
| **100K users**                  | Horizontal scaling, stateless workers, queues |
| **Traffic spike**               | Queue, admission control, backpressure        |
| **One tenant dominates**        | Noisy neighbor, quota, fair queue             |
| **Overloaded system**           | Admission control, load shedding              |
| **Multiple customers**          | Multi-tenancy, isolation                      |
| **Slow requests**               | P95/P99 + trace stages                        |
| **Slow chat experience**        | TTFT + streaming                              |
| **Independent APIs**            | Parallelize                                   |
| **Slow dependency**             | Timeout, cache, async                         |
| **Flaky dependency**            | Retry, backoff, circuit breaker               |
| **Action happened twice**       | Idempotency                                   |
| **Duplicate event**             | Idempotent consumer                           |
| **Repeated job failure**        | DLQ                                           |
| **10-minute agent**             | Async + queue + durable state                 |
| **Agent crashes halfway**       | Checkpoint                                    |
| **Approval tomorrow**           | Durable state + HITL                          |
| **Conversation history**        | Session state                                 |
| **Long-term preferences**       | Memory                                        |
| **Growing prompt**              | Bounded context + summary                     |
| **Repeated requests**           | Cache                                         |
| **Freshness concern**           | TTL                                           |
| **Company documents**           | RAG                                           |
| **Current order status**        | Tool/API                                      |
| **Can't find document**         | Retrieval recall                              |
| **Too many irrelevant docs**    | Precision + reranking                         |
| **Document permissions**        | ACL-aware retrieval                           |
| **Unsupported claims**          | Grounding                                     |
| **Different request types**     | Router                                        |
| **Multi-step workflow**         | Orchestrator                                  |
| **Simple routing**              | Rules/code                                    |
| **Runaway agent**               | Execution bounds                              |
| **Production actions**          | Controlled tools                              |
| **Sensitive action**            | Policy + executor                             |
| **High-risk action**            | HITL                                          |
| **Policy unavailable**          | Fail-closed                                   |
| **Agent misbehaving**           | Kill switch                                   |
| **Multiple LLMs**               | Model gateway                                 |
| **Provider outage**             | Fallback                                      |
| **AI bill high**                | Model + context + calls + cache               |
| **Tenant cost**                 | Cost attribution                              |
| **New prompt/model**            | Offline eval + release gate                   |
| **Real traffic without impact** | Shadow                                        |
| **Gradual rollout**             | Canary                                        |
| **Selected tenants only**       | Feature flag                                  |
| **Bad deployment**              | Rollback                                      |
| **Measure agent quality**       | Offline + online eval                         |
| **Good answer, failed action**  | Task success                                  |
| **Wrong tool**                  | Trajectory evaluation                         |
| **Exact pass/fail**             | Deterministic eval                            |
| **Semantic quality**            | LLM/human judge                               |
| **Why slow/failing?**           | Observability                                 |
| **Why did AI act?**             | Audit                                         |
| **Reliability target**          | SLI/SLO/SLA                                   |
| **Worker dies**                 | Stateless + durable state                     |
| **Limit failure impact**        | Blast radius                                  |
| **Sensitive data**              | AuthN/AuthZ + least privilege                 |
| **Safe action-taking AI**       | Defense in depth                              |

---

# ⚡ 60-Second Architecture Pressure Test

After drawing your architecture, quickly ask yourself:

```text
1. SCALE
   What happens at 100K users?

2. LATENCY
   Where is the critical path?

3. COST
   Where are model calls/tokens growing?

4. FAILURE
   What happens if model/RAG/tool fails?

5. STATE
   What happens if a worker dies?

6. SECURITY
   Can users access unauthorized data/actions?

7. SAFETY
   Can the agent take dangerous actions?

8. QUALITY
   How do I know the AI works?

9. RELEASE
   How do I safely change it?

10. OPERATIONS
    How do I debug it?
```

---

# 🎯 10 Rapid Practice Questions

Try answering each in **1–2 minutes**, not 20 minutes.

### 1.

> "Build an AI customer-support agent."

What are your first discovery questions?

### 2.

> "Now it needs to issue refunds."

What changes architecturally?

### 3.

> "We now have 100K users."

What changes?

### 4.

> "P99 latency is 20 seconds."

How do you investigate and optimize it?

### 5.

> "The AI bill increased 3×."

How do you investigate and reduce it?

### 6.

> "The refund API is unreliable."

How do you design around it?

### 7.

> "Employees have different document permissions."

How does your RAG architecture change?

### 8.

> "We changed the prompt."

How do you safely release it?

### 9.

> "The agent gives good responses but sometimes chooses the wrong tool."

How do you evaluate this?

### 10.

> "One enterprise tenant consumes most model capacity."

How do you protect other tenants?

---

# Final Interview Checklist

Before finishing:

```text
□ Business problem clear?

□ Current workflow understood?

□ Functional requirements defined?

□ NFRs measurable?

□ Every architecture box justified?

□ RAG vs live API clear?

□ Agent actually required?

□ Actions protected by policy?

□ High-risk actions HITL?

□ Scale addressed?

□ Latency addressed?

□ Cost addressed?

□ Failure handling addressed?

□ Security addressed?

□ Evaluation defined?

□ Release strategy defined?

□ Observability defined?

□ Major trade-offs explained?
```

---

# The One Framework to Remember

If everything else disappears from your head:

```text
CUSTOMER PROBLEM
      ↓
DISCOVERY
      ↓
REQUIREMENTS
      ↓
SIMPLE HAPPY PATH
      ↓
DATA + AI + ACTIONS
      ↓
PRESSURE TEST
 ┌────┼────┬────┐
Scale Latency Cost Failure
 └────┼────┴────┘
      ↓
SECURITY + SAFETY
      ↓
EVALUATION
      ↓
RELEASE + OBSERVABILITY
      ↓
TRADE-OFFS
```

And use this reasoning pattern repeatedly:

```text
Customer says X
      ↓
Therefore Requirement Y
      ↓
That creates Constraint Z
      ↓
So I introduce Component A
      ↓
Trade-off is B
```

> **Don't demonstrate how many architecture terms you know. Demonstrate that you know exactly when and why to use them.**
