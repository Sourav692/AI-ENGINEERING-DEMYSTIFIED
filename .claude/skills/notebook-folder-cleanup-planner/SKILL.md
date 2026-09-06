---
name: notebook-folder-cleanup-planner
description: >-
  Plans a notebook-folder cleanup instead of performing one — inventories a folder of
  Jupyter notebooks, triages every file as keep / consolidate / retire, lists the library
  migrations and formatting work each retained notebook needs, and writes it all to
  `.cleanup/<target>_cleanup_plan.md` as a tickable checklist with a stable ID per item.
  When the user then responds to that plan — approving rows, overturning verdicts, adding
  instructions — records their answers in the paired
  `.cleanup/<target>_cleanup_decisions.md`. Use when the user asks to "plan the cleanup",
  "what would you clean up in this folder", "triage these notebooks", "review before you
  change anything", or answers an existing cleanup plan; and always as the first stage of
  `notebook-folder-cleanup`, which reads the plan plus decisions and executes them. Never
  moves, deletes, or edits a notebook — planning and decision capture only.
---

# Notebook Folder Cleanup Planner

Stage 1 of the cleanup pipeline. This skill **reads and writes markdown**; it never touches
a notebook, never moves a file, never runs `git mv`.

```
notebook-folder-cleanup-planner   →  .cleanup/<slug>_cleanup_plan.md
        (user responds)           →  .cleanup/<slug>_cleanup_decisions.md
notebook-folder-cleanup           →  merges both, then executes
```

## Why the plan is a file and not a chat message

A cleanup is the one operation in this repo that *removes* things. The triage table used to
live in a single conversational turn — approve it and it scrolls away, and the reasoning
behind "retire this one" is gone the moment the session ends. Three consequences the file
fixes:

- **The judgment survives.** Six months later, "why is this in `archive/`?" is answerable
  from `.cleanup/`, not from a lost transcript. The `RETIRED_MANIFEST.md` row records *that*
  a notebook was retired; the plan records the evidence that made it the right call.
- **The user can answer at their own pace.** A 40-notebook folder is not a decision anyone
  should make inside one reply. They can edit the decisions file over days.
- **The execution stage becomes resumable and unattended-safe.** `notebook-folder-cleanup`
  no longer needs a human in the loop mid-run, because approval already exists on disk in a
  form it can read.

## Paths

```
<repo root>/.cleanup/<slug>_cleanup_plan.md
<repo root>/.cleanup/<slug>_cleanup_decisions.md
```

`<slug>` is the last path segment of the target, verbatim (`04_Chains` →
`04_Chains_cleanup_plan.md`), with the same two exceptions the `.plan/` convention uses:

- **Generic or repeated segment names** (`01_Foundations`, `LangGraph`, `src`) recur across
  phases — prefix with the owning phase so plans never collide:
  `10_Alternative_Agent_Frameworks__CrewAI__01_Foundations_cleanup_plan.md`.
- **A single file** as target → use the file stem.

The plan and its decisions file are paired **by slug**. `<slug>_cleanup_decisions.md`
belongs to `<slug>_cleanup_plan.md` and to nothing else. Never write a decisions file that
has no plan beside it.

Create `.cleanup/` if it does not exist, and write `.cleanup/README.md` from
`references/cleanup-dir-readme.md` on first use. These files are **tracked in git on
purpose**, exactly like `.plan/` — they are the record of what was removed and why.

## Process

### 1. Scope

Confirm the target path. If the user said "this folder" without naming one, ask — do not
default to the repo root (~500 notebooks; the plan becomes unreadable and the triage
worthless). Reasonable units are one phase or one track.

`archive/` is skipped and stays skipped. It is already-retired content; re-triaging it is
how a retired notebook gets retired twice.

Derive the slug now — you need it in step 4.

**If a plan already exists for this slug**, do not overwrite it. Read it, re-run the
inventory, and *refresh* it: update counts, keep every `- [x]`, keep every recorded
decision, add newly-found notebooks as new IDs, mark vanished ones `(gone)`, and append a
`## Changelog` entry. Renumbering existing IDs breaks the decisions file that points at
them — IDs are permanent once issued.

### 2. Inventory

```bash
python .claude/skills/notebook-folder-cleanup/scripts/inventory.py "<folder>" --json
python .claude/skills/langchain-v1-migration-audit/scripts/scan_langchain_v1.py "<folder>" --json
```

Both are read-only. The first gives per-notebook cell counts, title/summary presence,
markdown ratio, empty and fully-commented cells, syntax errors, abandonment markers, saved
error outputs, out-of-order execution counts, a fingerprint, and similarity clusters. The
second gives the LangChain 1.x migration burden, which is part of the keep/retire decision.

`dead_end_score` is a **heuristic, not a verdict.** Treat it as a reading order.

### 3. Read the notebooks before judging them

Open every notebook the inventory flags, plus every member of a similarity pair. Read the
**markdown, not just the code**: a notebook with two code cells and a long careful
explanation is a lesson, not a stub.

Rules for the judgment the score cannot make:

- **Retire only with positive evidence of abandonment**: syntax errors, saved tracebacks
  never fixed, TODO markers on the core path, a title promising content the notebook never
  delivers, scratch identifiers throughout.
- **Never retire for being short.** A focused 6-cell notebook that teaches one thing well is
  the goal, not a defect.
- **Never retire the only coverage of a concept**, however rough — mark it
  `keep (needs work)` and let it become a migration item instead.
- **Consolidate** means: keep the more complete version, port anything unique from the other
  into it, *then* retire the other. Say explicitly what gets ported. A high similarity score
  over genuinely different framings (LCEL-first vs agent-first) is **not** a duplicate.
- A notebook that is fine but sits in the wrong phase is `ai-roadmap-organizer`'s call.
  Record it as an open question; it is not a retirement.
- **Never plan an edit to a cell tagged `langchain-0x-contrast`** — those hold 0.x code on
  purpose.
- **Never plan an edit to `pyproject.toml`, `requirements.txt` or `requirements.lock.txt`.**
  If a migration would need a new package, that is an open question, not a plan item.

Check the pin before proposing any library rewrite: `requirements.txt` holds resolver-verified
pins and 18 are deliberately below latest; CrewAI is deliberately excluded. Code matching an
intentional pin is correct — record it as `already current (pinned)`, don't plan a "fix".

### 4. Write the plan

Use `references/plan-template.md` verbatim as the structure. Every row carries a **stable
ID** — this is the whole mechanism by which decisions attach to items:

| Prefix | Section |
| --- | --- |
| `NB-###` | one per notebook triage row |
| `DUP-###` | one per consolidation group |
| `MIG-###` | one per library migration item |
| `FMT-###` | one per formatting item |
| `Q-###` | one per open question needing a human answer |

IDs are assigned once and never reused or renumbered, including across refreshes.

Two things every plan must get right:

- **Evidence, not adjectives.** "3 cells with saved tracebacks, TODO on the core path, no
  summary cell" is evidence. "Looks abandoned" is not, and cannot be argued with.
- **Every `retire` row names its superseded-by**, or says explicitly that nothing supersedes
  it. A retirement with no replacement is a content decision the user must make, so it is
  also a `Q-###`.

### 5. Stop and present

Print a compact summary — counts by verdict, the retire list, and every `Q-###` — then the
plan path. **Do not proceed to cleanup, and do not offer to.** Say what happens next:

> Reply with your decisions (approve all, or per-ID), or edit the plan directly. Then run
> `notebook-folder-cleanup` and it will execute what you approved.

### 6. Capture decisions

When the user responds to a plan — in the same session or a later one — write
`.cleanup/<slug>_cleanup_decisions.md` from `references/decisions-template.md`.

One row per ID the user actually ruled on:

| Decision | Meaning |
| --- | --- |
| `approve` | Do what the plan says for this ID |
| `reject` | Do nothing for this ID; the notebook stays exactly as it is |
| `keep` / `consolidate` / `retire` | Overturns the plan's verdict for an `NB-###` row |
| `defer` | Explicitly out of scope for this run; carries to the next refresh |

Rules:

- **Record only what the user actually said.** Never infer approval from enthusiasm, from
  silence, or from a general "looks good" when the plan contains a retirement — see the
  merge defaults below for what an unruled ID means.
- **"Approve all" is a valid, sufficient answer** when the user says it plainly. Record it as
  a `scope: all` header rather than fabricating 40 identical rows, and still list any ID the
  user carved out.
- **Quote the user's own words** in the Note column for any row that overturns a verdict.
  The next reader needs to see it was theirs, not yours.
- **Preserve earlier decisions.** A second round appends and supersedes by ID; it never
  silently rewrites what round 1 recorded. Keep both, newest last, with the round number.
- If the user's instruction does not map to any ID — "also drop the emoji from headings" —
  put it under `## Additional instructions`, verbatim. Do not invent an ID for it.

Then update the plan's frontmatter `status:` to `decided` and print what will happen on
execution: the count of approvals, the retire list as approved, and anything still unruled.

## How the two files merge (the contract execution relies on)

`notebook-folder-cleanup` applies this and nothing else:

1. **Decisions win over the plan**, always, including when the decision looks wrong. If it
   looks wrong, say so once and follow it.
2. **An ID with no decision defaults to the safe side of its verdict**: `keep` and
   `consolidate`-into-target proceed; **`retire` does not.** Silence is never approval to
   remove a file. Report every skipped retirement in the final report.
3. **An unruled `Q-###` blocks only the items that depend on it**, not the run.
4. **A decision for an unknown ID is an error, not a guess.** Report it and continue.
5. **Additional instructions apply to the whole run**, after per-ID decisions.

## What this skill must never do

Move a file. Delete a file. Edit a notebook. Run `git mv`. Write to `archive/`. Touch
`requirements*.txt` or `pyproject.toml`. If the user asks for the cleanup itself, write or
refresh the plan first, then hand off to `notebook-folder-cleanup`.
