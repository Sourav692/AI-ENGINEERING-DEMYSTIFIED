---
name: notebook-review
description: >-
  Independently reviews a notebook produced or edited by a `.tasks/` board task and
  returns a machine-actionable APPROVED / CHANGES_REQUESTED verdict. Six static gates —
  syntax (AST parse), API correctness judged from knowledge of the concept, pedagogy,
  strict `Format_Python_Notebook` compliance, task fidelity, and placement. Use when the user says "review this
  notebook", "check the notebook", "is this notebook approved", or when a notebook-authoring
  skill needs sign-off before closing a review-gated task. Reviews only — never rewrites the
  notebook and never executes it (no kernel, no API calls, no cost). A task of type
  `explainer` or `migration` cannot close without an APPROVED verdict from this skill.
---

# Notebook Review

The approval gate for the migration pipeline. Tasks of type `explainer` and `migration`
carry `review: pending` and `tasks.py` **refuses** to close them until `review: approved`,
so this skill is the only way that work legitimately finishes.

**Pipeline position:**
`langchain-v1-migration-audit` → `plan-to-tasks` → `plan-to-teaching-notebook`
⇄ **this skill** (loop, max 3 rounds) → task closed → plan rollup.

## Independence is the point

Run this **as a fresh subagent** (`Agent` tool, `subagent_type: "general-purpose"`), not as
a self-review in the authoring session. The reviewer must see the notebook, the task file,
and the rubric — **not** the reasoning that produced the notebook. A model that just
convinced itself a kwarg exists will confirm that belief on re-read; a clean-context
reviewer checks it against the docs instead. That is the single defect class this gate
exists to catch.

When invoked directly by the user in the main session, review normally — but say in the
verdict that it was a same-session review, since it is weaker.

## Process

### 1. Gather inputs

You need, and should read in this order:

1. The **task file** (`.tasks/<board>/T-00N_*.md`) — objective, `rules`, `disposition`,
   `targets`, and its own acceptance criteria, which **override** this rubric on conflict.
2. The **notebook** under review (its `output` field, or the path given).
3. `references/rubric.md` — the six gates and the verdict schema.
4. The blueprint (`plan-to-teaching-notebook/references/notebook-blueprint.md`) and
   `LangChain_v0_vs_v1_Differences.md` for the standards being applied.

### 2. Parse, don't run

**This skill never executes a notebook.** No kernel, no `nbconvert --execute`, no API keys,
no cost. Correctness is judged by reading the code against what you know about the API —
which is the right tool anyway, because a cell can execute perfectly and still teach a
deprecated idiom, and a cell can fail for reasons (rate limit, expired key) that say nothing
about the notebook.

```bash
python .claude/skills/notebook-review/scripts/static_check.py "<notebook>" --json
```

It parses each code cell with `ast` and returns three things:

- **syntax errors** — cell index and line (Gate 1)
- **imports** — module/name inventory, with contrast-cell imports marked
- **call surface** — every `callee(kwarg, ...)` observed, which is the checklist for Gate 2

Entries flagged `contrast_only` come solely from the 0.x contrast cells; old API names there
are intentional. Everything else is live code a learner will copy, and must be right.

### 3. Work the remaining gates

Follow `references/rubric.md` gates 2-6. **Gate 2 is the one that matters** and it is
knowledge-driven: walk the call surface symbol by symbol and ask whether each keyword argument
genuinely exists on that symbol in LangChain 1.x, spelled that way. Verify against Context7
(`query-docs` on `/langchain-ai/langchain`) or the repo's own reference docs when you are less
than certain — an unverified symbol is a `blocker`, not a pass.

Beyond signatures, catch the errors that parse cleanly and would only surface at runtime:
wrong return shape (`result["output"]` where 1.x gives `result["messages"][-1].text`), a
property used as a method (`.text()` vs `.text`), `.run()`/`.predict()` on something that only
exposes `.invoke()`, a keyword-only argument passed positionally.

Gates 3-6 are the pedagogy and format half. **Gate 4 checks compliance with the
`Format_Python_Notebook` skill** — load that skill (`.claude/skills/format-notebook/SKILL.md`)
before judging it, since it is the contract and the rubric is only the checklist.
`md_to_notebook.py --check` mechanizes rules 1, 2, 3, 6 and 7; the rest (objective quality,
narrative after headings, import grouping, confirmation-print emoji, cleanup rules) is
inspection, and the rubric lists each one.

### 4. Return the verdict

Emit the JSON object from the rubric's "Verdict format" section, then a short prose
summary. Requirements:

- `APPROVED` only when **every** gate passes. There is no "approved with comments" — that
  is what `CHANGES_REQUESTED` plus a short findings list is for, and the loop is cheap
  (a static round costs no API calls).
- Every finding carries a **location** (cell index) and a **fix**. A finding without both
  just causes another round.
- Never rewrite the notebook or edit the task file. Reviewing and fixing are separate
  roles on purpose; the authoring skill applies fixes and re-submits.
- Don't manufacture findings to look thorough. A clean round-1 pass is a good outcome.

### 5. Record the review

The **calling skill** owns the bookkeeping (`tasks.py set --review ... --bump-round`).
If a user invokes this skill directly, do it yourself:

```bash
T=.claude/skills/plan-to-tasks/scripts/tasks.py
python $T set .tasks/<board>/T-00N_*.md --review approved --bump-round \
  --note "review r2: approved — all six gates pass"
# or
python $T set .tasks/<board>/T-00N_*.md --review changes-requested --bump-round \
  --note "review r1: 2 blockers — create_agent kwarg (cell 8), missing Common errors section"
python $T index .tasks/<board>
```

Append the full verdict JSON to the task's `## Notes / log`. The log is the audit trail:
someone reading the task later should be able to see what was wrong and what fixed it.

## The loop, and its cap

The authoring skill runs: **write → review → fix → review**, up to **3 review rounds**.

- Approved on any round → the authoring skill closes the task and rolls up the plan.
- Still `CHANGES_REQUESTED` after round 3 → **stop**. Leave the task `in-progress` with
  `review: changes-requested`, and report the unresolved blockers to the user. Do not
  force-close, and do not start a fourth round.
- If the same finding survives two rounds unchanged, say so explicitly — a finding the
  author cannot resolve usually means the *task* is wrong (wrong scope, wrong
  disposition, an API that genuinely doesn't exist), and that needs a human decision, not
  another round.

The cap exists because an unbounded loop against an unsatisfiable criterion burns tokens
without converging. Three rounds is a ceiling, not a target.
