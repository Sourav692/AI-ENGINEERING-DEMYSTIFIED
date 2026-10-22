# Repo audit (read-only, before any cleanup)

Run this before the first module branch, and on its own when the user asks only for an audit.
It produces one report. Nothing in the repo changes until the user approves recommendations.

Review as a senior AI engineer and technical curriculum reviewer. When goals conflict, rank them:
learning continuity, technical correctness, content preservation — and only then notebook count.

## Hard rules

1. **Read-only.** Don't modify, merge, rename, move or delete any notebook or tracked file. The only
   file written is the local report `.tracker/audit.md` (if `.tracker/` isn't git-ignored yet, don't stage it).
2. **Static analysis only.** Don't execute notebook code, call LLM APIs or trigger external services —
   that rules out `run_notebooks.py` and `check_credentials.py` until approval. Allowed: reading notebook
   JSON, `outline_notebooks.py`, `selfcheck_notebooks.py`, searching `git ls-files`, reading
   `pyproject.toml`/`uv.lock`, documentation lookups, and an import probe for one symbol in the repo env
   (`uv run python -c "from X import Y"` — imports a library, runs no notebook code, makes no network call).
3. **Exact locations.** Every finding names the notebook path and cell number(s). Cell N is the 1-based
   position among all cells (markdown and code) — `outline_notebooks.py` prints it as `[cN]`.
4. **Evidence for staleness.** Check a suspected stale API against the version pinned in `uv.lock`, then
   back it with a docs reference (Context7 `resolve-library-id` → `query-docs`, or the official
   docs/migration-guide URL) or a failing import probe. No evidence → report it as "unverified — check",
   never as stale.
5. **Preserve content.** Never recommend deleting unique technical content to cut the notebook count.
   A recommendation that removes or merges a notebook says where each of its unique parts goes
   (examples, explanations, exercises, insights).
6. **Keep progressions.** Basic → intermediate → advanced treatments of one concept stay distinct.

## Scope

Every `.ipynb` under `modules/` (recursive), plus `exercises/` and `solutions/` when present — they
belong to modules. Skip `.ipynb_checkpoints`. Compare across modules, not only within one.

Start with `outline_notebooks.py modules/ --code` (and the exercise/solution folders) for the map, then
read every notebook in full: code and graph edges decide what a notebook teaches, not headings
(`pitfalls.md` §3).

## What to check

### 1. Self-containment (per notebook)
- A learner can follow it without opening another notebook for essential explanations.
- Imports, configuration, keys, helper functions and dependencies are defined in the notebook.
  `selfcheck_notebooks.py` lists names the notebook uses but never defines.
- Concepts get enough context before the code that implements them; markdown and code run in a logical order.
- No broken references: other notebooks named by missing/old file names, data files or paths absent
  from `git ls-files`, undefined variables.
- Intentional external dependencies (datasets, services, keys, a running server) are stated, ideally
  under Prerequisites.
- Self-contained doesn't mean copying long theory into every notebook. A short contextual recap plus a
  cross-reference is the right shape.

### 2. Duplication and staleness (across the whole scope)
Classify each overlap:
- **Exact duplicate** — identical code, explanation or example.
- **Semantic duplicate** — different code or wording, same concept, no added value.
- **Partial overlap** — a substantial share of the same topic.
- **Redundant example** — a repeated demo that adds no new technique or learning outcome.
- **Stale** — outdated API, deprecated method, obsolete recommendation, or prose that contradicts the current code.

Not redundant — **intentional reinforcement**: the same concept shown with a different implementation
approach, at increasing complexity, or to make an architectural trade-off visible. Say which it is.

### 3. Consolidation
Weigh, per candidate pair or group:
- similarity of learning objectives and degree of overlap;
- whether one leads naturally into the other, and how much context switching a merge saves;
- whether the merged notebook stays manageable — rule of thumb: if its objectives list would grow past
  about five, keep the notebooks separate or split differently;
- whether each notebook has standalone learning value.

Principles: prefer fewer, well-structured notebooks over many fragments on closely related concepts —
but don't merge only because two notebooks share a broad topic. Keep fundamentals before advanced
material. Keep topics with distinct learning objectives separate. A redundant notebook can also fill a
gap the module promises but never shows, instead of being removed.

### 4. Learning flow
- Concept order within and across modules; prerequisites used before they are taught.
- Unnecessary switching between notebooks.
- Repeated introductory material.
- Inconsistent terminology and coding patterns (e.g. chat models created outside the LLM factory,
  mixed env-loading styles, one term used for two things).
- Explanations that can be simpler without losing technical depth.
- Titles that don't match what the notebook actually teaches.

## Report — `.tracker/audit.md`

### A. Executive summary
Totals: notebooks reviewed; self-contained; with missing dependencies or context; with stale content;
with significant duplication; consolidation opportunities. One notebook can count in several rows.

### B. Notebook-level audit
| Notebook | Self-Contained | Duplicate Content | Stale Content | Recommendation |
|---|---|---|---|---|
| `modules/01_x/a.ipynb` | Yes | None | None | Keep |
| `modules/01_x/b.ipynb` | Partial (c4: `llm` undefined) | High (≈ a.ipynb Part 2) | None | Merge with a.ipynb |
| `modules/02_y/c.ipynb` | Yes | Low | Deprecated API (c7) | Update |

Self-Contained: Yes / Partial / No, with the cell that breaks it. Duplicate Content: None / Low / High,
naming the other notebook. Recommendation: Keep / Merge with … / Update / Remove (covered by …).

### C. Consolidation recommendations
One entry per proposal, tagged **High / Medium / Low** priority:
1. Existing notebook names and paths.
2. Reason for consolidation.
3. Overlapping concepts or implementations (with cell numbers).
4. Unique content that must be preserved, and where each piece goes.
5. Proposed merged notebook name.
6. Recommended section structure (in the `notebook-format.md` skeleton: objectives → setup → parts → summary).
7. Expected improvement to the learning experience.

### D. Stale content and technical issues
Per issue: notebook path; cell number or section; description; recommended correction; evidence
(docs URL or Context7 reference, pinned version, import-probe result) — or "unverified — check".

### E. Proposed final notebook structure
A directory tree after consolidation, every notebook tagged:
`[Keep]`, `[Update: <what>]`, `[Merge ← a.ipynb + b.ipynb]` on the result, `[Remove → covered by <file>]` on each source.

### F. Implementation plan
Prioritized steps with minimal disruption, mapped onto the per-module workflow (SKILL.md §6): one
branch and PR per module, in module order. A cross-module merge lands in the PR of the module that
receives the content, with the source's removal and every reference update in the same PR. Note per
step which recommendation IDs from C/D it carries out.

## Success criteria (check the proposal against these before presenting)
- Every notebook has a clear, distinct learning objective.
- Notebooks are self-contained wherever practical.
- No unnecessary duplication remains; intentional reinforcement is labelled as such.
- Deprecated or stale implementations are identified, with evidence.
- Closely related topics are consolidated where it helps.
- Learners progress without unnecessary notebook switching.
- All unique technical knowledge and examples are preserved.
- The curriculum is easier to navigate, maintain and extend.

## Approval gate
Present in one message: the executive summary, the High-priority consolidations and stale issues, the
path to the full report, and the open SKILL.md §1 parameter questions. Then stop. Implement nothing
until the user explicitly approves — all, some, or amended recommendations. Record each decision
(approved / rejected / amended) in `.tracker/audit.md`; approved items seed each module's `plan.md`.
