# `.tasks/`

Task boards generated from `.plan/` documents. One board per plan; one file per task.

```
.tasks/
  <board-name>/
    INDEX.md            # generated tracker — progress, per-wave tables. DO NOT hand-edit.
    T-001_<slug>.md     # one task: frontmatter + objective, steps, acceptance criteria, log
    T-002_<slug>.md
```

A plan is a document; a board is **state**. The board is what survives across sessions and what
tells you whether work actually finished.

## The one rule

`INDEX.md` is generated from the task files' frontmatter. Never edit it by hand — change the task
file and regenerate:

```bash
python .claude/skills/plan-to-tasks/scripts/tasks.py index .tasks/<board>
```

Everything else follows from that: the tracker cannot drift from the tasks, because it is derived
from them.

## Task frontmatter

| Field | Meaning |
| --- | --- |
| `id` | `T-001`, assigned in order |
| `type` | `prereq` · `migration` · `explainer` |
| `status` | `todo` · `in-progress` · `blocked` · `done` · `wontfix` |
| `wave` | ordering group inherited from the plan |
| `effort` | `S` / `M` / `L` |
| `disposition` | `repoint` · `rewrite` · `n/a` — the editorial call from the plan |
| `plan` | source `.plan/` file |
| `targets` | files this task changes |
| `rules` | scanner rule ids this task closes |
| `depends_on` | task ids that must close first |
| `output` | artifact produced (e.g. a new notebook path) |

## Common commands

```bash
T=.claude/skills/plan-to-tasks/scripts/tasks.py

python $T next  .tasks/<board>                      # next unblocked task
python $T list  .tasks/<board> --type explainer      # what curriculum is outstanding
python $T set   .tasks/<board>/T-003_*.md --status done --note "why / what happened"
python $T index .tasks/<board>                       # after ANY change
```

## Pipeline

```
langchain-v1-migration-audit  ->  .plan/<folder>_langchain_v1_plan.md
plan-to-tasks                 ->  .tasks/<folder>/
plan-to-teaching-notebook     ->  works `type: explainer` tasks -> new notebooks
```

Tracked in git on purpose: these files are the record of what was done and why.
