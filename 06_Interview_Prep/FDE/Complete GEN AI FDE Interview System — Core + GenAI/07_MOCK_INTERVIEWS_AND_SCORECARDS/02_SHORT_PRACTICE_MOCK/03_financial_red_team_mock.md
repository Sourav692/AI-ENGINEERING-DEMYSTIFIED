# Mock Interview: Financial Compliance + Red Team

## Format
- Duration: 45 minutes
- Candidate target: GenAI FDE / Applied AI Engineer
- Evaluation: product thinking, architecture, security, evals, production rollout, communication

## Interviewer opening
“Our customer wants Financial Compliance + Red Team. They tried a quick LLM demo, but it failed in production. Walk me through how you would approach this as the FDE.”

## Strong candidate answer outline
1. Clarify the business workflow and users.
2. Define success metrics and risk boundaries.
3. Identify data sources, freshness, and permissions.
4. Propose a secure RAG/agent architecture.
5. Add evals, red-team tests, and human approval.
6. Discuss monitoring, cost, latency, and rollout.

## Transcript
**Interviewer:** What is the first thing you would ask the customer?

**Strong candidate:** I would not start with the model. I would ask which workflow is painful, who makes the decision, what data they trust today, what mistakes are unacceptable, and how we will measure success after the pilot.

**Interviewer:** The customer says they want “all company knowledge in chat.” How do you narrow that?

**Strong candidate:** I would separate information lookup from action-taking. For lookup, I would prioritize high-value workflows and documents with clear owners. For action-taking, I would require human approval until we have evidence that the system is reliable and safe.

**Interviewer:** What architecture would you propose?

**Strong candidate:** A web app sends the user request to an API gateway. Auth resolves tenant, role, and document permissions. Retrieval runs against indexed documents with metadata and ACLs. A policy layer filters chunks before the LLM sees them. The LLM produces grounded answers with citations. Risky actions go through approval. Every request has tracing, cost, latency, retrieval, and safety logs.

**Interviewer:** How do you know it works?

**Strong candidate:** I would build a golden dataset with SME-approved answers, measure groundedness and citation accuracy, run red-team tests for injection and data leakage, and compare model versions before release. I would not launch only because a few demos look good.

**Interviewer:** What are the biggest failure modes?

**Strong candidate:** Permission leakage, stale or low-quality documents, hallucinated answers, unsafe tool calls, cost spikes, slow responses, and users over-trusting the system. Each needs a detection signal and mitigation.

## Weak candidate signals
- Starts with “use GPT plus vector DB.”
- Does not ask about users, workflow, ROI, or risk.
- Ignores tenant permissions and data leakage.
- Has no evaluation plan beyond “accuracy.”
- Does not mention rollout or monitoring.

## Interviewer follow-ups
1. What if the retrieved document contains malicious instructions?
2. What if the answer is correct but cites the wrong source?
3. What if one customer sees another customer’s data?
4. What if the system becomes too expensive after launch?
5. What should be human-approved vs automated?

## Scorecard
| Signal | Strong evidence | Score 1-5 |
|---|---|---|
| Discovery | Clear workflow, users, metrics |  |
| Architecture | Secure, permission-aware, observable |  |
| Evals | Golden set, regression, red-team |  |
| Production | SLOs, costs, rollout, rollback |  |
| Communication | Clear business + technical framing |  |
