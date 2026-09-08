# What an Agent Actually Is

> **Level** 🟢 Foundations · **Module** 01 · **Doc** 3 of 5 · **Time** ~25 min
> **Prerequisites:** [What RAG Actually Is](01_What_RAG_Actually_Is.md)
> **Source material:** `1. Company_Wise_Preparation/2. DevRev/Coding_Round/agent_tool_calling_demo/README.md`, `src/tools.py`, `src/brain.py`; `3. AI_Engineer_Interview_Preparation/Enterprise Agentic Workflow Automation Platform/docs/01-theory.md` Part A §A.2–A.4

## Why this matters

RAG answers questions. An **agent** takes actions. The difference is not academic: a RAG system that is wrong gives a bad answer; an agent that is wrong refunds the wrong customer, closes the wrong ticket, or sends the wrong email. Every design decision in the agentic half of this handbook follows from that asymmetry, and it starts with being precise about what an agent is — because the word is used loosely enough to mean almost anything.

## The definition

Strip away the framework vocabulary and an agent is a loop:

```
query ─▶ [ THINK: brain picks a tool or finishes ]
             │ tool call
             ▼
        [ ACT: execute the tool ]
             │ result
             ▼
        [ OBSERVE: add the result to what the brain knows ] ─▶ back to THINK
                                                              (until a final answer, or a guard stops it)
```

This is the **ReAct** pattern — *Reason, Act* — and it has exactly three components:

1. **Tools** — the atomic things the agent can do.
2. **A brain** — the component that, given the query and everything observed so far, decides the next action: call a tool, or finish.
3. **The loop** — which runs the brain, executes what it asks for, feeds the result back, and stops when the brain says it is done *or when a guard says enough*.

In production the brain is an LLM. But notice that nothing in the definition requires that. The source project makes this point by shipping a deterministic, rule-based brain that runs with no API key — because the mechanics of the loop are the thing to understand, and an LLM only makes the brain's decisions harder to predict, not different in kind.

## Component 1 — Tools

A tool is a name, a description, a function, and a flag:

```python
@dataclass
class Tool:
    name: str            # unique id the agent references
    description: str     # what the model reads to pick a tool
    func: Callable       # the actual implementation
    destructive: bool = False   # True -> requires confirmation before running
```

Three of those fields are obvious. The fourth is the first safety decision you will make in any agent, and it is made at *registration* time, not at call time. `search_tickets` reads. `close_ticket` writes irreversibly. The tool declares which it is, and the loop treats the two differently forever after.

Tools live in a **registry** — a name-to-tool lookup with one extra method:

```python
def specs(self) -> List[Dict[str, str]]:
    """What you'd feed an LLM so it knows which tools exist."""
    return [{"name": t.name, "description": t.description, "destructive": t.destructive}
            for t in self._tools.values()]
```

That `specs()` view *is* the tool-calling interface. When people say "the model chooses a tool", they mean the model was shown this list and emitted the name of one entry plus arguments. The description field is therefore prompt engineering: it is the only thing the brain has to go on.

The source project's registry has four DevRev-flavoured tools over an in-memory ticket store:

| Tool | Does | Destructive |
|---|---|---|
| `search_tickets` | find open tickets matching a query string | no |
| `get_ticket` | fetch one ticket by id | no |
| `create_ticket` | create a new ticket | no |
| `close_ticket` | close (resolve) a ticket | **yes** |

Two exception types come with the store, and they matter more than they look:

```python
class TransientError(Exception):
    """A temporary failure (network blip, 503) — safe to RETRY."""

class NotFoundError(Exception):
    """A permanent 'no such record' failure — do NOT retry; consider a fallback."""
```

A tool's failures are part of its contract. Module 03 builds the retry and fallback policy on exactly this distinction.

## Component 2 — The brain

The brain has one method and one contract:

```python
Observation = Tuple[str, Any]     # (tool_name, result) — one past tool result

def decide(self, query: str, observations: List[Observation]) -> Decision: ...
```

It receives the query and every observation so far; it returns a `Decision`, which is either a tool call or a final answer:

```python
@dataclass
class Decision:
    tool: Optional[str] = None     # tool name to call (None if finishing)
    args: Optional[dict] = None    # arguments for that tool
    final: Optional[str] = None    # the final answer text (None if still working)

    @property
    def is_final(self) -> bool:
        return self.final is not None
```

Because the brain sees the observations, it is naturally *reactive*: asked to "close the ticket about login", it first decides `search_tickets(query="login")`, and on the next turn — now holding the search result — decides `close_ticket(ticket_id="TKT-1")`. Multi-step plans emerge from a single-step decision function called repeatedly. That is the whole trick of ReAct.

The source project's `RuleBasedBrain` implements this with regular expressions. Its `make_llm_brain()` shows the LLM version: same `.decide()` contract, but the decision comes from a model prompted to emit `{"tool": ..., "args": ...}` or `{"final": ...}` as JSON. **The loop does not change.** Swapping the brain is the only difference between the offline demo and a real agent.

## Component 3 — The loop, and why the guards are part of the definition

The next document walks the loop line by line. Here is the shape:

```
while iterations < max_iterations:          # ← guard
    decision = brain.decide(query, observations)
    if decision.is_final:
        return decision.final
    result = execute_tool(decision.tool, decision.args)   # ← confirmation gate, cache, retry live here
    observations.append((decision.tool, result))
    iterations += 1
return "Stopped: hit the max-iteration guard."
```

The `while` condition is not a detail. An LLM brain can decide to call a tool forever — because the tool keeps failing, because the answer is genuinely unreachable, because the prompt was adversarial. The max-iteration guard is the difference between an agent and an unbounded process spending your budget. It belongs in the definition.

## The hard part is not the loop

The source material for the agent-platform project makes a point that reframes everything above:

> Most people hear "AI agent platform" and think the hard part is: *how do I get an LLM to call the right tool?* That's not the hard part — the mechanics of "LLM picks a tool" were solved years ago. **The hard part is trust.**

An agent is a button that can refund real money, send a real email, close a real ticket. The question every later module answers is:

> How do you let someone trust that the agent will only do what they meant — and never something worse — even when the brain gets it wrong, or the network retries a request, or the server crashes mid-run?

That is a *systems and safety* problem wearing an AI costume. The LLM is almost incidental. It is why the `destructive` flag is on the `Tool` dataclass, why `execute_tool` has a confirmation gate, and why Module 05 spends most of its time on idempotency and staged rollout rather than on prompting.

## Vocabulary

| Term | Meaning |
|---|---|
| **Agent** | A loop that repeatedly asks a brain for the next action, executes it, and feeds the result back, under guards |
| **ReAct** | The reason-then-act pattern that loop implements |
| **Tool** | A named, described, callable action with a declared `destructive` flag |
| **Registry** | The lookup of tools; its `specs()` view is what the brain is shown |
| **Brain** | The decision function `(query, observations) → Decision`; an LLM in production |
| **Decision** | Either a tool call (`tool`, `args`) or a final answer (`final`) |
| **Observation** | One past `(tool_name, result)` pair; the agent's working memory within a run |
| **Max-iteration guard** | The loop bound that makes the agent a terminating process |

## Interview lens

"What is an agent?" is asked to see whether you reach for a framework name or for the mechanism. Give the mechanism — three components, one loop, one guard — then say where the difficulty actually is. The line that carries it:

> *"An agent is a loop: a brain picks a tool or finishes, the loop runs the tool and feeds the result back, under a step budget. The mechanics are easy. The hard part is that it can act, so every design decision is about containing what happens when it's wrong."*

## Checkpoint

- Draw the THINK / ACT / OBSERVE loop and label the three components.
- Why is `destructive` a field on `Tool` rather than a check the brain performs?
- Why does a single-step `decide()` function produce multi-step behaviour?
- What is the difference between a `TransientError` and a `NotFoundError`, and why should an agent care?
- Finish the sentence: "The hard part of agents is not the loop, it is ___."

**Next →** [The Tool-Calling Loop From Scratch](04_Tool_Calling_Loop_From_Scratch.md)
