# RAG & AI Agent Evaluation — Tutorial Plan

**Status:** ✅ Complete. All 6 modules (0–5), 15 notebooks, 198 cells, built at `Tutorial_RAG_Agent_Tool_Evaluation/`. No source notebook was deleted or modified at any point (one exception, unrelated to the merge itself: a hardcoded API key found in `Agent_Evaluation/CrewAI_Travel_Planner/tools/search_tool.py` was removed with the user's explicit go-ahead while building Module 5 — see that section below).

**Decisions confirmed:**
- Red teaming is **out of this tutorial** and has been moved to where it actually belongs: `12_Production_and_Observability/Safety_and_Alignment/02_Red_Teaming_Agents_and_RAG.ipynb` (done — a cleaned-up, narrated version of `red_teaming/test_rt.py` using `deepteam`, with a README entry added). The original `red_teaming/` folder here is untouched.
- The new tutorial folder stays **inside this current `Evaluation_and_Eval_Harnesses/` folder**, alongside `RAG_Evaluation/`, `Agent_Evaluation/`, etc. — no restructuring of the phase's existing flat layout.
- Target environment: **`deepeval==4.1.8`** (the repo root `.venv`), confirmed. Every metric class referenced in the plan below (`ConversationalGEval`, `TurnRelevancyMetric`, `KnowledgeRetentionMetric`, `ToolCorrectnessMetric`, `ArgumentCorrectnessMetric`, `ToolUseMetric`, `TaskCompletionMetric`, `ContextualRelevancyMetric`, `FaithfulnessMetric`, `AnswerRelevancyMetric`, `GEval`) is already confirmed present in that version. I still need to check whether `RAG_Evaluation/` and the Arize labs' own pins diverge before running anything sourced from them.
- **Still open:** how hard to touch Module 4 (Arize labs) and Module 5 (CrewAI capstone) — my default, absent other instructions, is the lower-risk "bridge notebook + leave the labs/app physically in place" option from §5, since both have real relative-path/live-service dependencies. I'll proceed on that basis unless told otherwise.

**Build note (discovered while building Module 1.2–1.4):** `RAG_Evaluation/1.Retriever_Evaluation_Metrics.ipynb`, `2.Generator_Evaluation_Metrics.ipynb`, and `3.Custom_LLM_as_a_Judge _(G-Eval).ipynb` all open with `%run Build_RAG_Pipeline_with_Source.ipynb` — the exact relative-path trap flagged in §5, just one level deeper than expected (it affects the *metric-teaching* notebooks, not only the capstone). Rather than dragging that dependency into three separate modules, Modules 1.2–1.4 teach each metric with hand-constructed, self-contained test cases instead (paired good/bad examples chosen to make each metric's specific failure mode visible) — the original explanatory text and metric-argument requirements are carried over, but the worked examples are new. The one live, end-to-end run against a real pipeline is reserved for Module 1.7, where it belongs.

**Build note (Module 1.7 — `deepeval` API drift):** the source notebooks' synthetic-dataset step calls `Synthesizer(model=..., embedder=...)` then `.generate_goldens(contexts=..., evolutions={...}, num_evolutions=..., scenario=..., task=...)`. In `deepeval==4.1.8` (this tutorial's target), `embedder` is gone from `Synthesizer`, the method is `generate_goldens_from_contexts(...)`, and `evolutions`/`num_evolutions`/`scenario`/`task` move into `EvolutionConfig`/`StylingConfig` objects passed to the constructor. Verified against the installed package (`inspect.signature`) before writing Module 1.7 — same underlying capability, reorganized API surface. Anyone running the *original* `RAG_Evaluation/4. End_to_End_RAG_System_Evaluation.ipynb` directly (rather than this tutorial's version) needs the older API or an older `deepeval` pin.

**Environment note:** installing `ragas` (needed for Module 1.6) into the root `.venv` initially caused `uv`'s resolver to downgrade `langgraph` 1.2.11 → 1.0.10, silently breaking `langgraph.runtime.ExecutionInfo`/`ServerInfo` (the exact compatibility issue `requirements.txt` already warns about) — this would have broken every other LangGraph-based notebook in the repo, including Module 1.5 here. Fixed by re-pinning `langgraph==1.2.11`, `langgraph-prebuilt>=1.0.10`, `langgraph-sdk==0.4.2` immediately after; both `ragas` and `langgraph.runtime.ExecutionInfo` import cleanly together now. `ragas==0.4.3` is now installed in the root `.venv` alongside `deepeval==4.1.8` — already covered by `pyproject.toml`'s existing `"ragas>=0.2.8"` pin in the `eval` extra, no change needed there. `mlflow` was also found in use (Module 2.4, source `mlflow_evaluation.ipynb`) but never declared in `pyproject.toml` — added `"mlflow>=3.15.1"` to the `eval` extra.

**Module 4 (Arize labs) — bridge, not rebuild.** Confirmed each lab has its own `helper.py`/`utils.py` and local `data/`/`images/`, and depends on a live Phoenix trace store — but that store isn't hardcoded to DeepLearning.AI's original hosted sandbox: `helper.py`'s `get_phoenix_endpoint()` reads `PHOENIX_COLLECTOR_ENDPOINT` from `.env`, so the labs are runnable against a self-hosted Phoenix instance too. Built `13_Production_Grade_Agent_Eval_Overview.ipynb` as a concept-map + prerequisites bridge instead, linking to the 5 labs in place rather than copying them — resolves the plan's one previously-open question (§6) in favor of the lower-risk option.

**Module 5 (CrewAI capstone) — security finding, fixed with sign-off.** While reading `Agent_Evaluation/CrewAI_Travel_Planner/tools/search_tool.py` to write the capstone, found a hardcoded Serper API key in plaintext inside an unused, dead-code method (`search_internet1` — not the method CrewAI actually calls, which correctly reads `SERPER_API_KEY` from the environment). Already committed to git history (commit `2a088ed`). Flagged to the user immediately; with their explicit go-ahead, removed the dead method (and its now-unused `json`/`requests` imports) — the key itself should still be rotated at Serper separately, since removing it from the file doesn't undo its exposure in git history. `14_Capstone_CrewAI_Travel_Planner_Eval.ipynb` was built as a walkthrough (architecture + annotated eval script, not executed — the app is a separate live FastAPI process needing its own dependencies/credentials), same treatment as Module 4.

## 1. What's actually in this folder today

I read every notebook and script under `Evaluation_and_Eval_Harnesses/`. It currently holds **five independent efforts that were never connected to each other**, at different levels of polish:

| Source | What it is | Shape |
|---|---|---|
| `RAG_Evaluation/` | Retriever + generator metric notebooks (DeepEval & RAGAS), a custom G-Eval notebook, a "build a RAG system → synthetic golden dataset → end-to-end eval" pair, 3 single-metric drill notebooks (Contextual Precision/Recall/Relevancy, 8-10 near-duplicate examples each), and a `RAGAS/` subfolder with **more RAGAS material than the one notebook shows** — 6 standalone scripts (`Evaluate_RAG.py`, `Faithfulness.py`, `ContextRecall.py`, a pytest-based CI script, a Streamlit app) plus a small FastAPI RAG bot used as the eval target. | Mixed notebooks + scripts, some with a persisted Chroma DB (`my_db/`) and dataset files on disk |
| `Agent_Evaluation/` | The DeepLearning.AI × Arize course, **kept whole as 5 progressive labs** (build agent → trace with Phoenix → router/skill LLM-judge evals → trajectory evals via Phoenix experiments → structured evals comparing prompt versions), plus a real CrewAI travel-planner app with a `pytest`-driven end-to-end `TaskCompletionMetric` suite that reads test cases from Excel and hits a live FastAPI backend. | Full mini-courses with their own shared `utils.py` / parquet data / images per lab folder |
| `multi-turn eval and tool evaluations/` | `evaluation.ipynb` (multi-turn conversational eval, 3 tool-use metrics, task-completion eval — the file we already extended together) + `mlflow_evaluation.ipynb`, which re-implements the *same three areas* using MLflow's eval APIs instead of DeepEval, as a direct framework comparison. | 2 notebooks, own `uv` project |
| `04_Agent_RAG_Eval/` | Interview-prep-style notebooks: deterministic retrieval metrics, a mocked RAG-eval LangGraph, a mocked agent-eval LangGraph with a **9-metric trace-level suite** (tool selection, argument correctness, redundant calls, step-wise accuracy, task success, fuzzy trajectory match, end-state verification, recovery rate, cost proxy) plus a Databricks production-mapping table, then live-OpenAI counterparts of both. | 4 notebooks, 2 of which are strict earlier-draft subsets of the other 2 (already identified last session) |
| `LLM_as_Judge/` | One script (`test_firstdeepeval.py`), a thin DeepEval G-Eval smoke test | Script only |
| `red_teaming/` | `deepteam` adversarial/safety testing | **Moved, not included here.** Confirmed as a different discipline from quality/correctness evaluation — now lives at `12_Production_and_Observability/Safety_and_Alignment/02_Red_Teaming_Agents_and_RAG.ipynb`. The original folder here is untouched. |
| `Agent_RAG_Tools_Evaluation_MASTER.ipynb` | The notebook from last session — a straight concatenation of `evaluation.ipynb` + the 2 fullest `04_Agent_RAG_Eval` notebooks, dividers added, nothing condensed. | Stays as-is; superseded in spirit by this tutorial but not deleted |

**The actual problem, in one sentence:** the same handful of ideas — reference-free vs reference-based metrics, LLM-as-judge, tool-call correctness vs task completion, trajectory vs outcome evaluation — are taught **four separate times, in four different frameworks (DeepEval, RAGAS, MLflow, Arize Phoenix), at wildly different depths**, with no on-ramp between them and a lot of near-duplicate example cells (the `DeepEval_Metrics/` drill notebooks in particular).

## 2. Design goals for the tutorial

1. **One learning path, ascending in realism**: toy/deterministic → single-metric LLM-judge → full pipeline eval → production tracing/experiments → real multi-agent capstone.
2. **Teach the concept once, then show the multi-framework reality** (DeepEval / RAGAS / MLflow / Arize) as a deliberate "same idea, different tool" comparison rather than four separate unconnected tracks.
3. **Cut repetition, keep every unique idea.** The `DeepEval_Metrics/` drill notebooks each run the same metric on 8-10 near-identical examples (basic → perfect score → poor score → domain example → batch → real-pipeline-integration → "how the LLM judge reasons"). I'll condense each to the 3-4 examples that teach something the others don't (one worked example, one deliberately-bad example so you see a low score and *why*, one "wired into a real pipeline" example) and cut the rest — not because they're wrong, just because 8 runs of the same lesson isn't a tutorial, it's a stress test.
4. **Don't break what already runs.** Several sources load real files by relative path — `RAG_Evaluation/my_db/` (a persisted Chroma DB), the Arize labs' shared `utils.py`/parquet/image assets per lab folder, and the CrewAI app's `trip_questions.xlsx` + live FastAPI backend. I am **not** copy-pasting those cells into a new location and hoping the paths still resolve. See §5.
5. **Nothing gets deleted.** Every original notebook/script stays exactly where it is. The tutorial is new, additive material that pulls concepts and (where safe) code forward into a clean sequence.

## 3. Proposed structure

A new folder, `Evaluation_and_Eval_Harnesses/Tutorial_RAG_Agent_Tool_Evaluation/`, with a `README.md` course index and numbered notebooks grouped into 5 modules.

### Module 0 — Foundations *(new content, ~1 notebook)*
- `00_Evaluation_Landscape.ipynb` — taxonomy (retrieval vs generation vs end-to-end vs trajectory vs conversational), reference-based vs referenceless, what "LLM-as-judge" actually means and its failure modes, and a map of which tool (DeepEval / RAGAS / MLflow / Arize Phoenix) you reach for and when. No source notebook covers this directly — it's the connective tissue the folder is currently missing, written fresh, short.

### Module 1 — RAG Evaluation *(from `RAG_Evaluation/` + `04_Agent_RAG_Eval/`)*
| Notebook | Built from | Notes |
|---|---|---|
| `01_Retrieval_Metrics_Deterministic.ipynb` | `04_Agent_RAG_Eval/rag_agent_eval_langgraph_new.ipynb` Part 1 | Precision@K, Recall@K, MRR, nDCG — no API calls, builds intuition first |
| `02_Retrieval_Metrics_LLM_Judged.ipynb` | `RAG_Evaluation/1.Retriever_Evaluation_Metrics.ipynb` **+ condensed** `DeepEval_Metrics/Contextual_{Precision,Recall,Relevancy}.ipynb` | Contextual Precision/Recall/Relevancy; the 3 drill notebooks collapse into this one file, 3-4 examples per metric instead of ~9 |
| `03_Generator_Metrics_Referenceless.ipynb` | `RAG_Evaluation/2.Generator_Evaluation_Metrics.ipynb` | Faithfulness, Answer Relevancy, Hallucination — DeepEval and RAGAS shown side by side, as they already are in the source |
| `04_Generator_Metrics_Reference_Based.ipynb` | `RAG_Evaluation/3.Custom_LLM_as_a_Judge _(G-Eval).ipynb` + `04_Agent_RAG_Eval/rag_agent_eval_langgraph_openai.ipynb` Part 2b (Answer Correctness / Semantic Similarity slice) | Why Answer Correctness has no dedicated DeepEval class and needs a custom `GEval` rubric; embedding-based Answer Semantic Similarity |
| `05_RAG_Eval_Inside_the_Pipeline.ipynb` | `04_Agent_RAG_Eval` Parts 2/2b (mock) + Part 6 (real) | Wiring context-relevance and faithfulness checks in *as LangGraph nodes*, not just after-the-fact scoring — mocked judge first, then live-LLM version |
| `06_RAGAS_in_Practice.ipynb` | `RAG_Evaluation/RAGAS/Ragas/SigleTurnSample.ipynb` + selected scripts (`Faithfulness.py`, `ContextRecall.py`, `Evaluate_RAG_PyTest.py`) | The one existing notebook is a 4-cell quickstart; I'll fold in the pytest-CI pattern and one more metric script so this module doesn't undersell RAGAS relative to what's actually sitting in that folder |
| `07_RAG_Capstone_Build_and_Evaluate.ipynb` | `RAG_Evaluation/Build_RAG_Pipeline_with_Source.ipynb` + `RAG_Evaluation/4. End_to_End_RAG_System_Evaluation.ipynb` | Merged into one flow: build the RAG system → generate a synthetic golden reference dataset → run the full retriever+generator suite against it |

### Module 2 — Conversational, Tool & Task Evaluation *(from `evaluation.ipynb` + `mlflow_evaluation.ipynb`)*
| Notebook | Built from |
|---|---|
| `08_MultiTurn_Conversational_Evaluation.ipynb` | `evaluation.ipynb` Part 1 |
| `09_Tool_Use_Evaluation.ipynb` | `evaluation.ipynb` Part 2 |
| `10_Task_Completion_Evaluation.ipynb` | `evaluation.ipynb` Part 3 |
| `11_Same_Evals_with_MLflow.ipynb` | `mlflow_evaluation.ipynb` | Deliberately placed right after 08-10 as a "same 3 questions, different framework" comparison, per design goal 2 |

### Module 3 — Agent Trajectory Evaluation *(from `04_Agent_RAG_Eval`)*
| Notebook | Built from |
|---|---|
| `12_Agent_Trajectory_Evaluation.ipynb` | `04_Agent_RAG_Eval/rag_agent_eval_langgraph_new.ipynb` Parts 3-4 (mocked, incl. the 9-metric refund-agent suite + Databricks mapping table) **and** `rag_agent_eval_langgraph_openai.ipynb` Part 3 (same idea, real tool-calling agent) as two parts of one notebook, same "mock then real" pairing already used successfully in the MASTER notebook |

### Module 4 — Production Tracing & Experimentation *(Arize/Phoenix, from `Agent_Evaluation/DeepLearningAI_Arize/`)*
Kept as **its own linked sub-sequence, lightly touched, not cell-merged** — see §5 for why. Proposed treatment: a short bridge notebook plus pointers.
| Notebook | Role |
|---|---|
| `13_Production_Grade_Agent_Eval_Overview.ipynb` *(new, short)* | Explains what's different here (live tracing, offline experiments, prompt-version comparison) vs Modules 1-3, and how the 5 labs map onto concepts already taught (router/skill eval ≈ Module 2's tool eval, done via LLM-judge on trace spans instead of a test-case object; trajectory eval ≈ Module 3, done via Phoenix experiments instead of a hand-rolled trace) |
| Labs 1-5 (`L3`, `L5`, `L7`, `L9`, `L11`) | Left in place at `Agent_Evaluation/DeepLearningAI_Arize/Lab N .../`, referenced by relative link from the bridge notebook and from the tutorial README's table of contents |

### Module 5 — Capstone: Real Multi-Agent System Evaluation *(from `Agent_Evaluation/CrewAI_Travel_Planner/`)*
| Notebook | Built from |
|---|---|
| `14_Capstone_CrewAI_Travel_Planner_Eval.ipynb` | `evaluate_endtoend_test.py` turned into a walkthrough notebook: stand up the CrewAI app, run `TaskCompletionMetric` against real trip-planning outputs, batch-score from Excel, discuss why this is the same `TaskCompletionMetric` from Module 2 §10 but now scoring a real running system instead of a hand-constructed `LLMTestCase` |

Plus `README.md` at the tutorial root: course description, prerequisites (`.env` keys, which `deepeval` version, etc. — carrying forward the version-mismatch note from the MASTER notebook), a table of contents linking every notebook including Module 4/5's in-place originals, and a suggested "if you only have an hour" fast path (00 → 02 → 09 → 12).

## 4. What gets condensed vs. kept whole

- **Condensed:** `DeepEval_Metrics/Contextual_{Precision,Recall,Relevancy}.ipynb` (9→~4 examples each, folded into `02`). This is the only real "cutting," and only of repeated examples, not of unique content.
- **Merged, not cut:** `Build_RAG_Pipeline_with_Source.ipynb` + `4. End_to_End_RAG_System_Evaluation.ipynb` (the second is a superset of the first's build steps anyway), and the mock/real pairs in Modules 1 and 3 (already proven safe — that's exactly what the MASTER notebook did last session).
- **Left in place, referenced not duplicated:** the 5 Arize labs and the CrewAI app's supporting files (`tools/`, `TripCrew.py`, `api_server.py`, `trip_questions.xlsx`) — see §5.
- **New:** `00_Evaluation_Landscape.ipynb` and `13_Production_Grade_Agent_Eval_Overview.ipynb`.
- **Untouched, not part of the tutorial:** `red_teaming/`, `LLM_as_Judge/test_firstdeepeval.py` (too thin to be its own module — its one idea, general G-Eval, is already covered in `04`), `Agent_RAG_Tools_Evaluation_MASTER.ipynb` (superseded but kept).

## 5. Known risks / why some things aren't fully merged

- **Relative-path data dependencies.** `RAG_Evaluation`'s capstone notebooks read/write a persisted Chroma store (`RAG_Evaluation/my_db/`) and dataset files from their own folder; the Arize labs load shared `utils.py` + parquet/image assets per lab folder; the CrewAI app reads `trip_questions.xlsx` and calls a FastAPI backend that has to actually be running. Copy-pasting these cells into a new folder would silently break them. My plan: `07` and `14` will run the real logic but stay physically adjacent to (or explicitly `sys.path`/relative-load from) the original data locations rather than assuming a naive copy; Module 4 avoids the problem entirely by not moving the Arize labs at all.
- **Dependency/version drift.** Confirmed last session: `evaluation.ipynb`'s folder pins `deepeval==3.8.8`, `04_Agent_RAG_Eval` pins `deepeval==3.1.0`/`3.8.8`, `red_teaming` and the repo root `.venv` are on `4.1.8`. I have not yet checked what the Arize labs (`DeepLearningAI_Arize`) or `RAG_Evaluation` pin. Before execution I'll verify every metric class used across the merged notebooks exists in whatever single environment the tutorial is meant to run under, and flag any that don't.
- **Live services.** `13`/`14` and the Arize labs assume a running Phoenix instance / FastAPI backend respectively — the tutorial README will call this out as a prerequisite rather than something the notebook can bootstrap itself.

## 6. Remaining open question before I execute

**Scope of Module 4/5 touch:** okay with "bridge notebook + link to labs left in place" (my working default), or do you want the Arize labs and CrewAI app actually copied/rewritten into the tutorial folder (higher risk of breaking relative paths, more work, but a single self-contained folder)?

Everything else is confirmed — I'll build Module 0 first (it's new, low-risk) and work through the rest in order unless you say otherwise.
