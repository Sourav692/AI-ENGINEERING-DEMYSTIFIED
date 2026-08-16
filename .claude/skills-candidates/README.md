# Skill Candidates — Pending Review

Skills recovered from merged-in source repos, not yet wired into `.claude/skills/`. Claude Code does not auto-load skills from this folder — that's intentional, so nothing here activates until you've reviewed it.

| Skill | Source | What it does |
|---|---|---|
| `format-notebook/` | `LangChain_Demystified-main` (merged 2026-08-16) | Reformats Jupyter notebooks for educational readability |
| `virtual-env-setup/` | `LangChain_Demystified-main` (merged 2026-08-16) | Creates/manages Python venvs via `uv` + `pyproject.toml` |

Note: `AgenticAI_Projects_Demystified-main` (merged 2026-08-17) had byte-identical copies of both — no new candidates added from that merge.

To activate one: move its folder into `.claude/skills/`.
