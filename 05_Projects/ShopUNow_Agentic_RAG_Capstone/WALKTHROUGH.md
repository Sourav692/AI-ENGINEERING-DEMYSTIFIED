# ShopUNow Agentic RAG System — Full Walkthrough

This document provides a comprehensive walkthrough of the **ShopUNow Multi-User Conversational Agentic RAG System**, built with LangGraph. It covers the architecture, memory layers, routing logic, and the functionality of every node in the graph.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Knowledge Layer — Vector Databases](#knowledge-layer--vector-databases)
4. [State Definition](#state-definition)
5. [Node-by-Node Walkthrough](#node-by-node-walkthrough)
   - [Node 1: Categorize Query](#node-1-categorize-query)
   - [Node 2: Retrieve Docs](#node-2-retrieve-docs)
   - [Node 3: Generate Response](#node-3-generate-response)
   - [Node 4: Hallucination Check](#node-4-hallucination-check)
   - [Node 5: Finalize](#node-5-finalize)
6. [Routing Logic](#routing-logic)
7. [Memory Layers](#memory-layers)
   - [Layer 1: Conversation Memory (MemorySaver)](#layer-1-conversation-memory-memorysaver)
   - [Layer 2: History Formatting & Token Budget](#layer-2-history-formatting--token-budget)
   - [Layer 3: Persistent Memory (SqliteSaver)](#layer-3-persistent-memory-sqlitesaver)
8. [Multi-User Isolation](#multi-user-isolation)
9. [End-to-End Request Flow](#end-to-end-request-flow)
10. [Design Decisions & Trade-offs](#design-decisions--trade-offs)

---

## System Overview

The ShopUNow Agentic RAG system is a **multi-user, multi-department conversational assistant** for an e-commerce company that sells clothing, DIY tools, books, and toys. It combines:

- **Retrieval-Augmented Generation (RAG)** — answers are grounded in department-specific knowledge bases, not hallucinated.
- **Agentic routing** — an LLM autonomously classifies each query and routes it to the correct department's vector store.
- **Conversation memory** — each user gets isolated, persistent conversation history so follow-up questions resolve correctly.
- **Hallucination guardrails** — every generated response is verified against source documents before delivery.

The system serves two audiences across **7 departments**:

| Audience | Departments |
|---|---|
| Internal Employees | HR, IT Support, Facilities & Admin |
| External Customers | Customer Service, Product & Sales, Billing & Payments, Shipping & Delivery |

---

## Architecture Diagram

```
User Query + thread_id (user identity)
    │
    ▼
┌──────────────────────────────────────────────────┐
│                  MemorySaver                      │
│  Loads conversation history for this thread_id    │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Categorize Query │  LLM classifies → 1 of 7 departments
              │ (context-aware)  │  Uses conversation history for follow-ups
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Retrieve Docs   │  Similarity search on department's ChromaDB
              │                  │  Returns top-3 relevant documents
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │Generate Response │  LLM synthesizes answer from:
              │ (history-aware)  │    - Retrieved docs
              │                  │    - Conversation history (trimmed)
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Hallucination    │  LLM grades: "grounded" or "not_grounded"
              │ Check            │
              └────────┬────────┘
                  ┌────┴────┐
                  │         │
            grounded    not_grounded
            OR max        (retry ≤ 1)
            retries        │
                  │         │
                  ▼         └──► back to Generate Response
              ┌────────┐
              │Finalize │  Appends HumanMessage + AIMessage
              │         │  to conversation history
              └────┬───┘
                   │
                   ▼
                 [END]
```

The graph has **5 nodes** and **1 conditional edge**. In the best case (response is grounded on the first try), the system makes **3 LLM calls** per query: classify, generate, grade. In the worst case (one retry), it makes **4 LLM calls**.

---

## Knowledge Layer — Vector Databases

Before the agentic system runs, a separate preprocessing step (`01_create_vector_databases.ipynb`) builds the knowledge base.

### Data Source

Each department has **15 QA pairs** generated from a structured prompt template. The data is stored as JSON files under `data/`, with each record containing:

```json
{
  "doc": "Question: ...\nAnswer: ...",
  "category": "Department Name"
}
```

**Total: 105 QA pairs across 7 departments.**

### Embedding & Storage

Each department gets its own **persistent ChromaDB vector store**:

```
vectorstores/
├── hr/                    (15 vectors, ~0.74 MB)
├── it_support/            (15 vectors, ~0.74 MB)
├── facilities_admin/      (15 vectors, ~0.75 MB)
├── customer_service/      (15 vectors, ~0.74 MB)
├── product_sales/         (15 vectors, ~0.74 MB)
├── billing_payments/      (15 vectors, ~0.75 MB)
└── shipping_delivery/     (15 vectors, ~0.74 MB)
                           Total: ~5.2 MB
```

Embeddings are generated using a platform-aware factory (`get_embeddings()`) that selects `databricks-gte-large-en` on macOS or `text-embedding-3-small` (OpenAI) on Windows. Each ChromaDB collection is named `dept_<department>` (e.g., `dept_hr`).

### Why Separate Vector Stores?

Separate stores per department prevent cross-contamination of retrieval results. An HR query only searches HR documents — it never accidentally retrieves shipping policies. This is a **routing-first** architecture: classify first, then retrieve from the right silo.

---

## State Definition

The LangGraph state is defined as a `TypedDict` that flows through every node:

```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # conversation history
    query: str                        # original user question
    department: str | None            # classified department key
    retrieved_docs: str | None        # formatted retrieved context
    response: str | None              # generated answer
    hallucination_grade: str | None   # "grounded" or "not_grounded"
    retries: int                      # regeneration counter (cap at 1)
```

| Field | Purpose | Written By |
|---|---|---|
| `messages` | Accumulated conversation turns, managed by `add_messages` reducer | Finalize node |
| `query` | The raw user question for this turn | Caller (`chat()` function) |
| `department` | Which of the 7 departments to query | Categorize Query node |
| `retrieved_docs` | Formatted top-3 documents from ChromaDB | Retrieve Docs node |
| `response` | The LLM-generated answer text | Generate Response node |
| `hallucination_grade` | Whether the response is grounded | Hallucination Check node |
| `retries` | How many generation attempts have been made | Hallucination Check node |

The `add_messages` annotation on `messages` is the key mechanism — it tells LangGraph to *append* new messages rather than overwrite, enabling conversation history accumulation across turns.

---

## Node-by-Node Walkthrough

### Node 1: Categorize Query

**Function:** `categorize_query(state) -> {"department": str}`

**Purpose:** Classify the user's question into exactly one of 7 departments so retrieval targets the right knowledge base.

**How it works:**

1. Formats the last 3 conversation turns (6 messages) into a text block using `_format_history()`.
2. Feeds the history + current query into a classification prompt via `ChatPromptTemplate`.
3. Uses **structured output** (`llm.with_structured_output(QueryClassification)`) to force the LLM to return a valid Pydantic model with a single field — `department` — constrained to a `Literal` of exactly the 7 valid department keys.

**The classification prompt gives the LLM a lookup table:**

| Department Key | Topics |
|---|---|
| `hr` | Leave policy, salary, appraisals, onboarding, employee benefits |
| `it_support` | Password resets, VPN, software installs, hardware issues, email |
| `facilities_admin` | Meeting rooms, office supplies, parking, building access, maintenance |
| `customer_service` | Complaints, returns, account issues, order problems |
| `product_sales` | Product info, discounts, availability, recommendations, pricing |
| `billing_payments` | Invoices, refunds, payment methods, transaction issues |
| `shipping_delivery` | Tracking, delivery times, shipping costs, address changes |

**Why conversation history matters here:** Without history, a follow-up like *"What about refunds?"* after a billing question would be ambiguous. By injecting the last few turns, the classifier sees the billing context and correctly routes to `billing_payments` instead of guessing `customer_service`.

**Output:** `{"department": "hr"}` (or whichever department matches).

---

### Node 2: Retrieve Docs

**Function:** `retrieve_docs(state) -> {"retrieved_docs": str}`

**Purpose:** Load the appropriate department's ChromaDB vector store and run a similarity search to find the most relevant knowledge documents.

**How it works:**

1. Reads `state["department"]` to determine which vector store to load.
2. Calls `load_vectorstore(dept)` which opens the persistent ChromaDB directory at `vectorstores/<dept>/`.
3. Runs `similarity_search(query, k=3)` — this embeds the user's query and finds the 3 nearest neighbors by cosine similarity.
4. Formats the results into a numbered text block:

```
[Doc 1] Question: How many paid leaves...
Answer: Full-time employees...

---

[Doc 2] Question: What is the work-from-home policy...
Answer: ShopUNow follows a hybrid work model...

---

[Doc 3] Question: Can I carry forward unused leaves...
Answer: ...
```

**Output:** `{"retrieved_docs": "<formatted document string>"}` — this becomes the context for generation.

**Design note:** Retrieval uses the raw `query` string, not a reformulated version. For a production system, you might add a query rewriting step that uses conversation context to expand ambiguous follow-ups before retrieval.

---

### Node 3: Generate Response

**Function:** `generate_response(state) -> {"response": str}`

**Purpose:** Synthesize a natural-language answer from the retrieved documents and conversation history.

**How it works:**

1. **Trims conversation history** using LangChain's `trim_messages()` with a budget of ~4,000 tokens (estimated at 4 characters per token). This prevents the prompt from exceeding context limits on long conversations.
2. Formats the trimmed history into the same `User: ... / Assistant: ...` text block used by the classifier.
3. Injects three variables into the generation prompt:
   - `{history}` — trimmed conversation context
   - `{query}` — the current question
   - `{context}` — the retrieved documents from Node 2
4. The system prompt strictly constrains the LLM: *"Use ONLY the provided context to answer. If the context does not contain enough information, say so clearly. Do not make up information."*

**Output:** `{"response": "<answer text>"}` — the candidate response that will be graded next.

**Why history matters here:** When a user asks *"What about carry-forward?"* after asking about paid leaves, the history tells the generation LLM that "carry-forward" refers to leave policy. Without history, the LLM would have no way to connect the follow-up to the previous topic.

---

### Node 4: Hallucination Check

**Function:** `hallucination_check(state) -> {"hallucination_grade": str, "retries": int}`

**Purpose:** Verify that the generated response is fully supported by the retrieved documents — no fabricated facts, no contradictions.

**How it works:**

1. Takes the `retrieved_docs` and the `response` from state.
2. Feeds them into a hallucination grading prompt that asks: *"Is every claim in the response traceable back to the provided documents?"*
3. Uses **structured output** (`llm.with_structured_output(HallucinationGrade)`) to force a binary verdict:
   - `"grounded"` — the response is fully supported
   - `"not_grounded"` — the response contains unsupported claims
4. Increments the `retries` counter.

**Output:** `{"hallucination_grade": "grounded", "retries": 1}` (or `"not_grounded"`).

This node is a **self-correction guardrail**. It doesn't fix the response — it only decides whether the response should be accepted or regenerated.

---

### Node 5: Finalize

**Function:** `finalize(state) -> {"messages": [HumanMessage, AIMessage]}`

**Purpose:** Record the completed conversation turn into the message history so future queries have context.

**How it works:**

1. Creates a `HumanMessage` from `state["query"]`.
2. Creates an `AIMessage` from `state["response"]`.
3. Returns both as a list under the `messages` key.

Because `messages` uses the `add_messages` reducer, these two messages are **appended** to the existing conversation history rather than replacing it. This is what builds up the multi-turn conversation.

**Output:** `{"messages": [HumanMessage(...), AIMessage(...)]}`.

After this node, the graph reaches `END` and the response is returned to the caller.

---

## Routing Logic

The graph has one critical routing decision — the **conditional edge** after the Hallucination Check node. The routing function `route_after_hallucination_check` implements a bounded retry loop:

```
                    ┌────────────────────────┐
                    │   hallucination_check   │
                    └───────────┬────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
              grade == "grounded"    grade == "not_grounded"
              OR retries >= 2              │
                    │                       │
                    ▼                       ▼
              ┌──────────┐         ┌─────────────────┐
              │ finalize  │         │generate_response │
              └──────────┘         │   (retry)        │
                                   └─────────────────┘
```

**The decision logic:**

1. **Grounded** → proceed to `finalize`. The response is trustworthy.
2. **Not grounded AND retries < 2** → loop back to `generate_response` for one more attempt. The same retrieved docs are reused — only the generation is re-run.
3. **Not grounded AND retries >= 2** → proceed to `finalize` anyway. The system caps at 1 retry (original attempt + 1 regeneration = 2 total attempts) to avoid infinite loops and excessive LLM costs.

**All other edges are unconditional:**

| From | To |
|---|---|
| `START` | `categorize_query` |
| `categorize_query` | `retrieve_docs` |
| `retrieve_docs` | `generate_response` |
| `generate_response` | `hallucination_check` |
| `finalize` | `END` |

---

## Memory Layers

The system uses three distinct memory mechanisms, each operating at a different level.

### Layer 1: Conversation Memory (MemorySaver)

**What:** LangGraph's `MemorySaver` checkpointer provides per-thread conversation persistence.

**How:** The graph is compiled with `memory = MemorySaver()`, and every invocation passes a `thread_id` via the config:

```python
graph.invoke(
    {"query": "How many paid leaves?", ...},
    config={"configurable": {"thread_id": "employee_42"}},
)
```

After each turn, the Finalize node appends `HumanMessage` + `AIMessage` to the `messages` state field. The checkpointer saves this state keyed by `thread_id`. On the next invocation with the same `thread_id`, the full message history is restored automatically.

**Scope:** In-memory only — lost when the Python process restarts.

### Layer 2: History Formatting & Token Budget

**What:** A token-aware history management layer that prevents conversation history from overflowing the LLM context window.

**How:** Two mechanisms work together:

1. **`_format_history(messages, max_turns=3)`** — Extracts the last 3 conversation turns (6 messages), truncates individual messages to 200 characters, and formats them as `User: ... / Assistant: ...` text. Used by both the Categorize Query and Generate Response nodes.

2. **`trim_messages(max_tokens=4000)`** — LangChain's built-in message trimmer, used only in the Generate Response node. It applies a `"last"` strategy that keeps the most recent messages within a ~4,000 token budget (estimated at 4 characters per token). This ensures the generation prompt stays within context limits even for very long conversations.

The two layers are complementary: `trim_messages` handles the raw message list, then `_format_history` formats the trimmed result for prompt injection.

### Layer 3: Persistent Memory (SqliteSaver)

**What:** An optional upgrade path for production use. `SqliteSaver` stores conversation state in a SQLite database file (`memory.db`) that survives process restarts.

**How:** Swap `MemorySaver()` for `SqliteSaver.from_conn_string("memory.db")` when compiling the graph. The API is identical — the only difference is durability.

```python
with SqliteSaver.from_conn_string("memory.db") as persistent_memory:
    persistent_graph = workflow.compile(checkpointer=persistent_memory)
```

This is provided as commented-out code in the notebook for users who need conversations to survive kernel restarts.

---

## Multi-User Isolation

The system achieves user isolation through the `thread_id` parameter. Each unique `thread_id` gets its own independent conversation history:

```python
# User A — employee context
chat("How many paid leaves?", user_id="employee_42")
chat("What about carry-forward?", user_id="employee_42")  # follows up on leaves

# User B — customer context (completely separate)
chat("I received a damaged product", user_id="customer_99")
chat("How long will the refund take?", user_id="customer_99")  # follows up on damage
```

**Isolation guarantees:**

- User A's message history contains 6 messages (3 turns). User B's contains 4 messages (2 turns).
- User B's follow-up about refunds is classified in the context of *their* damaged product conversation, not User A's HR questions.
- The state for each user can be inspected independently:

```python
state_a = graph.get_state({"configurable": {"thread_id": "employee_42"}})
state_b = graph.get_state({"configurable": {"thread_id": "customer_99"}})
```

---

## End-to-End Request Flow

Here is the complete lifecycle of a single user query, using a concrete example:

**Scenario:** User `employee_42` asks *"What about carry-forward? Can I carry unused leaves to next year?"* as a follow-up to a previous question about paid leaves.

### Step 1 — Invocation

The `chat()` helper initializes state with the query and resets transient fields:

```python
{
    "query": "What about carry-forward? Can I carry unused leaves to next year?",
    "department": None,
    "retrieved_docs": None,
    "response": None,
    "hallucination_grade": None,
    "retries": 0,
}
```

The `config` carries `thread_id: "employee_42"`, which tells the checkpointer to restore this user's message history.

### Step 2 — Categorize Query

The node sees conversation history:

```
User: How many paid leaves do I get per year?
Assistant: Full-time employees at ShopUNow are entitled to 24 paid leaves...
```

Combined with the current query about "carry-forward," the classifier routes to `hr`.

### Step 3 — Retrieve Docs

Loads `vectorstores/hr/` and runs similarity search with k=3. Returns the 3 most semantically relevant HR QA pairs.

### Step 4 — Generate Response

Builds a prompt with:
- Trimmed conversation history (the prior leave discussion)
- The current query
- The 3 retrieved HR documents

The LLM generates a response grounded in the retrieved context, naturally referencing the prior conversation about paid leaves.

### Step 5 — Hallucination Check

Compares the generated response against the 3 retrieved documents.

- If **grounded** → proceeds to Finalize.
- If **not grounded** → loops back to Step 4 for one retry. On the retry, the same retrieved docs are reused but the LLM gets another chance at generation.
- If still not grounded after retry → proceeds to Finalize with the best-effort response.

### Step 6 — Finalize

Appends two new messages to conversation history:

```
HumanMessage("What about carry-forward? Can I carry unused leaves to next year?")
AIMessage("<the generated response>")
```

The checkpointer saves the updated state. The response string is returned to the caller.

### LLM Call Count

| Scenario | LLM Calls | Nodes Visited |
|---|---|---|
| Best case (grounded first try) | 3 | Categorize → Retrieve → Generate → Check → Finalize |
| Worst case (1 retry, then accept) | 4 | Categorize → Retrieve → Generate → Check → Generate → Check → Finalize |

---

## Design Decisions & Trade-offs

### Routing-first vs. unified retrieval

The system classifies the query *before* retrieval, searching only the matching department's vector store. The alternative — searching all 105 documents in a single store — would be simpler but risks cross-department contamination (e.g., an HR query retrieving shipping info that happens to share similar vocabulary).

### Bounded retry loop

The hallucination check allows exactly 1 retry. This balances quality (a second attempt often produces a better response) against cost and latency (each retry adds another LLM call). The system always returns *something* — it never enters an infinite failure loop.

### History truncation

Conversation history is capped at 3 turns for classification and ~4,000 tokens for generation. This prevents context window overflow while keeping enough context for follow-up resolution. Older turns are silently dropped, which means very long conversations may lose early context.

### Structured output for classification and grading

Both the Categorize Query and Hallucination Check nodes use Pydantic models with `with_structured_output()`. This eliminates parsing errors — the LLM is forced to return valid JSON that maps directly to typed Python objects. There is no string-matching or regex extraction.

### MemorySaver as default

In-memory storage is the default because it requires zero setup. The SqliteSaver upgrade path is documented but commented out, letting users opt in when they need durability. For production deployments, PostgreSQL-backed checkpointers would be more appropriate for concurrent multi-user access.
