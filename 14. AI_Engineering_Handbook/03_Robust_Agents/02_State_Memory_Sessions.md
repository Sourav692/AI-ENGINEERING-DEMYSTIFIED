# State, Memory and Sessions

> **Level** 🟡 Building Production Systems · **Module** 03 · **Doc** 2 of 5 · **Time** ~25 min
> **Prerequisites:** [Retry, Fallback, Memoization and the Confirmation Gate](01_Retry_Fallback_Memo_Confirm.md)
> **Source material:** `1. Company_Wise_Preparation/2. DevRev/Coding_Round/agent_tool_calling_demo/docs/DESIGN.md` §1, `src/scratch_agent.py`; `4. FDE_Related_Preparation/System_Design and Delivery/6. Customer Support AI Assistant Design.md` §6

## Why this matters

An agent turn is stateless in isolation. A *conversation* is not. "Where's my package?" followed by "Can you refund it?" only works if something remembers what "it" is. And an agent that survives a server restart mid-run only does so if its state lived somewhere other than the process that died. This document separates the kinds of state an agent needs, says where each should live, and connects the small `Session` object from Module 01 to the production architecture it stands in for.

## Three scopes of state

It helps to name three scopes, because they have different lifetimes and different storage:

```
 ┌─────────────────────────────────────────────────────────────┐
 │  RUN        one call to agent.run()                          │
 │             observations · iteration count                   │
 │             lives: local variables (or graph state)          │
 ├─────────────────────────────────────────────────────────────┤
 │  SESSION    one conversation, many turns                     │
 │             history · memo · trace                           │
 │             lives: Session object → Redis/DB by conversation_id│
 ├─────────────────────────────────────────────────────────────┤
 │  USER       across conversations                             │
 │             preferences · past interactions · entitlements   │
 │             lives: a user profile store, scoped per user     │
 └─────────────────────────────────────────────────────────────┘
```

Module 01 handled the first two. The third is where "memory" in the product sense lives, and it is the one that needs the most care.

## The `Session`, revisited

```python
@dataclass
class Session:
    history: List[Tuple[str, str]]   # (query, answer) pairs = memory
    memo: dict                       # tool-result cache (don't re-hit the API)
    logger: ToolCallLogger           # full observability trace
```

- **History** gives the brain context for follow-ups ("close *that* one"). In the demo it is a list; in an LLM brain it is rendered into the prompt.
- **Memo** is shared across turns, so a repeated `search_tickets("billing")` in turn 3 is free if turn 1 ran it. `test_session_memo_persists_across_turns` proves it.
- **Logger** accumulates every tool call across the whole conversation — one place to answer "what did this agent do for this user today?"

**Where does it live in production?** In-memory here. In production: a store keyed by `conversation_id` — Redis or a database — so *any worker* can resume a conversation, plus a **checkpointer** (LangGraph's `MemorySaver`, or a durable saver) that persists state after every node. The checkpointer is what gives you two things a plain session store does not:

1. **Crash recovery.** The process dies at step 4 of 7; the next worker loads the checkpoint and continues from step 5, not step 1. Module 05's orchestrator implements this by hand with a `next_step_index` so you see exactly what a checkpoint is.
2. **Human-in-the-loop pauses.** `blocked_on` from Module 01 becomes an `interrupt_before=["tools"]`: the graph checkpoints, waits for approval — minutes or days — and resumes in a different process.

**The guardrail on all of this:** cap history and memo size. Both grow with the conversation, both cost tokens (history) or memory (memo). Summarise or window old turns; expire memo entries.

## The three layers of memory

The customer-support design in Module 09 makes a distinction that is worth learning now, because it prevents a common architectural mistake:

| Layer | Holds | Example | Fails how |
|---|---|---|---|
| **Short-term (conversational)** | Context within the current session | "Where's my package?" … "Can you refund *it*?" — the agent knows *it* is the same order | Lost context → the agent asks again |
| **Long-term (customer)** | Persistent preferences and history across sessions | Preferred language, channel, previous purchases, past support interactions | A **stale preference** → mildly wrong personalisation |
| **Enterprise knowledge** | Product docs, policies, FAQs, troubleshooting — served by RAG | "What is your refund policy?" | An **outdated policy document** → a wrong, possibly contractual answer |

The mistake is conflating the second and third. They feel similar — both are "things the system knows" — but a stale customer preference and an outdated policy fail in very different ways, at very different costs, and are refreshed on very different cadences. Keep enterprise knowledge in the retrieval layer (Module 04) and customer memory in a per-user store. Conflating them makes both harder to fix.

## Scoping and isolation

Every memory read must be scoped to the user the agent is serving. The 12-part framework says it in one line: *scope memory strictly per user, and retrieve selectively rather than dumping everything.* Two reasons:

- **Isolation.** A memory store keyed only by `conversation_id` with no user check is a cross-user leak waiting for a guessed ID. Identity resolved at authentication is what keeps memory user-isolated — the same resolved principal that scopes retrieval in Module 04.
- **Token budget.** "Retrieve selectively" is context engineering: the window is finite, and everything you put in it displaces something else. Pull the three past interactions relevant to this question, not the last three hundred.

## Long-running work is not a long-running turn

One more distinction that saves a lot of pain. A refund investigation, a warranty cancellation, a shipping enquiry can take minutes or hours. Holding a conversation turn open for that is wrong. The pattern from the customer-support design: reply immediately — *"Your request has been submitted"* — and let background workers finish, with the run's state in the durable store so the result can be reported back in a later turn or on another channel. Module 08 covers multi-channel delivery and escalation as real workflows.

## In the code

| Concept | Where |
|---|---|
| Session state | `project/src/scratch_agent.py` → `Session` |
| History recorded on final answer | `Agent.run` → `session.history.append(...)` |
| Memo shared across turns | `execute_tool(..., memo=session.memo)` |
| Graph-level run state | `project/src/langgraph_agent.py` → `AgentState` |
| Checkpointing and interrupts | `project/notebooks/robust_langgraph_tool_calling_agent.ipynb` |
| Test | `test_session_memo_persists_across_turns` |

## Interview lens

"How do you handle state across turns?" is answered by the three scopes and where each lives, then the checkpointer and what it buys. The sentence that carries it:

> *"Run state is local; session state is keyed by conversation ID in a shared store so any worker can resume; user memory is a separate, per-user store — and enterprise knowledge is not memory at all, it's retrieval, because it fails differently and is refreshed differently."*

## Checkpoint

- Name the three scopes of state, their lifetimes, and where each lives in production.
- What two capabilities does a checkpointer give you that a plain session store does not?
- Why should enterprise knowledge never be stored in the same place as customer memory?
- What are the two reasons memory reads must be scoped per user?
- How should a two-hour refund investigation interact with a conversation turn?

**Next →** [Parallel vs Sequential Tool Calls](03_Parallel_vs_Sequential.md)
