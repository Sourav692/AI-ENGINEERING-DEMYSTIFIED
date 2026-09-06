# `.cleanup/`

Cleanup plans and the decisions taken on them, one pair of files per target folder.

A cleanup is the only operation in this repo that *removes* content. These files are the
record of what was proposed, what the human actually approved, and the evidence behind each
call — the thing `archive/RETIRED_MANIFEST.md` cannot hold, because a manifest row says a
notebook was retired without saying why it was the right call.

## Naming

```
<target-folder-name>_cleanup_plan.md
<target-folder-name>_cleanup_decisions.md
```

Paired by slug: `04_Chains_cleanup_decisions.md` belongs to `04_Chains_cleanup_plan.md` and
to nothing else. Folder names that recur across phases (`01_Foundations`, `LangGraph`) are
prefixed with their owning phase so plans never collide.

## Lifecycle

```
plan (status: draft) → user responds → decisions file → plan (status: decided)
    → notebook-folder-cleanup executes → plan (status: applied)
```

Item IDs (`NB-001`, `DUP-001`, `MIG-001`, `FMT-001`, `Q-001`) are permanent once issued.
The decisions file points at them by string, so a refresh adds new IDs and marks vanished
notebooks `(gone)` — it never renumbers.

## Producers

| Skill | Writes |
| --- | --- |
| `.claude/skills/notebook-folder-cleanup-planner/` | `*_cleanup_plan.md`, `*_cleanup_decisions.md` |
| `.claude/skills/notebook-folder-cleanup/` | updates `status:` and appends the run's changelog row |

## The one rule worth repeating here

An ID with no decision is **not** approved. For a `retire` row that means the file stays.
Silence is never permission to remove something.

These files are tracked in git on purpose, like `.plan/`.
