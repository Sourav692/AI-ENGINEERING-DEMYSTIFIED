# Learning Tracker

Tracks the user's **personal study progress** through this repo's 13-phase AI
Engineering roadmap — as a local, gitignored checklist the user checks off
themselves, notebook-existing-in-repo is NOT the same as concept-learned.

## When to Use

- The user invokes this skill directly (`/learning-tracker ...`).
- The user says things like "I completed `<folder>` end to end", "mark
  `<topic/notebook>` as done", "I finished the LangGraph fundamentals phase",
  "what's my progress", "what's left in Phase 4", "show me my tracker", or
  otherwise reports finishing/wants to check status on part of this repo's
  learning material.
- Do NOT use this for tracking migration/refactor tasks (that's `.tasks/` via
  `plan-to-tasks`) or for the repo's own build status (that's
  `NOTEBOOK_INDEX.md`) — this is exclusively the user's own learning progress.

## File Layout

```
.tracker/                      <- gitignored (never commit; see Setup below)
  TRACKER.md                   <- the concept checklist + overall progress summary
  progress/
    YYYY-MM-DD_HHMMSS.md       <- one file per completion report, append-only log
```

## Step 0 — Every Invocation: Verify Setup

Before doing anything else:

1. Check `.gitignore` at the repo root contains a `.tracker/` (or `.tracker`)
   entry. If missing, add it (with a short comment, matching the existing
   `.gitignore` comment style) — this must never be committed, it's the user's
   personal state.
2. Check whether `.tracker/TRACKER.md` exists.
   - **If missing → go to Step 1 (Bootstrap).**
   - **If present → go to Step 2 (Handle the Request).**

## Step 1 — Bootstrap (Only When `.tracker/TRACKER.md` Doesn't Exist)

This runs once, the first time the skill is ever invoked in this repo (or
after the user deliberately deletes `.tracker/` to rebuild).

1. Read `NOTEBOOK_INDEX.md` (source of truth for what's actually built —
   per `CLAUDE.md` its tables are more reliable than `README.md`) and
   `CLAUDE.md`'s Roadmap Structure section (source of truth for planned/
   aspirational tracks, marked 🚧).
2. Consult `graphify-out/` first if it exists and looks current (see
   `CLAUDE.md`'s "Navigating This Repo" section) to speed up re-reading large
   structure — but `NOTEBOOK_INDEX.md`/`CLAUDE.md` remain the authoritative
   content source, not the graph.
3. Build `.tracker/TRACKER.md` as a checklist, one `- [ ] **Concept** —
   \`path\`` line per **track/topic-group** (matching the granularity of
   `NOTEBOOK_INDEX.md`'s table rows — not one line per individual notebook,
   that would be too fine-grained to be useful; not one line per phase
   either, that's too coarse to tell what's actually done). Organize with
   `##` phase headers (matching the 13 phases) and `###` track sub-headers.
   Mark 🚧-planned tracks too, with a note that they have no content yet —
   the user may source/build material for them later and this file should
   already have a place for that.
   - **Every item starts unchecked (`- [ ]`)** regardless of whether the
     notebook already exists in the repo. This file tracks the user's
     learning, not the repo's build status.
4. Add an "Overall Progress" section at the top: total concept count, 0 done,
   0%, phases-complete count, "last updated: never".
5. Add a short header explaining the checkbox format and that this file is
   regenerated only on request, never automatically overwritten once it
   exists.
6. Create the empty `.tracker/progress/` folder.
7. Tell the user the tracker was created, roughly how many concepts it has,
   and that from now on they can report progress and it'll be tracked.

Use the existing `.tracker/TRACKER.md` in this repo (if you're reading this
after it was already bootstrapped once) as the concrete template for section
structure, checkbox format, and level of granularity — match it exactly for
any new sections rather than inventing a different format.

## Step 2 — Handle the Request (Normal Operation)

Read `.tracker/TRACKER.md` in full first.

### A. Completion report ("I completed X", "mark Y as done", "I finished Z end to end")

1. **Identify the matching concept line(s).** Match against the folder/
   notebook path or the topic wording the user gave, fuzzy-matching against
   the `- [ ]` lines' paths and bold concept text. A user statement can match:
   - **One track exactly** → straightforward, mark that one line.
   - **A whole phase or multiple tracks** (e.g. "I finished all of Phase 4") →
     mark every unchecked line under that `##`/`###` section.
   - **Something narrower than a tracked line** (e.g. one notebook out of a
     track bundling 5) → mark the whole line as done anyway (this tracker's
     granularity is track-level, not notebook-level) UNLESS the user is
     clearly working through a large multi-notebook track incrementally, in
     which case ask whether to (a) wait until the whole track is done, or
     (b) split that one line into per-notebook sub-checkboxes now for finer
     tracking — do whichever the user prefers, don't guess.
   - **No match found** — the wording doesn't correspond to anything in the
     tracker (e.g. a completely new folder that's shown up since bootstrap,
     or `production-course-main-code-main/` which is deliberately excluded).
     Ask the user whether to add a new tracker entry for it, rather than
     silently skipping or silently inventing one.
   - **Ambiguous match** (multiple plausible lines) — ask which one(s) rather
     than guessing.
2. **Mark each matched line done:** change `- [ ]` to `- [x]` and append
   ` _(done: YYYY-MM-DD)_` right after the path (use today's actual date).
   If the user mentioned a *specific* notebook/file that's more precise than
   the line's existing reference path, you may tighten the path to that
   specific reference — but don't lose the original track-level path if it
   covered multiple notebooks; keep the broader path and treat the user's
   mention as confirmation the whole thing is done.
3. **Update the "Overall Progress" section**: recount total `- [x]` vs total
   checklist lines, recompute the percentage, recount fully-complete phases
   (every line under a `##` phase header checked), and set "Last updated" to
   today's date.
4. **Log it.** Create `.tracker/progress/<YYYY-MM-DD_HHMMSS>.md` (use the
   actual current timestamp) containing: the user's original completion
   statement, the exact concept line(s) marked done with their paths, and the
   new overall progress percentage. This is an append-only audit trail — never
   edit or delete older progress files.
5. Confirm back to the user in the chat: what got checked off, and the new
   overall percentage. Keep it short — a couple of lines, not a essay.

### B. Status query ("what's my progress", "what's left in Phase X", "show me the tracker")

Read `.tracker/TRACKER.md` and answer directly from it — don't re-derive
anything from `NOTEBOOK_INDEX.md`. For "what's left," list the unchecked
lines in the relevant scope. For general progress, report the Overall
Progress numbers plus a one-line per-phase breakdown if helpful. No need to
touch `progress/` for a read-only query.

### C. Structural drift ("this folder doesn't exist anymore", "there's a new phase/track")

If the user points out the tracker is out of sync with the repo (a path
moved, a track was added), update just that section of `TRACKER.md` in place
— do not regenerate the whole file from scratch (that would discard
checked-off progress). Preserve any existing checked state for concepts that
still logically exist under their new path.

## Rules

- **Never mark something done that the user didn't say was done.** No
  inferring completion from the notebook merely existing or from unrelated
  conversation about a topic.
- **Never regenerate `TRACKER.md` from scratch once it exists**, except when
  the user explicitly asks for a full rebuild (and even then, confirm first
  since it discards checked-off state unless they still have the `progress/`
  logs to manually reconcile from).
- **Always write a progress log entry for every completion report** — that's
  the audit trail the user asked for, don't skip it even for a single small
  item.
- Keep `.tracker/` entirely out of git — verify the `.gitignore` entry every
  time (Step 0), since a future edit to `.gitignore` elsewhere could
  accidentally remove it.
