# Module brief template (for delegating one module to a subagent)

For repos with many modules, do the first module yourself (it becomes the worked reference), then
give each remaining module to a subagent with this brief — filled in, saved as a file, and pointed
to from a short prompt ("read your brief at <path> and follow it exactly"). Run modules **one at a
time** when they share a working tree and a `main` branch (they touch shared docs; parallel
branches collide). After each hand-back: verify the merge yourself, harvest its "Lessons for the
skill", and append the relevant ones to the brief before the next module.

---

You are cleaning up ONE module of the notebook course repo at {REPO_PATH}
Module: {MODULE_DIR}   (branch: cleanup/module-{NN}-{SLUG})
Extra notebooks belonging to this module: {EXERCISES_SOLUTIONS_OR_NONE}

Follow the skill `{SKILL_PATH}/SKILL.md` exactly (read it first, plus `references/notebook-format.md`
and `references/pitfalls.md`). The reference module is {REFERENCE_MODULE}: read its
`.tracker/modules/<module>/plan.md`, and open {EXEMPLAR_NOTEBOOKS} — the user's exemplars of the format.

Decisions already made by the user (do not ask again):
- Autonomy: {write plan.md and proceed | wait for approval}.
- Approved audit recommendations for this module (from `.tracker/audit.md`): {AUDIT_ITEMS — consolidations,
  stale fixes, renames; plus rejected ones not to re-propose}.
- LLM: every chat model goes through `{FACTORY_IMPORT}` → `{FACTORY_CALL_WITH_EXPLICIT_MODEL}`. Setup cells
  load keys with `{ENV_LOADING_LINE}`. Exceptions: {PROVIDER_DEMOS_POLICY}; {RAW_API_POLICY};
  {FRAMEWORK_FREE_NOTEBOOKS_POLICY (e.g. "from scratch" notebooks keep the raw SDK on the same model)}.
- Cost: {COST_POLICY — what to shrink, what to tag skip-execution + gap}.
- Landing: one branch per module → PR → merge ({merge commit|squash}) → `git switch main && git pull`.
- Environment rules: {ENV_RULES — package manager, no installs in notebooks, no platform-specific code, library versions}.

Repo facts:
- Run: `{RUN_COMMAND} .../run_notebooks.py <nbs> --report .tracker/modules/{MODULE}/run-report.json`, then
  `report_to_markdown.py` for `run-report.md`. Run with {TRACING_OFF_ENV} if tracing is on.
- Credentials: see `.tracker/environment.md` — working: {LIST}; not working: {LIST} → link the existing repo
  blockers from your gap files instead of filing new ones. Never print key values.
- Checks: {HOW_TO_RUN_CHECKS} ({staged-copy note if applicable}); pre-commit hooks run on commit — no `--no-verify`.
- Shared working tree: others may have uncommitted changes (e.g. {FILES}); stage explicit paths only.
- Optional dependency groups: {GROUPS_AND_HOW_TO_SYNC}.
- Docs to keep in sync: {MODULE_README, COURSE_TABLE_DOC, INVENTORY_CSV, …}.
- Commit trailers / PR footer: {ATTRIBUTION_LINES}.

Tracker (local, git-ignored — never stage it): update `.tracker/progress.md` (your row), `modules/{MODULE}/plan.md`,
`run-report.md` (+json), `blockers/{MODULE}--<slug>.md`, `gaps/{MODULE}--<slug>.md` (skeletons in SKILL.md).
The PR body must carry the plan summary, the run table and one line per blocker/gap, since the tracker isn't committed.
Don't commit while a notebook run is in progress (pre-commit stash race).

Definition of done: every notebook runs clean end to end in a fresh kernel, or its failing/skipped cells are
covered by a blocker/gap file; each notebook's output actually shows what its prose claims; checks pass;
self-check reports no undefined names; no stale references anywhere in the repo; PR merged; local main pulled.

Lessons accumulated from earlier modules:
{APPEND_LESSONS_HERE}

Do not edit the skill files. Final message: PR URL, notebooks before→after, run table, blockers/gaps (one
line each), surprises, and "Lessons for the skill" (only lessons not already listed). Under 60 lines.
