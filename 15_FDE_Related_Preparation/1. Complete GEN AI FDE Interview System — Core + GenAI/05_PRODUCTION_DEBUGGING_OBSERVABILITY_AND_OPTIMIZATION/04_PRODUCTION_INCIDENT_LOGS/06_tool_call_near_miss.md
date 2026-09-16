# Incident 6: Agent Tool-Call Near Miss on Refund Workflow

## Scenario

A retail support agent uses an AI assistant that can summarize orders, draft replies, check policy, and recommend refunds. The assistant is not allowed to execute refunds above €250 without manager approval. It may only create a proposed refund ticket.

On 2026-07-08, an agent asked the assistant to “handle all delayed VIP shipments from yesterday.” The agent planner selected the refund tool for 18 orders, including several above the approval threshold. The tool gateway blocked execution, so no money was sent, but the near miss exposed a dangerous gap in agent planning and tool authorization.

This incident is valuable because it tests whether candidates understand that tool safety must be enforced at the tool boundary, not only in the planner prompt.

## User-Visible Symptom

The support agent saw: “I could not complete part of this action because approval is required.” The operations manager received an alert that the assistant attempted bulk refunds exceeding policy limits.

## System Context

Agent workflow: user request → planner LLM → policy retriever → tool-selection policy → tool gateway → order API/refund API/ticket API → audit log. The planner can propose tool calls, but the tool gateway enforces authorization using user role, tenant policy, amount, customer segment, and approval state.

## Production Telemetry

```text
2026-07-08T16:07:51.119Z level=warn service=agent-planner
  trace_id=trc_tool_9031 request_id=req_retail_22018 tenant_id=shopline
  user_role=support_agent user_intent="handle delayed VIP shipments from yesterday"
  planned_tool_calls=18 selected_tool=refund_customer
  policy_doc_version=refund_policy_v3 planner_model=agent_planner_2026_07

2026-07-08T16:07:51.522Z level=critical service=tool-gateway
  trace_id=trc_tool_9031 tool_call_id=tc_77881 tool=refund_customer
  order_id=ord_884120 customer_tier=vip refund_amount_eur=740.00
  approval_state=missing user_role=support_agent max_allowed_without_approval_eur=250.00
  tool_call_blocked=true block_reason=approval_required policy_decision=deny

2026-07-08T16:07:51.800Z level=warn service=agent-safety-evaluator
  trace_id=trc_tool_9031 event=unsafe_bulk_action_near_miss
  bulk_action=true affected_orders=18 blocked_calls=6 allowed_calls=12
  safer_alternative=create_refund_review_ticket
  planner_policy_compliance_score=0.42
```

## What Changed Recently

A new planner prompt, `agent_planner_2026_07`, was deployed to make the agent “more action-oriented.” The examples emphasized completing workflows end-to-end but did not include bulk-action approval boundaries. The tool gateway policy was unchanged and correctly blocked the risky calls.

## Root Cause

The planner over-generalized “handle delayed shipments” into direct refund execution for all affected orders. It retrieved the refund policy but failed to apply the approval threshold during planning. The incident did not become a financial loss because the tool gateway enforced policy independently.

## Debugging Path

A strong engineer reviews the agent plan, retrieved policy context, proposed tool calls, gateway decisions, and audit log. They check whether the planner had access to approval thresholds, whether the tool schema encoded risk constraints, and whether the gateway blocked correctly. They also examine allowed calls to ensure smaller refunds were legitimate.

The important distinction is between planner failure and enforcement success. The system had a near miss, not a completed unauthorized transaction.

## Fix / Mitigation

Immediate mitigation: disable bulk refund planning, force all VIP refund actions into review-ticket mode, and add a user confirmation step for financial actions.

Long-term fix: add risk-aware tool schemas, pre-execution policy simulation, planner training examples for approval thresholds, and a separate “action risk classifier” before tool calls. Keep hard enforcement in the tool gateway regardless of planner confidence.

## Red-Team / Safety Risk

A malicious user could phrase a request as operational cleanup to induce bulk financial actions. Without gateway enforcement, this could cause unauthorized refunds, fraud, or revenue loss. The same pattern applies to account deletion, data export, and permission changes.

## Interview Explanation

A strong candidate should praise the gateway block but still treat the planner behavior as a serious near miss. They should discuss defense in depth: planner constraints, tool schema design, policy simulation, approval workflow, and auditability.

## Weak Candidate Answer

“The tool was blocked, so there is no problem. I would just tell the agent to be more careful.”

## Strong Candidate Answer

“This is a near miss. The gateway prevented loss, but the planner attempted unauthorized high-value refunds. I would inspect the planned calls, policy retrieval, and gateway decisions. Then I would disable bulk refund execution, route VIP refunds to review tickets, encode approval thresholds in the tool schema, add policy simulation before execution, and keep the gateway as a non-bypassable enforcement layer.”

## Scorecard

| Criterion | Strong Signal | Weak Signal |
|---|---|---|
| Problem framing | Identifies near miss in agentic tool safety | Says no issue because blocked |
| Telemetry interpretation | Reads planned calls, blocked calls, role, amount, approval state | Looks only at final user error |
| Root-cause reasoning | Separates planner failure from gateway success | Blames tool API generally |
| Production debugging | Audits plan, policy context, tool schema, gateway logs | Only edits prompt |
| Security/privacy awareness | Notes fraud and unauthorized action risk | Ignores financial impact |
| Mitigation quality | Bulk disable, HITL, risk classifier, gateway enforcement | “Tell model not to refund” |
| Communication clarity | Explains near miss and control effectiveness | Minimizes incident |
