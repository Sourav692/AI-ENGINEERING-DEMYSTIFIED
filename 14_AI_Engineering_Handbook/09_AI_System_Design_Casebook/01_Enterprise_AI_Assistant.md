# Case 1 — Enterprise AI Assistant over 100+ Applications

> **Level** 🔴 Design Mastery · **Module** 09 · **Doc** 1 of 6 · **Time** ~30 min
> **Prerequisites:** Module 02, Module 05 doc 3, Module 07 doc 1
> **Source material:** `4. FDE_Related_Preparation/System_Design and Delivery/5. Enterprise AI Assistant Design.md`

## The prompt

Design an Enterprise AI Assistant — like ChatGPT Enterprise — that integrates with **100+ internal business applications**, and explain when you would reach for REST APIs, MCP servers, function calling and agent frameworks. The test is whether you treat these as **complementary layers**, not competing technologies.

## Step 1 — Define the problem space

Employees ask *"What's my remaining vacation balance?"*, *"Create a Jira ticket"*, *"Show last month's sales"*, *"Book a meeting room"*. Five clarifying questions reshape the design before a box is drawn:

| Question | Answer | What it decides |
|---|---|---|
| Read-only, or can it act? | Read **and** write | Every containment mechanism from Module 05 is in scope |
| Do backends already speak REST? | REST, GraphQL, SOAP and legacy SQL mixed | Integration diversity → an abstraction over transports |
| Multi-step requests? | Yes — *"schedule a meeting with John and send him the latest proposal"* | An orchestration layer, not just function calling |
| Scale? | 50,000 employees globally, ~8,000 concurrent at peak | Stateless, horizontally scaled services |
| Does every employee see the same data? | No — Finance walled off from HR | Identity propagation as a first-class requirement |

**Functional:** natural-language conversation; read/write enterprise applications; multi-step workflows; 100+ integrations; tool execution; enterprise authentication. **Non-functional:** scalable, available, secure, easy onboarding of new applications, maintainable, extensible.

## Step 2 — High-level architecture

```
Employee
│
Enterprise Chat UI
│
Authentication Layer
│
AI Gateway
│
LLM + Planner Agent
│
┌─────────────────┼─────────────────┐
│                  │                 │
Function Calls   MCP Servers     REST APIs
│                  │                 │
Business Apps    Business Apps   Business Apps
```

Authentication and the AI Gateway sit in front of every request, so **no application ever trusts the LLM directly** — it trusts the identity the gateway attaches. The Planner picks whichever integration path fits the task.

## Step 3 — The deep dive: three integration methods are layers, not alternatives

**REST APIs** — `GET /employees/123`, `POST /jira/ticket`. Ideal when the interface is stable, operations are deterministic, and no AI reasoning is needed. Fast, mature, easy to monitor. But an LLM does not natively understand authentication, endpoint discovery, request schemas or parameter validation, so REST alone never adds up to an assistant.

**Function calling** — `createTicket()`, `getVacation()`. Works when the tool count is small — the model chooses reasonably among twenty functions. Scale to **1,500 functions across 100 applications** and it breaks: prompt size explodes, tool selection gets inaccurate, every schema has to be maintained and re-embedded into prompts. This is Module 07's tool-count trigger, quantified.

**MCP** — one server per application (SAP, Jira, Salesforce, HR) advertising its resources, tools, prompts and capabilities. MCP solves the **discoverability** problem: the assistant asks *"what tools do you expose?"* instead of hardcoding 1,500 schemas. A common confusion: **MCP does not replace REST.** REST remains the transport; MCP standardises how an AI discovers and interacts with capabilities. Internally an MCP server may call REST, SOAP, SQL, Kafka or a legacy system.

**The distinction that separates REST from function calling is *who decides to make the call*, not how it happens on the wire.** REST-as-a-path means fixed application code already knows which endpoint to hit — the vacation page calling `GET /employees/123/vacation` when it renders. Function calling means the *LLM* decides, from natural language, whether to invoke something and with what arguments — and that function's implementation is very often the same REST endpoint underneath. Same wire call, two layers, because they carry different costs: another REST endpoint is cheap; another function the model must choose between costs prompt space and selection accuracy — exactly the ceiling MCP exists to remove.

The full stack, bottom to top:

```
 agent framework     coordinates more than one decision across a multi-step task
       ▲
 MCP                 how the model DISCOVERS which functions exist, without 1,500 hardcoded schemas
       ▲
 function calling    the model's mechanism for DECIDING to invoke one thing
       ▲
 REST / SOAP / SQL   what actually EXECUTES
```

## Step 4 — Agent frameworks and orchestration

Agent frameworks earn their place when a request needs multi-step reasoning. *"Prepare a renewal report for our top customers and email their managers"* means finding customers, retrieving CRM data, generating a report, creating charts, storing a PDF, sending an email — no single function coordinates that. A Planner decomposes the request onto a task queue; specialists — CRM, Email, Analytics, Calendar — execute their portion; results merge.

| | Single agent | Multi-agent |
|---|---|---|
| Shape | One tool, short workflow, deterministic execution | Planning required, many domains, independent specialists, long-running |
| Example | *"Create a Jira ticket"* — an orchestrator would be overhead | *"Analyse quarterly sales, identify declining regions, prepare a deck, notify leadership"* |

Module 07's rule, in this domain.

| Technology | Best use |
|---|---|
| REST API | Direct application communication |
| Function calling | Small, deterministic tool execution |
| MCP | Enterprise tool discovery and standardised AI integration |
| Agent framework | Multi-step planning, orchestration, reasoning |

## Step 5 — Scaling to 500+ applications and 200,000 employees

1. **Tool discovery** — loading every MCP server up front does not scale. A **Tool Registry** between the Planner and the universe of MCP servers loads only the servers relevant to the current task, keeping prompt size small.
2. **Caching** — employee profiles, org hierarchy, holiday calendar.
3. **Horizontal scaling** — Planner, authentication, gateway and LLM routing all stateless behind load balancers.
4. **Rate limiting** — user quotas, application quotas, circuit breakers against runaway agents, accidental loops and prompt abuse.
5. **Async execution** — long-running workflows return "task accepted" with a job ID; workers execute.
6. **Security** — every request propagates user identity, an OAuth token, RBAC/ABAC and audit logs. **No application trusts the LLM; applications trust enterprise identity.** Module 06's identity, applied per tool call.
7. **Observability** — every execution produces a full trace: prompt → selected tools → reasoning → API calls → latency → cost → errors.

**Global deployment:** regional AI gateways; region-local MCP servers for apps hosted in each geography; a global identity provider with regional token validation; read replicas and regional caches; active-active for stateless services with geo-DNS; data-residency controls keeping HR and financial data in jurisdiction.

## Trade-offs

| Criteria | REST | Function calling | MCP | Agent framework |
|---|---|---|---|---|
| Scalability | High | Medium | High | Medium |
| Maintainability | High | Medium | Very high | Medium |
| Discoverability | Poor | Medium | Excellent | Good |
| Security | Mature | Good | Excellent | Good |
| Extensibility | Medium | Medium | Excellent | High |
| AI-native | No | Yes | Yes | Yes |

## Summary

The architecture separates responsibilities rather than picking one technology. REST remains the foundational integration mechanism. MCP provides an AI-native abstraction over enterprise applications for standardised discovery and easy onboarding. Function calling invokes well-defined operations once the right tool has been selected. An agent framework orchestrates multi-step workflows needing planning, retries, parallelism and cross-domain coordination. Scalability from stateless gateways, a tool registry, caching, async jobs and horizontally scaled planners; security from identity propagated end to end, RBAC/ABAC at the application layer, audit logs, and an LLM that never bypasses existing authorisation.

## What this case does not cover

Read against the [Agentic Coverage Map](06_Agentic_Coverage_Map.md): no RAG, no memory, no human-approval workflow, no guardrails or prompt-injection defence, no model routing. It goes deep on integration and discovery at scale and stops there. Pair it with Case 2.

## Checkpoint

- Explain why REST, function calling, MCP and agent frameworks are layers, and what each layer adds.
- What is the axis that actually separates REST from function calling?
- At what point does function calling break, and what does MCP change?
- What does a Tool Registry do that loading every MCP server does not?
- State the security principle in one sentence.

**Next →** [Case 2 — Customer Support Assistant](02_Customer_Support_Assistant.md)
