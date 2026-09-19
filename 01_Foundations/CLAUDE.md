<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working anywhere under this stage. Each phase inside also has its own CLAUDE.md, which is loaded on top of this one. -->

# Stage 01 — Foundations

**Entry rule: nothing in this stage may depend on a framework.** If the content needs LangChain, LangGraph, an agent or a retriever to make sense, it does not belong here.

| Phase | Owns |
|---|---|
| `00_Theory_and_Foundations/` | Python, HF ecosystem, fine-tuning, maths/architecture background |
| `02_Prompt_and_Context_Engineering/` | Prompting as a discipline, framework-independent |

## Routing — where does new content go?

- Teaches Python, HF, transformers, or fine-tuning → `00_Theory_and_Foundations/`
- Teaches prompting patterns independent of any framework → `02_Prompt_and_Context_Engineering/`
- Needs a framework to demonstrate → **not this stage.** Send it to `02_Core/`.

## Stage-wide convention

**Neither phase uses the `helpers` factory, and that is deliberate.** This stage teaches raw provider SDKs and HF pipelines; wrapping them in `get_llm()` would hide the subject. Zero notebooks here import it — keep it that way.

Requires the `hf` extra for the Hugging Face material (`uv pip install -e ".[hf]"`), a large download. Don't promote it into the core spine.

## Numbering

`00_` and `02_` with no `01_` — Phase 01 (LangChain) sits in `02_Core/`. Phase numbers were deliberately not renumbered when stage folders were introduced, so gaps inside a stage are expected, not errors to fix.
