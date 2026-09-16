# langchain-v1-migration (local plugin)

Groups the five LangChain 1.x migration pipeline skills in one place.

| Stage | Skill | Invoke as |
|---|---|---|
| 1. Audit → plan | `langchain-v1-migration-audit` | `/langchain-v1-migration:langchain-v1-migration-audit` |
| 2. Plan → task board | `plan-to-tasks` | `/langchain-v1-migration:plan-to-tasks` |
| 3. Tasks → teaching notebooks | `plan-to-teaching-notebook` | `/langchain-v1-migration:plan-to-teaching-notebook` |
| 4. Review gate | `notebook-review` | `/langchain-v1-migration:notebook-review` |
| All stages, unattended | `langchain-v1-pipeline` | `/langchain-v1-migration:langchain-v1-pipeline` |

Registered through the repo marketplace at `.claude-plugin/marketplace.json` and turned on in
`.claude/settings.json` (`enabledPlugins`). Claude Code copies marketplace plugins into its
plugin cache, so after editing a SKILL.md here run `/plugin` → update (or restart) to pick it up.
Scripts are always called by repo-relative path (`plugins/langchain-v1-migration/skills/...`),
so script edits take effect immediately.

The non-pipeline skills `notebook-folder-cleanup` and `notebook-folder-cleanup-planner` (still in
`.claude/skills/`) reuse this plugin's scanner and `md_to_notebook.py` by those same paths.
