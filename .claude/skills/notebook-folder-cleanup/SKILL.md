---
name: notebook-folder-cleanup
description: >-
  Cleans and modernizes a folder of Jupyter notebooks end to end — retires dead-end
  and abandoned notebooks, consolidates duplicate coverage, migrates deprecated library
  APIs (pandas, NumPy, scikit-learn, PyTorch, TensorFlow, CrewAI, AutoGen; LangChain via
  the dedicated audit skill), reformats everything to the Format_Python_Notebook contract,
  and reports what changed and why. Use when the user names a folder and asks to "clean
  up", "organize", "tidy", "deduplicate", "remove dead notebooks", "modernize the
  libraries", or "make these notebooks production/enterprise grade". Retires notebooks by
  moving them to `archive/` with a manifest — never deletes — and requires explicit
  approval before any file moves.
---

# Notebook Folder Cleanup

Takes one folder and returns a clean, non-redundant, current, consistently formatted set of
notebooks — plus a report of every removal, consolidation and code change.

This skill **composes** the others rather than reimplementing them:

| Need | Skill it delegates to |
| --- | --- |
| LangChain/LangGraph 0.x → 1.x | `langchain-v1-migration-audit` (its scanner + rewrite map) |
| Formatting contract | `Format_Python_Notebook` |
| Independent sign-off | `notebook-review` |
| Where a notebook belongs in the roadmap | `ai-roadmap-organizer` |

Only the triage (dead-end / duplicate) logic and the non-LangChain deprecation map
(`references/library-migration-map.md`) are its own.

## Two rules that are not negotiable

**1. Retire, don't delete.** `CLAUDE.md` documents `archive/` as the home for retired
notebooks. A "dead-end" judgment is a *guess about intent* made from the outside, and
guesses about someone's learning material should be reversible. Move to
`archive/<original-path>/`, write a manifest row, never `rm`.

**2. Nothing moves without explicit approval.** Stage 2 stops and shows the triage table.
This is the one blocking checkpoint even when the user asked for full automation — the
`langchain-v1-pipeline` skill can run unattended precisely because it only *adds* files;
this one removes them.

Before any move, confirm the working tree is clean (`git status --porcelain`). If it is
dirty, say so and offer to stop — an un-committed change plus a bulk move is unrecoverable
without a stash the user didn't ask for.

## Process

### 1. Inventory

```bash
python .claude/skills/notebook-folder-cleanup/scripts/inventory.py "<folder>" --json
```

Read-only. Returns per notebook: cell counts, title/summary presence, markdown ratio, empty
and fully-commented cells, syntax-error cells, abandonment markers (TODO/FIXME/scratch
names), saved error outputs, out-of-order execution counts, and a fingerprint (imports,
defined names, called symbols, normalized headings). Then it clusters notebooks by
fingerprint similarity and lists pairs above the threshold.

`dead_end_score` is a **heuristic, not a verdict.** Treat it as a reading order: open the
high scorers first. Then also run the LangChain scanner over the folder, since a notebook's
migration burden is part of the keep/retire decision:

```bash
python .claude/skills/langchain-v1-migration-audit/scripts/scan_langchain_v1.py "<folder>" --json
```

### 2. Triage — and stop

Open every notebook the inventory flags, plus every member of a duplicate pair. Read the
markdown, not just the code: a notebook with two code cells and a long careful explanation
is a lesson, not a stub.

Classify each notebook **keep / consolidate / retire**, and present one table:

| Notebook | Verdict | Evidence | Merge target |

Rules for the judgment the score can't make:

- **Retire** only with positive evidence of abandonment: syntax errors, saved tracebacks
  never fixed, TODO markers on the core path, a title promising content the notebook never
  delivers, scratch identifiers throughout.
- **Never retire for being short.** A focused 6-cell notebook that teaches one thing well is
  the goal, not a defect.
- **Never retire the only coverage of a concept**, however rough — mark it `keep (needs
  work)` and let it become a migration task instead.
- **Consolidate** means: keep the more complete version, port anything unique from the other
  into it, *then* retire the other. Say explicitly what gets ported. A high similarity score
  with genuinely different framings (e.g. LCEL-first vs agent-first) is **not** a duplicate.
- If a notebook is fine but sits in the wrong phase, that is `ai-roadmap-organizer`'s call,
  not a retirement. Flag it, don't move it.

Get approval. Then, and only then, continue.

### 3. Retire the approved set

```bash
mkdir -p "archive/<original relative path>"
git mv "<folder>/<nb>.ipynb" "archive/<original relative path>/<nb>.ipynb"
```

Use `git mv` so history follows the file. Append a row per notebook to
`archive/RETIRED_MANIFEST.md` (create it if absent):

```markdown
| Date | Notebook | From | Reason | Superseded by |
| --- | --- | --- | --- | --- |
| 2026-09-04 | 4.4_Chains_Scratch.ipynb | 02_.../04_Chains/ | 3 cells with saved tracebacks, TODO on core path | 4.2_Advanced_Chains.ipynb |
```

The manifest is the whole reason this is reversible — a move with no recorded reason is a
deletion with extra steps.

### 4. Migrate the libraries

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

Structure the final report as:

1. **Retired** — notebook, reason, archive path. Presented as reversible: give the
   `git mv` needed to restore any one of them.
2. **Consolidated** — kept vs retired, and exactly what content was ported across.
3. **Migrated** — per notebook, per library: old API → new API, with cell references.
   Separate "changed" from "already current" from "left alone because the pin says so".
4. **Reformatted** — which rules were violated before, and the `--check` result after.
5. **Reviewed** — rounds and verdict per notebook; anything still unresolved.
6. **Not done** — anything you deliberately left, and why.

Report failures as plainly as successes. A cleanup that overstates itself is worse than one
that stops early, because the next person trusts it.

## When to use the pipeline instead

If the folder's only problem is LangChain 0.x code and you want plan → tasks → notebooks →
review tracked on a board, use `langchain-v1-pipeline`. Use **this** skill when the folder
also needs pruning, deduplication, non-LangChain migrations, or a formatting pass.
