# Run 2026-09-05 — LangChain_Fundamentals

- **Target:** `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals`
- **Args:** (defaults — `--max-notebooks 5`, 3 review rounds)
- **Preflight:** `resume_from: stage-1` (no prior plan or board) — full run
- **Plan:** `.plan/LangChain_Fundamentals_langchain_v1_plan.md`
- **Board:** `.tasks/LangChain_Fundamentals/`

## Stage 1 — audit

- 28 files scanned, **17 need work**. 59 BLOCKING / 0 BREAKING / 12 MODERNIZE / 13 INFO.
- Dominant themes: legacy chains (38 findings, 8 files), moved imports (34 findings, 13 files).
- No agent content in this track, so no `create_agent` work — unusually uniform plan.

### Decisions made alone — repoint vs rewrite

Rule applied: does the notebook's title/folder *name* the legacy construct (repoint), or is
the construct a *vehicle* for another lesson (rewrite)?

- `04_Chains/4.0_Basics_of_Chains.ipynb` → **repoint** — folder + headings "Simple Chains",
  "Multi Step Chains"; the chain API is the subject.
- `04_Chains/4.1_Chains_Basics_and_OutputParsers.ipynb` → **repoint** — heading is literally
  "LLMChains & OutputParsers".
- `04_Chains/4.2_Advanced_Chains.ipynb` → **repoint** — same folder; heaviest file (score 46).
- `04_Chains/4.3_Branching_Routing_Merging_Chains.ipynb` → **repoint** — same family.
- `03_LCEL/3.5_Chain_Migrations.ipynb` → **repoint** — inspected: it is *already* a
  before/after migration lesson (headings "Legacy Chains / LCEL / Legacy RAG / LCEL"). Its
  legacy halves are deliberate contrast, not debt.
- `03_LCEL/3.6_Chain_Migration_Advanced.ipynb` → **repoint** — same, for
  `ConversationalRetrievalChain`.
- `05_Summarization/8.0`, `8.1`, `app.py` → **rewrite** — the lesson is summarization;
  map-reduce/refine are summarization strategies, and the chain loaders are just the vehicle.

### Correction logged

- First recorded T-001 as "add `langchain-classic` to the dependency files". **That was
  wrong.** Both `langchain-classic==1.0.8` and `langchain-text-splitters==1.1.2` are already
  pinned in `requirements.txt` with matching floors in `pyproject.toml`; they are simply not
  installed in `.venv`. Corrected in both the plan and T-001. No dependency file needs editing
  — the environment needs syncing.

## Stage 2 — board

8 tasks created. Decomposition rule: one task = one sitting with a single acceptance criterion.

- Grouped the 6 repoint notebooks into **one** task (T-002) — same mechanical change, one
  decision applied across them.
- Split the summarization rewrites (T-005) from the 3.5/3.6 relabel (T-006) — different
  dispositions, different judgment.
- T-001 (`prereq`) left **`todo`**: an unattended run does not change the environment.
  T-002 → T-005 / T-006 / T-008 all depend on it transitively.

### Which concepts became notebooks

- **T-007 — the package split** (~34 import findings across 13 files). No notebook in
  `01_Getting_Started/` covers it (1.0–1.7 are provider/setup lessons). → **new notebook**
- **SKIPPED — "Chains → LCEL" explainer.** `03_LCEL/3.5_Chain_Migrations.ipynb` already
  teaches exactly this, with before/after pairs for both `LLMChain` and legacy RAG. Per the
  destination rule, the correct action is to refresh that notebook (T-006), **not** create a
  sibling. This is the single largest finding cluster (38) and it deliberately produced no
  new notebook.
- **T-008 — document-combining chains** (`load_summarize_chain`, stuff/map-reduce/refine,
  7 findings). Not covered by 3.5/3.6, which handle `LLMChain` and `RetrievalQA`. → new
  notebook, but **blocked** behind T-005.
- **Folded:** the 13 INFO pip-pin/pip-install findings — mechanical, no conceptual depth.
  They became part of T-004 rather than any notebook.

## Stage 3 — notebooks

- **T-007** → `01_Getting_Started/1.8_Package_Split_and_Imports_LangChain_v1.ipynb`
  (12 cells: 4 code, 8 markdown; format check clean on first write).
  - Verified every 1.x symbol against the **installed** package before drafting:
    `langchain.messages`, `langchain.chat_models.init_chat_model`, `langchain.tools`,
    `langchain.agents.create_agent`, and the four `langchain_core.*` paths all resolve.
    Confirmed `langchain.chains`, `.schema`, `.text_splitter`, `.memory`, `.llms` are all
    genuinely `ModuleNotFoundError` — so the error strings quoted in the notebook are real,
    not paraphrased.
  - Kept `langchain_classic` and `langchain_text_splitters` out of every runnable cell, since
    neither is installed; they appear in the mapping table and the contrast cell only.
- **T-008** — not started: `depends_on` T-005, which is blocked by T-001.

## Stage 4 — review

- T-007 submitted to a fresh `general-purpose` subagent running `notebook-review`
  (static gates only; no execution).

### Round 1 — CHANGES_REQUESTED (3 blockers, 1 nit)

- **Blocker 1 was a tooling bug, not a draft defect.** The final markdown cell fused three
  sections with literal `<!-- split -->` markers intact. Root cause: in `md_to_notebook.py`, a
  *closing* plain fence (```` ``` ```` with no language) also matches the fence regex, and the
  loop tested "is a fence and not in code" before "am I inside a plain fence" — so the closer
  was re-read as an opener and the parser stayed stuck in fence mode, swallowing every later
  `<!-- split -->` and `---`. Any draft with a plain fence followed by more sections would have
  hit this. Fixed with an explicit `in_plain_fence` toggle checked first; 12 -> 14 cells.
- Blocker 2: format rule 5 — added commented provider alternatives under `init_chat_model`.
- Blocker 3: `NOTEBOOK_INDEX.md:64` said `(8 nb)` for `01_Getting_Started/`; now `(9 nb)`.
- Nit: `### Next Steps` referenced `8.2_...`, which is T-008's unwritten output — marked upcoming.

### Round 2 — APPROVED

All six gates pass. Reviewer verified against `.venv` rather than from memory: `init_chat_model`
accepts `temperature` via `**kwargs`; `langchain.messages.HumanMessage` *is* the
`langchain_core` object (so the notebook's `is` claim is literally true); all seven paths in the
audit cell genuinely raise `ModuleNotFoundError` on installed `langchain` 1.4.0; no runnable
cell imports the uninstalled `langchain_classic` / `langchain_text_splitters`.

Three nits raised. Two applied post-approval using the reviewer's own prescribed fixes:
the audit loop's anomaly branch printed the LLM emoji instead of the warning emoji, and
`LangChain_Fundamentals/README.md` did not carry the new topic. One declined: the reviewer
itself judged `init_chat_model` correct here despite the phase's direct-instantiation
convention, since it *is* the subject of Part 5.

## Stage 5 — close

- T-007 closed. Board 1/8. Plan **not** complete — 7 tasks remain open.

## Bookkeeping error worth recording

T-007 was never marked `in-progress`: that `tasks.py set` call was chained after a bash
heredoc that failed to parse, so the whole line aborted and the board showed `todo` while the
task was being worked. Corrected mid-run. The heredoc failure mode has now bitten twice this
session; drafts are written with the Write tool instead.
