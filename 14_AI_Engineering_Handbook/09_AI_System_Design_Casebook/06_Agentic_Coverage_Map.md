# The Agentic Coverage Map

> **Level** 🔴 Design Mastery · **Module** 09 · **Doc** 6 of 6 · **Time** ~20 min
> **Prerequisites:** [Case 1](01_Enterprise_AI_Assistant.md), [Case 2](02_Customer_Support_Assistant.md)
> **Source material:** `4. FDE_Related_Preparation/System_Design and Delivery/Agentic Coverage Map.html`

## Why this matters

Cases 1 and 2 are the two canonical agentic-assistant designs, and neither is complete on its own. Read side by side against the vocabulary of agentic system design, they are complementary rather than redundant — and together they still leave four gaps. This document is the map: which concept each case covers, and what you must bring from the rest of the handbook.

**Verdict:** between them they cover nearly every concept an agentic-system-design round expects. The Enterprise Assistant goes deep on integration methods and tool discovery at scale but never mentions RAG, memory or human approval. The Customer Support Assistant covers the full agent loop — RAG, memory, human-in-the-loop, model routing — but does not revisit the tool-registry scaling problem.

## The combined architecture

One generic agentic-assistant spine, each stage tagged by which case covers it:

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │ Client channels            web · mobile · WhatsApp · chat UI     both  │
  │ Authentication             OAuth / SSO / JWT                     both  │
  │ API Gateway                routing · quota                       both  │
  │ Semantic Cache             repeated queries, no LLM call         both  │
  │ Orchestrator / Planner     decomposes the request                both  │
  ├── PARALLEL CAPABILITIES — reached from the orchestrator ───────────────┤
  │ RAG / knowledge retrieval  vector DB · docs · policies        Support  │
  │ Tool / function calling    deterministic actions                 both  │
  │ MCP servers                per-app tool discovery                both  │
  │ Tool registry at scale     loads only relevant tools       Enterprise  │
  │ Memory                     short-term + long-term             Support  │
  │ Specialised agents         CRM · refund · ticket · …             both  │
  ├── CONVERGE ────────────────────────────────────────────────────────────┤
  │ Model gateway / routing    small for FAQs, large for reasoning Support │
  │ Human approval queue       high-value / high-risk actions      Support │
  │ Response                   streamed, trace-id retained           both  │
  ├── CROSS-CUTTING ───────────────────────────────────────────────────────┤
  │ Async execution · rate limiting · RBAC/ABAC · audit · observability    │
  │ Multi-region · data residency                                    both  │
  │ Guardrails & prompt-injection defence                     GAP IN BOTH  │
  │ DR / chaos testing                                        GAP IN BOTH  │
  └────────────────────────────────────────────────────────────────────────┘
```

## Concept by concept

| Concept | Case 1 · Enterprise | Case 2 · Support | Note |
|---|---|---|---|
| **Foundations** | | | |
| Clarifying questions before architecture | ✓ | ✓ | Both open with five questions that shape scope |
| Functional vs non-functional split | ✓ | ✓ | |
| High-level diagram before deep dive | ✓ | ✓ | |
| A reusable interview framework named as a takeaway | ✓ | — | Only Case 1 names the meta-framework |
| **Knowledge and retrieval** | | | |
| RAG | — | ✓ | Case 1 is action/read-write only; RAG never appears |
| Vector DB partitioning by geography / product | — | ✓ | |
| Embedding pipeline as a cost item | — | ~ | Implied in the trade-off table |
| **Action and integration** | | | |
| REST as the integration substrate | ✓ | ✓ | Both: MCP standardises discovery, REST still does the calling |
| Function / tool calling | ✓ | ✓ | |
| MCP servers | ✓ | ✓ | |
| Tool registry / dynamic discovery at scale | ✓ | — | Case 1 solves the "1,500 functions" problem explicitly |
| Integration-method trade-off table | ✓ | ✓ | |
| **Orchestration** | | | |
| Single- vs multi-agent decision rule | ✓ | ✓ | Both give a concrete "one agent when…" rule |
| Planner / orchestrator agent | ✓ | ✓ | |
| Specialised domain agents | ✓ | ✓ | |
| **Memory** | | | |
| Short-term session memory | — | ✓ | |
| Long-term customer memory | — | ✓ | |
| Memory kept separate from enterprise knowledge | — | ✓ | Named as a deliberate choice |
| **Governance and safety** | | | |
| Human-in-the-loop approval | — | ✓ | Thresholds, VIP, compliance triggers, manager queue |
| RBAC / ABAC | ✓ | ✓ | Both: the application, never the LLM, is the source of truth |
| Identity propagation per tool call | ✓ | ✓ | |
| Audit logging | ✓ | ✓ | |
| **Guardrails / prompt injection / moderation** | **—** | **—** | **Neither mentions validating against adversarial content** |
| **Scale and performance** | | | |
| Stateless, horizontally scaled services | ✓ | ✓ | |
| Semantic caching, named explicitly | ~ | ✓ | Case 1 mentions generic caching of profile data |
| Model routing | — | ✓ | |
| Async execution / job-id pattern | ✓ | ✓ | |
| Rate limiting and circuit breakers | ✓ | ✓ | |
| Cost optimisation as its own goal | ~ | ✓ | |
| **Operations** | | | |
| Observability / tracing | ✓ | ✓ | |
| Multi-region / global deployment | ✓ | ✓ | |
| Data residency | ✓ | ✓ | |
| **Disaster recovery / chaos testing** | **—** | **—** | **No backup/restore or failure-injection discussion** |
| Final trade-off table | ✓ | ✓ | |

## What neither covers — and where the handbook fills it

| Gap | Why it matters | Where it is covered |
|---|---|---|
| **Guardrails and prompt-injection defence** | Neither treats retrieved documents or tool output as untrusted input, or validates model output before it triggers an action | Module 04 doc 6 (architectural defence), Module 06 doc 4 (separate channels, schema as firewall, egress), Module 08 doc 5 (red teaming) |
| **Prompt management / versioning** | System prompts are implied but never treated as versioned, tested artefacts | Module 04 doc 8 (`PROMPT_VERSION`), Module 08 docs 1–2 |
| **Disaster recovery and chaos testing** | Multi-region is covered for latency and residency, but neither walks through what happens when a region — or the LLM provider — goes down | Module 02 doc 1 (chaos testing, multi-region failover, reliability vs availability), Module 06 doc 2 (backup provider, bulkhead, kill switch) |
| **Explicit capacity estimation** | Both state a target (1M or 10M conversations/day; 50K–200K employees) but neither derives RPS, storage or bandwidth from it | Module 02 doc 1 §4 (capacity estimation), Case 3's latency-budget decomposition, Case 5's event-throughput sizing |

## How to use this map

When you draw an agentic assistant in a design round, walk the spine top to bottom and check every row. The four gap rows are the ones most candidates leave silent, and they are the ones a senior interviewer is waiting for. Raise them in Step 5 of the 60-minute method, unprompted.

## Checkpoint

- Which concepts does only Case 1 cover, and which only Case 2?
- Name the four gaps in both and the handbook module that fills each.
- Why does "the application, never the LLM, is the source of truth" appear in both cases, and where else in the handbook is it stated?
- Draw the combined spine from memory and tag each stage.

**Next →** [whiteboard_scripts/](whiteboard_scripts/) — the four full 60-minute scripts — then [Module 10 · FDE Delivery and Operating Model](../10_FDE_Delivery_Operating_Model/README.md)
