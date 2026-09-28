# Proposed Multi-Repository Structure

This folder proposes how to split `AI-ENGINEERING-DEMYSTIFIED` into a sequence of smaller, self-contained repositories.

## Recommendation

Use this naming convention for every repository:

```text
ai-engineering-demystified-NN-topic-name
```

- `NN` is a zero-padded learning-order number (`01`, `02`, ... `14`).
- The number is the canonical order. Do not renumber after publishing; add new material inside the owning repository or reserve a future number.
- The topic name says what the repository owns, not which framework happens to implement it.

The proposed path is:

```text
01 foundations
   -> 02 prompt and context engineering
   -> 03 LangChain fundamentals
   -> 04 LangGraph fundamentals
   -> 05 retrieval and RAG
   -> 06 agent fundamentals
   -> 07 first-party agent SDKs
   -> 08 advanced agent systems
   -> 09 advanced RAG
   -> 10 agent protocols
   -> 11 alternative agent frameworks
   -> 12 AI coding tools
   -> 13 production and observability
   -> 14 projects
      ├── 01 foundational projects
      ├── 02 retrieval and agent projects
      └── 03 enterprise and realtime capstones
```

## Repository status

| # | Repository | Topic | Status |
|---|---|---|---|
| 01 | [ai-engineering-demystified-01-foundations](https://github.com/Sourav692/ai-engineering-demystified-01-foundations) | Foundations | ✅ Created (private), migrated 2026-09-29 |
| 02 | [ai-engineering-demystified-02-prompt-context-engineering](https://github.com/Sourav692/ai-engineering-demystified-02-prompt-context-engineering) | Prompt and context engineering | ✅ Created (private), migrated 2026-09-29 |
| 03 | [ai-engineering-demystified-03-langchain-fundamentals](https://github.com/Sourav692/ai-engineering-demystified-03-langchain-fundamentals) | LangChain fundamentals | ✅ Created (private), migrated 2026-09-29 |
| 04 | [ai-engineering-demystified-04-langgraph-fundamentals](https://github.com/Sourav692/ai-engineering-demystified-04-langgraph-fundamentals) | LangGraph fundamentals | ✅ Created (private), migrated 2026-09-29 |
| 05 | [ai-engineering-demystified-05-retrieval-rag](https://github.com/Sourav692/ai-engineering-demystified-05-retrieval-rag) | Retrieval and RAG | ✅ Created (private), migrated 2026-09-29 |
| 06 | [ai-engineering-demystified-06-agent-fundamentals](https://github.com/Sourav692/ai-engineering-demystified-06-agent-fundamentals) | Agent fundamentals | ✅ Created (private), migrated 2026-09-29 |
| 07 | [ai-engineering-demystified-07-first-party-agent-sdks](https://github.com/Sourav692/ai-engineering-demystified-07-first-party-agent-sdks) | First-party agent SDKs | ✅ Created (private), migrated 2026-09-29 |
| 08 | `ai-engineering-demystified-08-advanced-agent-systems` | Advanced agent systems | 🚧 Not yet created |
| 09 | `ai-engineering-demystified-09-advanced-rag` | Advanced RAG | 🚧 Not yet created |
| 10 | `ai-engineering-demystified-10-agent-protocols` | Agent protocols | 🚧 Not yet created |
| 11 | `ai-engineering-demystified-11-alternative-agent-frameworks` | Alternative agent frameworks | 🚧 Not yet created |
| 12 | `ai-engineering-demystified-12-ai-coding-tools` | AI coding tools | 🚧 Not yet created |
| 13 | `ai-engineering-demystified-13-production-observability` | Production and observability | 🚧 Not yet created |
| 14 | `ai-engineering-demystified-14-projects` | Projects | 🚧 Not yet created |

Repositories 01–07 were extracted from tag `pre-multirepo-split-2026-09` of this monorepo. Content they deferred to 08–14 stays here until those repositories are created; each repository's `docs/content-inventory.csv` lists it with `status=deferred`.

See:

- [REPOSITORY_CATALOG.md](REPOSITORY_CATALOG.md) for scope, boundaries, prerequisites, and current-source mappings.
- [STANDARD_REPO_LAYOUT.md](STANDARD_REPO_LAYOUT.md) for the structure every new repository should use.
- [MIGRATION_PLAN.md](MIGRATION_PLAN.md) for a safe extraction and validation sequence.
- [BOUNDARY_RULES.md](BOUNDARY_RULES.md) for the rules that prevent an earlier repository from teaching a later repository's topic.

## Core decisions

1. Each concept has one primary owner.
2. Earlier repositories must not teach topics owned by later repositories.
3. A later repository may briefly recap an earlier concept, but only to apply it in a new context.
4. Repositories depend on prior knowledge, never on files or Python packages from another course repository.
5. Every repository carries its own environment definition, sample data, helper code, tests, and `.env.example`.
6. The current `archive/` is not migrated into the teaching repositories. Preserve the monorepo as a read-only legacy archive after the split.
7. The already-separated `Agent_Evaluation_Demystified` and interview-preparation repository remain separate; link to them rather than copying their content back.

## Why 14 repositories

Thirteen repositories give each major concept a clear owner. One final projects repository keeps all 18 applications together, while three numbered group folders prevent it from becoming an unordered collection: basic component projects first, integrated retrieval/agent applications second, and enterprise/realtime systems last.

## Proposed umbrella navigation

Do not create a code dependency or shared-package repository. Instead, place the complete 14-repository table in:

- the GitHub organization/profile README;
- the README of every repository, with Previous/Next links; and
- a `docs/learning-path.md` file copied into each repository.

This keeps discovery easy without making any repository depend on a central catalog at runtime.
