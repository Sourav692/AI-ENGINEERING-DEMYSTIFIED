# Review rubric

Six gates. **Every gate must pass for `APPROVED`.** Any single failure means
`CHANGES_REQUESTED` — there is no "approved with minor comments" verdict, because the
loop exists precisely to handle that case.

Severity on each finding: `blocker` (fails the gate) or `nit` (record it, doesn't fail).
A gate passes if it has no `blocker` findings.

---

## Gate 1 — Syntax and static structure

**Never execute the notebook.** No kernel, no `nbconvert --execute`, no API calls. This
review is entirely static: parsing plus your own knowledge of the APIs involved.

Run `scripts/static_check.py <notebook> --json`. It parses every code cell with `ast`
(execution is not involved) and returns syntax errors, an import inventory, and a
**call surface** — every callee with the keyword arguments used on it.

| Condition | Verdict |
| --- | --- |
| A syntax error in any code cell | **blocker** |
| A syntax error inside a `raises-exception` contrast cell | **blocker** — a 0.x example must still be valid Python; it fails at *import* time, not parse time |
| An import that cannot resolve on the pinned versions (by inspection, not by running) | **blocker** |
| Magics / `!pip` lines | not errors; the parser blanks them. Judge them under Gate 4 |

The call surface is the input to Gate 2 — work through it symbol by symbol. Entries marked
`contrast_only` come solely from 0.x cells, where old API names are intentional and correct.

## Gate 2 — API correctness

The failure mode that matters most: a confidently-written kwarg that does not exist.

- Every LangChain 1.x symbol, parameter and return shape must be verifiable against the
  official docs (Context7 `query-docs` on `/langchain-ai/langchain`), the repo's
  `LangChain_v0_vs_v1_Differences.md`, or the audit skill's `v0-to-v1-rewrite-map.md`.
- Check specifically the things 1.x renamed: `system_prompt=` (not `prompt=`),
  `message.text` (property, not method), `content_blocks`, `context=` vs
  `config["configurable"]`, `"model"` (not `"agent"`) as the stream node name.
- Imports must match the pinned versions (`langchain>=1.2.7`, `langgraph==1.2.11`) and
  must not reference a package absent from `pyproject.toml` — `langchain-classic` is the
  usual offender.
- Work the `call_surface` from Gate 1 pair by pair: for each `callee(kwarg, ...)`, does that
  parameter exist on that symbol in 1.x, spelled that way? This is where you apply what you
  know about the concept — nothing runs, so your knowledge *is* the check.
- Also catch the errors that parse fine and would only fail at runtime: wrong return shape
  (`result["output"]` vs `result["messages"][-1].text`), a method used as a property or vice
  versa, a `.run()`/`.predict()` call on something that only has `.invoke()`, an argument
  passed positionally that is keyword-only.
- **blocker:** any symbol or kwarg you cannot verify, or that you know to be wrong.
- **Bare graph/agent object as a cell's last expression** = **blocker**. Jupyter calls
  `_repr_mimebundle_` on a compiled LangGraph, which calls `draw_mermaid_png()`, which
  POSTs to the `mermaid.ink` web service and raises `ValueError` when it is unreachable
  or rate-limited. A teaching notebook must not depend on a third-party render service.
  Fix: `print(type(agent).__name__)` + `print("Nodes:", list(agent.get_graph().nodes))`,
  or `print(agent.get_graph().draw_mermaid())` for the diagram source — all local.
  (`static_check.py`'s call surface won't show this; look at the last non-comment line of
  each code cell yourself.)

## Gate 3 — Pedagogy

From `plan-to-teaching-notebook/references/notebook-blueprint.md`:

- Required sections present: `What you'll learn`, `Why this changed`, `Common errors`,
  `Key takeaways`. Missing any of the last three = **blocker** (they're what makes it a
  lesson rather than an API diff).
- Every 0.x snippet is paired with its 1.x replacement, and carries the
  `⚠️ Does not run on LangChain 1.x` callout. Unpaired 0.x code = **blocker**.
- "Why this changed" explains the design pressure, not just "it was deprecated".
  A changelog restatement = **blocker**.
- At least one real error string a learner would search for.
- Exercises present and solvable from the notebook's own content.
- One concept per notebook. Two unrelated concepts = **blocker** (split the task).

## Gate 4 — Repo conventions

Run `md_to_notebook.py <notebook> --check` and treat its output as findings:
title cell, single `#` heading, `# ==== BANNER ====` first line per code cell,
markdown summary last, no saved outputs.

Plus, by inspection:

- Imports grouped stdlib → third-party → local.
- **Model init matches the destination phase** — `helpers.get_llm` for phases 3/5/7/8;
  direct instantiation in `LangChain_Fundamentals/` and `RAG_Demystified`-sourced folders.
  Getting this backwards is a **blocker**; it's the most common real defect.
- Filename and numbering fit the destination folder's existing sequence.

## Gate 5 — Task fidelity

Read the task file the notebook came from.

- Does the notebook satisfy the task's stated `## Objective`?
- Does it cover every rule id in the task's `rules` field?
- Does it honour `disposition`? A `repoint` task's notebook teaches "this is legacy,
  here's the modern equivalent"; a `rewrite` task's notebook teaches the modern form as
  the default. Getting this inverted is a **blocker**.
- Are the task's own `## Acceptance criteria` met? Those override this rubric where they
  conflict — they were written for this specific piece of work.

## Gate 6 — Placement and wiring

- The notebook is in the phase that owns the topic (blueprint's placement table).
- It does not duplicate a concept an existing notebook already covers — if one does,
  the correct outcome was extending that notebook. **blocker.**
- `NOTEBOOK_INDEX.md` has a row for it; the folder `README.md` is updated if it lists
  notebooks.
- No dependency was silently added. If one was needed, all three dep files changed together
  (`pyproject.toml`, `requirements.txt`, `requirements.lock.txt`) via a `prereq` task.

---

## Verdict format

Return exactly this shape so the calling skill can act on it without parsing prose:

```json
{
  "verdict": "APPROVED | CHANGES_REQUESTED",
  "round": 1,
  "notebook": "03_LCEL/3.7_Chains_to_LCEL_LangChain_v1.ipynb",
  "task": "T-005",
  "gates": {
    "syntax": "pass|fail",
    "api_correctness": "pass|fail",
    "pedagogy": "pass|fail",
    "conventions": "pass|fail",
    "task_fidelity": "pass|fail",
    "placement": "pass|fail"
  },
  "findings": [
    {
      "gate": "api_correctness",
      "severity": "blocker",
      "cell": 8,
      "what": "create_agent(..., prompt=...) — 1.x renamed this to system_prompt=",
      "fix": "rename the kwarg; verified in docs/oss/python/migrate/langchain-v1"
    }
  ],
  "summary": "one or two sentences"
}
```

Rules for the reviewer:

- **Cite a location for every finding** (cell index, or file:line). A finding without a
  location cannot be acted on and will just cause another round.
- **Say what the fix is**, not only what is wrong.
- Do not invent findings to look thorough. An empty `findings` list with
  `APPROVED` is the correct output for good work, and a clean pass on round 1 is a
  success, not a suspicious result.
- Do not rewrite the notebook. Review only — the authoring skill applies fixes.
- Be specific about uncertainty: if you could not verify an API, that is a `blocker`
  with `"what"` naming exactly which symbol you could not confirm and where you looked.
