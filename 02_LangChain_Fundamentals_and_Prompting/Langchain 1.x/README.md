# LangChain 1.0 / LangGraph concept notebooks

Four small, focused notebooks instead of one heavy one. Run them in order —
each builds on the previous one's mental model.

| # | Notebook | Covers |
|---|---|---|
| 01 | `01_create_agent_basics.ipynb` | `.env` + `ChatOpenAI` setup, `.profile`, `create_agent`, `.content_blocks` |
| 02 | `02_middleware_deep_dive.ipynb` | Built-in middleware (summarization, PII redaction, call limits) + writing your own |
| 03 | `03_human_in_the_loop_middleware.ipynb` | `HumanInTheLoopMiddleware` — approve/edit/reject tool calls, checkpointing |
| 04 | `04_langgraph_interrupt_primitive.ipynb` | The raw `interrupt()` / `Command(resume=...)` primitive underneath notebook 03, in a hand-built LangGraph graph |

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# then edit .env and add your real OPENAI_API_KEY
jupyter notebook
```

## Why split like this

- Notebook 01 stands alone as "how do I even build an agent in 1.0."
- Notebook 02 isolates middleware so you can see the hook points without
  the added complexity of interrupts.
- Notebooks 03 and 04 are a deliberate pair: 03 shows the convenient,
  high-level HITL path; 04 opens the hood and shows the LangGraph
  mechanism it's built on, so you know when to drop down to it.
