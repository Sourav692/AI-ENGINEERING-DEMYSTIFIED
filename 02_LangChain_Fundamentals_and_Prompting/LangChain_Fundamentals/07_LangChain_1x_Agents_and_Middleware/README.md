# LangChain 1.0 / LangGraph concept notebooks

Small, focused notebooks instead of one heavy one. Run them in order —
each builds on the previous one's mental model.

| # | Notebook | Covers |
|---|---|---|
| 7.0 | `7.0_LangChain_First_Agent.ipynb` | `.env` + `ChatOpenAI` setup, verifying the LangChain 1.x install, `create_agent`, reading the message trail, `.content_blocks` |
| 7.1 | `7.1_Model_Integration.ipynb` | `init_chat_model`, provider classes directly (OpenAI/Gemini/Groq), streaming, batching |
| 7.2 | `7.2_Tools.ipynb` | `@tool`, binding tools, reading tool calls, the execution loop |
| 7.3 | `7.3_Messages.ipynb` | The four message types, metadata, token usage |
| 7.4 | `7.4_Structured_Output.ipynb` | Pydantic / TypedDict / dataclass schemas, provider support |
| 7.5 | `7.5_Middleware.ipynb` | `SummarizationMiddleware` (all three trigger units), `HumanInTheLoopMiddleware` (approve/edit/reject), `PIIMiddleware`, call-limit middleware, and writing a custom `AgentMiddleware` |
| 7.6 | `7.6_LangGraph_Interrupt_Primitive.ipynb` | The raw `interrupt()` / `Command(resume=...)` primitive underneath `HumanInTheLoopMiddleware`, in a hand-built LangGraph graph |

## Setup

Dependencies are managed centrally at the repo root — see the top-level
`README.md` / `requirements.txt`. No separate per-folder install needed.

## Why split like this

- 7.0 stands alone as "how do I even build an agent in 1.0."
- 7.1–7.4 cover the surrounding fundamentals (models, tools, messages,
  structured output) that an agent is built from.
- 7.5 isolates middleware — both the built-ins and writing your own — so you
  see every hook point in one place, including the HITL approve/edit/reject
  scenarios.
- 7.6 opens the hood and shows the LangGraph `interrupt()` mechanism that
  `HumanInTheLoopMiddleware` is built on, so you know when to drop down to it
  for a pause that isn't gating a tool call.

## History

This folder consolidates what used to be two separate, overlapping drafts
(`Langchain 1.x/` and `langchainupdated/updatedlangchain/`). The duplicate
intro and middleware-deep-dive notebooks, and the human-in-the-loop notebook
that `7.5`'s HITL section already supersedes, were retired to `archive/` —
see `archive/RETIRED_MANIFEST.md`.
