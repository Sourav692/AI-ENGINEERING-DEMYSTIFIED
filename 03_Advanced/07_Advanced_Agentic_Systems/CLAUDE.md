<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working under this folder. Root rules still apply; this file adds what is specific to this phase. -->

# Phase 07 — Advanced Agentic Systems

**Owns:** composing agents into systems — memory, orchestration, harnesses. Stage `03_Advanced/`.

| Track | Content |
|---|---|
| `Memory_and_State/` | `LangGraph/` (memory & threads, long-term PostgreSQL memory, memory-layers tutorial series) + `LangChain/` (chat/conversation memory, multi-user SQL persistence) — both frameworks consolidated here, not left in their fundamentals phases |
| `Multi_Agent_Orchestration/` | Supervisor pattern, swarm architecture, production-course multi-agent |
| `Deep_Agents_and_Harness_Engineering/` | The `deepagents` framework — **has its own `CLAUDE.md`, read it** |

## Conventions here

- `helpers` factory used in 16 files — the heaviest user in the repo. Use it.
- Runs off the root env; no separate install. `python examples/simple_coding_agent.py` from the Deep Agents folder.

## Gotchas

- **`Deep_Agents_and_Harness_Engineering/app/` has hit a file lock during 3 separate restructurings.** If a move fails with "device busy"/"permission denied", drain its contents one level at a time, then remove the empty shell. Don't assume `git mv` will just work on it.

## Don't

- **Don't recreate an evaluation track here.** `Evaluation_and_Eval_Harnesses/` was removed 2026-09-19 — all of it lives in the sibling repo `Agent_Evaluation_Demystified` (`courses/` + `labs/`), which had already migrated the same material and kept it more current. Verified by content hash: 147 duplicated files, none unique. If eval content arrives, it goes to that repo.
