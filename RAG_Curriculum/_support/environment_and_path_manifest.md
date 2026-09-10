# Environment and Path Manifest

Required by `RAG_CURRICULUM.md` section 7A/7C/7D. Records the runtime the curriculum is validated against, where input assets actually live, and how lessons reach them.

Created during the basic-RAG pilot batch on September 10, 2026. Covers only what the pilot touched; extend it with each batch.

## 1. Runtime matrix

Verified against the interpreter this repository's notebooks currently run on (`03_LangGraph_Fundamentals/.venv`, Python 3.12).

| Package | Version | Notes |
| --- | --- | --- |
| `langchain` | 1.4.0 | **1.x.** Exposes only `agents`, `chat_models`, `embeddings`, `mcp`, `messages`, `rate_limiters`, `tools`. |
| `langchain-core` | 1.6.1 | `prompts`, `runnables`, `output_parsers`, `documents`. |
| `langchain-classic` | 1.0.8 | Where every pre-1.x chain abstraction was retired to. |
| `langchain-community` | 0.4.2 (pinned) | Emits a sunset `DeprecationWarning` on import. Retained: no standalone FAISS or PyPDF integration package is available. |
| `langchain-openai`, `langchain-text-splitters`, `langchain-chroma` | per `requirements.txt` | |
| `faiss`, `scikit-learn`, `tiktoken`, `numpy`, `pandas`, `pydantic`, `python-dotenv` | per `requirements.txt` | |
| `pypdf` | 6.17.0 | Declared in `pyproject.toml` and pinned in `requirements.txt`, but **was not installed** in the venv these notebooks run on. Installed at the pinned version on 2026-09-10 after it broke the pilot's PDF cell. |
| `unstructured` | 0.27.5 | Declared in `pyproject.toml`; installed 2026-09-10 for lesson 02 (34 transitive packages — spacy, numba, llvmlite). **Purely additive: no pinned package was changed.** Needs a per-format extra; its `.docx` path hung past 110s on `Intel Strategy.docx`, so lesson 02 uses `Docx2txtLoader` for Word. |
| `docx2txt` | 0.9 | Declared; installed 2026-09-10. The reliable Word loader. |
| `markdown` | 3.10.3 | **Not declared anywhere** — installed 2026-09-10 because `unstructured.partition.md` imports it. Add it to `pyproject.toml` if lesson 02's Markdown section should be a hard requirement. |
| `jq` | **not installed, by design** | `JSONLoader` needs it; it requires a C toolchain and does not build on Windows. Lesson 02 teaches the `JSONLoader` API but uses plain `json` + `Document` construction throughout, which is portable and often clearer. Not a gap to close. |
| `torch` / `transformers` / `sentence-transformers` | **not installed** | This repository's `hf` extra, a multi-gigabyte download. Lesson 03's local-embeddings section is behind a `RUN_LOCAL_MODEL = False` flag. |
| `helpers` (this repo) | editable install | Provides `get_experientiallabs_llm`. Import it as `from helpers import ...`; the `rag_paths` bootstrap adds `_support/helpers/` to `sys.path` but does not shadow this package. |

### Environment provisioning gap

There is **no `.venv` at the repository root**, despite `CLAUDE.md`'s setup instructions. Notebooks currently run on `03_LangGraph_Fundamentals/.venv` (Python 3.12.14), which is under-provisioned relative to `pyproject.toml`. Gaps found so far: `pypdf`, `unstructured`, `docx2txt` (all declared but absent), and `markdown` (needed by `unstructured` but declared nowhere).

Install the **pinned** version from `requirements.txt` rather than resolving fresh, and **dry-run first** (`uv pip install --dry-run`) to confirm the install is purely additive. `unstructured` pulls 34 transitive packages; it happened not to disturb any existing pin, but that was verified rather than assumed.

### LangChain 1.x import migration

Inherited from the pilot's LangChain 0.x source notebooks. These raise `ModuleNotFoundError` rather than warning, so they are hard failures:

| LangChain 0.x | LangChain 1.x |
| --- | --- |
| `langchain.chains.retrieval` | `langchain_classic.chains.retrieval` |
| `langchain.chains.combine_documents` | `langchain_classic.chains.combine_documents` |
| `langchain.chains` (`RetrievalQA`) | `langchain_classic.chains` |
| `langchain.prompts` | `langchain_core.prompts` |
| `langchain.vectorstores.faiss` | `langchain_community.vectorstores` |
| `langchain.text_splitter` | `langchain_text_splitters` |
| `langchain.schema` (`Document`) | `langchain_core.documents` |

The repository's `langchain-v1-migration-audit` skill covers this class of change across the wider repo.

## 2. Environment variables

Names only; values live in the repository-root `.env`, which is never copied into this folder or into any archive.

| Variable | Used by | Needed from |
| --- | --- | --- |
| `EXPERIENTIALLABS_API_KEY` | **All generation.** `helpers.get_experientiallabs_llm()` → `gpt-5.6-luna`, a `ChatOpenAI` pointed at `https://api.experientiallabs.ai/v1`. | Lesson 01 Part 4 onward |
| `OPENAI_API_KEY` | **Embeddings only** — `text-embedding-3-small`. | Lesson 01 Part 3 onward |

**Provider convention for this curriculum:** lesson notebooks do **not** instantiate chat models directly. Every LLM call goes through `helpers.get_experientiallabs_llm()`, so provider and model are configured in one place. This matches the `helpers`-factory convention that `CLAUDE.md` already mandates for LangGraph-phase notebooks, and extends it here. Embeddings still use `OpenAIEmbeddings` directly; verified working alongside the Experiential Labs generation endpoint.

`with_structured_output` was confirmed working on `gpt-5.6-luna` before the pilot adopted it, since it is not guaranteed on every OpenAI-compatible endpoint.

Lessons load these with `load_dotenv(repo_root() / ".env")`. **Do not use `find_dotenv()`**: it infers the path by walking caller stack frames and raises `AssertionError` outside a normal interactive kernel.

## 3. Asset roots

`_support/helpers/rag_paths.py` resolves assets by filename across these roots, in order. The curriculum's own folder is first so a local copy can later supersede a stationary source without editing any notebook.

1. `RAG_Curriculum/_support/shared_data/` *(currently empty — see section 4)*
2. `04_Retrieval_and_RAG/shared_data/`
3. `04_Retrieval_and_RAG/09_RAG_with_LangChain/`
4. `04_Retrieval_and_RAG/01_Introduction_to_RAG/`
5. `04_Retrieval_and_RAG/02_Embeddings_and_Vector_Databases/data/`
6. `08_Advanced_RAG/Comprehensive_RAG_Techniques/data/`
7. `08_Advanced_RAG/Comprehensive_RAG_Techniques/images/`

A missing asset raises `FileNotFoundError` listing every root searched. It never falls back to a different file that happens to share a basename — section 7B forbids treating a filename match as proof of interchangeability. `rag_paths.find_all()` returns every candidate when a lesson needs to disambiguate.

## 4. Asset movement policy

**No assets have been moved.** Section 7B requires shared corpora to stay put during early passes; the resolver is what makes that possible without fragile relative paths.

| Asset | Resolved location | Used by |
| --- | --- | --- |
| `bella_vista.txt` | `04_Retrieval_and_RAG/09_RAG_with_LangChain/` | Lesson 01, main corpus |
| `Transformer.pdf` | `04_Retrieval_and_RAG/shared_data/` | Lesson 01, PDF loading demo |

Both were previously referenced by hardcoded paths that do not resolve from their notebooks' own directories — `./bella_vista.txt` in `7.1_RAG_Comprehensive.ipynb`, and `DOC_PATH = "Transformer.pdf"` in `Naive_RAG.ipynb`, whose file actually lives in `shared_data/`. This is the path fragility recorded in `CLAUDE.md`'s Known Gaps; the resolver fixes it for migrated lessons only. Both source notebooks are now archived; other un-migrated notebooks still carry their own original broken references.

## 5. Generated artifacts and protected state

Section 7D: immutable inputs are separated from generated outputs, and validation must not overwrite existing indexes.

| Artifact | Policy |
| --- | --- |
| Lesson vector stores | Written to `tempfile.mkdtemp(prefix="rag_lesson01_")`. Never persisted into the repository. |
| `04_Retrieval_and_RAG/09_RAG_with_LangChain/index/` | **Protected.** A pre-existing FAISS store, loaded by the now-archived `7.1_RAG_Comprehensive.ipynb`. Never read or written by the curriculum; left in place so a restored archive still works. |
| `04_Retrieval_and_RAG/09_RAG_with_LangChain/vs_db/` | **Protected.** Written by the now-archived `7.1_RAG_Comprehensive.ipynb`. Never read or written by the curriculum; left in place for the same reason. |
| `CHROMA_PATH = "/usr/local/notebooks"` in `Naive_RAG.ipynb` | Pre-existing defect: an absolute POSIX path that cannot resolve on this Windows working tree. Not repaired — the notebook was archived rather than fixed, and the canonical lesson writes to `tempfile.mkdtemp()` instead. |

## 6. Module-name collisions

Section 7C requires that local module names resolve to the intended module rather than to whichever directory reaches `sys.path` first.

| Name | Collision |
| --- | --- |
| `utils` | Three distinct `utils.py` files under `04_Retrieval_and_RAG/` (`01_Introduction_to_RAG/`, `04_Query_Transformation_Techniques/`, `10_RAG_with_LlamaIndex/`), each with different contents. Any notebook doing `from utils import ...` binds to whichever directory is first on `sys.path`. |
| `helpers` | The installed repository package (`helpers/utils.py`, providing `get_llm`, `get_embeddings`, `get_experientiallabs_llm`) shares its name with per-project `helpers/` directories elsewhere, e.g. `08_Advanced_RAG/GraphRAG/helpers/`. |

The resolver is therefore named **`rag_paths`** — deliberately neither `utils` nor `helpers` — so it can neither shadow nor be shadowed by any of these.

## 7. Validation layers and current status

Per section 7F. Recorded honestly: a skipped test is not a passing test.

| Layer | Status for the pilot |
| --- | --- |
| 1. Static — nbformat schema, cell ids, AST parse, cleared outputs, banner conventions, attachment binding, tag survival | **PASS** |
| 2. Imports — every distinct import executed against the real environment | **PASS** (25/25, after correcting four LangChain 0.x imports) |
| 3. Isolated offline execution — fresh namespace, no network, temporary outputs | **PASS**, 6 cells |
| 4. Service-backed execution — full run-all with real API calls | **PASS — 27/27 code cells**, in order, in a fresh namespace, 2026-09-10. 52s wall time. Cost: 13 completions (2,664 in / 370 out tokens) plus ~20 embedding calls. Authorized by the user. |
| 5. Regression comparison against source behaviour | **Not performed — no usable baseline.** Five of the six sources ship with outputs stripped by `nbstripout`, so no recorded prior behaviour exists to compare against. The sixth (`1_rag_overview.ipynb`) retains outputs but runs over a different corpus (a web blog post, not `bella_vista.txt`), so its results are not comparable. |

### What layer 4 actually confirmed

Behavioural claims the lesson makes, checked against real output:

- Cosine similarity separates meaning as taught: identical `1.0000`, paraphrase `0.6341`, unrelated `0.0016`.
- Part 2's lexical baseline fails on paraphrase at cosine distance `1.0000` (fully orthogonal) — the motivation for embeddings is real, not asserted.
- Indexing integrity holds: 9 chunks → 9 vectors, preserved across a disk round trip.
- The out-of-scope fallback refused both out-of-scope questions and answered the in-scope one.
- `with_structured_output` returned a validated `RAGResponse` object.
- The deprecated `RetrievalQA` contrast cell still executes, returning an answer plus 4 source documents.

Retirement of the pilot's six source notebooks is therefore **unblocked**, pending a separate decision to archive them.
