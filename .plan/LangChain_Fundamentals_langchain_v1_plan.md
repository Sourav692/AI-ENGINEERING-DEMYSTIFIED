# LangChain 1.x Migration Plan — LangChain_Fundamentals

- **Target:** `02_LangChain_Fundamentals_and_Prompting/LangChain_Fundamentals`
- **Generated:** 2026-09-05
- **Scanner:** `.claude/skills/langchain-v1-migration-audit/scripts/scan_langchain_v1.py`
- **Pinned versions at scan time:** langchain `>=1.2.7`, langchain-core `>=1.2.7`, langgraph `1.2.11`
- **Files scanned / needing work:** `28` / `17`

<!-- rollup:start -->
- [ ] **Plan complete** — closes automatically when every task on its board is done
**Board:** `.tasks/LangChain_Fundamentals`
**Task progress:** `██████████████████████░░` 18/20
**Last rollup:** 2026-09-05
<!-- rollup:end -->

## Verdict

**17 of 28 files do not run on LangChain 1.x today.** 59 BLOCKING findings, and a single theme
dominates: **legacy chain classes** (38 findings across 8 files) followed by **moved imports**
(34 findings across 13 files). Nothing here needs an agent rewrite — this track predates agents
— so the work is unusually uniform: imports, then chains.

Severity: 59 BLOCKING · 0 BREAKING · 12 MODERNIZE · 13 INFO.

## Prerequisites

- **`langchain-classic` and `langchain-text-splitters` are pinned but not installed.**
  `requirements.txt` carries `langchain-classic==1.0.8` and `langchain-text-splitters==1.1.2`,
  with matching floors in `pyproject.toml` — but neither imports from the current `.venv`.
  So **no dependency file needs editing**; the environment needs syncing:

  ```bash
  uv pip install langchain-classic==1.0.8 langchain-text-splitters==1.1.2
  # or, to re-sync everything: uv pip install -r requirements.txt
  ```

  Boarded as **T-001**, left `todo` — an unattended run does not change the environment.
  T-002 (and through it T-005, T-006, T-008) depends on it.

  *An earlier draft of this plan said these had to be added to the dependency files. That was
  wrong and is corrected here.*

## Disposition per notebook

The editorial call, applied by the rule "does the notebook's title/folder name the legacy
construct, or is the construct just a vehicle?"

| Notebook                                                 | Disposition       | Why                                                                                               |
| -------------------------------------------------------- | ----------------- | ------------------------------------------------------------------------------------------------- |
| `04_Chains/4.0_Basics_of_Chains.ipynb`                 | **repoint** | Folder + headings ("Simple Chains", "Multi Step Chains") — the chain API*is* the subject       |
| `04_Chains/4.1_Chains_Basics_and_OutputParsers.ipynb`  | **repoint** | Heading is literally "LLMChains & OutputParsers"                                                  |
| `04_Chains/4.2_Advanced_Chains.ipynb`                  | **repoint** | Same; heaviest file in the folder (46 score)                                                      |
| `04_Chains/4.3_Branching_Routing_Merging_Chains.ipynb` | **repoint** | Same family; only 1 chain import + pip noise                                                      |
| `03_LCEL/3.5_Chain_Migrations.ipynb`                   | **repoint** | Already a before/after migration lesson — its legacy halves are*deliberate contrast*, not debt |
| `03_LCEL/3.6_Chain_Migration_Advanced.ipynb`           | **repoint** | Same, for`ConversationalRetrievalChain`                                                         |
| `05_Summarization/8.0_Summarization_Essentials.ipynb`  | **rewrite** | The lesson is*summarization*; the chain is the vehicle                                          |
| `05_Summarization/8.1_Text_Summarization.ipynb`        | **rewrite** | Same — map-reduce/refine are summarization strategies, not chain-API lessons                     |
| `05_Summarization/app.py`                              | **rewrite** | Application code a learner copies                                                                 |
| `03_LCEL/3.1, 3.2, 3.4`, `02_.../2.6`                | mechanical        | One moved import each, no conceptual change                                                       |
| `03_LCEL/3.0`, `01_.../1.2`, `02_.../2.3, 2.4`     | mechanical        | Stale`langchain==0.3.x` pip pins only                                                           |

## Waves

### Wave 0 — prerequisite

- [x] **T-001** Install the already-pinned `langchain-classic` + `langchain-text-splitters` into `.venv`

### Wave 1 — imports (mechanical, unblocks everything)

- [x] **T-002** Repoint `langchain.chains` → `langchain_classic.chains` across the 6 repoint notebooks
- [x] **T-003** Fix `langchain.schema` → `langchain_core.*` (7 files) and `langchain.text_splitter`
  → `langchain_text_splitters` (3), `langchain.llms` → partner packages (2)
- [x] **T-004** Drop/refresh stale `langchain==0.3.x` pip pins (7 files, INFO only)

### Wave 4 — chains

- [x] **T-005** Rewrite the two summarization notebooks + `app.py` off `load_summarize_chain`
- [!] **T-006** Refresh `3.5` / `3.6` so their "legacy" halves import from `langchain_classic`
  and are labelled as such

### Explainers

- [x] **T-007** New notebook: the package split — where every moved import went, and why
- [x] **T-008** New notebook: document-combining chains → LCEL / map-reduce

## Discovered during execution (not in the original plan)

The 8 tasks above were the plan as first written. Working it surfaced 9 more, most of
them from scanner blind spots that only appeared once the migration was actually applied:

- [x] **T-009** `langchain.prompts` imports — 12 BLOCKING findings across 8 files that **no
      scanner rule matched**. The original plan undercounted because of it.
- [x] **T-010** an orphaned `IMP-chains` hit in `3.1` that belonged to no task on the board
- [x] **T-012** stale non-LangChain pins in `1.1`/`1.3` (`openai==1.57.0` conflicts with
      `langchain-openai`'s `openai>=2.45.0`)
- [x] **T-013** personal filesystem paths committed inside notebook outputs
- [x] **T-014** 194 saved output cells cleared folder-wide
- [x] **T-015** `from langchain import PromptTemplate` in `3.0` — a second new-rule find, in a
      file four earlier scans had called clean
- [x] **T-016** `3.5`/`3.6` formatted to `Format_Python_Notebook`
- [ ] **T-011** `PipelinePromptTemplate` in `2.2` — the class was **removed from the ecosystem**
      with no replacement anywhere. Needs a pedagogy decision, not a repoint. *Open.*
- [ ] **T-017** nbstripout pre-commit hook — split out of T-014. Changes every contributor's
      commit flow, so it is **consent-gated**. *Open.*

Four scanner rules were added as a result: `IMP-prompts`, `IMP-toplevel`, `MOD-direct-call`,
plus a fix to `IMP-hub`'s over-match and contrast-cell skipping.

## Explicitly out of scope

Checked and deliberately left alone:

- **LCEL itself** — `|`, `Runnable`, `RunnableParallel`, `RunnablePassthrough`, `.batch()`,
  `.stream()`. Unchanged in 1.x; `03_LCEL/3.0–3.4` are correct as written.
- **Prompt templates, output parsers, `with_structured_output`** — unchanged.
- **Partner-package classes** (`ChatOpenAI`, `ChatGroq`) — unchanged, and this track
  instantiates them directly **on purpose** (`CLAUDE.md`); that is not a convention violation.
- **`load_dotenv()` / `.env` usage** — the repo's documented pattern.
- **No agent content in this track** — `create_agent` does not apply here.

## Explainer notebooks

| Task  | Notebook                                                                | Rounds | Verdict     |
| ----- | ----------------------------------------------------------------------- | ------ | ----------- |
| T-007 | `01_Getting_Started/1.8_Package_Split_and_Imports_LangChain_v1.ipynb` | 2      | APPROVED    |
| T-008 | _(blocked behind T-005 -> T-002 -> T-001)_                            | —     | not started |

**Not written, deliberately:** a "Chains -> LCEL" explainer. `03_LCEL/3.5_Chain_Migrations.ipynb`
already teaches it with before/after pairs for both `LLMChain` and legacy RAG, so the largest
finding cluster (38) became a refresh task (T-006) rather than a duplicate notebook.
