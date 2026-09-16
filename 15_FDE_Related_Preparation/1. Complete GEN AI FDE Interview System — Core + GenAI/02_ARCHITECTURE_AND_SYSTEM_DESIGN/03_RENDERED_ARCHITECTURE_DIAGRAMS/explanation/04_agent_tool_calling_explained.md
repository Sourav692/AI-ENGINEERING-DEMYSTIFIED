# 04. Agent Tool Calling
## What the diagram shows

This diagram shows an agent workflow where a user goal is converted into a plan, available tools are discovered through a tool registry, policies are checked, human approval may be required, tools are executed, observations are verified, and the final answer is returned.

The system emphasizes that agents should not freely call tools. Tool use must be governed, logged, and verified.

## How to explain it in an interview

A strong spoken explanation could be:

> I would separate planning from execution. The planner proposes steps, but a policy engine validates whether each tool call is allowed for the user, tenant, risk level, and business context. Low-risk read-only tools may execute automatically. High-risk actions, such as refunds, account changes, or data exports, require human approval. After execution, the verifier checks whether the observation satisfies the plan and whether the final answer should mention uncertainty or failure.

## Key trade-offs

- **Autonomy vs control:** More autonomy improves speed but increases business risk.
- **Tool flexibility vs safety:** Rich tool schemas help agents solve tasks but increase the attack surface.
- **Human approval vs latency:** Approval protects high-risk actions but slows down workflows.
- **Planner complexity vs reliability:** Complex multi-step plans can solve bigger tasks but are harder to debug.
- **Retry behavior vs duplicate actions:** Retries improve reliability but can cause duplicate tickets, payments, or notifications.

## Failure modes

- Agent selects the wrong tool for the goal.
- Tool schema is ambiguous and causes incorrect parameters.
- Prompt injection convinces the planner to bypass policies.
- Human approval is requested for too many low-risk actions, causing workflow fatigue.
- Tool execution succeeds but the verifier misinterprets the result.
- Retry logic repeats a non-idempotent action.
- Tool observation contains malicious instructions that contaminate the next step.

## Security concerns

- Use allowlisted tools per user role and tenant.
- Validate parameters before execution.
- Require approval for irreversible or externally visible actions.
- Treat tool outputs as untrusted data.
- Log tool name, parameters, risk level, approver, execution result, and trace ID.
- Use idempotency keys for write actions.
- Prevent the model from directly deciding authorization.

## What a weak candidate misses

A weak candidate says: “The agent can decide which tool to call.” That is not production-grade. It ignores permissioning, approvals, audit logs, unsafe observations, and rollback concerns.

## What a strong candidate says

A strong candidate says tool calling must have a policy boundary. They define read vs write tools, low-risk vs high-risk actions, human approval, idempotency, tool output sanitization, and verification before final response.

## Visual improvement suggestion

Show the diagram in four zones:

- **Reasoning Zone:** User Goal, Planner
- **Control Zone:** Tool Registry, Policy Engine, Risk Scoring
- **Approval Boundary:** Human Approval for high-risk actions
- **Execution Zone:** Tool Executor, Observation, Verifier, Final Answer

Add a visible “untrusted tool output” warning before the verifier.
