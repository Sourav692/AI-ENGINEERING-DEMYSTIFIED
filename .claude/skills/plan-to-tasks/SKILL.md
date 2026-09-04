---
name: plan-to-tasks
description: >-
  Turns a migration plan in `.plan/` into a tracked task board under
  `.tasks/<plan-name>/` — one task file per unit of work, each with frontmatter
  (id, status, wave, effort, target files, scanner rules, dependencies, output) plus
  a generated INDEX.md tracker showing progress. Use when the user says "create tasks
  from the plan", "break the plan into tasks", "make a task tracker", "track this
  migration", or asks what to work on next. Also the skill that maintains the board:
  flipping task status, logging notes, regenerating the index. Sits between
  langchain-v1-migration-audit (which writes the plan) and plan-to-teaching-notebook
  (which consumes `type: explainer` tasks).
---

# Plan → Tasks

A plan is a document; a task board is state. This skill converts one into the other and then
maintains it, so work survives across sessions and nothing gets half-done silently.

**Pipeline position:**
`langchain-v1-migration-audit` → `.plan/*.md` → **this skill** → `.tasks/<board>/` →
`plan-to-teaching-notebook` (picks up `type: explainer` tasks).

## What a task is

One task = **one sitting of work with a single acceptance criterion**. Not one finding, not one
whole wave.

- A wave of 13 files that all need the same import repointed is **one** task, not 13 — the
  decision is made once and applied mechanically.
- A single notebook needing a full `LLMChain` → LCEL rewrite plus narrative rework is **one** task
  on its own, because it carries its own judgment.
- "Add `langchain-classic` to `pyproject.toml` + `requirements.txt` + `requirements.lock.txt`"
  is a **prereq** task that
  everything in Wave 1 depends on.

If you can't write a one-line acceptance criterion for it, it's not a task yet — split it.

Three task types:

| `type` | Meaning | Consumed by |
| --- | --- | --- |
| `prereq` | Environment/dependency work that unblocks others | you, first |
| `migration` | Change existing notebooks to 1.x | you / the user |
| `explainer` | Write a new teaching notebook for a concept | `plan-to-teaching-notebook` |

## Process

### 1. Read the plan

Read the `.plan/*_plan.md` file(s) named by the user (or list `.plan/` and ask if ambiguous).
Harvest: waves, per-notebook rows with their **repoint vs rewrite** decisions, effort buckets,
rule IDs, prerequisites, and any `- [x]` already ticked — **ticked rows become tasks with
`status: done`**, not omitted tasks. The board must account for the whole plan or it stops being
a reliable record.

Board name = the plan's target folder name: `.plan/04_Chains_langchain_v1_plan.md` →
`.tasks/04_Chains/`.

### 2. Decompose, then confirm

Group the plan's rows into tasks by the rule above. Present the proposed list — id, title, type,
wave, effort, targets — and get approval before writing files. Cheap to change now, annoying later.

Include the `explainer` tasks in the same board: the concepts a learner needs are part of the
same body of work, and putting them on the board is what lets the notebook skill find them.

### 3. Create the task files

```bash
python .claude/skills/plan-to-tasks/scripts/tasks.py new .tasks/04_Chains \
  --title "Repoint legacy chain imports to langchain-classic" \
  --type migration --wave 1 --effort S --disposition repoint \
  --plan .plan/04_Chains_langchain_v1_plan.md \
  --targets "04_Chains/4.0_Basics_of_Chains.ipynb,04_Chains/4.2_Advanced_Chains.ipynb" \
  --rules "IMP-chains,CHN-llmchain" \
  --depends-on T-001 \
  --objective "Notebooks import and run on 1.x without changing what they teach."
```

IDs are assigned automatically (`T-001`, `T-002`, …) and the file is written as
`T-00N_<Slugged_Title>.md` with a body scaffold: Objective / Scope / Steps / Acceptance criteria /
Notes log.

Then **fill in the `## Steps` section by editing the file** — the scaffold ships one placeholder
step. Steps should be checkable actions, not restatements of the title. Refine the acceptance
criteria too; the generated ones are a floor, not a ceiling.

Set `--depends-on` wherever real ordering exists (prereqs before Wave 1; Wave 2 agent rewrites
before an explainer that documents the result). The index renders unmet dependencies as
"Blocked by", and `tasks.py next` refuses to suggest a blocked task.

### 4. Generate the tracker

```bash
python .claude/skills/plan-to-tasks/scripts/tasks.py index .tasks/04_Chains
```

Writes `INDEX.md`: progress bar, status counts, and per-wave tables linking each task file, with
blockers and output paths. **`INDEX.md` is generated — never hand-edit it.** Edit the task files'
frontmatter and re-run `index`; that way the tracker cannot drift from reality, which is the
usual way trackers die.

### 4b. The review gate

Tasks of type `explainer` and `migration` are created with `review: pending` and **cannot be
closed** until `review: approved` — `tasks.py set --status done` refuses them, printing the
command sequence needed. Approval comes only from the `notebook-review` skill.

`prereq` tasks are `review: n/a` and close on their own acceptance criteria.

`--force` exists for a deliberate human override and stamps a ⚠️ line in the task log. Never
use it to get past a review you couldn't satisfy; that is the one thing that makes the board
lie.

### 5. Maintain the board

This is the part that matters. While work happens:

```bash
tasks.py set .tasks/04_Chains/T-003_*.md --status in-progress
tasks.py set .tasks/04_Chains/T-003_*.md --status done --note "3 files done; 4.3 deferred, see T-009"
tasks.py set .tasks/04_Chains/T-007_*.md --status blocked --note "needs langchain-classic (T-001)"
tasks.py set .tasks/04_Chains/T-005_*.md --output 03_LCEL/3.7_Chains_to_LCEL_LangChain_v1.ipynb
tasks.py index .tasks/04_Chains          # after ANY status change
```

Rules:

- **Flip status when it changes, not at the end.** A board that is only accurate after the fact
  is a report, not a tracker.
- `--note` appends a dated line to the task's log. Use it for decisions and surprises — that log
  is the only record of *why* something was done a particular way.
- Re-run `index` after every change. If you forget, `INDEX.md` lies.
- `wontfix` is legitimate — a plan row you deliberately decline. Record why in the log.
- Never delete a task file to "clean up"; close it as `done` or `wontfix`.

Reading state: `tasks.py list <board> [--status todo] [--type explainer]` and
`tasks.py next <board>` (lowest-id unblocked `todo`).

### 6. Roll up to the plan

```bash
python .claude/skills/plan-to-tasks/scripts/tasks.py rollup .tasks/<board>
```

`rollup` reads the board and rewrites a managed block in each source `.plan/` file
(between `<!-- rollup:start -->` / `<!-- rollup:end -->`): a **Plan complete** checkbox, the
board path, a task-progress bar, and the rollup date.

**A plan is marked complete only when every task on its board is closed** (`done` or
`wontfix`) **and** no review-gated task was closed without approval. One notebook landing never
closes a plan. `rollup` re-derives this every time, so a reopened task automatically un-ticks
the plan.

Run `rollup` after any status change, right after `index`. Also tick the matching per-notebook
`- [ ]` rows in the plan's own checklist as their tasks close — the rollup block tracks the
board, those rows track the narrative.

## Board layout

```
.tasks/
  <board-name>/
    INDEX.md                 # generated tracker — do not hand-edit
    T-001_<slug>.md          # one task, frontmatter + body
    T-002_<slug>.md
```

Task frontmatter fields: `id`, `title`, `type`, `status`, `wave`, `effort`, `disposition`,
`plan`, `targets`, `rules`, `depends_on`, `output`, `created`, `updated`.
Statuses: `todo`, `in-progress`, `blocked`, `done`, `wontfix`.

`.tasks/` is tracked in git alongside `.plan/` — it is the record of what was done and why.

## Extending

`tasks.py` is domain-agnostic — nothing in it mentions LangChain. Any future plan in `.plan/`
can be boarded with the same script; only the decomposition judgment in §2 is specific to what
the plan describes.
