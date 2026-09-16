# 08. MCP Tool Server
## What the diagram shows

This diagram shows an LLM client connecting to an MCP host, which communicates with a tool server. The tool server uses a schema registry, authorization middleware, secrets manager, rate limiter, business API, and audit log.

The purpose is to show how tool access should be standardized and governed when LLM applications use external systems.

## How to explain it in an interview

A strong spoken explanation could be:

> I would treat the MCP tool server as a controlled integration boundary. Tools expose explicit schemas, parameter validation, authentication, authorization, rate limits, and audit logs. The LLM should not directly access business APIs or secrets. The host sends structured tool calls, the server validates them, the authorization middleware checks user and tenant permissions, and the business API executes only approved operations.

## Key trade-offs

- **Centralized tool server vs app-specific integrations:** Centralization improves governance but can become a bottleneck.
- **Strict schemas vs flexibility:** Strong schemas reduce errors but require more upfront design.
- **Rate limits vs user experience:** Limits protect backend systems but can block legitimate workflows.
- **Generic tool interface vs domain-specific tools:** Generic tools are reusable; domain-specific tools are safer and easier for the model to use correctly.

## Failure modes

- Tool schema does not constrain dangerous parameters.
- LLM client passes malformed or ambiguous tool arguments.
- Authorization middleware checks app identity but not end-user permission.
- Secrets are exposed to the model or logs.
- Rate limiter is missing per-tenant controls.
- Business API executes non-idempotent actions multiple times.
- Audit log records success/failure but not the original tool payload.

## Security concerns

- Never expose secrets to the LLM context.
- Validate all tool input server-side.
- Use per-user and per-tenant authorization.
- Apply least privilege to business API credentials.
- Log every tool call with trace ID, actor, tenant, parameters, risk level, and result.
- Use idempotency keys for write operations.
- Limit tool availability based on role and workflow.

## What a weak candidate misses

A weak candidate says: “Use MCP so the model can call tools.” That misses the core production challenge: MCP needs governance, schema validation, authorization, rate limits, audit logs, and secrets isolation.

## What a strong candidate says

A strong candidate explains MCP as a secure tool boundary. They mention schema registry, authZ middleware, secrets manager, rate limiting, business API isolation, audit logging, and policy-based tool exposure.

## Visual improvement suggestion

Show three layers:

- **LLM App Layer:** LLM Client, MCP Host
- **Tool Governance Layer:** Tool Server, Schema Registry, AuthZ Middleware, Rate Limiter, Secrets Manager
- **Enterprise System Layer:** Business APIs, Databases, Audit Logs

Add a visible boundary: **“No direct model access to business APIs or secrets.”**
