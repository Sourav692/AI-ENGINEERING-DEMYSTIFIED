# 05. Human Approval Workflow
## What the diagram shows

This diagram shows how an agent proposal is classified by risk. Low-risk actions can be auto-executed. High-risk actions enter a review queue, require an approver, then call the action API. User notifications and audit trails record what happened.

This is essential for production GenAI systems that can affect customers, money, compliance, or operational state.

## How to explain it in an interview

A strong spoken explanation could be:

> I would not use human-in-the-loop as a vague safety phrase. I would define exactly which actions require approval based on risk, amount, data sensitivity, reversibility, and customer impact. The approval UI should show the proposed action, evidence, confidence, policy reason, affected records, and rollback option. Approved actions are executed with idempotency keys and logged for audit.

## Key trade-offs

- **Speed vs safety:** Auto-execution is fast but risky for sensitive actions.
- **Approval volume vs reviewer fatigue:** Too many approval requests reduce productivity and may lead to rubber-stamping.
- **Strict thresholds vs business flexibility:** Fixed thresholds are easier to govern but may not fit every customer.
- **Explainability vs UI complexity:** Reviewers need enough evidence, but too much information slows decisions.

## Failure modes

- Risk classifier underestimates a dangerous action.
- Approval queue becomes a bottleneck.
- Approver lacks enough context to make the right decision.
- Agent modifies the action after approval.
- Duplicate execution occurs after timeout or retry.
- Audit trail misses the original model proposal.
- User is notified before action success is confirmed.

## Security concerns

- Use role-based approver permissions.
- Prevent self-approval for sensitive actions.
- Make approved payload immutable after approval.
- Log model proposal, reviewer decision, final API payload, and execution result.
- Require stronger controls for financial, legal, healthcare, and customer-impacting actions.
- Add escalation for unusual patterns, such as many high-risk proposals from one user.

## What a weak candidate misses

A weak candidate says: “For risky actions, add human review.” That answer is too generic. It does not define risk criteria, approval UI, auditability, immutability, or reviewer fatigue.

## What a strong candidate says

A strong candidate defines specific approval thresholds and reviewer workflows. They mention immutable approval records, evidence bundles, idempotency, escalation paths, and metrics such as approval rate, rejection rate, queue time, and post-approval incident rate.

## Visual improvement suggestion

Separate the workflow into:

- **Agent Decision:** Proposal and Risk Classifier
- **Auto Lane:** Low-Risk Auto Execute
- **Human Review Lane:** High-Risk Queue, Approver, Evidence Bundle
- **Execution/Audit Lane:** Action API, User Notification, Audit Trail

Add a clear human approval boundary before any irreversible action.
