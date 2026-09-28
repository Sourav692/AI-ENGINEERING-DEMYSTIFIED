# RAG Curriculum

A concept-first route through Retrieval-Augmented Generation, with **one active teaching notebook per concept**. Built from `RAG_CURRICULUM.md` and executed in bounded batches recorded in `RAG_MIGRATION_MANIFEST.md`.

> **Status: `01_Foundations/` complete; `02_Chunking_and_Indexing/` 4 of 9 built.** Everything else is an empty scaffold.
>
> **Location.** This is a sibling track inside Phase 4 (`02_Core/04_Retrieval_and_RAG/RAG_Curriculum/`), not a top-level folder. It was built on the `RAG_Curriculum` branch as a top-level folder in September 2026 and ported here on 2026-09-28, after the stage restructure; paths in this folder were rewritten to the stage layout.
>
> **Scope inside Phase 4.** Phase 4 owns *foundational* RAG only. The plan's `06_Evaluation/`, `07_Agentic_RAG/` and `08_Advanced_Architectures/` folders are **out of scope for this track**: evaluation lives in the sibling repo `Agent_Evaluation_Demystified`, and anything that needs agents belongs to `03_Advanced/08_Advanced_RAG/`. They stay in `RAG_CURRICULUM.md` as a record of the original plan, not as folders to build here.
>
> **Retired sources.** The pilot lesson's seven source notebooks were retired to the repo's `archive/04_Retrieval_and_RAG/` (rows in `archive/RETIRED_MANIFEST.md`). Every other source under `02_Core/04_Retrieval_and_RAG/` and `03_Advanced/08_Advanced_RAG/` is still live.

## Build status

| Folder | Planned lessons | Built |
| --- | --- | --- |
| `00_Curriculum_Guide/` | 1 | 0 |
| `01_Foundations/` | 5 | **5** |
| `02_Chunking_and_Indexing/` | 9 | **4** |
| `03_Retrieval/` | 6 | 0 |
| `04_Query_Transformation_and_Routing/` | 8 | 0 |
| `05_Context_and_Generation/` | 7 | 0 |
| `06_Evaluation/` | 7 | 0 |
| `07_Agentic_RAG/` | 6 | 0 |
| `08_Advanced_Architectures/` | 7 | 0 |
| `09_Multimodal_RAG/` | 4 | 0 |
| `10_Production_RAG/` | 5 | 0 |
| `11_Applications_and_Capstones/` | 5 | 0 |
| **Total** | **70** | **9** |

Built lessons — `01_Foundations/`, complete:

| # | Lesson | Concept | Cells | Runs |
| --- | --- | --- | --- | --- |
| 01 | [RAG Lifecycle and Baseline](01_Foundations/01_RAG_Lifecycle_and_Baseline.ipynb) | `RAG-F-01` | 56 | 27/27 |
| 02 | [Document Loading and Metadata](01_Foundations/02_Document_Loading_and_Metadata.ipynb) | `RAG-F-02` | 45 | 22/22 |
| 03 | [Embeddings and Model Selection](01_Foundations/03_Embeddings_and_Model_Selection.ipynb) | `RAG-F-03` | 32 | 11/11 |
| 04 | [Vector Stores and Index Operations](01_Foundations/04_Vector_Stores_and_Index_Operations.ipynb) | `RAG-F-04` | 40 | 18/18 |
| 05 | [Structured Data RAG](01_Foundations/05_Structured_Data_RAG.ipynb) | `RAG-F-05` | 38 | 19/19 |

Every code cell in all five executes end to end against live services. Lesson 02 needs no API key at all.

Each lesson deliberately hands off rather than sprawling: 01 builds the whole pipeline at baseline depth, then 02–05 each take one stage deeper and name the later lesson that owns anything beyond their boundary.

Built lessons — `02_Chunking_and_Indexing/`, 4 of 9:

| # | Lesson | Cells | Runs |
| --- | --- | --- | --- |
| 01 | [Document Splitting and Chunking](02_Chunking_and_Indexing/01_Document_Splitting_and_Chunking.ipynb) | 39 | not recorded |
| 02 | [Semantic Chunking](02_Chunking_and_Indexing/02_Semantic_Chunking.ipynb) | 47 | 19/19 |
| 03 | [Proposition Chunking](02_Chunking_and_Indexing/03_Proposition_Chunking.ipynb) | 30 | not recorded |
| 04 | [Choosing Chunk Size](02_Chunking_and_Indexing/04_Choosing_Chunk_Size.ipynb) | 31 | not recorded |

Execution records for 01, 03 and 04 were not captured when they were built — see `RAG_MIGRATION_MANIFEST.md`.

## Reading the folder numbering

The folders are ordered as a learning path, and each has a deliberate boundary:

| Folder | What it changes |
| --- | --- |
| `01_Foundations` | The reusable building blocks |
| `02_Chunking_and_Indexing` | **What is indexed** |
| `03_Retrieval` | **How candidates are selected** |
| `04_Query_Transformation_and_Routing` | **The query, before retrieval** |
| `05_Context_and_Generation` | **The context supplied to generation** |
| `06_Evaluation` | How quality is measured |
| `07_Agentic_RAG` | Control loops and tools |
| `08_Advanced_Architectures` | Graph, hierarchy and memory architectures |
| `09_Multimodal_RAG` | Image and document modalities |
| `10_Production_RAG` | Production constraints |
| `11_Applications_and_Capstones` | End-to-end applications, kept with their code and data |

`_support/` holds dependencies, not lessons. `_archive/` is recoverable history and is excluded from the active route.

## Forward links

Built lessons link forward to lessons that do not exist yet. That is intentional: every such link names a destination declared in `RAG_CURRICULUM.md`'s target structure, so it marks where a topic will live rather than pointing at a file that was lost. Until a destination is built, the live content for that concept is still in its original phase folder.

## Relationship to Phases 4, 7 and 8

This folder is the consolidation target. The existing phases remain the source of truth for everything not yet migrated:

| Concept area | Current live home |
| --- | --- |
| Foundational RAG, chunking, retrieval, query transformation | `02_Core/04_Retrieval_and_RAG/` |
| RAG evaluation | sibling repo `Agent_Evaluation_Demystified` (`courses/01-rag-agent-tool-evaluation/`, `labs/rag-evaluation/`) — not in this repo |
| Agentic RAG, GraphRAG, the technique anthology, multimodal | `03_Advanced/08_Advanced_RAG/` |
| RAG applications | `05_Projects/`, plus application bundles inside Phases 4 and 8 |

Consult `RAG_MIGRATION_MANIFEST.md` before assuming a source notebook has been superseded. A source is only superseded once the manifest records its disposition **and** the canonical lesson has passed validation.

## Running the lessons

Lessons resolve their input assets through `_support/helpers/rag_paths.py` rather than relative paths, so they work regardless of notebook depth or the directory the kernel started in:

```python
import pathlib, sys
p = pathlib.Path.cwd()
while not (p / "RAG_Curriculum").is_dir() and p != p.parent:
    p = p.parent
sys.path.insert(0, str(p / "RAG_Curriculum" / "_support" / "helpers"))

from rag_paths import asset, repo_root
asset("Transformer.pdf")     # found wherever it currently lives
```

**LLM calls go through the shared factory**, not through directly-instantiated chat models:

```python
from helpers import get_experientiallabs_llm
llm = get_experientiallabs_llm(temperature=0.2)   # gpt-5.6-luna
```

This keeps provider and model configured in one place. Embeddings use `OpenAIEmbeddings` directly. Two keys are needed in the root `.env`: `EXPERIENTIALLABS_API_KEY` for generation and `OPENAI_API_KEY` for embeddings.

Environment, runtime and asset details are in [`_support/environment_and_path_manifest.md`](_support/environment_and_path_manifest.md). Every lesson also carries its own **Provenance and runtime status** cell stating which of its sections have actually been verified and which have not.
