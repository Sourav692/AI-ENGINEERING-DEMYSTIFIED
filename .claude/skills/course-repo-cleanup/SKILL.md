---
name: course-repo-cleanup
description: Audit and clean up an AI Engineering Demystified course repo (or any notebook-based course repo). First a read-only audit report (self-containment, duplicates, stale APIs, consolidation plan) gated on user approval; then module by module — merge notebooks teaching the same concept, make each self-contained, apply one educational format, route every chat model through one LLM factory (AIED default `aied_helpers.get_openai_llm(model="gpt-4o-mini")`), run every notebook end to end and fix failures (including demos that run but don't show what they claim), track progress/blockers/gaps in a git-ignored .tracker folder, and land each module via its own branch, PR and merge. Use whenever the user wants to audit, tidy, deduplicate, restructure, standardize, "make executable" or verify the notebooks of an ai-engineering-demystified-* or other course/workshop repo (audit-only requests included), wants a consistent teaching format, or says "do the same cleanup for this repo". Works for a whole repo or for one module or folder.
---

> **Paths:** `<skills-root>` means the folder that holds this skill — the parent of its base directory (e.g. `~/.claude/skills`, or a repo's `.claude/skills`). Sibling skills referenced below live there too.

# AIED notebook course cleanup

Goal: every notebook in the repo **teaches one concept, follows one educational format, runs top to
bottom on its own in a fresh kernel, and visibly demonstrates what its prose claims**. Audit the whole
repo read-only first (§0); after the user approves, work module by module — each module lands through
its own branch → PR → merge before the next one starts.

"Ran clean" is not the finish line. The most common defect is a notebook that executes without error
while its output contradicts (or fails to show) what the markdown says — read outputs, not just exit codes.

## 0. Audit first (read-only, approval gate)

Before any branch, edit or notebook run, audit every notebook under `modules/` (plus `exercises/`,
`solutions/`) by static analysis and write `.tracker/audit.md`, following `references/audit.md`:
self-containment, exact/semantic/partial duplicates vs intentional reinforcement, stale APIs (verified
against docs and the pinned versions — never guessed), consolidation proposals with priorities, the
proposed final structure, and an implementation plan. No notebook changes, no executed notebook code,
no LLM/API calls (so no `check_credentials.py` yet).

Present the summary together with the §1 questions, then **stop until the user explicitly approves**.
Approved recommendations seed each module's `plan.md`; rejected ones are not re-proposed. If the user
asked only for an audit, the report is the deliverable — finish here.

## 1. Settle the parameters (ask once, together, before touching anything)

Start from the AIED house defaults below, infer what you can from the repo (`pyproject.toml`,
`README.md`, `.env.example`, folder layout, existing `.tracker/README.md`), then ask the user **one**
batch of questions for whatever is still open or where the repo contradicts a default. Write the
settled values into `.tracker/README.md`.

| Parameter | AIED default | Notes |
|---|---|---|
| Module folders and order | `modules/NN_*` in numeric order, plus matching `exercises/`, `solutions/` | one branch + PR each |
| LLM factory + model | `from aied_helpers import get_openai_llm` → `get_openai_llm(model="gpt-4o-mini")` | always pass the model explicitly (the factory's default differs) |
| Shared package | `aied-helpers @ git+https://github.com/Sourav692/ai-engineering-demystified-shared.git@<tag>` in `pyproject.toml` | if missing, add it with `uv add` and `uv sync` — don't vendor a copy |
| Environment | `uv` only, one root env, LangChain 1.x, keys in project-root `.env` | no `!pip install`, no Colab/Kaggle code in notebooks; 0.x agent APIs → `langchain_classic` |
| Format reference | exemplar notebooks the user names, else the `format-notebook` skill (`<skills-root>/format-notebook/SKILL.md`) | see §3 |
| Autonomy | after the §0 audit is approved: write `plan.md` per module and proceed | the audit gate always applies; ask per module only if the user wants approval |
| Cost policy | shrink expensive demos; tag `skip-execution` only what can't be shrunk (+ gap file) | end-to-end runs call paid APIs |
| Landing | `cleanup/module-NN-<slug>` → PR → merge → `git switch main && git pull` | before the next module branches |
| Model-switch exceptions | provider-comparison demos, provider-only APIs, "from scratch" notebooks (raw SDK, same model) | keep them, on the standard model where possible |
| Notebook outputs | **committed**, from one clean scripted run: `nbstripout --keep-output --keep-count` pre-commit hook + a staged-copy check (counts 1..n, no errors, no key-like strings, no workstation paths, ≤ 2 MB); no nbstripout git filter | learners read results on GitHub without keys; set up with a `python-repo-env`-style skill (its step 8) |
| Tracker | `.tracker/` is **local only** — added to `.gitignore`, never committed | PR bodies carry the summaries instead (§4) |
| Retired notebooks | `git rm` (history keeps them) | if the repo keeps an `archive/` folder (its `CLAUDE.md` says so): `git mv` to `archive/<original-path>/` and add a row to `archive/RETIRED_MANIFEST.md` (columns: Date, Notebook, From, Reason, Superseded by, Plan) |
| Unavailable provider in an optional demo | ask: swap to a provider that works here (e.g. Databricks `system.ai.*` via `get_databricks_llm`), or keep it skipped + gap | never leave it failing |

If the repo still strips outputs with an nbstripout git filter (`.gitattributes` `filter=nbstripout`), switch it to the committed-outputs setup in the first module's PR (confirm with the user first).

## 2. Bundled tooling

| Path | Use |
|---|---|
| `scripts/check_credentials.py [--markdown]` | one cheap authenticated call per key in `.env` (values never printed); flags wrong-provider keys and global tracing switches |
| `scripts/outline_notebooks.py <dir> [--code]` | headings, tools, API/graph signals per notebook, each line tagged with its cell number `[cN]` — raw material for the audit and the overlap table |
| `scripts/run_notebooks.py NB... [--timeout S] [--report r.json]` | executes each notebook in its own folder on a fresh kernel; honours the `skip-execution` tag; writes outputs to the working copy |
| `scripts/report_to_markdown.py r.json --title "Module NN"` | JSON report → `run-report.md` |
| `scripts/selfcheck_notebooks.py <dir>` | names a notebook uses but never defines (static self-containment check; needs `ruff`) |
| `references/audit.md` | the §0 read-only audit: rules, checks, report sections A–F, approval gate |
| `scripts/scan_langchain_v1.py <dir> [--json] [--min-severity S]` | finds LangChain 0.x patterns that break or are legacy on 1.x (read-only) |
| `references/langchain-v1-migration.md` + `references/langchain-v1-rewrite-map.md` | how to judge scanner hits in teaching notebooks, and the 0.x → 1.x rewrite rules |
| `references/library-migration-map.md` | deprecations for the rest of the stack (pandas, NumPy, scikit-learn, PyTorch, TensorFlow, CrewAI, AutoGen) |
| `references/pitfalls.md` | what went wrong in practice, by step — **read the matching section before each step** |
| `references/module-brief-template.md` | brief for delegating one module to a subagent |

Run scripts with the repo's interpreter: `uv run python <skills-root>/course-repo-cleanup/scripts/<script>`.

## 3. The format reference

If the user names exemplar notebooks (in this repo or another), open them and derive the format:
skeleton (title, objectives, where-this-fits, prerequisites, setup, LLM init, parts, summary, next
steps), cell conventions (banner comments, a printed result per cell, markdown that reads the output)
and tone. Write that list into `.tracker/README.md` as this repo's format. Otherwise use the
`format-notebook` skill (`<skills-root>/format-notebook/SKILL.md`) — the single owner of the
educational format, derived from AIED exemplars and repo-agnostic. Install it next to this skill.
Restructure *around* existing good explanations — don't rewrite prose that already works.

## 4. Tracker (local, git-ignored)

```
.tracker/
  README.md                         parameters, the format, conventions
  environment.md                    credential check results (check_credentials.py --markdown)
  progress.md                       one row per module: branch, notebooks before→after, run result, blockers, gaps, PR
  modules/<module>/plan.md          overlap table, new structure, what moved where, content bugs fixed
  modules/<module>/run-report.md    final run (+ run-report.json)
  blockers/<module|repo>--<slug>.md could not be made to run here
  gaps/<module>--<slug>.md          deliberately not run/verified (skipped cells, missing credentials, interactive paths)
```
Skeleton for blockers and gaps:
```markdown
# <short title>
- **Status**: open | resolved (<date>, how — or "closed by decision: <why>")
- **Module / notebook**: <module> / `<file>` (cell N / Part N)
- **Symptom**: <error text or what is missing>
- **Tried**: <what was attempted and why it didn't work>
- **Next step**: <what the user needs to do / decide>
```
- Repo-wide problems (a rejected key, missing cloud credentials, an exhausted quota) get one
  `repo--<slug>.md` blocker; module gap files link to it.
- Add `.tracker/` to `.gitignore` in the first module's PR. If the repo already tracks `.tracker/`,
  `git rm -r --cached .tracker` (files stay on disk; history is left alone).
- Because the tracker isn't committed, each **PR body** carries the module's plan summary, run table
  and a one-line list of its blockers/gaps — that is the durable record.
- When the user fixes something (new key, credentials) or decides to accept it, mark the blocker
  `resolved` with the date and how, update `environment.md` and the module's `progress.md` counts,
  and re-run the affected notebook when a fix makes that possible — confirm the output shows the
  thing the gap said was never seen before closing a gap.

## 5. Preflight (once per repo)

1. `git status` clean on an up-to-date `main`; note other people's uncommitted work.
2. Environment works: `uv sync`; `aied_helpers` imports; notebooks' imports resolve. If not, fix the
   environment first (a `python-repo-env`-style skill, if present).
3. `check_credentials.py --markdown` → `.tracker/environment.md`. File repo blockers for anything rejected.
4. **Tracing off for bulk runs**: if `.env` enables LangSmith/LangChain tracing, run with
   `LANGSMITH_TRACING=false LANGCHAIN_TRACING_V2=false` in the environment (`load_dotenv` doesn't
   override variables already set); never make tracing a notebook requirement.
5. Note how the repo's checks/pre-commit hooks read files (disk vs staged copy), and that outputs
   are committed: the output check must pass on every notebook you stage.

## 6. Per-module workflow

1. **Branch** `cleanup/module-NN-<slug>` off updated `main`. Stage explicit paths only, ever.
2. **Inventory** with `outline_notebooks.py` (include exercises/solutions), plus `scan_langchain_v1.py` for LangChain 0.x hits (`references/langchain-v1-migration.md`) and `references/library-migration-map.md` for other deprecated APIs; scan for hard-coded secrets (remove, report for rotation); then read notebooks in full — code and graph edges decide what a notebook teaches, not headings. Include duplicates across modules.
3. **Plan** a concept × notebook table, starting from the approved audit recommendations for this module; decide keep / merge / move / delete / rename; one concept per notebook, in teaching order. Write `plan.md`, noting any departure from the approved audit and why.
4. **Consolidate** with a re-runnable script (restore sources from `HEAD` first) that copies existing cells and writes with `nbformat`; `git mv` first, then write over the moved file; `git rm` deletions.
5. **Format** every notebook (§3); name the next notebook by file name; remove stale numbering schemes.
6. **Standardize the LLM** to the chosen factory + explicit model; `load_dotenv(find_dotenv(usecwd=True))` in the setup cell; update prerequisite key names.
7. **Self-containment**: `selfcheck_notebooks.py` reports no undefined names.
8. **References**: search every tracked text file (`git ls-files`) for old names *and* for descriptions of behaviour you changed; finish with a search that returns nothing.
9. **Run** the module (`run_notebooks.py`, tracing off). Fix failures and re-run the affected notebook. Shrink before skipping; tag only what can't be shrunk; file a gap/blocker for anything left — never a silent failure. Optional demos that catch their own exceptions "pass" even when they fail: read their printed output.
10. **Make each demo prove its point** (`references/pitfalls.md` §1–2): gates show both outcomes, judges are per-criterion with code-computed verdicts, "A beats B" is checked against ground truth over samples, loops are capped, timing claims are measured. Fix the demo or the prose until they agree, then re-run.
11. **Verify**: repo checks/tests pass (stage first if they read the staged copy).
12. **Track**: `run-report.md`, `progress.md` row, blocker/gap files.
13. **Land**: the module's notebooks carry the outputs of their final clean run (re-run any notebook edited after it — stale outputs next to changed code mislead learners; never commit outputs from a half-run IDE session); commit explicit paths, push, PR (plan summary, run table, blockers/gaps), merge, `git switch main && git pull`; confirm no leftover branches. **Don't commit while a notebook run is in progress** — the pre-commit hook stashes unstaged changes, and a runner that reads/writes notebooks in that window silently reverts your edits.

For many modules: do the first yourself as the worked reference, then delegate one module at a time
with `references/module-brief-template.md` (sequentially — modules share `main` and docs). After each
hand-back, verify the merge and fold new lessons into the brief.

## 7. Finish

1. Final full run of every notebook from `main` (fresh kernels, tracing off, heavy notebooks last).
2. `progress.md` totals: notebooks before → after, passing, skipped cells, open blockers/gaps.
3. Report to the user: per-module results, what needs their action (open blockers, keys to rotate),
   and what was deliberately not run (gaps). Offer to fold new lessons into this skill's
   `references/pitfalls.md`.
