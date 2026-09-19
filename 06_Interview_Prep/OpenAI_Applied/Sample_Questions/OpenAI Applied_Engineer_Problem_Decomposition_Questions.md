# OpenAI Applied Engineer Problem Decomposition Round

## Case Study Preparation Guide

> Prepared for Sourav
> Focus: OpenAI Applied AI Engineer / Applied Engineering problem decomposition round

---

## Overview

I checked OpenAI’s current Applied AI Engineer role description, OpenAI’s interview guidance, and publicly shared candidate reports.

The exact prompts are not public, so the questions below should be treated as **high-probability practice cases—not leaked interview questions**.

OpenAI’s current Applied AI Engineer role description suggests that the problem-decomposition round will test the ability to move from an ambiguous customer problem to:

- A clearly scoped use case
- A technical architecture
- An evaluation strategy
- A production and integration plan
- Measurable business outcomes
- Reliability, latency, cost, safety, security, and governance considerations

OpenAI describes the role as taking systems from:

> Use-case selection through architecture, prototyping, evaluation, production launch, and scale.

Source: [OpenAI Applied AI Engineer role](https://openai.com/careers/applied-ai-engineer-delhi-india/)

---

# How the Round Will Probably Feel

A typical prompt may be deliberately vague:

> “A large enterprise wants to use AI to improve customer support. How would you approach it?”

You will likely be expected to ask questions rather than immediately draw a RAG architecture.

A strong structure is:

1. Clarify the business objective and user
2. Define the current workflow and pain points
3. Choose and prioritize the use case
4. Define success metrics and evaluation data
5. Decompose the solution into components
6. Discuss risks, trade-offs, and failure modes
7. Explain the MVP and production rollout plan

---

# High-Priority Case Study Questions

## 1. Enterprise Knowledge Assistant

> A global enterprise wants an AI assistant that answers employee questions using internal documents, policies, and wikis. Design the solution.

### Be ready to discuss

- Document ingestion and freshness
- Chunking and metadata
- Hybrid retrieval versus vector-only search
- Reranking
- Citations and answer grounding
- Access-control-aware retrieval
- Evaluation of retrieval and answer quality
- Handling contradictory or stale documents
- Prompt injection from retrieved content
- Latency and cost controls
- Human escalation

### Likely follow-up

> “The assistant gives a confident but incorrect answer. How do you detect and reduce this?”

---

## 2. Customer-Support Agent

> A telecom or financial-services company wants an AI agent to resolve customer-support tickets.

### Decompose the workflow into

- Intent classification
- Customer authentication
- Knowledge retrieval
- Account lookup
- Resolution recommendation
- Tool execution
- Human escalation
- Conversation summary and CRM update

### Important trade-offs

- Assistive copilot versus autonomous agent
- Read-only tools versus write-capable tools
- Automation rate versus customer-impact risk
- First-response time versus answer quality
- Model fallback strategy
- Auditability and traceability

### Likely follow-up

> “The customer wants 80% autonomous resolution in six months. What would you challenge?”

---

## 3. Claims-Processing Assistant

> An insurance company wants to automate claims processing using documents, emails, and historical claims data.

### Discuss

- Document classification
- OCR and structured extraction
- Policy lookup
- Missing-information detection
- Fraud or anomaly signals
- Human review thresholds
- Explainability
- Regulatory constraints
- PII protection
- Evaluation against human decisions
- Gradual rollout by claim type

A strong answer should avoid promising full automation. Start with lower-risk activities such as:

- Extraction
- Triage
- Summarization
- Missing-information detection

Move toward automated adjudication only after sufficient evaluation and governance.

### Likely follow-up

> “How would you prove that the system is safe enough for production?”

---

## 4. AI-Powered Sales or Account-Research Assistant

> A B2B company wants an AI assistant that prepares account briefs for sales representatives.

### Explore

- CRM, email, product-usage, support, and public-data integrations
- Entity resolution
- Freshness and source prioritization
- Permission boundaries
- Citation and provenance
- Personalization
- Human review
- Measuring seller adoption and time saved

### Possible success metrics

- Preparation-time reduction
- Brief accuracy
- Citation coverage
- Sales-representative adoption
- Conversion improvement
- Meeting-quality improvement

### Likely follow-up

> “What if the model generates a fabricated customer fact?”

---

## 5. Enterprise Document-Processing Platform

> A bank processes millions of financial documents and wants to extract structured data using AI.

### Break it into

- Ingestion
- File validation
- Document classification
- OCR or multimodal extraction
- Schema-constrained output
- Confidence scoring
- Validation against business rules
- Human review
- Correction feedback
- Audit storage
- Reprocessing and model versioning

Discuss:

- Batch versus online processing
- Idempotency
- Retry behavior
- Data lineage
- Model versioning
- Document-format drift

### Likely follow-up

> “How would you handle a new document format appearing without warning?”

---

## 6. AI Agent for Enterprise Workflow Automation

> A customer wants an AI agent that reads incoming requests and performs actions across Salesforce, SAP, Jira, and email.

### Focus on

- Tool discovery and tool schemas
- Agent state
- Workflow orchestration
- Read versus write actions
- Idempotency
- Approval gates
- Permissions
- Timeouts and retries
- Non-termination
- Observability
- Replay and recovery
- Prompt-injection defense

A key principle:

> Assume the model will occasionally make the wrong decision. Design the system so that the blast radius is limited.

### Likely follow-up

> “The agent wants to issue a refund. Should it be allowed to do so automatically?”

---

## 7. Enterprise AI Coding Assistant

> A large company wants an internal coding assistant grounded in its private repositories.

### Discuss

- Repository indexing and incremental updates
- Code-aware chunking
- Symbol and dependency retrieval
- Access control
- IDE integration
- Code generation versus code explanation
- Static analysis and test execution
- Secret scanning
- IP and licensing concerns
- Measuring accepted suggestions
- Measuring developer productivity
- Preventing insecure code generation

### Likely follow-up

> “How would you evaluate whether the assistant actually improves developer productivity?”

---

## 8. The Model Got Worse After an Upgrade

> A customer says their AI application quality declined after switching to a newer model.

### Diagnostic plan

- Collect before-and-after production examples
- Replay a fixed evaluation set
- Segment by task, language, customer, and input size
- Compare structured-output compliance
- Check prompt compatibility
- Check retrieval changes
- Compare latency and token usage
- Conduct human evaluation
- Calibrate LLM-as-judge evaluations
- Roll back or pin the model version
- A/B test future upgrades

### Likely follow-up

> “The offline benchmark improved, but the customer still says quality declined. What could explain that?”

Possible explanations include:

- The benchmark does not represent production traffic
- A specific customer segment regressed
- Retrieval quality changed
- The user experience became slower
- Structured output became less reliable
- The model improved average quality but worsened important edge cases
- Users are judging task completion rather than answer quality

---

## 9. Latency Regression in an LLM Application

> An enterprise customer reports that responses have become slow. Walk through your investigation.

### Decompose latency into

- Client and network
- Authentication
- Application middleware
- Retrieval
- Prompt construction
- Model prefill
- Token generation
- Tool calls
- Output post-processing
- Streaming behavior

First clarify whether the problem is:

- Time to first token
- Time between tokens
- Total completion time
- User-perceived latency

### Check

- Input and output token counts
- Retrieval p95 and p99 latency
- Retry rates
- Rate-limit throttling
- Traffic patterns
- Model version
- Prompt changes
- Cache hit rates
- Regional routing

### Likely follow-up

> “The latency problem happens only during peak traffic. What changes in your design?”

---

## 10. RAG System with Poor Answer Quality

> A customer has built a RAG assistant, but users complain that answers are unreliable. How do you debug it?

Separate the problem into:

1. Retrieval failure
2. Context assembly failure
3. Reasoning or synthesis failure
4. Prompt or instruction failure
5. Output-format failure
6. Evaluation failure
7. User-experience failure

### Measure separately

- Recall@k
- Precision@k
- MRR or nDCG
- Citation correctness
- Context sufficiency
- Answer faithfulness
- Answer relevance
- Abstention quality
- End-to-end task success

### Likely follow-up

> “Would you fine-tune the model?”

Distinguish between:

- **Knowledge problem:** Usually retrieval or better data access
- **Behavior problem:** Prompting, fine-tuning, or structured output
- **Freshness problem:** Indexing and data pipeline
- **Permission problem:** Access-control-aware retrieval

---

## 11. Build an Evaluation Strategy for an AI Application

> A customer wants to deploy an AI assistant but has no reliable way to measure quality. What would you do?

### Cover

- Representative production dataset
- Golden examples
- Task-specific rubrics
- Ground-truth labels
- Automated graders
- Human evaluation
- LLM-as-judge calibration
- Safety and refusal tests
- Regression tests
- Online metrics
- User feedback
- Slice-based analysis
- Statistical confidence
- Continuous evaluation in CI/CD

Important distinction:

> Model quality is not the same as application quality.

Evaluate the complete workflow, including:

- Retrieval
- Tools
- Business rules
- User interaction
- Operational performance
- Business outcomes

### Likely follow-up

> “What if there is no labeled data?”

Discuss:

- Sampling production traffic
- Expert labeling
- Weak supervision
- Synthetic examples used carefully
- Measuring grader agreement
- Human review of difficult cases

---

## 12. Deploying AI in a Highly Regulated Industry

> A healthcare or banking customer wants to deploy a generative AI system that handles sensitive data.

### Discuss

- Data classification
- PII and sensitive-data handling
- Encryption
- Access control
- Tenant isolation
- Retention and deletion
- Audit logging
- Data residency
- Human oversight
- Explainability
- Model and prompt versioning
- Incident response
- Vendor and third-party risk
- Governance approvals

### Likely follow-up

> “The business wants to move quickly and skip the governance review for the MVP. What do you do?”

A strong answer should balance speed with risk reduction:

- Narrow the scope
- Use synthetic or masked data where possible
- Start with read-only or assistive functionality
- Define explicit approval gates
- Obtain security and legal review before production exposure

---

## 13. AI Search Across Many Enterprise Data Sources

> An enterprise has information spread across SharePoint, Slack, Google Drive, Confluence, Salesforce, and databases. Build a unified search assistant.

### Difficult areas

- Identity resolution
- Permission propagation
- Connectors
- Incremental synchronization
- Deleted or revoked documents
- Source reliability
- Deduplication
- Freshness
- Ranking across heterogeneous sources
- Citation and provenance
- Tenant isolation
- Search analytics

### Likely follow-up

> “A user has access to a document today but loses access tomorrow. How do you prevent retrieval of stale permissions?”

---

## 14. AI-Powered Operations or Incident-Response Assistant

> A technology company wants an AI assistant to help engineers diagnose production incidents.

### Discuss

- Logs, metrics, traces, alerts, tickets, and runbooks
- Time-window correlation
- Service topology
- Retrieval of historical incidents
- Hypothesis generation
- Tool access
- Proposed versus executed remediation
- Approval workflow
- Incident timeline
- Auditability
- False-positive cost
- Safe rollback

### Likely follow-up

> “Should the agent be allowed to restart production services automatically?”

A safe progression is:

1. Read-only investigation
2. Suggested remediation
3. Human-approved execution
4. Limited autonomous action for low-risk, reversible operations

---

## 15. AI Assistant for Sales or Customer-Service Calls

> A company wants to transcribe calls, summarize them, extract actions, and update its CRM.

### Decompose into

- Audio ingestion
- Speaker diarization
- Transcription
- PII redaction
- Summarization
- Action-item extraction
- CRM integration
- Confidence scoring
- Human correction
- Retention policy
- Evaluation by call type and language

### Likely follow-up

> “How do you evaluate summaries when there is no single correct summary?”

Possible evaluation methods:

- Rubric-based human assessment
- Action-item precision and recall
- Factual consistency
- Coverage of required fields
- CRM update accuracy
- User-edit distance
- Downstream task completion

---

## 16. Prioritize AI Use Cases for a Large Enterprise

> An executive gives you a list of 30 potential AI use cases. How do you decide what to build first?

Use a prioritization matrix based on:

- Business value
- User pain
- Feasibility
- Data availability
- Integration complexity
- Risk
- Time to value
- Adoption likelihood
- Reusability
- Evaluation difficulty

You should explicitly avoid selecting the most impressive demo.

Select the use case with:

- A measurable outcome
- A realistic path to adoption
- Manageable risk
- Available data
- A practical integration path
- A credible evaluation strategy

### Likely follow-up

> “The highest-value use case is also the riskiest. What do you recommend?”

Possible answer:

- Narrow the initial scope
- Introduce human approval
- Start with decision support rather than automation
- Limit the user population
- Use shadow mode
- Define explicit go/no-go gates
- Expand only after measured evidence

---

## 17. Scale a Successful AI Prototype to Production

> A prototype works for 100 users. The customer now wants to deploy it to 100,000 users.

### Cover

- Traffic and capacity modeling
- Multi-tenancy
- Rate limits
- Queuing
- Caching
- Model routing
- Batch processing
- Streaming
- Cost controls
- Autoscaling
- Observability
- Reliability targets
- Rollbacks
- Security review
- Support model
- Change management
- Adoption measurement

### Likely follow-up

> “The system is technically ready but users are not adopting it. What do you investigate?”

Investigate:

- Whether the problem is important enough
- Workflow fit
- User trust
- Response quality
- Latency
- Training and onboarding
- Incentives
- Integration friction
- Whether the product solves the user’s actual pain point

---

## 18. Build an AI System When the Customer’s Data Is Poor

> The customer wants an AI solution, but its data is incomplete, inconsistent, and poorly documented.

### Discuss

- Data-quality profiling
- Ownership
- Missingness
- Duplicates
- Schema inconsistencies
- Label quality
- Freshness
- Data contracts
- Human-in-the-loop correction
- Narrowing the initial use case
- Whether AI is actually the right solution

A strong answer may conclude:

> “I would not begin with model selection. I would first determine whether the available data can support a measurable workflow improvement.”

---

# Cases Especially Relevant to a Cloud Data Platform Background

Given your cloud-data-platform and Databricks experience, prioritize these five cases.

---

## A. Enterprise AI Data Platform

> Design a platform that ingests structured, unstructured, and streaming data to support enterprise AI applications.

### Be ready to connect

- Data lakehouse
- Batch and streaming ingestion
- Metadata and lineage
- Data quality
- Feature or retrieval pipelines
- Governance
- Evaluation datasets
- Production monitoring

---

## B. Lakehouse-Powered RAG Platform

> A large organization wants a reusable RAG platform for multiple business units. Design it.

### Cover

- Multi-tenant architecture
- Document ingestion
- Delta-based processing
- Metadata management
- Vector and keyword retrieval
- ACL propagation
- Evaluation framework
- Cost isolation
- Model and embedding versioning

---

## C. Real-Time Fraud or Anomaly-Detection Assistant

> A bank wants to detect suspicious activity in near real time and provide explanations to investigators.

### Discuss

- Streaming ingestion
- Feature freshness
- Detection versus investigation
- Alert prioritization
- Human feedback
- False positives
- Explainability
- Historical backtesting
- Online monitoring
- Data and model drift

---

## D. Enterprise Data Quality Copilot

> Build an AI assistant that helps data engineers diagnose pipeline and data-quality issues.

### Cover

- Catalog and lineage
- Pipeline logs
- Quality checks
- Schema evolution
- Incident history
- Natural-language investigation
- Safe remediation suggestions
- Read-only versus write operations
- Auditability

---

## E. AI Migration from Prototype to Production

> A team has a successful notebook-based AI prototype. How do you productionize it?

### Discuss

- Reproducibility
- CI/CD
- Evaluation gates
- Model and prompt versioning
- Secrets management
- Monitoring
- Cost controls
- Security
- SLAs
- Rollback
- Ownership and support

---

# What the Interviewer Is Likely Evaluating

Public decomposition-interview guidance emphasizes the following signals:

- Do you clarify before solving?
- Can you identify the real user and business outcome?
- Can you separate the problem into clean workstreams?
- Do you make assumptions explicit?
- Can you define measurable success?
- Do you identify risks and failure modes?
- Can you discuss trade-offs instead of asserting one “best” design?
- Can you move from prototype to production?
- Do you communicate clearly while the problem changes?

A publicly shared OpenAI candidate report described the problem-decomposition screen as **very vague**, with likely signals including:

- Identifying risks
- Defining success metrics
- Breaking down a complex problem
- Communicating confidently under pressure

Treat that report as anecdotal, not authoritative.

Source: [Candidate report](https://www.reddit.com/r/FAANGJobs/comments/1w6cjej/openai_applied_engineering_interview/)

---

# Reusable Answer Template

Use this opening for almost every case:

> “Before proposing a solution, I’d like to clarify the business outcome, primary user, current workflow, constraints, and how success will be measured. I’ll make assumptions explicit where information is missing. Then I’ll decompose the problem into use-case selection, data and integrations, AI workflow, evaluation, production architecture, and rollout.”

## Business questions

- Who is the user?
- What decision or task should improve?
- What is the current process?
- What is the cost of the current problem?
- Is the objective automation, assistance, speed, quality, or revenue?

## Constraint questions

- What latency is acceptable?
- What volume and concurrency are expected?
- What data is available?
- How fresh must the data be?
- What privacy, security, and regulatory constraints exist?
- What actions may the system take autonomously?

## Evaluation questions

- What does a correct answer or successful task mean?
- Do we have historical examples or labels?
- What is the human baseline?
- Which errors are tolerable?
- Which errors require escalation?

## Architecture questions

- What are the inputs?
- What processing is required?
- Where do retrieval, models, tools, and business rules fit?
- What state must be persisted?
- How is the system monitored and rolled back?

## Rollout questions

- What is the lowest-risk MVP?
- Which users or workflows get the pilot?
- What gates must be passed before expansion?
- How will adoption and business impact be measured?

---

# Biggest Mistakes to Avoid

1. Starting with “I would use RAG and agents.”
2. Not asking who the user is.
3. Treating automation as the objective.
4. Ignoring permissions and data governance.
5. Discussing model accuracy without defining evaluation.
6. Designing only the happy path.
7. Forgetting human escalation.
8. Ignoring latency and cost.
9. Treating a prototype as a production system.
10. Giving a technically impressive answer without connecting it to business impact.

---

# Recommended Preparation Plan

Practice **8–10 cases in 45-minute sessions**.

For each case, force yourself to produce:

- Five clarifying questions
- Three to five workstreams
- Three measurable success metrics
- Two major trade-offs
- Three failure modes
- A phased MVP-to-production plan

For your profile, do not over-index on generic LLM theory.

Your strongest differentiator will be showing that you can connect:

- Enterprise data
- Architecture
- Evaluation
- Governance
- Production operations
- Customer outcomes

The goal is not to design the most sophisticated AI system.

The goal is to demonstrate that you can turn an ambiguous customer problem into a measurable, safe, deployable, and adoptable production solution.
