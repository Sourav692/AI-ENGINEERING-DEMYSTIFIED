# RAG Migration Manifest

Status: implementation started on September 10, 2026.

This manifest is the first execution artifact for `RAG_CURRICULUM.md`. It records source identity, proposed ownership, disposition, and dependency boundaries before notebook movement. It does not replace the detailed curriculum mapping in `RAG_CURRICULUM.md` and it does not authorize deletion.

## Current execution state

| Step | Status | Result |
| --- | --- | --- |
| Freeze and re-inventory | Complete; re-verified September 10, 2026 | Counts unchanged: `04_Retrieval_and_RAG/` 74 notebooks, `08_Advanced_RAG/` 61 (42 technique, 5 anthology evaluation, 7 GraphRAG, 1 ecosystem, 6 advanced LangGraph). |
| Source registry and dependency map | Initial pass complete | Phase 8 source folders and the first Phase 4 pilot sources are registered below. |
| Curriculum destination decided | Complete | A standalone top-level `RAG_Curriculum/` folder, chosen by the user on September 10, 2026 over distributing the numbered folders into existing phase homes. Folders `00`–`11`, `_support/` and `_archive/` are scaffolded. |
| Basic-RAG pilot | **Consolidated and fully validated** | `RAG_Curriculum/01_Foundations/01_RAG_Lifecycle_and_Baseline.ipynb` written from six sources. All five validation layers complete: **27/27 code cells execute end to end**. **No source notebook has been moved, archived, or deleted.** |
| Retirement of pilot sources | **Complete** | 7 notebooks moved to `RAG_Curriculum/_archive/source_notebooks_preserved_by_migration_manifest/`, original relative layout preserved, SHA-256 verified identical after the move. Nothing deleted. All inbound references updated in the same pass. |
| Foundations batch (`01_Foundations/02`–`05`) | **Complete and validated** | Four lessons built and executed end to end: 22/22, 11/11, 18/18, 19/19 code cells. Sources **not** yet archived. |
| Chunking & Indexing batch (`02_Chunking_and_Indexing/01`–`04`) | **Built; `02` reworked and re-validated September 10, 2026** | Four of the batch's nine lessons exist. Their dispositions were **not recorded here when they were built** — that omission is corrected in the batch section below. `02_Semantic_Chunking.ipynb` has been reworked to restore its canonical source to full weight. Sources **not** archived. |
| Remaining batches | Pending | `02_Chunking_and_Indexing/05`–`09` (incremental indexing, parent-document retrieval, multi-representation indexing, document augmentation, HyPE), then the retrieval, query-transformation, context, agentic, advanced, multimodal and evaluation batches. |

## Dispositions

| Disposition | Meaning |
| --- | --- |
| `canonical` | The active teaching source for the concept until a richer merged notebook is produced. |
| `donor` | Source material to merge or extract into the canonical lesson. |
| `support` | Helper, script, data, test, framework variant, provenance, or optional implementation; not an active duplicate lesson. |
| `application` | Coupled application bundle retained with its data, code, tests, and runtime files. |
| `incomplete` | Not counted as completed curriculum coverage. |
| `archive-candidate` | Recoverable original after unique content and dependencies are recorded. No archive move occurs in this pass. |

## Pilot batch: basic RAG

| Source | Proposed canonical destination | Disposition | Dependencies and preservation notes |
| --- | --- | --- | --- |
| `04_Retrieval_and_RAG/09_RAG_with_LangChain/7.1_RAG_Comprehensive.ipynb` | `04_Retrieval_and_RAG/01_Introduction_to_RAG/01_RAG_Lifecycle_and_Baseline.ipynb` | `canonical` | Strongest current baseline source. Inspect local imports, data paths, model/provider configuration, and output-free notebook structure before any move or rename. |
| `04_Retrieval_and_RAG/01_Introduction_to_RAG/1_rag_overview.ipynb` | Same canonical baseline lesson | `donor` | Preserve indexing/retrieval explanation and introductory diagrams or exercises that are absent from the canonical source. |
| `04_Retrieval_and_RAG/RAG_Production_Course/06_rag_pipeline.ipynb` | Same canonical baseline lesson | `donor` | Preserve fallback, structured-output, exercise, and pipeline-inspection material; keep the research-assistant integration in its application home. |
| `04_Retrieval_and_RAG/09_RAG_with_LangChain/7.0_RAG_Essentials.ipynb` | Baseline lesson comparison only | `archive-candidate` | Older/overlapping baseline. Compare unique cells and dependencies before archive classification; do not delete. |
| `04_Retrieval_and_RAG/01_Introduction_to_RAG/Basics of RAG.ipynb` | Part 2 of the canonical baseline lesson | `donor` (**reclassified** from `archive-candidate`) | Inspection found this is *not* an overlapping baseline. It uses TF-IDF + `NearestNeighbors` with no LangChain and no LLM, demonstrating the retrieval mechanism before any framework hides it. Merged into the lesson as its framework-free Part 2, which is also the only part that runs offline. |
| `04_Retrieval_and_RAG/01_Introduction_to_RAG/Naive_RAG.ipynb` | Baseline lesson comparison only | `donor` | Preserve any minimal-pipeline explanation not already present in the canonical baseline. |
| `04_Retrieval_and_RAG/01_Introduction_to_RAG/Naive_RAG_Alt.ipynb` | Baseline lesson comparison only | `support` (confirmed) | Diffed against `Naive_RAG.ipynb`: identical except for two cells that swap `get_apikey()` for a literal empty API-key string. No unique pedagogy. Provider/credential variant only. |
| ~~`04_Retrieval_and_RAG/04_Query_Transformation_Techniques/Naive_RAG.ipynb`~~ | — | **entry withdrawn** | **Stale path.** No such file exists. `04_Query_Transformation_Techniques/` was renumbered and reorganized after this manifest was drafted, and now holds only the eight query-transformation notebooks. The only `Naive_RAG*` files in the repository are the two under `01_Introduction_to_RAG/`. |
| ~~`04_Retrieval_and_RAG/04_Query_Transformation_Techniques/Naive_RAG_Alt.ipynb`~~ | — | **entry withdrawn** | Same as above. |
| `04_Retrieval_and_RAG/RAG_Production_Course/08_research_assistant.ipynb` | `11_Applications_and_Capstones/05_Research_Assistant_RAG.ipynb` | `application` | Keep application workflow, data, scripts, and generated artifacts coupled; link to the canonical baseline instead of duplicating its teaching. |

### Pilot outcome

The canonical lesson is **`RAG_Curriculum/01_Foundations/01_RAG_Lifecycle_and_Baseline.ipynb`** (concept ID `RAG-F-01`, 56 cells). It teaches the RAG lifecycle end to end at baseline depth, and every later lesson modifies exactly one stage of it.

#### Donor cell traceability

| Source | Material preserved | Where it landed |
| --- | --- | --- |
| `7.1_RAG_Comprehensive.ipynb` | Loader/`Document` structure, splitter mechanics and overlap inspection, cosine-similarity comparison of identical/related/unrelated texts, FAISS build and save/load round trip, retriever `search_kwargs` (`k` + metadata filter), modern-vs-legacy chain contrast | Parts 3 and 4 |
| `1_rag_overview.ipynb` | Four-component framing, indexing-vs-query-phase split, "what this validates" checkpoints, `tiktoken`/`cl100k_base` token measurement, **all three diagram attachments** | Parts 1, 3 (title cell carries the four-component diagram) |
| `06_rag_pipeline.ipynb` | Source-attribution formatting, out-of-scope fallback prompt, `with_structured_output` + Pydantic `RAGResponse`, `DocumentQA` exercise class | Parts 5 and 7 |
| `Basics of RAG.ipynb` | TF-IDF vectorization, `NearestNeighbors` index, `query_index()` | Part 2, extended with a paraphrase-failure demonstration that motivates embeddings |
| `Naive_RAG.ipynb` | Indexing → retrieval → augmentation → generation stage names, `similarity_search_with_score` | Parts 1 and 4 (scores are framed as the primary retrieval debugging tool) |
| `7.0_RAG_Essentials.ipynb` | `return_source_documents` provenance | Part 4 legacy-contrast cell |

Material deliberately **not** carried, with its destination:

| Not carried | Reason | Destination |
| --- | --- | --- |
| Vector-store backend comparison table | Belongs to the dedicated backend lesson | `01_Foundations/04` |
| Loader catalogue beyond text/PDF/manual | Belongs to the dedicated loader lesson | `01_Foundations/02` |
| `7.0`'s multi-document summarization variant | Not a lifecycle concept | `05_Context_and_Generation/03` |
| `06_rag_pipeline.ipynb`'s research-assistant integration | Application, not lesson | `11_Applications_and_Capstones/05` |

#### Additions not present in any source

- A **failure-diagnosis section** (Part 6) built around the single question "was the correct passage in the retrieved context?", with a routing table from each observed failure mode to the lesson that fixes it. No source notebook taught how to tell retrieval failure from generation failure.
- A **LangChain 1.x migration table** — see defects below.
- The paraphrase-failure demonstration that connects Part 2's lexical baseline to Part 3's embeddings.

#### Defects found and fixed in the merged lesson

| Defect in sources | Fix |
| --- | --- |
| `from langchain.chains.retrieval import ...`, `from langchain.chains.combine_documents import ...`, `from langchain.chains import RetrievalQA`, `from langchain.prompts import PromptTemplate` — all four raise `ModuleNotFoundError` on this repo's LangChain 1.4 | Corrected to `langchain_classic.*` / `langchain_core.prompts`, and the migration is now **taught** in Part 4 with a before/after table |
| `TextLoader("./bella_vista.txt")` resolves only if the kernel starts in `09_RAG_with_LangChain/` | Resolved via `rag_paths.asset()` |
| `DOC_PATH = "Transformer.pdf"` — the file is actually in `shared_data/` | Resolved via `rag_paths.asset()` |
| `FAISS.load_local("index", ...)` and `save_local("vs_db")` write into checked-in directories | Lesson writes to `tempfile.mkdtemp()`; the existing `index/` and `vs_db/` are untouched |
| `find_dotenv()` raises `AssertionError` outside an interactive kernel (it walks caller stack frames) | `load_dotenv(repo_root() / ".env")` |

Defects **recorded but not repaired**, because their notebooks are outside the pilot's edit scope: `Naive_RAG.ipynb`'s `CHROMA_PATH = "/usr/local/notebooks"` (absolute POSIX path, cannot resolve on this Windows tree), and the three colliding `utils.py` modules under `04_Retrieval_and_RAG/`.

#### Validation performed

| Layer | Result |
| --- | --- |
| Static (nbformat schema, unique cell ids, AST parse of all 27 code cells, cleared outputs, `# ====` banner convention, attachment binding, tag survival) | **PASS** |
| Imports — 25 distinct statements executed against the real environment | **PASS** (after the four LangChain 1.x corrections above) |
| Isolated offline execution — fresh namespace, no network, Part 0 bootstrap + all of Part 2 | **PASS**, 6 cells |
| Path resolution from repository root **and** from a nested notebook directory | **PASS** |
| Service-backed execution — full run-all with real API calls | **PASS — 27/27 code cells** in order in a fresh namespace, 2026-09-10, authorized by the user. 52s wall time; 13 completions (2,664 in / 370 out tokens) plus ~20 embedding calls. |
| Regression comparison against source behaviour | **Not performed — no usable baseline.** Five of six sources ship outputs-stripped, so no prior behaviour is recorded; the sixth runs over a different corpus. |

Behavioural claims confirmed by the run: cosine similarity separates meaning as taught (identical 1.0000 / paraphrase 0.6341 / unrelated 0.0016); Part 2's lexical baseline genuinely fails on paraphrase at distance 1.0000; 9 chunks → 9 vectors survive a disk round trip; the fallback refuses both out-of-scope questions; `with_structured_output` returns a validated object; the deprecated `RetrievalQA` contrast cell still runs.

Two defects surfaced only by execution:

| Found by running | Resolution |
| --- | --- |
| `pypdf` declared in `pyproject.toml` and pinned in `requirements.txt` but **not installed** in the venv these notebooks run on (`03_LangGraph_Fundamentals/.venv`; there is no root `.venv`) | Installed at the pinned 6.17.0. Recorded as an environment-provisioning gap, not a dependency change. |
| Provider change requested mid-pilot | All LLM calls now route through `helpers.get_experientiallabs_llm()` (`gpt-5.6-luna`) instead of direct `init_chat_model("gpt-4o-mini")`. `with_structured_output` was verified on that endpoint before adoption. Embeddings still use `OpenAIEmbeddings`. |

The lesson's own "Provenance and runtime status" cell reports this to the learner, including the measured token cost.

#### Archive record (2026-09-10)

Moved to `RAG_Curriculum/_archive/source_notebooks_preserved_by_migration_manifest/`, which mirrors each file's original path exactly. Restore is a plain copy; see that folder's `ARCHIVE_MANIFEST.md`.

| Source (also its path inside the archive) | SHA-256 | Bytes |
| --- | --- | --- |
| `04_Retrieval_and_RAG/09_RAG_with_LangChain/7.1_RAG_Comprehensive.ipynb` | `d6b4abdace3c7ae2a8105e815a8735cbba90ae553eaf1916389b90c95cbcc849` | 82,374 |
| `04_Retrieval_and_RAG/09_RAG_with_LangChain/7.0_RAG_Essentials.ipynb` | `e9ee69318d3f68c693b9308893d6a8753df2e43c6909aaac74f2f15936eda041` | 20,700 |
| `04_Retrieval_and_RAG/01_Introduction_to_RAG/1_rag_overview.ipynb` | `95172c564fbaaeb326282ed8d419810a6b7b3355011b91723c2990e69b95c3b9` | 813,838 |
| `04_Retrieval_and_RAG/01_Introduction_to_RAG/Basics of RAG.ipynb` | `9240d9a628313f5a9a21ad2c000f5772109e08441078a767fd5c745d0ae5ec97` | 6,827 |
| `04_Retrieval_and_RAG/01_Introduction_to_RAG/Naive_RAG.ipynb` | `c94dbdf57369407f62eb0b4682800b09b855a0f76541697abe25242c2c8113a4` | 7,557 |
| `04_Retrieval_and_RAG/01_Introduction_to_RAG/Naive_RAG_Alt.ipynb` | `fed822b42c2dcd47ff1aab5350e831a7050cea0462f23e36cddce187548ae7b1` | 7,560 |
| `04_Retrieval_and_RAG/RAG_Production_Course/06_rag_pipeline.ipynb` | `f4b43440b77c3935134950b24ed8732fa600505d0cb3a90618991c0a3e7d6d38` | 27,488 |

Every checksum was taken before the move and re-verified after it. **No file was deleted, and no file was modified.**

One disposition changed at archive time: **`Naive_RAG_Alt.ipynb` was recorded `support`** (keep in place as a provider variant) but was archived alongside `Naive_RAG.ipynb`. Retiring the original while leaving a byte-near-identical credential variant as the only active copy would have left the repository in a worse state than either archiving both or keeping both. Recorded here rather than made silently.

#### Inbound references updated in the same pass

Section 5 of the plan requires reference updates to ship with the move, not after it.

| File | Change |
| --- | --- |
| `04_Retrieval_and_RAG/01_Introduction_to_RAG/README.md` | Archived rows removed; pointer to the canonical lesson added. |
| `04_Retrieval_and_RAG/09_RAG_with_LangChain/README.md` | **Created** — folder had none. Notes the two retirements and why `bella_vista.txt`, `index/`, `vs_db/` must stay. |
| `04_Retrieval_and_RAG/RAG_Production_Course/README.md` | **Created** — folder had none. Explains both numbering gaps (`03` retired 2026-09-08, `06` retired 2026-09-10) and where to read `06`'s content instead. |
| `04_Retrieval_and_RAG/04_Query_Transformation_Techniques/README.md` | Stale `Naive_RAG` rows removed and the "baseline index" reference repointed. |
| `04_Retrieval_and_RAG/04_Query_Transformation_Techniques/Query_Transformation_Techniques_Explained.md` | Same two corrections. |
| `04_Retrieval_and_RAG/RAG_Production_Course/04_embeddings_deep.ipynb` | Its forward-reference to `06_rag_pipeline.ipynb` repointed. |
| `tutorials/02_rag_and_retrieval_INTERVIEW_TUTORIAL.md` | 3 references annotated with the new location. |
| `NOTEBOOK_INDEX.md` | Phase 4 tables corrected; every archived notebook removed from the active listing. |

**A pre-existing defect this surfaced:** `04_Query_Transformation_Techniques/`'s README, its explainer, *and* `NOTEBOOK_INDEX.md` all documented `Naive_RAG.ipynb` / `Naive_RAG_Alt.ipynb` as living in that folder. They had already been relocated to `01_Introduction_to_RAG/` in an earlier reorganization, and three documents were never updated. This is what produced the two stale rows in this manifest's pilot table. All three are now corrected.

#### What was deliberately not done

- **Nothing was deleted.** Retirement was a move into `_archive/`, with checksums verified on both sides.
- **No assets were moved.** Section 7B's stationary-asset rule is satisfied by the resolver instead. `bella_vista.txt`, `Transformer.pdf`, `index/` and `vs_db/` are all untouched in their original homes — the canonical lesson still reads two of them from there.
- **No notebook outside the pilot's source set was retired.** `7.2`, `7.3`, `Indexing.ipynb`, `Langchain+Rag.ipynb`, `Retrieval Strategies.ipynb`, and the rest of `RAG_Production_Course/` all stay. `08_research_assistant.ipynb` stays because it is an application bundle whose destination folder is not yet built.
- **No dependency versions were changed.** `pypdf` was installed at the version already pinned in `requirements.txt`; nothing was added, removed, or upgraded. No commits or branches were created.

### Pilot dependency checklist

- Preserve `04_Retrieval_and_RAG/shared_data/` and inspect every referenced asset before changing notebook depth.
- Preserve environment/provider configuration and do not execute paid or service-backed cells during static migration.
- Compare markdown explanations, code cells, exercises, diagrams, and failure cases across the three baseline sources before producing a merged canonical lesson.
- Keep the source notebooks recoverable until the merged lesson passes JSON, import, path, and isolated-execution checks.
- Update `NOTEBOOK_INDEX.md`, relevant Phase 4 README content, and this manifest together when the pilot is physically moved.

## Phase 8 source registry

The advanced anthology remains an intact dependency bundle during this first pass. Its current source folders and proposed ownership are registered here; the detailed notebook-level mapping remains in `RAG_CURRICULUM.md`.

| Current source folder | Current contents | Proposed ownership | Disposition |
| --- | --- | --- | --- |
| `08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/` | 42 technique notebooks, including the seven notebooks merged from the former nested checkout | Concepts in foundations, chunking, retrieval, query transformation, context, agentic, advanced architecture, and multimodal tracks | `donor`/`canonical` sources; keep folder intact until shared-path migration is validated |
| `08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques_runnable_scripts/` | 21 standalone Python mirrors | `_support/helpers/` or source support bundle | `support` |
| `08_Advanced_RAG/Comprehensive_RAG_Techniques/evaluation/` | 5 evaluation notebooks plus `evalute_rag.py` | `06_Evaluation/` and `_support/evaluation_data/` | `donor`/`support` |
| `08_Advanced_RAG/Comprehensive_RAG_Techniques/data/` | Shared JSON/CSV and other notebook inputs | `_support/shared_data/` | `support`; preserve relative paths |
| `08_Advanced_RAG/Comprehensive_RAG_Techniques/images/` | Shared diagrams and images | `_support/shared_data/` or coupled anthology support | `support` |
| `08_Advanced_RAG/Comprehensive_RAG_Techniques/tests/` | Import/test discovery files | `_support/helpers/` or coupled anthology support | `support` |
| `08_Advanced_RAG/Comprehensive_RAG_Techniques/helper_functions.py` | Shared notebook helper module | `_support/helpers/` only after import mapping | `support` |
| `08_Advanced_RAG/GraphRAG/` | 7 notebooks, graph helpers, extraction assets, and incomplete KG exercise | `08_Advanced_Architectures/03`–`07` | `donor`/`support`/`incomplete` by file |
| `08_Advanced_RAG/RAG_with_LangGraph_Advanced/` | 6 advanced agentic-RAG notebooks and research-paper references | `07_Agentic_RAG/` plus healthcare application | `donor`/`application`/`support` |
| `08_Advanced_RAG/RAG_Ecosystem/` | `rag_ecosystem.ipynb` and app support | Curriculum guide plus ColBERT lesson | `support`/`donor`; keep whole walkthrough |
| `08_Advanced_RAG/building-adaptive-rag/` | Adaptive-RAG application source, data, and tests | Capstone/application and helper support | `application` |
| `08_Advanced_RAG/CacheRAG/` | Planned area; no completed notebook verified | No active destination yet | `incomplete`/`planned` |

## Non-negotiable dependency rules

1. Do not split `Comprehensive_RAG_Techniques/` notebook-by-notebook until imports, `data/`, `images/`, tests, scripts, and relative paths have a recorded replacement.
2. Do not merge framework variants by deleting the variant; extract unique teaching material and keep the implementation as support/reference.
3. Do not archive a donor until its unique cells and dependencies have a destination entry.
4. Do not overwrite existing vector indexes, databases, generated outputs, or user assets during validation.
5. Do not claim `CacheRAG` or the incomplete KG exercise as completed curriculum content.

## Foundations batch — `01_Foundations/02`–`05`

Completed September 10, 2026, after the pilot's lesson shape was approved. Four lessons, all validated by full execution against live services.

| Lesson | Concept | Primary sources | Cells run |
| --- | --- | --- | --- |
| `02_Document_Loading_and_Metadata.ipynb` | `RAG-F-02` | The eleven notebooks of `06_RAG_Naive_to_Production/01_Loading_Data/` | 22/22 |
| `03_Embeddings_and_Model_Selection.ipynb` | `RAG-F-03` | `RAG_Production_Course/04_embeddings_deep.ipynb`; `02_Embeddings_and_Vector_Databases/{1, 4, 5, 6}` | 11/11 |
| `04_Vector_Stores_and_Index_Operations.ipynb` | `RAG-F-04` | `RAG_Production_Course/05_vector_stores.ipynb`; `02_Embeddings_and_Vector_Databases/{2, 2.3, 3}` | 18/18 |
| `05_Structured_Data_RAG.ipynb` | `RAG-F-05` | `all_rag_techniques/{2. simple_csv_rag, json_rag}.ipynb`; `01_Loading_Data/{3, 4}` | 19/19 |

### Defects found in the sources

| Finding | Affected | Action |
| --- | --- | --- |
| **All eleven loader notebooks are unrunnable.** Every one addresses inputs as `../../data/` or `../../docs/`; from `01_Loading_Data/` that resolves to `04_Retrieval_and_RAG/`, which has neither. The files all exist in `shared_data/`. | `06_RAG_Naive_to_Production/01_Loading_Data/*` (11 notebooks) | Lesson 02 resolves via `rag_paths.asset()`. Sources left untouched and still broken — they are not yet archived. |
| `CacheBackedEmbeddings` and `LocalFileStore` are not in `langchain` on 1.x | Lesson 03's sources | Corrected to `langchain_classic.*`; the migration is taught in the lesson, as with lesson 01's chain imports. |
| Eight of eleven loader notebooks repeat an identical "Document Loaders / Examples / Functionality" preamble | `01_Loading_Data/*` | Consolidated once into lesson 02 Part 1. |
| `6. Compare_Embedding_Models.ipynb` cannot run locally — it depends on Databricks Vector Search and MLflow | Lesson 03's sources | Approach carried (empirical model comparison); implementation reworked onto the local stack. The Databricks plumbing belongs to `10_Production_RAG/03`. |
| `json_rag.ipynb` imports a local `jrag` module absent from this repository | Lesson 05's sources | Approach carried; implementation not. |

### Environment gaps surfaced

`pypdf`, `unstructured` and `docx2txt` are declared in `pyproject.toml` but were absent from the venv these notebooks run on; all three installed at pinned versions after a dry-run confirmed the installs were purely additive. `markdown` was also installed — required by `unstructured.partition.md` but declared nowhere; it should be added to `pyproject.toml`.

Two dependencies were deliberately **not** installed: `jq` (needs a C toolchain, does not build on Windows — lesson 02 uses portable `json` + `Document` instead and says so) and the `hf` extra (`torch`/`transformers`, multi-gigabyte — lesson 03's local-model section sits behind a flag). `unstructured`'s `.docx` path hung past 110 seconds on `Intel Strategy.docx`, so lesson 02 uses `Docx2txtLoader` for Word and records the tradeoff.

### Material added that no source contained

- **Lesson 02:** load validation (reconciling glob matches against documents returned; detecting silent empty PDF extraction), and a deliberate four-axis metadata schema.
- **Lesson 03:** a `margin` metric alongside `recall@1`, because recall saturates at 1.0 on a small set and stops discriminating — margin degrades continuously and shows truncation damage. Also the mismatched-model demonstration, which measured recall dropping 6/6 → 1/6 with mean top-1 similarity collapsing 0.4949 → 0.0449.
- **Lesson 04:** the duplicate-ID trap, and a startup assertion that converts silent index/model mismatch into a loud failure.
- **Lesson 05:** the three structural failure classes (aggregation, numeric comparison, exact lookup) with measured wrong answers, and routing by question type. Every source builds a structured-data pipeline and stops where it works.

### Sources not yet archived

**No Foundations source has been retired.** The pilot's precedent — archive only after the replacing lesson is validated — is met, but archiving these is a larger action than the pilot's seven files (the eleven loader notebooks alone are a coherent track) and has not been requested. All sources remain in place.

## Chunking and Indexing batch — `02_Chunking_and_Indexing/01`–`04`

Built September 10, 2026. **Their source dispositions were not recorded in this manifest at the time** — the four lessons carried their provenance only in their own "Provenance and runtime status" cells. Since `CLAUDE.md` makes this manifest the sole authority on which sources are canonical, donor, support or archive-candidate, that omission meant a reclassification (below) happened invisibly. The registry is backfilled here.

Five of the batch's nine planned lessons (`05`–`09`) are not built.

### Source registry and dispositions

| Source | Canonical destination | Disposition | Notes |
| --- | --- | --- | --- |
| `04_Retrieval_and_RAG/06_RAG_Naive_to_Production/02_Splitting_and_Chunking/1. Document_Splitters_and_Chunkers.ipynb` | `02_Chunking_and_Indexing/01_Document_Splitting_and_Chunking.ipynb` | `canonical` | The splitter catalogue — fixed, sentence, paragraph, sliding window, recursive, character, code, Markdown, token-based, section-based. 87 cells, the largest single source in this batch. Unrunnable as written: reads `../../docs/layoutparser_paper.pdf`, a path that does not exist; the file is in `shared_data/` and is reached through `rag_paths.asset()` in the lesson. |
| `04_Retrieval_and_RAG/RAG_Production_Course/02_text_splitters.ipynb` | Same | `donor` | Structure and the chunk-size / overlap comparison framing. |
| `08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/semantic_chunking.ipynb` | `02_Chunking_and_Indexing/02_Semantic_Chunking.ipynb` | `canonical` (**reclassified** — see below) | The anthology's semantic-chunking notebook. `RAG_CURRICULUM.md` section 4 names it the canonical explanation; section 6 (line 424) calls it a donor and defers to "the richer dedicated semantic-chunking source identified in Section 4", which is this same file. The plan contradicts itself here; section 4 governs. |
| `04_Retrieval_and_RAG/06_RAG_Naive_to_Production/02_Splitting_and_Chunking/2. Semantichunking.ipynb` | Same | `donor` | From-scratch implementation and the purpose-built `langchain_intro.txt` corpus. Cannot run as written — LangChain 0.x throughout (`langchain.chat_models`, `langchain.document_loaders`, `langchain.vectorstores`, `langchain.schema`, `langchain.prompts`) plus `sentence_transformers`, which is not installed (the `hf` extra). |
| `08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/5. proposition_chunking.ipynb` | `02_Chunking_and_Indexing/03_Proposition_Chunking.ipynb` | `canonical` | Proposition generation, the quality-check grading step, the comparison against larger chunks. Cannot run here: `langchain_core.pydantic_v1` was removed in LangChain 1.x, alongside `langchain.text_splitter` and sunset `langchain_community.embeddings` paths, and it uses a different provider (`langchain_groq`). Technique carried, implementation rebuilt on pydantic v2. |
| `08_Advanced_RAG/Comprehensive_RAG_Techniques/all_rag_techniques/4. choose_chunk_size.ipynb` | `02_Chunking_and_Indexing/04_Choosing_Chunk_Size.ipynb` | `canonical` | Method carried (sweep sizes, evaluate each, compare); implementation not. Built entirely on **LlamaIndex**, which is neither installed nor declared in `pyproject.toml`/`requirements.txt`. Its `FaithfulnessEvaluator`/`RelevancyEvaluator` LLM judges are replaced with a deterministic retrieval metric — faster, free of judge variance, comparable to the sweeps in `01_Foundations/03`. |
| `08_Advanced_RAG/Comprehensive_RAG_Techniques/images/semantic_chunking_comparison.svg` | Rasterized to `_support/shared_data/semantic_chunking_comparison.png`, attached in `02_Semantic_Chunking.ipynb` | `support` | Stationary and **untouched**; it remains the master copy. Carried as a PNG notebook attachment rather than a path reference, so the lesson does not depend on the anthology folder's layout. See "Generated asset" below. |
| `08_Advanced_RAG/Comprehensive_RAG_Techniques/data/Understanding_Climate_Change.pdf` | Read by `02_Semantic_Chunking.ipynb` Part 6 | `support` | Stationary, resolved through `rag_paths.asset()`. 33 pages, 72,523 characters, 13,016 tokens. |
| `08_Advanced_RAG/Comprehensive_RAG_Techniques/helper_functions.py` | Not carried | `support` | `semantic_chunking.ipynb` reaches it with `from helper_functions import *` for `read_pdf_to_string`, `retrieve_context_per_question` and `show_context`. The lesson uses `PyPDFLoader` and a local `show_context` instead, so no import dependency on the anthology folder is created. Consistent with dependency rule 1. |

**No source in this batch has been moved, modified, archived or deleted.** All four remain live and are still the source of truth for anything not carried.

### Correction: `semantic_chunking.ipynb` restored to canonical (September 10, 2026)

As first built, `02_Semantic_Chunking.ipynb` used the anthology notebook as a **donor only**, taking `SemanticChunker` usage and the breakpoint-threshold types and nothing else, while `2. Semantichunking.ipynb` supplied the lesson's spine. That inverted the roles section 4 of the plan assigns, and it dropped material that section 2's "preserve insight, not duplication" rule requires be carried — rule 2 names diagrams explicitly, and the pilot batch had already set the precedent by carrying all three of `1_rag_overview.ipynb`'s diagram attachments.

Four things were lost and have now been restored:

| Restored | Where it now lives |
| --- | --- |
| The conceptual framing — the problem with arbitrary breakpoints, the coherence claim, the four method stages, the claimed benefits | New "The idea, before the code" section, ahead of Prerequisites |
| Attribution — [Greg Kamradt's original proposal](https://youtu.be/8OJC21T2SL4?t=1933) and the [LangChain how-to](https://python.langchain.com/docs/how_to/semantic-chunker/) | Opening section |
| `semantic_chunking_comparison.svg` | Rasterized to PNG and attached in the same section |
| The end-to-end pipeline: PDF → `SemanticChunker.create_documents` → FAISS → retriever → `"What is the main cause of climate change?"` | New Part 6, four stages, on the anthology's own 33-page climate PDF |

The lesson's existing material was kept: the from-scratch implementation, the `gradient` threshold type (added to `SemanticChunker` after the anthology notebook was written, so absent from its three-type list), the Part 4 separation measurement, the Part 5 cost measurement, and the Part 7 when-*not*-to-use guidance. "When to use it" moved from Part 6 to Part 7 to make room.

Adapted rather than copied, and why: the anthology's `from helper_functions import *` is replaced with `PyPDFLoader` and an explicit local `show_context`; its `read_pdf_to_string` flattens a PDF to a string, whereas the lesson loads pages and joins them, so it can state *why* page breaks must not become chunk boundaries.

### Build tooling change

`_support/lesson_sources/build_lesson.py` gained an `attachfile=<filename.png>` cell option: the file is resolved through `rag_paths.asset()`, base64'd, and attached under its filename stem, so the cell body references it as `![alt](attachment:<stem>)`. The build **fails** if a cell attaches a file it never references, which is the failure mode that would otherwise ship a silently invisible diagram. This is additive — the existing `attach=` path, which pulls the pilot donor's three PNG attachments, is unchanged, and all four other built lessons rebuild with cells identical to what is on disk.

**First attempt, and why it was wrong.** The diagram was initially inlined as raw `<svg>` markup in the markdown cell, on the reasoning that inlining renders everywhere and avoids a base64 payload. **It did not render in Jupyter.** The diagnosis that followed matters more than the fix:

- The first hypothesis — that the SVG's blank lines terminate the CommonMark HTML block early — was **tested and disproved**: both `markdown-it` (what JupyterLab uses) and `mistune` (what nbconvert uses) pass all 14 `<rect>` and 32 `<text>` elements through intact with or without blank lines.
- The actual cause is downstream of the markdown parser: the renderer's HTML sanitizer. Inline `<svg>` survives parsing and is then stripped before display, which fails **silently** — no error, no broken-image icon, just nothing.

The lesson generalizes: **do not carry a diagram as inline markup in a notebook.** Use an attachment, which is Jupyter's own mechanism and is what the pilot lesson's three diagrams already used. That precedent was available and should have been followed first.

### Generated asset

`RAG_Curriculum/_support/shared_data/semantic_chunking_comparison.png` (1600×1400, 2× the source's 800×700 viewBox) — the **first** file in the curriculum's own asset root, which had been empty.

It is a faithful rasterization of the anthology's `images/semantic_chunking_comparison.svg`, which uses only `<rect>` and `<text>`. No SVG rasterizer is installed in this environment (`cairosvg`, `svglib` and `reportlab` are all absent, and none is declared in `pyproject.toml`), so the conversion was done with a throwaway Pillow script that parses those two element types and honours `text-anchor`, `font-size`, `font-weight`, `fill` and `stroke`; it warns on any element it does not handle, and warned on none. The output was inspected before use. **No dependency was added.**

The source SVG is untouched. If the diagram ever needs regenerating, the SVG remains the master.

### Material added that no source contained

- **Lesson 01:** the deliberate deferral notes — semantic chunking, empirical size selection, and the retrieve-small/return-large family are separate lessons, and the notebook says why rather than silently omitting them.
- **Lesson 02:** the Part 4 separation test (margin between two topic queries, character vs semantic on identical text), the Part 5 cost measurement and the bounding pattern, the Part 6 character-splitter comparison on the same PDF, and Part 7's when-*not*-to-use. Both sources demonstrate the technique working and stop there.
- **Lesson 03:** the atomic-vs-self-contained distinction, the measured comparison, and the cost extrapolation.
- **Lesson 04:** the cost axis, guidance on reading a sweep curve including the case where the honest answer is "no difference", and the escape hatch when no size works.

### Validation performed

| Lesson | Layer | Result |
| --- | --- | --- |
| `01_Document_Splitting_and_Chunking.ipynb` | Built (39 cells, 18 code) | Execution record not captured at build time; **not re-validated in this pass** |
| `02_Semantic_Chunking.ipynb` | Static — nbformat schema, AST parse of all 19 code cells, SVG inlined, outputs cleared, `# ====` banner convention | **PASS** |
| `02_Semantic_Chunking.ipynb` | Service-backed execution — full run-all with real API calls in a fresh kernel, 2026-09-10 | **PASS — 19/19 code cells**, 50s wall time, ~40k embedding tokens, no completions |
| `03_Proposition_Chunking.ipynb` | Built (30 cells, 13 code) | Execution record not captured at build time; **not re-validated in this pass** |
| `04_Choosing_Chunk_Size.ipynb` | Built (31 cells, 11 code) | Execution record not captured at build time; **not re-validated in this pass** |

Lessons `01`, `03` and `04` are recorded as **built but not execution-validated in this manifest**. That is weaker than the Foundations batch, where every lesson has a cell count from a real run. Do not treat them as validated to the pilot's standard until they have been run.

Behavioural claims confirmed by lesson `02`'s run:

- **The unbounded-chunk warning is real, and the toy corpus could not show it.** On the 33-page PDF, `SemanticChunker` at the 90th percentile produced 62 chunks whose sizes ranged from 118 to **5,719 characters** (979 tokens) against a median of 752. That 7.6× spread over the median is the Part 5 argument in one line of output.
- **Semantic boundaries land on section starts.** The top hit for `"What is the main cause of climate change?"` began at "Understanding Climate Change / Chapter 1: Introduction to Climate Change" and ran to the end of the introduction — a self-contained passage containing the answer.
- **The character-splitter contrast is visible, not hypothetical.** At the same median size (752 chars, 103 chunks), its top hit for the same query *began mid-sentence* — "provide a historical record that scientists use to…" — and its second hit ended mid-word. Both still retrieved relevant material; neither passage stands on its own. This is the clearest evidence in the batch for the coherence claim, and it exists only because the end-to-end pipeline was restored.
- **Part 4's margin result held on the toy corpus:** mean margin 0.5340 → 0.6966, a 1.30× sharpening, with the character splitter's mixed chunk showing the expected blended vector (0.1439 / 0.5027).

## Next batch

`01_Foundations/` is complete. The lesson shape held across five notebooks of quite different character, so it is now the working template.

Remaining order: ingestion and embeddings, vector stores and chunking, indexing and retrieval, query transformation/routing, context and conversational RAG, then agentic/advanced/multimodal/evaluation batches. Each batch must update this manifest, `NOTEBOOK_INDEX.md`, and the roadmap map before the next batch begins.
