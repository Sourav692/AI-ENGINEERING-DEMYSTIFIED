---
name: plan-to-teaching-notebook
description: >-
  Works the `type: explainer` tasks on a `.tasks/<board>/` board (created by plan-to-tasks)
  and turns each into a runnable teaching notebook — before/after examples, why-it-changed
  narrative, the real error messages, exercises — placed in the roadmap phase that owns that
  topic, then flips the task to done with its output path recorded. Use when the user says
  "create the notebooks", "work the explainer tasks", "explain these concepts in a notebook",
  "turn the tasks into lessons/tutorials", or points at `.tasks/` and asks for teaching
  material. Drafts in markdown and converts with a script rather than hand-writing notebook
  JSON; never executes notebooks. Third stage of the pipeline: langchain-v1-migration-audit
  (plan) → plan-to-tasks (board) → this skill (curriculum).
---

# Tasks → Teaching Notebook

This skill is **driven by the task board**, not by the plan. `.tasks/<board>/` holds
`type: explainer` tasks; each one becomes a notebook, and closing the task is part of the job.

**Pipeline position:**
`langchain-v1-migration-audit` → `.plan/*.md` → `plan-to-tasks` → `.tasks/<board>/` →
**this skill**.

The plan remains useful as *background* — it carries the finding counts and per-notebook
repoint/rewrite reasoning a task references — but the task file is the unit of work, the source
of scope, and the thing that gets updated when you finish.

Read `references/notebook-blueprint.md` before drafting — it carries the section structure,
the pedagogy rules, the placement table, and the model-init convention per phase.
Concept background lives in
`02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/LangChain_v0_vs_v1_Differences.md`
and the audit skill's `references/v0-to-v1-rewrite-map.md` — reuse those code pairs rather than
inventing new ones.

## One task, one notebook

The "which findings make a concept" judgment was already made by `plan-to-tasks` — each
`type: explainer` task **is** one notebook. Do not re-derive the decomposition, and do not
silently merge or split tasks.

If a task turns out to be wrong-sized while you work it — genuinely two concepts, or too thin to
stand alone — **stop and fix the board first**, don't improvise:

```bash
# too thin: fold into a neighbour
tasks.py set .tasks/<board>/T-007_*.md --status wontfix --note "folded into T-005 as a section"
# too big: split
tasks.py new .tasks/<board> --title "..." --type explainer --wave 4 --depends-on T-005
tasks.py index .tasks/<board>
```

The board staying truthful matters more than finishing the notebook in one pass.

## Process

### 1. Pick up the task

```bash
python .claude/skills/plan-to-tasks/scripts/tasks.py list .tasks/<board> --type explainer
python .claude/skills/plan-to-tasks/scripts/tasks.py next .tasks/<board>
```

Work the task the user named, or the next unblocked one. **Respect `depends_on`** — an explainer
usually depends on the migration task that produced the code it documents; writing it first means
teaching code that doesn't exist yet. If `next` reports the task blocked, say so rather than
starting anyway.

Read the task file in full. It gives you:

- `title` + `## Objective` — the concept and what the notebook must achieve
- `rules` — scanner rule IDs, which map to concrete before/after pairs in the audit skill's
  `references/v0-to-v1-rewrite-map.md`
- `disposition` — *repoint* → the notebook teaches "this is legacy, here's the modern
  equivalent"; *rewrite* → it teaches the modern form as the default
- `targets` — the real notebooks in the repo this concept affects; cite them so a learner can
  see the concept in context
- `plan` — the source plan, for finding counts and surrounding reasoning
- `## Steps` / `## Acceptance criteria` — the definition of done for *this* task, which overrides
  any general guidance here

Then mark it started:

```bash
tasks.py set .tasks/<board>/T-00N_*.md --status in-progress
tasks.py index .tasks/<board>
```

### 2. Confirm destination and check for an existing home

Read `references/notebook-blueprint.md` (section structure, pedagogy rules, placement table,
per-phase model-init convention). Concept background is in
`02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/LangChain_v0_vs_v1_Differences.md`
and the audit skill's `references/v0-to-v1-rewrite-map.md` — reuse those verified code pairs
rather than inventing new ones.

Before writing: check the destination folder's existing notebooks (`NOTEBOOK_INDEX.md` plus an
`ls`). If one already covers the concept, **extend it** rather than adding a sibling — a second
home for one topic is exactly what `ai-roadmap-organizer` exists to prevent. Record that choice
on the task (`--note "extending 3.5_Chain_Migrations rather than adding a new notebook"`).

State the destination path and get a nod before creating a new file. Notebooks land in a curated
roadmap and are expensive to undo.

### 3. Draft in markdown, to the formatter's contract

**Load the `Format_Python_Notebook` skill first** (`Skill` tool, name `Format_Python_Notebook`).
It owns the formatting contract for every notebook in this repo — title cell shape, heading
hierarchy and emoji, the 3-line code banner, confirmation prints, import grouping, summary
cell, cleanup rules. This skill supplies the migration *content*; that skill supplies the
*form*. Do not invent a competing structure.

Its sample notebook (`.claude/skills/format-notebook/notebook/sample.ipynb`) is the concrete
reference — skim it before your first draft so the output looks like the rest of the repo.

One documented override: the formatter's **rule 5** shows `get_databricks_llm(...)`
unconditionally, but model init here follows the destination phase (see the blueprint's table).
Everything else in rule 5 still applies.

Write each notebook as a single `.md` draft in the scratchpad, following the blueprint's part
order. Fences drive cell types:

- ` ```python ` → runnable code cell
- ` ```python-noexec ` → 0.x contrast cell (renders as a code cell; the tag is your reminder that
  it must never be presented as runnable — always precede it with the ⚠️ callout)
- anything else stays inside the markdown cell
- `<!-- split -->` forces a markdown cell break

Every code fence must open with the 3-line banner, or the check in step 4 fails:

```
# ==============================================================================
# SECTION_NAME: Brief description
# ==============================================================================
```

Drafting in markdown rather than notebook JSON is the point: it diffs cleanly and keeps you
writing prose instead of assembling cells.

**Verify every 1.x API you write.** Do not reproduce a parameter name from memory — check it in
the rewrite map, or via Context7 (`query-docs` on `/langchain-ai/langchain`), or against a
notebook in this repo already using it. An explainer notebook teaching a hallucinated kwarg is
worse than no notebook.

### 4. Convert and check

```bash
python .claude/skills/plan-to-teaching-notebook/scripts/md_to_notebook.py \
  "<scratchpad>/draft.md" --out "<destination>/3.7_Concept_LangChain_v1.ipynb"
```

The script converts and then validates against `Format_Python_Notebook`'s rules in one pass —
title cell (H1 + emoji + Learning Objectives + Prerequisites), `---` before `##` sections, one
emoji per heading, the 3-line banner on every code cell, `## 📝 Summary` + `### Next Steps` last,
outputs cleared and `execution_count: null`. Each failure names the format rule it violates. Fix
the **draft** and re-run with `--force`.

To validate a notebook you edited by other means: `md_to_notebook.py <file.ipynb> --check`.

**Never execute the notebook** — API keys, cost, and rate limits. Correctness comes from
verifying the APIs while drafting, not from running cells.

### 5. Wire it into the repo

A notebook nobody can find is not curriculum. After creating each one:

- Add a row to `NOTEBOOK_INDEX.md` in the destination's section (it is the source of truth for
  what exists — `README.md` tables have historically drifted from it).
- Update the destination folder's `README.md` if it lists its notebooks.
- Tick the matching rows in the source `.plan/` file, so plan and board agree.
- If the notebook needs a package not in `pyproject.toml` (`langchain-classic` is the likely
  one), say so — do not silently add deps. `pyproject.toml` is source of truth,
  `requirements.txt` the resolver-verified pinned mirror, and `requirements.lock.txt` the full
  transitive lock — all three change together (`uv pip compile requirements.txt
  --python-version 3.12 -o requirements.lock.txt`), so an unpinned addition is a real risk.
  If it's genuinely needed, that's a **new `prereq` task on the board**, not a quiet edit.

### 6. Submit for review — the loop

You **cannot** close this task yourself. `tasks.py` refuses `--status done` on an `explainer`
or `migration` task until `review: approved`, and that verdict comes only from the
`notebook-review` skill.

Record the artifact and move the task into review:

```bash
T=.claude/skills/plan-to-tasks/scripts/tasks.py
python $T set .tasks/<board>/T-00N_*.md --status in-review \
  --output "03_LCEL/3.7_Chains_to_LCEL_LangChain_v1.ipynb"
```

Then run the loop, **maximum 3 review rounds**:

1. **Review.** Spawn a *fresh subagent* — `Agent` tool, `subagent_type: "general-purpose"` —
   and have it invoke the `notebook-review` skill on this notebook + task. It must not inherit
   your authoring context; a clean-context reviewer is the only thing that reliably catches a
   kwarg you already convinced yourself was real. **Do not review your own notebook.**
2. **Record the round** regardless of verdict:
   ```bash
   python $T set .tasks/<board>/T-00N_*.md --review changes-requested --bump-round \
     --note "review r1: <verdict summary>"
   ```
   Append the verdict JSON to the task's `## Notes / log`.
3. **If `CHANGES_REQUESTED`:** apply every `blocker` finding (nits are optional), then go back
   to step 1. Fix the draft `.md` and re-run `md_to_notebook.py --force` — never hand-patch the
   `.ipynb`, or the draft and the notebook diverge.
4. **If `APPROVED`:** close it.
   ```bash
   python $T set .tasks/<board>/T-00N_*.md --review approved --bump-round \
     --note "review r2: approved — all six gates pass"
   python $T set .tasks/<board>/T-00N_*.md --status done
   python $T index  .tasks/<board>
   python $T rollup .tasks/<board>
   ```
   `rollup` writes task progress back into the source `.plan/` file and ticks its
   **Plan complete** checkbox — but only when *every* task on the board is closed. A plan is
   never marked done because one notebook landed.

**After 3 rounds still not approved: stop.** Leave the task `in-progress` with
`review: changes-requested` and report the unresolved blockers. Do not start a fourth round and
do not use `--force`; a finding that survives three rounds usually means the *task* is wrong
(wrong scope, wrong disposition, an API that genuinely doesn't exist) and needs a human call.

Also tick the task file's own `## Steps` / `## Acceptance criteria` boxes as they're met. If any
is unmet, the task is not done — a board recording unfinished work as finished is worse than no
board.

### 7. Report

Per notebook: task id, path, concept, cell count, **review rounds and final verdict**, and
anything you could not verify. Flag explicitly if any 1.x API is unverified — that is the
failure mode that matters most. Finish with the board progress line from `INDEX.md` and the
plan's rollup state, so the user can see what's left and whether the plan closed.

## Extending

`scripts/md_to_notebook.py` is generic — it has nothing LangChain-specific in it, so it is the
right tool for any future "draft in markdown, ship as a notebook" work in this repo. The
`--check` rules encode `CLAUDE.md`'s notebook conventions; if those conventions change, update
`check()` there and the blueprint together.
