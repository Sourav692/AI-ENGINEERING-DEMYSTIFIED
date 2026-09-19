# Reasoning and Model Selection

**Status:** ✅ Built — 2 notebooks.

Which model, and how hard should it think? Both questions are model-level and
framework-independent, which is why they live in this stage.

| Notebook | Teaches |
|---|---|
| `01_Reasoning_vs_NonReasoning.ipynb` | What a reasoning model does differently, measured on identical tasks — including a task where reasoning is the wrong choice |
| `02_Reasoning_Effort_Levers.ipynb` | Effort as a dial. Sweeps low/medium/high over a mixed task set, finds the knee via cost-per-accuracy-point, and shows the case where effort is the **wrong lever** — flat accuracy with rising reasoning tokens means the fix is upstream |

## Conventions here

- **Raw `openai` SDK, no LangChain, no `helpers`.** The stage entry rule forbids
  framework dependencies, and the phase forbids `get_llm()` — correctly, because the
  subject *is* the provider parameter. Wrapping it would hide the thing being taught.
- Model names are constants at the top of each notebook. They are the ones the rest of
  this repo already uses (`o4-mini`, `gpt-4o-mini`) so you are not juggling two sets, but
  they change often — check what your account can reach before running.
- Pricing is a dict you edit, not a hardcoded constant. Published prices move; a notebook
  that pretends otherwise teaches a wrong number confidently.

## Where the applied version lives

Routing *between* tiers at runtime — a cheap model triaging work to an expensive one — is
a framework question, so it is not here. It belongs to the Routing workflow pattern:
`02_Core/05_AI_Agent_Fundamentals/4. Workflow_Pattern/2. Routing/`.

## Why this is its own track

`Model_Landscape_and_Hugging_Face/` is the Hugging Face ecosystem — Transformers,
Diffusers, audio, Gradio. Frontier reasoning models reached over an API are not that.
Root `CLAUDE.md` gives this phase "the model landscape" as a topic it owns, so this sits
as a sibling track rather than an eighth module inside the HF one.
