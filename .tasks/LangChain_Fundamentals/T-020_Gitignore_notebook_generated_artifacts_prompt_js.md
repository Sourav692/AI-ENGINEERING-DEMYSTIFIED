---
id: T-020
title: Gitignore notebook-generated artifacts (prompt.json / prompt.yaml)
type: migration
status: done
review: approved
review_rounds: 2
wave: 5
effort: S
disposition: rewrite
plan: .plan/LangChain_Fundamentals_langchain_v1_plan.md
targets: [02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/prompt.json, 02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/prompt.yaml, .gitignore]
rules: []
depends_on: []
output: .gitignore + untracked prompt.json/prompt.yaml
created: 2026-09-05
updated: 2026-09-05
---
- [x] **Gitignore notebook-generated artifacts (prompt.json / prompt.yaml)** — `done` · review: ✓ approved · round 2

## Objective

prompt.json and prompt.yaml are notebook-generated artifacts COMMITTED to the repo (in dad1931) and absent from .gitignore, so anyone running 2.2 gets spurious diffs. Two parts: add a .gitignore rule, and decide whether to git rm the two tracked files. prompt.yaml is now ORPHANED - after T-018 no cell writes YAML, because dumps is JSON-only. Deleting tracked files is destructive so it needs a human yes; the .gitignore line alone does not untrack them.

## Scope

Files in scope:

- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/prompt.json`
- `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/prompt.yaml`
- `.gitignore`

Findings this task closes: _n/a_

## Steps

- [x] Confirm both files are tracked (`git ls-files`) and identify what still writes them
- [x] Establish `prompt.yaml` is orphaned — after T-018 no cell writes YAML (`dumps` is JSON-only)
- [x] Check for filename collisions repo-wide before choosing rule shape (none: these two only)
- [x] Record HEAD blob hashes so both files stay recoverable by exact hash
- [x] Add path-anchored `.gitignore` rules (not bare filenames) with a comment saying why
- [x] Untrack with `git rm --cached` — reversible, leaves both files on disk
- [x] Verify: 0 tracked, both still on disk, `check-ignore` matches, no `??` noise in status
- [x] Verify the rule is neither dead nor over-broad (collateral + negative-control test)

## Acceptance criteria

_The first three are the board's stock notebook criteria and do not apply: this
task touches no notebook. Restated below as what actually needs to hold._

- [x] ~~Scanner re-run~~ → n/a; no notebook in scope. `.gitignore` is not scanned.
- [x] ~~Narrative matches code~~ → n/a; replaced by: the ignore rule carries a
      comment explaining why the files are generated, not authored
- [x] ~~`static_check.py` parses every cell~~ → n/a; replaced by: `git check-ignore`
      proves the rule is live, and a collateral test proves it is not over-broad
- [x] Both files untracked but still present on disk (reversible, non-destructive)
- [x] Recovery path recorded (HEAD blob hashes) before any index change
- [x] **Approved by `notebook-review`** (`review: approved`) — required to close

## Notes / log

### Survey

- Both files were tracked: `git ls-files` returned each of them.
- Only `prompt.json` is still written by any cell — `2.2_Prompt_Templates.ipynb`
  cell 23 (`dumps` → `Path("prompt.json").write_text`), read back in cell 24.
- **`prompt.yaml` is fully orphaned.** T-018 replaced `.save()` with `dumps`, which
  is JSON-only, so no cell writes YAML any more.
- Nothing else in `02_Inputs_Outputs_Prompts/` needed untracking. That folder holds
  the six `2.x` notebooks and these two artifacts — **and nothing else**; it has no
  `images/` subfolder. Widening to the whole `LangChain_Fundamentals/` tree, the
  eleven other tracked non-notebook files are all authored inputs or assets, none
  of them cell-generated:

      05_Summarization/apjspeech.pdf              Docs/prompt_engineering.pdf
      05_Summarization/app.py                     LangChain_v0_vs_v1_Differences.md
      Docs/Build an Intelligent Travel Assistant AI.pdf   README.md
      Docs/Ecommerce_Product_List.csv             Reference_Links.md
      images/{image1,image2,sqllite}.png

  (`Chinook.db`, used by `3.1_LCEL_Introduction.ipynb`, is generated but already
  untracked and already covered by the pre-existing `*.db` rule.)

  **Correction.** An earlier draft of this bullet named the three PNGs as living in
  `02_Inputs_Outputs_Prompts/images/`. They do not — they are one level up, at
  `LangChain_Fundamentals/images/`, and that folder has no `images/` dir at all.
  The survey's *conclusion* (nothing else needs untracking) held up under
  independent re-derivation; the sentence describing it named the wrong scope and
  an incomplete file list. Logged rather than silently edited, because the failure
  mode — reporting a survey result whose stated scope does not match what was
  actually surveyed — is the same one that let 50 leaked `~/` paths through earlier
  in this migration.

### A finding the task description did not anticipate

Both committed files are **old `.save()` output**, not what the notebook writes now.
The tracked `prompt.json` has top-level keys
`['_type', 'input_variables', 'metadata', 'name', 'optional_variables',
'output_parser', 'partial_variables', 'tags', 'template', 'template_format',
'validate_template']` — the flat legacy shape. `dumps()` writes an
`{lc, type, id, kwargs}` envelope instead; the check for that envelope on the
tracked file returned `False`.

So these were not merely stale-on-next-run. They were committed examples of the
exact deprecated serialization format T-018 removed from the lesson — a learner
inspecting the checked-in file would have seen the old API's output while the
notebook beside it taught the new one. That strengthens the case for untracking
rather than refreshing them.

### Decisions

1. **Path-anchored rules, not bare `prompt.json`.** A bare filename would ignore
   any file of that name anywhere in the repo. Checked first: `git ls-files`
   matching `(^|/)prompt\.(json|yaml|yml)$` returned these two and nothing else,
   so a bare rule would have been safe *today* and a trap later. Anchored instead.
2. **`git rm --cached`, not `git rm`.** Untracks while leaving both files on disk.
   Reversible; nothing is destroyed in the working tree.
3. **Residual gap the anchored rule does not close: CWD.** The cell writes
   `Path("prompt.json")`, which is relative to the *kernel's* working directory.
   Under Jupyter and VS Code that is the notebook's own folder, so the rule fires.
   Run the notebook with a different CWD — papermill or a CI job invoked from the
   repo root, or `jupyter lab` with `notebookFileRoot` overridden — and the file
   lands somewhere the anchored rule does not cover, reappearing as `??`. Accepted
   rather than fixed: a bare `prompt.json` rule would cover every CWD but ignore
   unrelated files repo-wide, and making the cell write an absolute path would add
   noise to a lesson about prompts. If this ever bites, the fix is to widen the
   rule, not to loosen it to a bare filename.
4. **`prompt.yaml` left on disk despite being orphaned.** It is now untracked and
   ignored, so it is invisible to git and costs nothing. Deleting a file from the
   user's working tree was not asked for and is not needed to close this task.
   It is nonetheless a dead file: nothing writes it, nothing reads it, and the
   notebook now says outright that YAML has no 1.x equivalent. To clear it:

       rm "02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals/02_Inputs_Outputs_Prompts/prompt.yaml"

   Recoverable afterwards from blob `ba91880` (see Recovery below).

### Recovery

Both blobs are preserved in history. Exact handles, captured before touching the index:

    prompt.json  f745de577aef36701508275a9e2eaa5f0ad62e5e
    prompt.yaml  ba91880832c5ca651add8a9690c0018dc02205f7

    git show f745de5 > prompt.json      # or: git show HEAD:<path>
    git checkout HEAD -- <path>         # fully restores tracking

### Staging

The `.gitignore` edit and the two index deletions must land in the **same** commit.
Committing the deletions alone would untrack both files while leaving no rule to
ignore them, so they would immediately return as `??` — precisely the noise this
task removes. All three are staged together:

    M  .gitignore
    D  .../02_Inputs_Outputs_Prompts/prompt.json
    D  .../02_Inputs_Outputs_Prompts/prompt.yaml

`.gitignore` was also normalised to CRLF across all 31 lines. The file was CRLF
throughout; the appended block arrived as LF, leaving it mixed. The diff is now
additions-only apart from one `-*log` / `+*log` pair, which is the append
supplying a trailing newline the file had been missing at EOF.

### Verification

    tracked after change ......... 0 (was 2)
    on disk ...................... both present, unmodified
    check-ignore ................. .gitignore:30 and :31 match
    git status --porcelain ....... three staged entries and no others — the two
                                   `D` index deletions plus `M .gitignore`
                                   (see Staging above); no `??` lines anywhere,
                                   so the ignore rule is doing its job

Liveness and breadth test — the rule must fire on the real paths and *not*
elsewhere. Verified `04_Retrieval_and_RAG/prompt.json`, `13_Projects/prompt.yaml`
and a root-level `prompt.json` are all **not** ignored, while `.env` (negative
control, a known-ignored path) and the real target both **are**. This is the
"fix with the specific pattern, verify with the general one" check that the
personal-paths sweep earlier in this migration failed to do.

### Review

Two rounds, independent reviewer, no execution.

**Round 1 — CHANGES_REQUESTED, one blocker.** The Survey's claim that
`images/image1.png`, `image2.png`, `sqllite.png` sat in `02_Inputs_Outputs_Prompts/`
was false: that folder has no `images/` subfolder, the PNGs are one level up, and
the list omitted eight further tracked non-notebook files. Conclusion held,
description of scope did not. Plus four nits — `.gitignore` unstaged while the
deletions were staged, mixed CRLF/LF, unstated CWD sensitivity, and "delete by
hand" where a concrete command belonged. All five addressed.

**Round 2 — APPROVED.** The reviewer independently re-derived every fix and ran
the check that could have falsified the load-bearing claim: a repo-tree grep for
`%%writefile|to_csv|savefig|write_bytes|.write(` across every notebook in
`LangChain_Fundamentals/` returned nothing. That mattered specifically for
`05_Summarization/app.py` — a Streamlit app is exactly the sort of file a notebook
cell emits via `%%writefile`, which would have made it a missed artifact. It does
not; it is authored. `apjspeech.pdf` is read by `8.1_Text_Summarization.ipynb`,
never written. So the eleven other tracked non-notebook files really are inputs,
and this task has no gap. One closing nit — a stale "only the two staged
deletions" line in Verification, contradicting the new Staging section — fixed
before close.

### Not done here

`pre-commit install` still has to be run once per clone before the nbstripout hook
does anything. Committed config alone is inert. Out of scope for this task.
