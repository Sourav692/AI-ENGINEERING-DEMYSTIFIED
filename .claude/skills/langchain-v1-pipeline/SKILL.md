---
name: langchain-v1-pipeline
description: >-
  Runs the entire LangChain 1.x migration pipeline end to end on one folder, unattended —
  audit → plan → task board → explainer notebooks → independent review loop → close tasks →
  roll the plan up to complete. Chains the four stage skills (langchain-v1-migration-audit,
  plan-to-tasks, plan-to-teaching-notebook, notebook-review) and makes their normally-human
  decisions autonomously, logging every one to a run log for later override. Use when the
  user says "run the whole pipeline", "do the full automation", "audit and migrate <folder>
  end to end", "no prompts, just run it", or invokes it by name. For a single stage, call
  that stage's skill directly instead.
---

# LangChain 1.x Pipeline (unattended)

One command, four stages, no per-stage prompting. The stage skills each contain a
"stop and confirm with the user" step; **this skill explicitly overrides those** and decides
instead — that is the whole point. In exchange it owes the user a complete, honest record of
every decision it made alone.

```
preflight ─► ① audit ──► .plan/<slug>_langchain_v1_plan.md
             ② board ──► .tasks/<slug>/  (INDEX.md + T-00N files)
             ③ write ──► explainer notebooks   ┐
             ④ review ─► static, fresh subagent ┘ loop, max 3 rounds each
             ⑤ close ──► tasks done → rollup → plan marked complete
```

## Arguments

`<target folder>` is required. Optional flags in the skill args:

| Flag | Effect |
| --- | --- |
| `--stop-after audit\|tasks\|notebooks` | Run only up to that stage |
| `--max-notebooks N` | Cap explainer notebooks this run (**default 5**) |
| `--no-notebooks` | Stages 1–2 only; board the work, write nothing |
| `--review-rounds N` | Override the 3-round cap (keep it small) |

If no target is given, **stop and ask** — that is the one blocking question. Scanning the
whole repo (~500 notebooks) produces an unusable plan, and guessing wastes an entire run.

## Preflight

```bash
python .claude/skills/langchain-v1-pipeline/scripts/preflight.py "<target>" --json
```

Returns the resolved target, the shared `slug` (phase-prefixed when the folder name is
generic, so `01_Foundations` can't collide across phases), `plan_path`, `board_dir`,
`run_log`, verified stage-script paths, and **`resume_from`**.

**Honour `resume_from`.** A re-run continues; it does not start over:

| `resume_from` | Do |
| --- | --- |
| `stage-1` | full run |
| `stage-2` | plan exists — re-scan to refresh counts, then board it |
| `stage-3` | board has open work — go straight to working tasks |
| `complete` | everything closed — re-scan only, report drift, change nothing |

Then open the run log (`.plan/runs/<date>_<slug>.md`) and append to it as you go. **Every
autonomous decision goes in it**, one line each, with enough detail to reverse:

```markdown
## Run <date> — <target>
- args: --max-notebooks 5
- stage 1: 28 files scanned, 17 need work, 59 BLOCKING
- decision: `4.2_Advanced_Chains.ipynb` → **repoint** (module's subject IS the chain API)
- decision: `8.1_Text_Summarization.ipynb` → **rewrite** (chain was a vehicle, not the lesson)
- decision: folded `MSG-example-kwarg` (1 finding) into T-006 rather than its own notebook
- stage 3: T-005 → 03_LCEL/3.7_... (review r2 APPROVED)
- SKIPPED: T-008 — destination already covers the concept (3.5_Chain_Migrations.ipynb)
```

## The decisions this skill makes alone

Each stage skill normally asks. Here are the rules that replace those questions. **Apply
them mechanically and log each application** — a wrong call recorded is fixable; a wrong
call made silently is not.

### Repoint vs rewrite (stage 1)

- The notebook's **title or folder name** names the legacy construct (`04_Chains/`,
  "Chains Basics", "Memory") → **repoint**. The legacy API is the subject.
- The legacy construct is a **vehicle** for another task (summarize, retrieve, converse,
  extract) → **rewrite**.
- Tie → **rewrite**, and log it as a tie. Learners copy this code; the modern form is the
  safer default when uncertain.

### Task decomposition (stage 2)

- One task = one sitting with a single acceptance criterion.
- Same mechanical change across N files in one wave → **one** task.
- One notebook needing a conceptual rewrite → its **own** task.
- A dependency the repo lacks (`langchain-classic`) → a `prereq` task everything in that
  wave depends on. **Never edit `pyproject.toml` / `requirements.txt` /
  `requirements.lock.txt` unattended** — board it, log it, leave it `todo`, tell the user.

### Which concepts become notebooks (stage 2)

- Test: *would a learner who understood this fix all N findings themselves?* Yes → one
  `explainer` task.
- A concept with fewer than ~5 findings and no conceptual depth → fold into a neighbour,
  log as "folded".
- Order explainer tasks by finding count, descending, and **stop at `--max-notebooks`**.
  Leave the rest boarded as `todo` — a capped run is a feature, not a failure.

### Destination (stage 3)

- Placement table in `plan-to-teaching-notebook/references/notebook-blueprint.md`.
- If a notebook there already covers the concept → **skip and log**. Do **not** create a
  sibling, and do not silently rewrite someone's existing notebook unattended. Extending an
  existing notebook is a judgment call that stays with the user.
- Filename/numbering follows the destination folder's existing sequence.

## Stage loop

For each `explainer` task, in board order:

1. `tasks.py set <task> --status in-progress`
2. Draft markdown → `md_to_notebook.py --out <destination>` (conventions checked on write).
3. **Review as a fresh subagent** — `Agent` tool, `subagent_type: "general-purpose"`,
   invoking `notebook-review` on the notebook + task. Never self-review: a clean-context
   reviewer is the only thing that reliably catches a kwarg you already believed was real.
   Review is static — it parses, it never executes, so rounds cost no API calls.
4. `tasks.py set <task> --review <verdict> --bump-round --note "review rN: ..."`, appending
   the verdict JSON to the task log.
5. `CHANGES_REQUESTED` → fix **the markdown draft**, re-run `md_to_notebook.py --force`,
   back to 3. Never hand-patch the `.ipynb`, or draft and notebook diverge.
6. `APPROVED` → `--status done --output <path>`, then `tasks.py index` and `tasks.py rollup`.
7. **3 rounds without approval → stop that task.** Leave it `in-progress`, log the
   unresolved blockers, move to the next task. Never `--force` past review unattended, and
   never start a fourth round.

Between tasks, keep going: one task failing its review does not end the run.

## Stop conditions

Finish the run and report — do not push through — when:

- No target was given (the one blocking question).
- A stage script is missing or the target doesn't exist (preflight exits 2).
- A dependency would have to be added to make a notebook work.
- Every remaining task is blocked by an unmet `depends_on`.
- Three consecutive tasks hit the review cap — that pattern means the plan's assumptions are
  wrong, not that the notebooks are; another five rounds will not fix it.

Never expand scope beyond the named target. Never delete or overwrite an existing notebook.
Never edit dependency files. Never force-close a review-gated task.

## Final report

Because nothing was confirmed along the way, the report is the user's only checkpoint. Give,
in this order:

1. **Board progress line** from `INDEX.md`, and whether `rollup` marked the plan complete.
2. **Notebooks created** — path, task id, review rounds, final verdict.
3. **Decisions made alone** — every repoint/rewrite call, every fold, every skip. Present
   these as a list the user can overrule, not as settled fact.
4. **Not done and why** — capped tasks, review-capped tasks, prereqs left `todo`, skipped
   destinations.
5. **Anything unverified** — any 1.x API the reviewer could not confirm. Say it plainly;
   this is the failure mode that survives an unattended run.
6. The run log path.

Report what actually happened, including the parts that failed. An unattended run that
overstates its success is worse than one that stops early.
