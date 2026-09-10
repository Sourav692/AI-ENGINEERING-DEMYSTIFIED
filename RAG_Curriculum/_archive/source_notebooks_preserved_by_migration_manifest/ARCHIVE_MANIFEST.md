# Archive Manifest — basic-RAG pilot batch

Retired 2026-09-10, after `RAG_Curriculum/01_Foundations/01_RAG_Lifecycle_and_Baseline.ipynb` passed full execution validation (27/27 cells).

**Nothing here was deleted.** Every file was *moved*, byte-for-byte, and its SHA-256 verified identical after the move. The directory tree below mirrors each notebook's original path exactly, so restoring is a plain copy.

**These are not active lessons.** They are excluded from the curriculum route and from uniqueness checks. Do not link to them from teaching material; link to the canonical lesson instead.

## Contents and restore mapping

| Archived file (relative to this folder) | Original location | SHA-256 | Bytes |
| --- | --- | --- | --- |
| `04_Retrieval_and_RAG/09_RAG_with_LangChain/7.1_RAG_Comprehensive.ipynb` | same | `d6b4abdace3c7ae2…` | 82,374 |
| `04_Retrieval_and_RAG/09_RAG_with_LangChain/7.0_RAG_Essentials.ipynb` | same | `e9ee69318d3f68c6…` | 20,700 |
| `04_Retrieval_and_RAG/01_Introduction_to_RAG/1_rag_overview.ipynb` | same | `95172c564fbaaeb3…` | 813,838 |
| `04_Retrieval_and_RAG/01_Introduction_to_RAG/Basics of RAG.ipynb` | same | `9240d9a628313f5a…` | 6,827 |
| `04_Retrieval_and_RAG/01_Introduction_to_RAG/Naive_RAG.ipynb` | same | `c94dbdf57369407f…` | 7,557 |
| `04_Retrieval_and_RAG/01_Introduction_to_RAG/Naive_RAG_Alt.ipynb` | same | `fed822b42c2dcd47…` | 7,560 |
| `04_Retrieval_and_RAG/RAG_Production_Course/06_rag_pipeline.ipynb` | same | `f4b43440b77c3935…` | 27,488 |

Full checksums are in `RAG_MIGRATION_MANIFEST.md`.

## Why each one was retired

| File | Disposition | Reason |
| --- | --- | --- |
| `7.1_RAG_Comprehensive.ipynb` | canonical source | Primary structural source for the new lesson. Its full teaching content is preserved there. |
| `7.0_RAG_Essentials.ipynb` | archive-candidate | Superseded by `7.1` on the same material, entirely on LangChain 0.x APIs. Its `return_source_documents` provenance idea survives in the lesson's legacy-contrast cell. |
| `1_rag_overview.ipynb` | donor | Four-component framing, phase split, validation checkpoints, token counting, and **all three diagrams** carried into the lesson as attachments. |
| `Basics of RAG.ipynb` | donor | The TF-IDF + nearest-neighbour mechanism demo is now the lesson's Part 2 — reclassified from archive-candidate once inspection showed it was not a duplicate baseline. |
| `Naive_RAG.ipynb` | donor | Stage naming and scored retrieval carried over. **Could not run as archived**: `CHROMA_PATH = "/usr/local/notebooks"` is an absolute POSIX path, and `DOC_PATH = "Transformer.pdf"` does not resolve from its own directory. |
| `Naive_RAG_Alt.ipynb` | support → archived | Diffed identical to `Naive_RAG.ipynb` except for two credential-plumbing cells. Retiring the original while keeping a near-identical variant as the only active copy would have left a worse state, so both went together. This is a deliberate change to its recorded disposition. |
| `06_rag_pipeline.ipynb` | donor | Fallback, structured output, source attribution and the `DocumentQA` exercise all carried into the lesson. |

## Restoring

```bash
# One file, back to where it came from:
cp "RAG_Curriculum/_archive/source_notebooks_preserved_by_migration_manifest/04_Retrieval_and_RAG/01_Introduction_to_RAG/Naive_RAG.ipynb" \
   "04_Retrieval_and_RAG/01_Introduction_to_RAG/Naive_RAG.ipynb"

# Everything, in one go (paths already mirror the originals):
cp -r "RAG_Curriculum/_archive/source_notebooks_preserved_by_migration_manifest/04_Retrieval_and_RAG" .
```

Restoring puts the files back where they were. It does **not** undo the accompanying edits to `NOTEBOOK_INDEX.md`, the folder `README.md`s, or `tutorials/02_rag_and_retrieval_INTERVIEW_TUTORIAL.md`, which now point at the canonical lesson — revert those separately if you want the previous state exactly.

## Runtime caveat

These are preserved for **recovery and provenance**, not as working notebooks. No claim is made that any of them executes in place today:

- `Naive_RAG.ipynb` / `Naive_RAG_Alt.ipynb` have the broken paths described above, and import a local `utils.py` that is still in `01_Introduction_to_RAG/` — restoring the notebook alone is enough for that import, but the paths remain broken.
- `7.0` and `7.1` use LangChain 0.x imports (`langchain.chains`, `langchain.prompts`, `langchain.vectorstores.faiss`) that raise `ModuleNotFoundError` on this repository's LangChain 1.4. The migration table is in `RAG_Curriculum/_support/environment_and_path_manifest.md`.
- `7.1` also reads `./bella_vista.txt` and `FAISS.load_local("index", ...)`, which resolve only when the kernel starts in `09_RAG_with_LangChain/`. Both of those assets are still there, untouched.

No `.env`, credentials, or secret-bearing outputs were copied into this archive.
