# Agent Memory Types — LangGraph + SQLite

Companion notes for `02_Agent_Memory_Types_SQLite.ipynb`. This document explains the three memory types used by the agent, how each is persisted, and walks through concrete examples drawn from the notebook's end-to-end demo.

---

## The Mental Model

A stateless LLM call forgets everything the moment it returns. An **agent** needs memory — but not all memory is the same. Borrowing from cognitive science, this agent implements three distinct kinds:

| Memory Type | Analogy | Scope | Lifetime | Stored In |
|---|---|---|---|---|
| **Short-Term (Working)** | RAM — what you hold in mind mid-conversation | Single `thread_id` | Session (persisted across restarts) | `SqliteSaver` checkpoint tables |
| **Long-Term (Semantic)** | Facts you *know* about a person | Per `user_id`, across all threads | Persistent | `semantic_memory` table |
| **Episodic** | Experiences you *lived through* | Per `user_id`, across all threads | Persistent | `episodic_memory` table |

All three live in one file: `agent_memory.db`.

---

## 1. Short-Term (Working) Memory

### What it is
The running conversation — every `HumanMessage`, `AIMessage`, and tool call within a single thread. LangGraph saves a checkpoint after each node step, so if the process restarts the thread resumes where it left off.

### How it works in this agent
- The graph is compiled with `checkpointer=SqliteSaver(...)`.
- Each invocation carries `config={"configurable": {"thread_id": "..."}}`.
- LangGraph writes checkpoints to `checkpoints` / `writes` tables inside `agent_memory.db`.
- Starting a new `thread_id` yields a fresh, empty conversation.

### Example from the notebook
```python
cfg_a = {"configurable": {"thread_id": "thread-A"}}
chat_agent.invoke({"messages": [HumanMessage("My favorite color is teal.")]}, cfg_a)
chat_agent.invoke({"messages": [HumanMessage("What color did I just say?")]}, cfg_a)
# -> "Teal."   (remembered — same thread)

cfg_b = {"configurable": {"thread_id": "thread-B"}}
chat_agent.invoke({"messages": [HumanMessage("What color did I say earlier?")]}, cfg_b)
# -> "I don't know."   (new thread — isolated)
```

### When it's the right tool
- Multi-turn reasoning where recent context matters (follow-up questions, clarifications).
- Tool-call transcripts the model needs to reference mid-task.

### When it fails you
- The user comes back tomorrow on a new thread — short-term memory is gone.
- You want facts shared across threads (user's name, preferences) — use semantic memory instead.

---

## 2. Long-Term (Semantic) Memory

### What it is
Durable, *timeless* facts about the user. Not "what did we talk about yesterday" but "who is this person."

Examples:
- "User's name is Alice."
- "Works as a data engineer."
- "Prefers Python over Scala."

### How it works in this agent
Schema:
```sql
CREATE TABLE semantic_memory (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL,
    fact       TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

The LLM drives writes and reads through two tools:
- `save_user_fact(fact: str)` — inserts a row scoped to the current `user_id`.
- `recall_user_facts()` — returns every stored fact for that user.

The `user_id` is injected at the node level (via `_CURRENT_USER`) so the model cannot spoof another user's memory.

### Preloading for free context
Rather than forcing a tool call every turn, the agent node preloads all known facts into the system prompt:

```python
facts = sem_recall(user_id) or ["(none)"]
system = SystemMessage(SYSTEM_TEMPLATE.format(facts=..., episodes=...))
```

So on turn 1, the model already "knows" Alice without asking.

### Example from the notebook
Conversation 1 (thread `alice-session-1`):
> **User:** "Hi, I'm Alice. I work as a data engineer and prefer Python over Scala."

The model calls `save_user_fact("User's name is Alice")`, `save_user_fact("Works as a data engineer")`, `save_user_fact("Prefers Python over Scala")`.

Conversation 2 (thread `alice-session-2` — brand new thread, same user):
> **User:** "What's my name and which language do I prefer?"
> **Agent:** "Your name is Alice, and you prefer Python over Scala."

Short-term memory is empty on this thread, yet the agent still knows — because `sem_recall("user-alice")` was loaded into the system prompt.

### Isolation check
A different `user_id` sees nothing:
```python
cfg3 = {"configurable": {"user_id": "user-bob", "thread_id": "bob-1"}}
# Agent: "I don't know anything about you yet."
```

---

## 3. Episodic Memory

### What it is
Time-stamped records of *what happened* — past tasks, outcomes, and optional user feedback. This is how an agent learns from experience ("last time we tried X it failed — try Y first").

### How it works in this agent
Schema:
```sql
CREATE TABLE episodic_memory (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL,
    task       TEXT NOT NULL,
    outcome    TEXT NOT NULL,
    feedback   TEXT,
    created_at TEXT NOT NULL
);
```

Tools:
- `save_episode(task, outcome, feedback="")` — after completing a substantive task, the agent records a short summary.
- `recall_recent_episodes(limit=5)` — returns the most recent episodes for this user.

Like semantic memory, the most recent 3 episodes are preloaded into the system prompt each turn.

### Example from the notebook
After the agent helps Alice with a Spark-to-PySpark migration plan, it calls:
```python
save_episode(
    task="Outline migration from Scala Spark to PySpark",
    outcome="Provided 3-step plan: inventory UDFs, port DataFrame API, validate with parity tests",
)
```

Later, when Alice returns with a new but related request, the system prompt contains:
```
Recent past interactions (episodic memory):
- Outline migration from Scala Spark to PySpark -> Provided 3-step plan: ...
```

The agent can now reference prior work instead of starting from zero.

### Semantic vs. Episodic — the difference
| Semantic | Episodic |
|---|---|
| "Alice prefers Python" | "On 2026-04-24, Alice asked me to plan a Spark migration and I proposed 3 steps" |
| Timeless | Time-stamped |
| Who the user *is* | What the user *did* |

Both are scoped by `user_id` and persist across threads — but they answer different questions.

---

## How the Three Layers Compose

Here's the request flow for one turn:

```
          ┌──────────────────────────────────────────┐
          │  User sends a message on thread-X         │
          └──────────────────────┬───────────────────┘
                                 ▼
   ┌────────────────────────────────────────────────────────┐
   │  agent_node(state, config)                             │
   │  1. Read user_id from config                           │
   │  2. sem_recall(user_id)  → preload facts               │
   │  3. epi_recall(user_id)  → preload recent episodes     │
   │  4. Build SystemMessage with facts + episodes          │
   │  5. llm_with_tools.invoke([system] + state.messages)   │
   └───────────────────────┬────────────────────────────────┘
                           ▼
   ┌────────────────────────────────────────────────────────┐
   │  Model may call tools:                                 │
   │   - save_user_fact / recall_user_facts   (semantic)    │
   │   - save_episode / recall_recent_episodes (episodic)   │
   └───────────────────────┬────────────────────────────────┘
                           ▼
   ┌────────────────────────────────────────────────────────┐
   │  SqliteSaver checkpoints the new state for thread-X    │
   │  (short-term memory auto-persisted)                    │
   └────────────────────────────────────────────────────────┘
```

- **Fast context** (semantic + recent episodes) is preloaded into the system prompt — no extra tool roundtrip.
- **Deep retrieval** happens only when the model decides to call `recall_user_facts` or `recall_recent_episodes`.
- **Short-term memory** is invisible to the model's prompting logic; LangGraph handles it.

---

## Concrete Example — Tracing One User Across Two Sessions

**Day 1, thread `alice-session-1`:**
1. User: *"Hi, I'm Alice. I work as a data engineer and prefer Python over Scala."*
2. Agent calls `save_user_fact` three times.
3. User: *"Help me plan a Scala → PySpark migration."*
4. Agent responds with a plan, calls `save_episode(task=..., outcome=...)`.
5. `SqliteSaver` writes the full message history for `alice-session-1`.

**Inspecting the DB after day 1:**
```
Semantic facts:
 - User's name is Alice
 - Works as a data engineer
 - Prefers Python over Scala

Episodes:
 - {task: "Outline Spark migration", outcome: "3-step plan", ...}
```

**Day 2, thread `alice-session-2` (fresh thread):**
- Short-term memory for this thread: empty.
- System prompt on first turn already contains Alice's 3 facts and the migration episode.
- User asks *"What's my name?"* → agent answers correctly.

**Day 2, different user, thread `bob-1`:**
- System prompt contains `(none)` for both facts and episodes.
- Agent: *"I don't know anything about you yet."*

Memory scope is enforced by the `user_id` column — a row for `user-alice` is invisible to `user-bob`.

---

## Production Upgrades (mentioned in the notebook)

- **Semantic search** over facts/episodes using `get_embeddings` + `sqlite-vec` or `pgvector` — scales past what a preload can fit.
- **Reflection step** that summarizes long conversations into new facts/episodes (memory consolidation — turning short-term into long-term).
- **Swap** `SqliteSaver` → `PostgresSaver` and the custom tables → `PostgresStore` when moving from notebook to production.

---

## Quick Reference

| Need | Memory type | Mechanism |
|---|---|---|
| Follow-up question in same chat | Short-term | `SqliteSaver` checkpoint |
| Remember the user's name across sessions | Semantic | `save_user_fact` tool |
| Recall what you helped them with last week | Episodic | `save_episode` tool |
| Preload user context without a tool call | Semantic + Episodic | System prompt templating in `agent_node` |
| Isolate memory per user | All | `user_id` scoping + node-level injection |
