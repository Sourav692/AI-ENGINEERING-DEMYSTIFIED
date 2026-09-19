# Appendices

| Appendix | What it is |
|---|---|
| [A · Glossary](A_Glossary.md) | Every term in the handbook, one line each, linked to the document that teaches it — grouped by level |
| [B · Source Map](B_Source_Map.md) | Every handbook document → the original file(s) it was built from, with the treatment applied (rewritten, copied, new, project code) and a list of what was deliberately not carried over |
| [C · Interview Q&A Log](C_Interview_QA_Log.md) | A running log of conceptual questions and answers from the Enterprise RAG project's preparation sessions — kept as a reference artefact |
| [D · Progress Checklist](D_Progress_Checklist.md) | One box per module checkpoint and lab; tick only when you can pass without looking |

## Growing the handbook

The handbook is designed to absorb new material. When adding:

1. **Place it in a level.** A new topic belongs at the level whose plateau it extends — Foundations, Building, Scale/Security/Ops, or Mastery/FDE.
2. **Give it the standard header** — level, module, doc number, time, prerequisites, source material — and end with a Checkpoint and a Next pointer.
3. **Record provenance in the Source Map** with a treatment code, and add any new terms to the Glossary.
4. **If it is a project, copy it into a `project/` folder** minus generated artefacts, and strip its docs into rewritten handbook documents; keep its scripts and README runnable.
5. **If it is a performance artefact** — a script, a narrative, a quick reference — copy it with a header rather than rewriting it; those are used by rehearsing, not by reading.
6. **Update the module README's reading order and the Progress Checklist.**
