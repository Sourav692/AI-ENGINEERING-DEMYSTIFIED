# The Tool-Calling Loop From Scratch

> **Level** 🟢 Foundations · **Module** 01 · **Doc** 4 of 5 · **Time** ~35 min + lab
> **Prerequisites:** [What an Agent Actually Is](03_What_An_Agent_Actually_Is.md)
> **Source material:** `1. Company_Wise_Preparation/2. DevRev/Coding_Round/agent_tool_calling_demo/src/scratch_agent.py`, `src/brain.py`, `README.md`
> **Lab:** `project/notebooks/agent_tool_calling_demo.ipynb` · `project/src/scratch_agent.py` · `project/tests/test_agent.py`

## Why this matters

You can build an agent in ten lines with any framework. You cannot *debug* one, *extend* one, or *defend one in a design review* unless you know what those ten lines hide. This document builds the ReAct loop in plain Python with no dependencies — every moving part explicit — so that when you meet the framework version in the next document, you recognise every piece.

The source project was built for exactly this reason: a technical round that listed "tool-calling loop, coded from scratch" as a top-three focus.

## The two pieces of state

Before the loop, two dataclasses. The first is the thing most tutorials forget: state that must survive across *turns* of a conversation, not just across iterations of one run.

```python
@dataclass
class Session:
    """State that persists ACROSS turns of a conversation."""
    history: List[Tuple[str, str]] = field(default_factory=list)   # (query, answer) pairs — memory
    memo: dict = field(default_factory=dict)                       # cache of tool results
    logger: ToolCallLogger = field(default_factory=ToolCallLogger) # the observability trace
```

- `history` gives the brain context for follow-ups ("close *that* one").
- `memo` is shared across turns, so a repeated `search_tickets("billing")` in turn 3 is free if turn 1 already ran it.
- `logger` records every tool call for the whole session — Module 03 shows what it captures.

The second is what one run returns:

```python
@dataclass
class RunResult:
    answer: str
    iterations: int
    observations: List[Observation]
    blocked_on: Optional[Tuple[str, dict]] = None   # set if paused for confirmation
```

`blocked_on` is the first hint that a run has *three* endings, not two: it can finish, it can hit the guard, or it can **pause** because a destructive tool needs a human's approval. That third ending is what makes the loop safe to point at a real system.

## The agent

```python
class Agent:
    def __init__(self, registry, brain=None, *, max_iterations=6, confirm=deny_destructive):
        self.registry = registry
        self.brain = brain or RuleBasedBrain()
        self.max_iterations = max_iterations     # the loop guard — never run forever
        self.confirm = confirm                   # the confirmation policy for destructive tools
```

Two constructor arguments carry the safety posture. `max_iterations` bounds the loop. `confirm` is a **policy** — a function `(tool, args) -> bool` — and its default, `deny_destructive`, returns `False` unconditionally. Out of the box, this agent *cannot* close a ticket. You have to hand it a policy that says otherwise. That is the safe default, and it is a design choice worth being able to defend.

## The loop, line by line

```python
def run(self, query: str, session: Optional[Session] = None) -> RunResult:
    session = session or Session()
    observations: List[Observation] = []
    iterations = 0

    while iterations < self.max_iterations:                          # ① MAX-ITERATION GUARD
        decision: Decision = self.brain.decide(query, observations)  # ② THINK

        if decision.is_final:                                        # ③a the brain is done
            session.history.append((query, decision.final))
            return RunResult(decision.final, iterations, observations)

        tool = self.registry.get(decision.tool)                      # ③b the brain chose a tool
        try:
            result = execute_tool(                                   # ④ ACT — safely
                tool, decision.args,
                logger=session.logger,
                memo=session.memo,
                confirm=self.confirm,
            )
        except ConfirmationRequired as e:                            # ⑤ PAUSE for a human
            msg = f"Awaiting confirmation to run '{e.tool}' with {e.call_args}."
            return RunResult(msg, iterations, observations, blocked_on=(e.tool, e.call_args))

        observations.append((decision.tool, result))                 # ⑥ OBSERVE
        iterations += 1

    return RunResult("Stopped: hit the max-iteration guard.", iterations, observations)   # ⑦
```

Walk it:

| # | Step | What it guarantees |
|---|---|---|
| ① | `while iterations < max_iterations` | The run terminates. Whatever the brain does, the loop body executes at most six times. |
| ② | `brain.decide(query, observations)` | The brain sees *everything observed so far*. This is how a one-step decision function plans multi-step work. |
| ③a | `decision.is_final` | The normal exit. The answer is recorded in session history so the *next* turn has context. |
| ③b | `registry.get(decision.tool)` | The brain names a tool; the registry resolves it. An unknown name raises here, not deep inside execution. |
| ④ | `execute_tool(...)` | The tool runs behind the safety layer — confirmation gate, memo cache, retry — which Module 03 opens up. The loop itself stays clean. |
| ⑤ | `except ConfirmationRequired` | A destructive tool was requested and the policy said no. The run *pauses* and hands control back to the caller with exactly what was about to happen. It does not fail, and it does not proceed. |
| ⑥ | `observations.append(...)` | The result becomes part of what the brain sees next iteration. |
| ⑦ | fall-through | The guard exit. The answer says so explicitly rather than pretending. |

Notice what is *not* in the loop: no retry logic, no cache lookup, no logging calls. Those live inside `execute_tool`. The loop is the orchestration; robustness is a layer it calls. Keeping them separate is what lets the LangGraph version in the next document reuse `execute_tool` unchanged.

## A run, traced

Query: *"close the ticket about login"*, with `confirm=always_approve`.

```
iteration 0   brain.decide("close the ticket about login", [])
              → Decision(tool="search_tickets", args={"query": "login"})
              execute_tool → [{"id": "TKT-3", "subject": "Login page 500 error", ...}]
              observations = [("search_tickets", [...])]        (TKT-1 says "log in", two words — no match)

iteration 1   brain.decide(query, observations)          ← sees the search result
              → Decision(tool="close_ticket", args={"ticket_id": "TKT-3"})
              execute_tool → destructive → confirm(tool, args) → True → runs
              → {"id": "TKT-3", "status": "closed", ...}
              observations = [("search_tickets", [...]), ("close_ticket", {...})]

iteration 2   brain.decide(query, observations)          ← sees both results
              → Decision(final="Closed TKT-3 — 'Login page 500 error'.")
              return RunResult(answer=..., iterations=2, ...)
```

That is exactly what `test_multi_step_search_then_close` asserts: `"Closed TKT-3" in r.answer` and `r.iterations == 2`.

Run the same query with the default `deny_destructive` policy and iteration 1 ends differently: `execute_tool` raises `ConfirmationRequired`, and `run()` returns `blocked_on=("close_ticket", {"ticket_id": "TKT-3"})` with the ticket still open — `test_confirmation_blocks_destructive`. The caller — a UI, a Slack bot, a test — now knows precisely what to ask the human.

## The brain contract, and swapping in an LLM

The loop never inspects *how* the brain decides. It calls `.decide(query, observations)` and reads the `Decision`. The source project ships two brains behind that contract:

**`RuleBasedBrain`** — a deterministic router. It classifies the query with regular expressions into an intent (`close_by_topic`, `lookup`, `search`, `create`) and uses `len(observations)` to know which step of the plan it is on:

```python
if intent == "close_by_topic":
    if n == 0:  return Decision(tool="search_tickets", args={"query": arg})     # step 1: find it
    if n == 1:                                                                  # step 2: close first hit
        hits = observations[0][1]
        if not hits: return Decision(final=f"No open ticket found about '{arg}'.")
        return Decision(tool="close_ticket", args={"ticket_id": hits[0]["id"]})
    closed = observations[1][1]                                                 # step 3: report
    return Decision(final=f"Closed {closed['id']} — '{closed['subject']}'.")
```

It exists so the loop can be studied and tested with no API key and no nondeterminism.

**`make_llm_brain()`** — the real thing. A system prompt asks the model to emit the next action as JSON; the observations are rendered into the prompt; the reply is parsed into a `Decision`:

```python
SYSTEM = ("You are a support agent. Decide the single next tool call as JSON "
          "{\"tool\": name, \"args\": {...}} or {\"final\": answer}.")

def decide(self, query, observations):
    ctx = "\n".join(f"OBSERVATION {t}: {r}" for t, r in observations)
    reply = llm.invoke([SystemMessage(content=self.SYSTEM), HumanMessage(content=self.SYSTEM + "\nQUERY: " + query + ("\n" + ctx if ctx else ""))])
    data = json.loads(reply.content)
    if "final" in data: return Decision(final=data["final"])
    return Decision(tool=data["tool"], args=data.get("args", {}))
```

Same contract; the `Agent` class is untouched. This is the separation that matters: **the brain is replaceable, the loop and its guards are not**.

## In the code

| Concept | Where |
|---|---|
| The loop | `project/src/scratch_agent.py` → `Agent.run` |
| Cross-turn state | `project/src/scratch_agent.py` → `Session` |
| Max-iteration guard | the `while iterations < self.max_iterations` condition |
| Pause-for-confirmation ending | the `except ConfirmationRequired` branch and `RunResult.blocked_on` |
| Deterministic brain | `project/src/brain.py` → `RuleBasedBrain.decide`, `_classify` |
| LLM brain | `project/src/brain.py` → `make_llm_brain` |
| Tools and registry | `project/src/tools.py` → `Tool`, `ToolRegistry`, `build_registry` |
| Tests | `project/tests/test_agent.py` — 12 cases covering the loop, guard, gate, memo, retry, fallback, disambiguation |

Run it:

```bash
cd project
python -m pytest -q                              # 12 tests, all green, no API key
python -c "import sys; sys.path.insert(0,'.'); \
  from src.tools import TicketStore, build_registry; \
  from src.scratch_agent import Agent; from src.robustness import always_approve; \
  print(Agent(build_registry(TicketStore()), confirm=always_approve).run('close the ticket about login').answer)"
jupyter notebook notebooks/agent_tool_calling_demo.ipynb
```

## Interview lens

If asked to write the loop on a whiteboard, write ①–⑦ above, in that order, and narrate the guard and the pause ending as you go. The two sentences that separate a strong answer from a working one:

> *"The default confirmation policy denies every destructive tool — the agent can't close a ticket until you hand it a policy that says it may."*
>
> *"The brain is behind a one-method contract, so swapping the rule-based router for an LLM changes nothing in the loop or its guards."*

## Checkpoint

- Write `Agent.run` from memory, including all three exits.
- What does `Session` hold, and why is each field there rather than on `Agent`?
- What happens, step by step, when the brain requests `close_ticket` under the default policy?
- Why does robustness live in `execute_tool` rather than in the loop?
- How does `RuleBasedBrain` know which step of a multi-step plan it is on?

**Next →** [The Same Loop in LangGraph](05_Same_Loop_In_LangGraph.md)
