# Lesson sources

Lessons are authored as `%%`-delimited markdown and converted to `.ipynb` by `build_lesson.py`,
rather than by hand-editing notebook JSON. Editing the `.src.md` and rebuilding is the intended
workflow; editing the `.ipynb` directly means the source here goes stale.

```bash
python RAG_Curriculum/_support/lesson_sources/build_lesson.py \
       RAG_Curriculum/_support/lesson_sources/01_RAG_Lifecycle_and_Baseline.src.md \
       RAG_Curriculum/01_Foundations/01_RAG_Lifecycle_and_Baseline.ipynb
```

## Format

| Marker | Meaning |
| --- | --- |
| `%%markdown` | Start a markdown cell |
| `%%code` | Start a code cell |
| `%%code tags=a,b` | Code cell with notebook cell tags (e.g. `legacy-contrast`) |
| `%%markdown attach=<key>` | Markdown cell carrying an image attachment, pulled from a donor notebook via `ATTACHMENT_MAP` |

The builder emits cleared outputs and null `execution_count` (the repo's `nbstripout` contract),
assigns stable per-cell ids, and copies donor attachments so diagrams survive consolidation.

`ATTACHMENT_MAP` in `build_lesson.py` points at the archived donor
(`RAG_Curriculum/_archive/.../1_rag_overview.ipynb`), falling back to the original path if the
archive is ever restored.
