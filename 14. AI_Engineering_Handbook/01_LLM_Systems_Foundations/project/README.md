# 🤖 Agent Tool-Calling Loop — Demo Project

> **DevRev Technical Round · Section 3.** A minimal, DevRev-flavored **ReAct agent** that
> routes a query to tools, loops over observations, and synthesizes an answer — with a
> **max-iteration guard**, **confirmation gate**, **memoization**, **retry**, **fallback**,
> and full **observability**. Built **two ways**: from scratch *and* with **LangGraph**.

The prep note lists "tool-calling loop, coded from scratch" as a top-3 focus and says it
"maps directly to DevRev's AI-native agent product surface." This project is the study aid.

---

## Why two implementations?

| | `src/scratch_agent.py` | `src/langgraph_agent.py` |
|---|---|---|
| Dependencies | **none** (pure Python) | LangGraph |
| Purpose | prove you understand the **mechanics** (the interview ask) | show you can express it in the **framework the team uses** |
| The loop | an explicit `while` loop | a two-node `StateGraph` with a conditional edge |

Both share the *same* tools, brain, robustness, and observability modules — only the
orchestration differs.

---

## The loop in one picture

```
query ─▶ [ THINK: brain picks a tool or finishes ]
             │ tool call
             ▼
        [ ACT: execute_tool ]  ← confirmation gate · memo cache · retry
             │ result
             ▼
        [ OBSERVE ] ─▶ back to THINK   (until final answer or max-iteration guard)
```

---

## Run it

```bash
cd agent_tool_calling_demo
pip install -r requirements.txt          # (the from-scratch agent needs nothing installed)

python -m pytest -q                       # 12 tests, all green
python -c "import sys; sys.path.insert(0,'.'); \
  from src.tools import TicketStore, build_registry; \
  from src.scratch_agent import Agent; from src.robustness import always_approve; \
  print(Agent(build_registry(TicketStore()), confirm=always_approve).run('close the ticket about login').answer)"

jupyter notebook notebooks/agent_tool_calling_demo.ipynb   # the guided walkthrough
```

> **No API key needed.** The "brain" is a deterministic rule-based router
> (`src/brain.py`) that mimics an LLM's tool selection. To use a real LLM instead,
> implement the same `.decide()` contract — `make_llm_brain()` shows the wiring.

---

## Project layout

```
agent_tool_calling_demo/
├── README.md                 ← you are here
├── requirements.txt
├── src/
│   ├── tools.py              ← Tool + ToolRegistry + in-memory DevRev ticket backend
│   ├── brain.py              ← RuleBasedBrain (offline) + make_llm_brain() hook
│   ├── robustness.py         ← retry · memoization · fallback · confirmation gate · disambiguation
│   ├── observability.py      ← ToolCallLogger + trace table
│   ├── scratch_agent.py      ← the ReAct loop, coded from scratch  (+ Session for multi-turn state)
│   └── langgraph_agent.py    ← the same loop as a LangGraph StateGraph
├── notebooks/
│   └── agent_tool_calling_demo.ipynb   ← guided, runnable walkthrough of every concept
├── tests/
│   └── test_agent.py         ← 12 pytest cases
└── docs/
    └── DESIGN.md             ← state, observability, and parallel-vs-sequential tradeoffs
```

---

## What each interview bullet maps to

| Prep bullet (Section 3) | Where it lives |
|---|---|
| Minimal ReAct loop from a tool registry | `scratch_agent.Agent.run` + `tools.ToolRegistry` |
| Route a query to the right tool | `brain.RuleBasedBrain.decide` |
| Synthesize a final answer | the `decision.is_final` branch |
| Max-iteration guard | the `while iterations < self.max_iterations` guard |
| Tool error → retry / fallback / escalate | `robustness.execute_tool`, `with_fallback` |
| Memoize repeated calls | `robustness.execute_tool` (memo cache) + `Session.memo` |
| Disambiguate two plausible tools | `robustness.disambiguate` |
| Confirmation gate before destructive tools | `robustness` confirmation policy + `Tool.destructive` |
| State across turns | `scratch_agent.Session` |
| Logging/observability | `observability.ToolCallLogger` |
| Parallel vs sequential tradeoffs | `docs/DESIGN.md` |

See the companion tutorial: [`../tutorials/03_Agent_Tool_Calling_Loop.md`](../tutorials/03_Agent_Tool_Calling_Loop.md).
