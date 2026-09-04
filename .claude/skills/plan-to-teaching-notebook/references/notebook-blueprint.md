# Blueprint for a concept-explainer notebook

The output of this skill is **teaching material**, not a migration script. A learner who has never
seen LangChain 0.x should finish the notebook understanding *what the abstraction is now* — the 0.x
form appears as contrast, never as the main event.

## The shape

**The `Format_Python_Notebook` skill (`.claude/skills/format-notebook/SKILL.md`) owns the
formatting contract.** Read it before drafting — everything below is the migration-specific
*content* poured into that skill's *structure*, not a competing format.

The formatter mandates three fixed pieces; the middle is yours to shape:

```
CELL 0 (markdown)  # <emoji> <Concept> — <what changed, in five words>
                   ## Learning Objectives      (3-5 bolded items)
                   ## Prerequisites            (packages, keys, prior notebooks)

  ...body: `---` + `## <emoji> Part N: ...` markdown cell, then code cell,
     repeated. Every code cell opens with the 3-line banner.

LAST CELL (markdown)  ---
                      ## 📝 Summary
                      ### 1. <Section Title>  - **Key point**: ...
                      ### Next Steps
```

For a migration explainer, the body parts are:

| Part | Content |
| --- | --- |
| `## 🤔 Part 1: Why this changed` | the design pressure, not the changelog |
| `## ⚙️ Part 2: Setup` | imports + model init, one code cell, ends with a confirmation print |
| `## 🕰️ Part 3: The old way` | 0.x, `python-noexec`, kept short |
| `## ✨ Part 4: The new way` | 1.x, runnable, the bulk of the notebook |
| `## 🔀 Part 5: Side by side` | a mapping table |
| `## 🚨 Part 6: Common errors when migrating` | error text → cause → fix |
| `## 🧪 Part 7: Try it yourself` | 1-2 exercises, no inline solutions |

Parts 1, 6 and the Summary are the three most often skipped and the three that separate a
lesson from an API diff — none of them is optional. Extra parts are fine when a concept needs
them (`## 🔬 Under the hood`, `## 🧭 When to still use the old way`).

## Rules that make it teachable

1. **Every 0.x snippet is a `python-noexec` fence.** It will not run on the pinned environment, and a
   notebook that raises `ImportError` in cell 4 teaches nothing. Precede it with a bold
   `> ⚠️ Does not run on LangChain 1.x — shown for contrast only.`
2. **Pair every before with an after.** Never show a 0.x pattern you don't immediately replace.
3. **Runnable means runnable.** New-way cells must execute against this repo's pinned versions
   (`langchain>=1.2.7`, `langgraph==1.2.11`) with only the documented env vars. No invented
   parameters, no APIs you have not verified.
4. **One concept per notebook.** "Chains → LCEL" and "AgentExecutor → create_agent" are two
   notebooks, even though one plan wave produced both.
5. **Explain the pressure, not the changelog.** "`AgentExecutor` was removed" is a fact;
   "the executor loop and the graph runtime were two ways to express the same cycle, so 1.x kept
   the one that could also express interrupts, durability, and streaming" is a lesson.
6. **Show the error the learner will actually hit.** `ImportError: cannot import name 'LLMChain'
   from 'langchain.chains'` is what sends people searching — put the literal string in the notebook
   so it is findable.
7. **No saved outputs.** Cells ship with `execution_count: null` and empty `outputs` (the repo has
   no committed-output convention and outputs leak keys/paths).

## Format rules the checker enforces mechanically

`md_to_notebook.py --check` validates these on every write, straight from
`Format_Python_Notebook`. It reports the rule number, so a failure points back at that skill:

| # | Rule | Checked |
| --- | --- | --- |
| 1 | Cell 0: `# <emoji> Title` + `## Learning Objectives` + `## Prerequisites` | yes |
| 2 | `##` section cells open with a `---` separator; every heading carries one emoji | yes |
| 3 | Every code cell opens with the **3-line** banner (`# ====` / `# NAME: desc` / `# ====`) | yes |
| 6 | Final cell: `## 📝 Summary` **and** `### Next Steps` | yes |
| 7 | `outputs` empty, `execution_count: null`, no Databricks cell metadata | yes |

The rest of the formatter is judgment and lands on the reviewer instead: import grouping
(stdlib → third-party → LangChain → helpers), confirmation prints with the right emoji
(`✅` success, `🤖` LLM, `🔧` tool, `⚠️` warning, `❌` error), inline comments only where the
*why* is non-obvious, `# ---` separators between blocks in a long cell, and the
merge-tiny-cells / split-overloaded-cells rules.

Model initialization depends on where the notebook lands:

| Destination phase | Init style |
| --- | --- |
| 3, 5, 7, 8 (LangGraph-side) | `from helpers import get_llm, get_embeddings` — **required** |
| 2 `LangChain_Fundamentals/` | direct `ChatOpenAI` / `ChatGroq` — the documented convention there |
| 4 (`RAG_Demystified`-sourced) | direct instantiation, matches surrounding notebooks |

**This overrides `Format_Python_Notebook`'s rule 5**, which shows `get_databricks_llm(...)`
unconditionally. That skill was written for the LangGraph-side notebooks; the per-phase
convention in `CLAUDE.md` wins. Everything else in rule 5 still applies — show the active
choice, list alternatives as comments, and print which model was loaded.

Getting this wrong is the most likely review comment — check the sibling notebooks in the
destination folder before writing the setup cell.

## Placement

One topic, one phase (see `.claude/skills/ai-roadmap-organizer/`). For migration explainers:

| Concept | Destination |
| --- | --- |
| Package split, imports, `langchain-classic` | `02_.../LangChain_Fundamentals/01_Getting_Started/` |
| Chains → LCEL | `02_.../LangChain_Fundamentals/03_LCEL/` (a `3.x` sibling; `3.5_Chain_Migrations` already exists — extend the numbering, don't duplicate the topic) |
| `AgentExecutor` / `create_react_agent` → `create_agent` | `05_AI_Agent_Fundamentals/LangChain_Tools_and_Agents/` |
| Middleware | `05_AI_Agent_Fundamentals/Workflow_and_Agent_Patterns/` |
| `*Memory` → checkpointers | `07_Advanced_Agentic_Systems/Memory_and_State/LangChain/` |
| Content blocks / message API | `02_.../LangChain_Fundamentals/02_Inputs_Outputs_Prompts/` |
| `RetrievalQA` → LCEL / agentic RAG | `04_Retrieval_and_RAG/RAG_with_LangChain/` |

Number the new file to fit the destination folder's existing sequence. If the destination already
has a notebook covering the concept, **extend it instead of adding a second one** — a second home
for one topic is the failure mode `ai-roadmap-organizer` exists to prevent.

## Naming

`<n.n>_<Concept>_LangChain_v1.ipynb`, matching the destination's numbering style — e.g.
`3.7_Chains_to_LCEL_LangChain_v1.ipynb`. Match the neighbours; some tracks use `01_`, others `3.5_`.
