---
name: notebook-folder-cleanup
description: >-
  Cleans and modernizes a folder of Jupyter notebooks end to end — retires dead-end
  and abandoned notebooks, consolidates duplicate coverage, migrates deprecated library
  APIs (pandas, NumPy, scikit-learn, PyTorch, TensorFlow, CrewAI, AutoGen; LangChain via
  the dedicated audit skill), reformats everything to the Format_Python_Notebook contract,
  and reports what changed and why. Use when the user names a folder and asks to "clean
  up", "organize", "tidy", "deduplicate", "remove dead notebooks", "modernize the
  libraries", or "make these notebooks production/enterprise grade". Does not clean on
  first contact: it delegates to `notebook-folder-cleanup-planner`, which writes
  `.cleanup/<slug>_cleanup_plan.md`, and only executes once that plan and its paired
  `.cleanup/<slug>_cleanup_decisions.md` exist. Retires notebooks by moving them to
  `archive/` with a manifest — never deletes — and never removes anything without a
  recorded decision.
---

# Notebook Folder Cleanup

Takes one folder and returns a clean, non-redundant, current, consistently formatted set of
notebooks — plus a report of every removal, consolidation and code change.

**It does not start by cleaning.** Stage 1 produces a plan on disk and stops; the cleaning
runs on the next invocation, against that plan and the decisions recorded on it:

```
notebook-folder-cleanup (1st call) → planner → .cleanup/<slug>_cleanup_plan.md   [stop]
user responds                      → planner → .cleanup/<slug>_cleanup_decisions.md
notebook-folder-cleanup (2nd call) → merge both → retire / migrate / reformat / review
```

This skill **composes** the others rather than reimplementing them:

| Need | Skill it delegates to |
| --- | --- |
| Inventory, triage, and the plan itself | `notebook-folder-cleanup-planner` |
| LangChain/LangGraph 0.x → 1.x | `langchain-v1-migration-audit` (its scanner + rewrite map) |
| Formatting contract | `Format_Python_Notebook` |
| Independent sign-off | `notebook-review` |
| Where a notebook belongs in the roadmap | `ai-roadmap-organizer` |

Only the execution of an approved plan and the non-LangChain deprecation map
(`references/library-migration-map.md`) are its own. The triage rules — what counts as
evidence of abandonment, what is never a reason to retire — live in the planner, because
that is where the judgment is made.

## Two rules that are not negotiable

**1. Retire, don't delete.** `CLAUDE.md` documents `archive/` as the home for retired
notebooks. A "dead-end" judgment is a *guess about intent* made from the outside, and
guesses about someone's learning material should be reversible. Move to
`archive/<original-path>/`, write a manifest row, never `rm`.

**2. Nothing moves without a recorded decision.** Approval is a file
(`.cleanup/<slug>_cleanup_decisions.md`), not a message in a transcript. No plan, no run —
and within a plan, an ID with no decision row is **not** approved: `keep` and `consolidate`
proceed, `retire` does not. That is what lets this skill run unattended without becoming
the one skill that quietly removes files nobody agreed to remove.

## Process

### 1. Plan first — always

Derive the slug (last path segment of the target, phase-prefixed when it is a name that
recurs across phases) and look for `.cleanup/<slug>_cleanup_plan.md`.

**No plan?** Load `notebook-folder-cleanup-planner`, let it inventory and triage the folder
and write the plan, then **stop**. Report the plan path and what it proposes. Do not clean.
This holds even when the user asked for the whole thing in one go — the planner is fast,
costs no notebook edits, and the plan is what makes the run reversible and reviewable.

**Plan exists but `status: draft` and no decisions file?** The user has not ruled on it yet.
Show the outstanding items and stop. If they respond now, hand back to the planner to record
the decisions properly, then continue.

**Plan exists and is `decided`?** Continue to stage 2.

A user who explicitly says "skip the plan, just do it" is asking you to remove files with no
record of why. Write the plan anyway — it takes one pass — and tell them it is written; then
ask for the one thing you still need, which is their approval of the retire list.

### 2. Merge the plan with the decisions

Read `.cleanup/<slug>_cleanup_plan.md` and `.cleanup/<slug>_cleanup_decisions.md`, and build
the work list by this contract — the planner's `## How the two files merge` section is
authoritative, and this is its short form:

1. **Decisions win over the plan**, always. If a decision looks wrong, say so once and
   follow it.
2. **An ID with no decision defaults to the safe side of its verdict**: `keep` and
   `consolidate`-into-target proceed; **`retire` does not.**
3. **`scope: all`** in the decisions frontmatter approves every ID, minus any row that
   carves one out. Those rows win over the blanket approval.
4. **An unruled `Q-###` blocks only the items it lists**, not the run.
5. **A decision for an unknown ID is an error, not a guess.** Report it and continue.
6. **`## Additional instructions` apply to the whole run**, after the per-ID decisions.

Then re-verify the plan against reality before acting on it: a plan can be days old.
Confirm every notebook it names still exists at that path, and that nothing new has appeared
in the folder. If it has drifted, refresh the plan through the planner rather than executing
a stale one.

Confirm the working tree is clean (`git status --porcelain`). If it is dirty, say so and
offer to stop — an un-committed change plus a bulk move is unrecoverable without a stash the
user didn't ask for.

Print the resolved work list — what will be retired, consolidated, migrated, reformatted,
and what was skipped for want of a decision — then proceed.

### 3. Retire the approved set

```bash
mkdir -p "archive/<original relative path>"
git mv "<folder>/<nb>.ipynb" "archive/<original relative path>/<nb>.ipynb"
```

Use `git mv` so history follows the file. Append a row per notebook to
`archive/RETIRED_MANIFEST.md` (create it if absent):

```markdown
| Date | Notebook | From | Reason | Superseded by | Plan |
| --- | --- | --- | --- | --- | --- |
| 2026-09-04 | 4.4_Chains_Scratch.ipynb | 02_.../04_Chains/ | 3 cells with saved tracebacks, TODO on core path | 4.2_Advanced_Chains.ipynb | 04_Chains NB-007 |
```

The `Plan` column is the link back to the evidence and to the decision that approved this —
`.cleanup/<slug>_cleanup_plan.md` plus its `_decisions.md`. The manifest says *what* was
retired; the plan says why it was the right call and who agreed.

The manifest is the whole reason this is reversible — a move with no recorded reason is a
deletion with extra steps.

### 4. Migrate the libraries

Work the approved `MIG-###` items. The plan already recorded the old API, the new one, and
the rewrite-vs-repoint call per notebook — apply that, don't re-derive it. If a notebook
turns out to need a migration the plan never listed, add it to the plan as a new ID and
carry it as unapproved work: report it, don't silently do it.

Per retained notebook, in this order:

1. **LangChain/LangGraph** — from the scanner output, applying
   `langchain-v1-migration-audit/references/v0-to-v1-rewrite-map.md`. Honour the
   repoint-vs-rewrite distinction: a notebook whose *subject* is the legacy API keeps it,
   repointed at `langchain-classic` and labelled.
2. **Everything else** — `references/library-migration-map.md` (pandas, NumPy, scikit-learn,
   PyTorch, TF/Keras, CrewAI, AutoGen).

**Check the pin before every rewrite.** `requirements.txt` holds 172 resolver-verified pins
and 18 are deliberately below latest; CrewAI is deliberately excluded and installs from its
own per-folder file. Code matching an intentional pin is correct — record it, don't "fix" it.

Never edit `pyproject.toml` / `requirements.txt` / `requirements.lock.txt` as part of a
cleanup. If a migration needs a new package, stop and say so.

Two things that make a migration real rather than cosmetic:

- **Update the narrative with the code.** Markdown explaining `df.append` beside
  `pd.concat` code is worse than either alone.
- **Flag behaviour changes.** If the replacement changes numbers (`normalize=` →
  `StandardScaler`), say so in the notebook.

### 5. Reformat

Load the `Format_Python_Notebook` skill and apply it to every retained notebook: title cell
(H1 + emoji + Learning Objectives + Prerequisites), `---` before each `##` section, one
emoji per section heading, the 3-line banner on every code cell, grouped imports,
confirmation prints, `## 📝 Summary` + `### Next Steps`, cleared outputs.

Validate mechanically:

```bash
python .claude/skills/plan-to-teaching-notebook/scripts/md_to_notebook.py "<nb>.ipynb" --check
```

Every line it prints names the format rule broken. Use `NotebookEdit` for the edits — never
hand-edit notebook JSON.

### If you must script a bulk edit

`NotebookEdit` needs a `cell_id`, and older notebooks in this repo have none. When a change is
mechanical enough to script across many files (a verified import-path swap, say), a
`json.load`/`json.dump` round-trip is defensible — but **it will wreck the diff unless you
preserve the file's existing serialization**:

```python
# indent: sniff what git already has, do NOT hardcode. Notebooks in this repo
# are a mix of indent=1 and indent=2; rewriting at the wrong one turned four
# real edits into ~15,700 changed lines across three files.
indent = len(line2) - len(line2.lstrip(" "))     # from `git show HEAD:<path>`

# newline="": json.dump into a text-mode file on Windows emits CRLF for every
# line, churning the whole working tree.
with open(path, "w", encoding="utf-8", newline="") as fh:
    fh.write(json.dumps(nb, indent=indent, ensure_ascii=False) + "\n")
```

Then verify before moving on: cell counts unchanged per file, `git diff --stat` proportional to
the number of real edits, and the notebooks still parse as valid nbformat. Two known-benign
round-trip effects: duplicate JSON keys collapse (invalid JSON, last-wins — this repairs the
file), and key order normalises.

**Never let a scripted pass touch cells tagged `langchain-0x-contrast`** — those hold 0.x code
on purpose, and "fixing" them destroys the lesson.

### Verify with a different pattern than you fixed with

The single most expensive mistake in a scripted pass: writing a narrow regex, applying it, then
"verifying" with the same regex. It always reports success, because it is asking the same
question that produced the edit.

A real case from this repo: a pass stripped version pins matching `!pip install …==`, then
verified with that pattern and logged "0 pinned lines remain". A `# pip install -qq torch==2.7.1`
line — no `!` — sat one cell later in the same file and was reported clean. The reviewer found it
by enumerating *every* `pip install` line regardless of form.

So: **fix with the specific pattern, verify with the general one.** Enumerate the whole
category (every `pip install` line, every import, every path-looking string), print what
survives, and read the list. A verification that can only say "yes" is not a verification.

This mistake recurs. It happened twice in one session on the same folder: first with pip pins
(fix matched `!pip install …==`, missed `# pip install …==`), then immediately again with
personal filesystem paths — the sweep matched `/Users/`, `/home/` and `C:\Users\` but never
`~/`, which is exactly how IPython renders a traceback for a path under `$HOME`. 50 leaked
path occurrences survived a sweep that reported zero. **When sweeping for a class of string,
enumerate the shapes it can take before writing the pattern**, and include the abbreviated,
environment-variable and Windows forms:

```python
PERSONAL = re.compile(r"[A-Za-z]:\\+Users\\+[^\\\"]+|/Users/\w|/home/\w"
                      r"|~[/\\]Documents[/\\]|%USERPROFILE%[/\\]|\$HOME[/\\]")
BENIGN   = re.compile(r"~[/\\]\.cache[/\\]")   # keep generic cache paths
```

Add a **liveness check** to any sweep that reports zero: assert that something you *expect*
to match still matches (a known-benign hit), so a dead regex cannot masquerade as a clean
result.

One more shell-specific trap: write these patterns in a **script file**, never in a
`bash -c` string or heredoc. Backslashes and `$HOME` get eaten by the shell before Python
sees them — this session produced a literal backspace byte, a literal `0x01` byte, and an
expanded `$HOME` that way, each time inside a regex that then silently matched nothing.

The same applies to the scanner's own rules — a task's acceptance criterion of "scanner reports
no findings" passes vacuously when the rule is narrower than the task's stated objective.

### 6. Review

For each substantially changed notebook, spawn a **fresh subagent** (`Agent` tool,
`subagent_type: "general-purpose"`) running `notebook-review`. Its Gate 4 is exactly the
formatter compliance check, and Gate 2 catches migrations that parse but are wrong. Nothing
is executed, so a review round costs no API calls. Apply blockers, re-review, **max 3
rounds**; after that, report the unresolved findings rather than forcing it through.

### 7. Report

Cite the plan ID beside every item, so the report and the plan can be read against each
other. Structure it as:

1. **Retired** — ID, notebook, reason, archive path. Presented as reversible: give the
   `git mv` needed to restore any one of them.
2. **Consolidated** — kept vs retired, and exactly what content was ported across.
3. **Migrated** — per notebook, per library: old API → new API, with cell references.
   Separate "changed" from "already current" from "left alone because the pin says so".
4. **Reformatted** — which rules were violated before, and the `--check` result after.
5. **Reviewed** — rounds and verdict per notebook; anything still unresolved.
6. **Skipped for want of a decision** — every ID that was planned but had no approval,
   named individually. This section is the point of the whole two-file design: it is how
   the user sees what is still waiting on them. Never fold it into "not done".
7. **Not done** — anything you deliberately left, and why.

Then close the loop on the plan: set its frontmatter `status: applied`, append a
`## Changelog` row with the date and a one-line summary of the run, and leave every unruled
ID exactly as it was so the next round can pick it up.

Report failures as plainly as successes. A cleanup that overstates itself is worse than one
that stops early, because the next person trusts it.

## When to use something else instead

| Situation | Use |
| --- | --- |
| You only want to know what *would* change | `notebook-folder-cleanup-planner` on its own — it writes the plan and stops |
| The user is answering an existing plan | `notebook-folder-cleanup-planner`, which records the decisions file; then come back here |
| The folder's only problem is LangChain 0.x, tracked on a board | `langchain-v1-pipeline` (plan → tasks → notebooks → review) |
| The folder also needs pruning, deduplication, non-LangChain migrations or reformatting | **this skill** |
