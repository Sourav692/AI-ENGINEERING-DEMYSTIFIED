# Memory Types in Deep Agent

This document describes every memory and persistence mechanism available in the deep agent system, how they work, and where data lives.

---

## At a Glance

```
Immediate (within a single turn)
  |
  v
Short-Term (within a thread)          -- Message History + MemorySaver
  |
  v
Medium-Term (within a thread, large)  -- Conversation Summarization
  |
  v
Long-Term (across threads & restarts) -- JSON File Memory, AGENTS.md, Filesystem
```

| # | Memory Type | Scope | Survives Restart? | Used In |
|---|---|---|---|---|
| 1 | [Message History](#1-message-history) | Within thread | No | Both agents |
| 2 | [MemorySaver Checkpointer](#2-memorysaver-checkpointer) | Within thread | No | Both agents |
| 3 | [Conversation Summarization](#3-conversation-summarization) | Within thread | Depends on backend | Both agents (implicit) |
| 4 | [JSON File Memory](#4-json-file-memory-long-term) | Cross-thread, cross-session | Yes | `long_term_memory_agent.py` |
| 5 | [AGENTS.md Memory](#5-agentsmd-memory) | Project-level | Yes | Available but unused |
| 6 | [Skills Storage](#6-skills-storage) | Project-level | Yes | Both agents |
| 7 | [Filesystem Backend](#7-filesystem-backend) | Cross-thread, cross-session | Yes | Both agents |
| 8 | [State Backend](#8-state-backend) | Within thread | No | Default fallback |
| 9 | [Store Backend](#9-store-backend) | Cross-thread | Depends on store | Available but unused |

---

## 1. Message History

**What it stores:** All messages in the current thread — user inputs, assistant responses, tool calls and results.

**Scope:** Within a single thread only.

**How it works:**
- Built into LangGraph's `AgentState` as `messages: list[BaseMessage]`
- Messages are appended automatically after each agent step
- The full history is passed to the LLM on every turn, giving it conversational context
- When history grows too large, the Summarization Middleware (see #3) compresses it

**Where data lives:** In-memory (Python process RAM), checkpointed by MemorySaver.

**Example:**
```python
# Each call appends to the thread's message list
agent.stream(
    {"messages": [{"role": "user", "content": "Hello!"}]},
    config={"configurable": {"thread_id": "thread-1"}},
)
```

---

## 2. MemorySaver Checkpointer

**What it stores:** Full agent state snapshots after each graph step — message history, tool results, intermediate state.

**Scope:** Within a thread (keyed by `thread_id`).

**How it works:**
- `MemorySaver()` from `langgraph.checkpoint.memory` keeps an in-memory dict of state snapshots
- After each step in the graph, the current state is checkpointed
- On subsequent calls with the same `thread_id`, the previous state is restored — enabling multi-turn conversations within a thread
- Different `thread_id` values get independent conversation histories

**Where data lives:** RAM only. Lost when the script exits.

**Used in both agents:**
```python
checkpointer = MemorySaver()
agent = create_deep_agent(..., checkpointer=checkpointer)
```

> **Upgrade path:** Replace with `SqliteSaver` or `PostgresSaver` for persistence across restarts.

---

## 3. Conversation Summarization

**What it stores:** AI-generated summaries of old messages that have been evicted from context.

**Scope:** Within a thread, but offloaded to backend storage.

**How it works:**
- `SummarizationMiddleware` (from deepagents) monitors message history size
- When context exceeds a threshold (fraction of token limit, message count, or token count), it triggers summarization
- The LLM generates a summary of the oldest messages
- Old messages are removed from active context and written to a file: `/conversation_history/{thread_id}.md`
- The summary replaces them in the message list, preserving context without bloating the window

**Where data lives:** Backend storage (filesystem or state backend), as a Markdown file.

**Key insight:** This is automatic and transparent — neither the user nor the agent explicitly triggers it. It prevents context window overflow in long conversations.

---

## 4. JSON File Memory (Long-Term)

**What it stores:** User preferences, personal facts, project decisions, deadlines — anything the user wants remembered across conversations.

**Scope:** Cross-thread, cross-session. Survives script restarts.

**How it works:**
- Three tool functions: `save_memory()`, `recall_memories()`, `forget_memory()`
- Memories are organized by category: `preference`, `fact`, `decision`, `project`, `feedback`
- Each memory is a dict: `{content, category, saved_at}`
- The full memory store is read from / written to a JSON file on every operation
- A dedicated `memory-manager` subagent specializes in memory operations

**Where data lives:** `07_Deep_Agents/long_term_memories.json`

**Used in:** `long_term_memory_agent.py` only.

**Example flow:**
```
[thread-1] > Remember my name is Alice and I prefer concise answers.
  -> save_memory("User's name is Alice", category="fact")
  -> save_memory("User prefers concise answers", category="preference")

[type 'new' to start thread-2]

[thread-2] > What do you know about me?
  -> recall_memories()
  -> "Found 2 memories: [fact] User's name is Alice, [preference] User prefers concise answers"
```

**JSON file structure:**
```json
{
  "memories:default-user": {
    "uuid-1": {
      "content": "User's name is Alice",
      "category": "fact",
      "saved_at": "2026-04-21T10:30:00"
    },
    "uuid-2": {
      "content": "User prefers concise answers",
      "category": "preference",
      "saved_at": "2026-04-21T10:30:05"
    }
  }
}
```

> **Upgrade path:** Replace with `PostgresStore` for multi-user support and concurrent access.

---

## 5. AGENTS.md Memory

**What it stores:** Static project-level context — build commands, code guidelines, architecture notes, agent behavior rules.

**Scope:** Project-level. Applies to all threads and sessions.

**How it works:**
- `MemoryMiddleware` (from deepagents) reads `AGENTS.md` files from specified paths
- Content is loaded once at startup and injected into the system prompt as `<agent_memory>` blocks
- The agent can update these files via `edit_file`, making it a self-evolving knowledge base
- Guidelines tell the agent when to update memory (role descriptions, feedback) and when not to (transient info, credentials)

**Where data lives:** Markdown files on disk (typically `AGENTS.md` at the project root).

**How to enable:**
```python
agent = create_deep_agent(..., memory=["/AGENTS.md"])
```

**Currently unused** in both `simple_coding_agent.py` and `long_term_memory_agent.py`, but available via the `memory` parameter.

---

## 6. Skills Storage

**What it stores:** Skill definitions — structured instructions that teach subagents specific workflows (e.g., how to plan a project, how to review code).

**Scope:** Project-level. Loaded from disk, applied to all executions.

**How it works:**
- `SkillsMiddleware` reads `SKILL.md` files from backend paths
- Each skill has YAML frontmatter (`name`, `description`) and Markdown instructions
- Skills are injected into the system prompt when the agent or subagent is invoked
- Later skill sources override earlier ones (progressive disclosure)

**Where data lives:** `07_Deep_Agents/skills/{skill-name}/SKILL.md`

**Current skills:**

| Skill | Purpose |
|---|---|
| `senior-developer` | Project planning, code generation, delivery |
| `code-reviewer` | Bug detection, style review |
| `research-agent` | Web research, source synthesis |
| `memory-manager` | Long-term memory operations |
| `aia-customer-analytics` | Customer data queries |
| `aia-distribution-channels` | Agent performance queries |
| `aia-policy-underwriting` | Policy metrics queries |
| `aia-claims-analytics` | Claims and fraud queries |

---

## 7. Filesystem Backend

**What it stores:** Actual files written by the agent — project code, READMEs, requirements files.

**Scope:** Cross-thread, cross-session. Persists on disk permanently.

**How it works:**
- `FilesystemBackend` provides `write_file`, `read_file`, `edit_file`, `ls` operations on the real filesystem
- Supports `virtual_mode` which restricts access to `root_dir` (prevents path traversal)
- `LocalShellBackend` extends this with code execution capability

**Where data lives:** Real filesystem, typically under `07_Deep_Agents/projects/`.

**Used in both agents:**
```python
def _create_backend():
    if USE_SANDBOX:
        return LocalShellBackend(root_dir=PROJECTS_DIR)
    return FilesystemBackend(root_dir=BASE_DIR, virtual_mode=True)
```

---

## 8. State Backend

**What it stores:** Virtual files in agent state — used when no explicit backend is provided.

**Scope:** Within a single thread. Ephemeral.

**How it works:**
- `StateBackend` is the default when `create_deep_agent()` is called without a `backend` parameter
- File reads/writes go through LangGraph's state channels
- Files exist only in the agent's in-memory state

**Where data lives:** RAM (agent state). Lost on thread completion.

**Not directly used** in either agent (both specify an explicit backend), but serves as the fallback.

---

## 9. Store Backend

**What it stores:** Files shared across multiple threads via LangGraph's `BaseStore` abstraction.

**Scope:** Cross-thread. Persistence depends on the store implementation.

**How it works:**
- `StoreBackend` adapts LangGraph's `BaseStore` (e.g., `InMemoryStore`, `PostgresStore`) for the deepagents file protocol
- Files are stored as items with namespaces and keys
- Supports binary data via Base64 encoding

**Where data lives:** Depends on the backing store (RAM for `InMemoryStore`, PostgreSQL for `PostgresStore`).

**Not used** in either agent. Enable with:
```python
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()
agent = create_deep_agent(..., store=store)
```

---

## How Memory Layers Work Together

A typical interaction in `long_term_memory_agent.py` uses multiple memory types simultaneously:

```
User: "Remember I prefer Python with type hints. Now build me a CSV parser."

1. [Message History]        User message added to thread state
2. [JSON File Memory]       save_memory("Prefers Python with type hints", "preference")
                            -> Written to long_term_memories.json
3. [Skills Storage]         senior-developer SKILL.md loaded for coding task
4. [Filesystem Backend]     Project files written to projects/csv-parser/
5. [MemorySaver]            State checkpointed after each step
6. [Summarization]          (If history grows large, old messages are summarized)

--- User types 'new' (new thread) ---

User: "What coding style do I prefer?"

1. [Message History]        Fresh thread — no prior messages
2. [JSON File Memory]       recall_memories("prefer")
                            -> Reads from long_term_memories.json
                            -> "User prefers Python with type hints"
3. [MemorySaver]            New checkpoint for this thread
```

The key insight: **short-term memory (MemorySaver) resets per thread, but long-term memory (JSON file) carries over** — giving the agent both conversational context and persistent knowledge.
