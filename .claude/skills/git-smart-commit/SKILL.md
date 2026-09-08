---
name: git-smart-commit
description: >-
  Commit changes cleanly in a Python-based AI/ML or Agentic AI Engineering
  repo. Use this whenever the user asks to commit, git commit, stage my
  changes, push this, or clean up my repo before committing — especially in
  repos that use vector databases (Chroma, FAISS, Pinecone, Weaviate,
  Qdrant), LangChain/LangGraph agents, Jupyter notebooks, or virtual
  environments. Make sure to trigger this even if the user doesn't mention
  .gitignore by name — any mention of accidentally committed cache files,
  bloated repos, __pycache__, .pyc files, local vector store folders,
  checkpoint files, or what to ignore in a Python/ML context should trigger
  this skill. Also use it to audit and repair an existing .gitignore, or to
  strip already-tracked junk files out of git history going forward.
allowed-tools: >-
  Bash(git status *) Bash(git diff *) Bash(git ls-files *)
  Bash(git rev-parse *) Bash(git add *) Bash(git rm --cached *)
  Bash(git commit *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/preflight_check.py *)
---

# Git Smart Commit (Python / Agentic AI Engineering repos)

## Why this skill exists

AI Engineering repos are messier than typical Python repos. Beyond the usual
`__pycache__/` and virtual environments, every run of the code can generate:

- **Persisted vector stores** — Chroma writes a `chroma.sqlite3` + UUID-named
  folders wherever you point `persist_directory`; FAISS dumps `.index` /
  `.faiss` files; local Qdrant/Weaviate write whole data directories.
- **Model & embedding artifacts** — downloaded checkpoints, `.safetensors`,
  `.gguf`, HuggingFace caches.
- **Notebook cruft** — `.ipynb_checkpoints/`, cell-execution noise.
- **Secrets** — `.env` files holding API keys for OpenAI/Anthropic/Databricks.

None of this is source code. If it gets committed once, it tends to keep
getting re-committed every run because git already tracks it — the `.gitignore`
entry alone won't fix a file that's already staged in history. So this skill
does two jobs, not one: **prevent** future junk from being staged, and
**detect + fix** junk that's already tracked.

## Workflow

Follow these steps in order. Don't skip straight to `git commit` — the value
of this skill is in steps 1–3, which is where repos usually go wrong.

### Step 1 — Make sure `.gitignore` is actually complete

Read `${CLAUDE_SKILL_DIR}/assets/gitignore-ai-engineering.txt` (a maintained
template covering Python, Jupyter, common vector DBs, and OS/IDE noise).
Compare it against the repo's current `.gitignore`:

- If there's no `.gitignore`, copy the template in as-is.
- If one exists, merge in any missing sections rather than overwriting —
  preserve whatever custom rules the user already added, and append missing
  categories under clearly commented headers (e.g. `# Vector stores`).
- Ask the user which vector DB(s) and frameworks are actually in play only if
  it's not obvious from the repo (e.g. `requirements.txt`, `pyproject.toml`,
  or import statements) — otherwise infer it and mention what you added.

### Step 2 — Run the preflight check

Run the bundled script from the repo root:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/preflight_check.py
```

This script (no dependencies beyond stdlib + git) does three things:

1. Lists **untracked files that match ignore patterns but aren't yet
   covered by `.gitignore`** — the stuff that's about to get accidentally
   staged.
2. Lists **already-tracked files that match junk patterns** — these got
   committed before a `.gitignore` existed, and adding a rule now won't
   remove them. These need `git rm --cached <file>` (keeps the file on disk,
   removes it from git going forward).
3. Buckets the remaining real changes into source vs. config vs. docs, so you
   can sanity-check what's about to be committed.

Walk the user through any files in bucket 2 before removing them — that's a
history-changing action worth a quick confirmation, even though it's just
`--cached` and won't touch their working copy.

### Step 3 — Stage only what belongs

- Stage source, config, and docs changes the user actually intends to commit.
- Never blanket `git add .` in these repos — a single stray `chroma_db/` or
  `.env` slipping through defeats the point of step 1. Prefer explicit
  `git add <path>` for anything not already covered cleanly by `.gitignore`.
- If large model or data files are intentionally tracked (e.g. via Git LFS),
  don't flag them as junk — check for a `.gitattributes` with `filter=lfs`
  entries first and respect it.

### Step 4 — Write the commit message

Use Conventional Commits. Read `${CLAUDE_SKILL_DIR}/references/commit-conventions.md`
for the full type list and AI-engineering-flavored examples (agent changes,
prompt tweaks, retrieval pipeline changes, eval harnesses, etc.) — this
repo's commits benefit from a type system that distinguishes "changed a
prompt" from "changed retrieval logic" from "added an eval," since those
have very different review implications.

Base the message on the actual diff (`git diff --staged`), not just the
filenames — a good subject line names *what changed functionally*, not just
which files touched.

### Step 5 — Commit

Show the user the exact commit that will run (files staged + message) and
then execute:

```bash
git commit -m "<type>(<scope>): <subject>" -m "<optional body>"
```

Don't push automatically. Pushing to a remote sends data off the user's
machine and should only happen if they ask for it explicitly in this
conversation.

## Edge cases worth knowing

- **Monorepo with multiple vector stores per experiment**: if the user's repo
  pattern is "one Chroma folder per notebook run" (e.g. `experiments/*/chroma_db/`),
  a single top-level ignore rule (`**/chroma_db/`) handles all of them — don't
  write one rule per experiment folder.
- **`.env.example` vs `.env`**: only the latter should ever be ignored — the
  example file is meant to be committed. Check the template handles this
  distinction before applying it.
- **Partial commits (`git add -p`)**: if the user only wants to commit part of
  their changes, still run the preflight check first so ignored junk doesn't
  end up in the same patch review.

## Additional resources

- `references/commit-conventions.md` — full Conventional Commits type table
  and before/after examples for agent, retrieval, and eval changes.
- `assets/gitignore-ai-engineering.txt` — the template applied in Step 1.
- `scripts/preflight_check.py` — the script run in Step 2.
