# Case 2 — Customer Support AI Assistant

> **Level** 🔴 Design Mastery · **Module** 09 · **Doc** 2 of 6 · **Time** ~30 min
> **Prerequisites:** Module 03 doc 2, Module 04, Module 05 doc 5, Module 07
> **Source material:** `4. FDE_Related_Preparation/System_Design and Delivery/6. Customer Support AI Assistant Design.md`

## The prompt

Design an AI customer-support platform — Salesforce Einstein plus Zendesk plus AI agents — that answers FAQs, creates and updates tickets, queries CRM, processes refunds and escalates cases. Explain when you would reach for **RAG, agent orchestration, tool calling, MCP servers, human approval and memory**, and the trade-offs each carries.

## Step 1 — Define the problem space

| Question | Answer | What it decides |
|---|---|---|
| Answering only, or executing actions? | **Both** | Retrieval *and* action paths |
| Where does product knowledge live? | Docs, knowledge base, CRM, order management, ticketing | Exactly the shape RAG is built for |
| Can the AI make business decisions independently — a $5,000 refund? | No | Human-in-the-loop for sensitive operations |
| Scale? | ~1M conversations/day globally | Cost optimisation is first-class |
| Should it remember previous conversations? | Yes | Conversational memory on top of enterprise knowledge |

**Functional:** answer FAQs; search enterprise knowledge; create/update tickets; query CRM; process refunds; escalate; maintain conversation history. **Non-functional:** availability, low latency, enterprise security, accuracy, easy onboarding of new systems, scale, cost.

## Step 2 — High-level architecture: three peers, not a pipeline

```
Customer
│
Web / Mobile / WhatsApp
│
API Gateway
│
Authentication Layer
│
AI Orchestrator Agent
┌──────────────┼──────────────┐
│              │              │
RAG Layer   Tool Calling    Memory
│              │              │
│         MCP Servers         │
│              │              │
Knowledge    CRM  Ticketing  Order Mgmt
Base         ERP  Payments   Inventory
│
Enterprise LLM
│
Human Approval
│
Customer Response
```

RAG, tool calling and memory sit side by side as capabilities the orchestrator draws on — not a sequential pipeline every request passes through. Module 02's travel-agent lesson: retrieval is something an agent calls when it needs it.

## Step 3 — The deep dives

### RAG vs tool calling — why both

They solve different problems. *"What is your refund policy?"* → retrieve from the knowledge base. *"Refund my order"* → invoke a business system. LLMs generate text; they do not update enterprise databases by themselves. RAG retrieves accurate, current answers rather than relying on model memory; tool calling executes deterministic operations that are reliable and auditable in a way free text is not.

### Where MCP fits

Dozens or hundreds of backend systems. Instead of exposing thousands of APIs to the LLM, MCP servers — CRM, Ticketing, Payments, Inventory — each advertise their tools; the AI discovers what is available. REST remains the transport; MCP solves interoperability and discoverability. Case 1's argument, from the support side.

### Multi-agent orchestration — not every request needs a planner

*"Track my order"* is a single tool call. *"My laptop arrived damaged. Refund the order, cancel the warranty, notify shipping, and create a high-priority ticket"* requires planning across systems — that is when a Planner earns its cost, decomposing across Knowledge, CRM, Refund, Ticket, Shipping and Notification agents and merging results. Simple requests: a single agent or direct tool call, faster and cheaper. Multi-agent: reserved for cross-system tasks. Module 07 doc 1.

### Three layers of memory

| Layer | Holds | Example |
|---|---|---|
| **Short-term** | Context within the session | *"Where's my package?"* … *"Can you refund it?"* — *it* is the same order |
| **Long-term customer** | Preferences and history across sessions | Language, channel, past purchases, past support interactions |
| **Enterprise knowledge** | Stored separately in RAG | Product docs, policies, FAQs, troubleshooting |

Keeping enterprise knowledge apart from conversational memory improves both accuracy and maintainability — a stale preference and an outdated policy fail very differently, and conflating them makes both harder to fix. Module 03 doc 2.

### Human approval workflow

Required for high-risk or high-value actions: refunds above a threshold, VIP escalations, account deletion, legal or compliance requests, changes to payment information.

```
Refund Request → AI Validation → Approval Required? ─yes─▶ Manager Approval Queue → Approved → Execute Refund
                                          └──no──▶ Execute
```

The AI validates first; most requests never reach a human. Only those crossing a risk or value threshold route to a manager queue before execution. Module 05's guardrail decision, in product form.

## Step 4 — Scaling to 50M customers, 10M conversations a day

1. **Stateless AI services** — gateways, orchestrators, LLM routing behind load balancers.
2. **RAG scaling** — partition embeddings by product, region, language and business unit rather than searching everything.
3. **Semantic cache** — *"What is your return policy?"*, *"Where is my order?"* answered without invoking the LLM.
4. **Asynchronous workflows** — refunds, warranty cancellations, shipping investigations run in the background; the AI replies *"your request has been submitted"* immediately.
5. **Rate limiting** — per-user, per-tenant, tool-invocation limits, circuit breakers.
6. **Security** — every tool invocation propagates enterprise identity, OAuth, RBAC/ABAC, audit. **The LLM never bypasses application authorisation; business systems remain the source of truth.**
7. **Cost — model routing** — FAQ → small model; refund investigation → large reasoning model.

**Global:** regional gateways and orchestrators; knowledge indexes partitioned by geography where residency requires; stateless services active-active; customer data within compliance boundaries; global load balancing to the nearest healthy region.

## Trade-offs

| Technology | Best use | Advantages | Trade-offs |
|---|---|---|---|
| RAG | Enterprise knowledge retrieval | Accurate, current | Indexing and embedding pipeline |
| Tool calling | Deterministic business actions | Reliable, auditable | Limited to predefined tools |
| MCP | Standardised integrations | Discoverability, extensibility | An extra abstraction layer |
| Agent framework | Multi-step workflows | Modular, parallel | Orchestration complexity |
| Human approval | High-risk operations | Governance, compliance | Response time |
| Memory | Personalised conversations | Better experience | Lifecycle management, privacy |
| Semantic cache | Repeated questions | Latency and cost | Invalidation complexity |

## The detailed end-to-end design

Customer channels → authentication → load balancer → API gateway and rate limiter → **semantic cache immediately after the gateway** (a repeated question never reaches the orchestrator) → orchestrator / planner → specialist agents → the shared capability layer (RAG over partitioned vector DBs; short- and long-term memory; tool calling through MCP servers; model gateway routing small vs large) → backend systems (CRM/ERP, ticketing, payments, inventory) → human approval queue for high-risk actions → response → monitoring and observability over the whole path.

## Summary

Specialised responsibilities, not one LLM doing everything. RAG for accurate answers from current knowledge; tool calling for deterministic operations; MCP as the standard interface letting new systems onboard with minimal change; orchestration for cross-domain workflows; memory split three ways; human approval governing high-risk actions. Scale from stateless services, semantic caching, async processing, partitioned vector DBs and regional deployment. Security from enterprise authentication, RBAC/ABAC, identity propagation, encryption, audit and tenant isolation.

## What this case does not cover

Against the [Agentic Coverage Map](06_Agentic_Coverage_Map.md): no tool-registry-at-scale discussion (Case 1 has it), no guardrails or prompt-injection defence, no prompt versioning, no DR or chaos testing, no derived capacity numbers. Modules 06 and 08 fill those.

## Checkpoint

- Why are RAG, tool calling and memory peers rather than a pipeline?
- Give one request that needs a planner and one that must not have one.
- Name the three memory layers and say why the third is not memory.
- Which actions route to human approval, and where does the AI's validation sit relative to that?
- State the security principle and compare it to Case 1's.

**Next →** [Case 3 — Coding Assistant](03_Coding_Assistant.md)
