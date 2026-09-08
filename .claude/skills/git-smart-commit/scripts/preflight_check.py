#!/usr/bin/env python3
"""
preflight_check.py
-------------------
Stdlib-only sanity check for git-smart-commit.

Run from anywhere inside a git repo:
    python scripts/preflight_check.py

What it reports:
  1. Untracked files that match known "junk" patterns but are NOT yet
     covered by .gitignore (about to be accidentally staged).
  2. Already-TRACKED files that match junk patterns (a .gitignore rule
     won't remove these — they need `git rm --cached`).
  3. A quick bucket breakdown (source / config / docs / other) of the
     real pending changes, so the user can sanity check before staging.

Exit code is always 0 — this is a reporting tool, not a gate.
"""

import fnmatch
import subprocess
import sys
from pathlib import Path

# Patterns mirrored from assets/gitignore-ai-engineering.txt.
# Kept independently here so this script works even before a .gitignore
# exists at all (that's the whole point of "detect junk that isn't ignored yet").
JUNK_PATTERNS = [
    "__pycache__", "*.pyc", "*.pyo", "*.pyd",
    ".venv", "venv", "env", "ENV",
    ".env", ".env.*",
    "*.egg-info", ".eggs", "build", "dist",
    ".ipynb_checkpoints",
    "chroma_db", ".chroma", "chroma.sqlite3",
    "*.faiss", "*.index", "faiss_index",
    "qdrant_storage", "weaviate_data", ".lancedb",
    "vectorstore", "vector_store", "*.vecs",
    "*.safetensors", "*.gguf", "*.bin", "*.ckpt", "*.pt", "*.onnx",
    ".cache",
    ".langgraph_api", ".langsmith",
    "*.log", "logs", "runs", "outputs", "*.tmp", "*.bak", "tmp", "scratch",
    "mlruns", "mlflow.db", ".mlflow",
    ".DS_Store", "Thumbs.db", ".vscode", ".idea", "*.swp",
    ".pytest_cache", ".coverage", "htmlcov", ".mypy_cache", ".ruff_cache",
]

# Files that look like junk by pattern but should never be flagged.
ALLOWLIST = {".env.example", ".env.sample", ".env.template"}

SOURCE_EXT = {".py", ".pyx", ".pyi"}
CONFIG_EXT = {".yaml", ".yml", ".toml", ".ini", ".cfg", ".json"}
DOCS_EXT = {".md", ".rst", ".txt"}


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return result.stdout.strip("\n")


def is_junk(path_str):
    name = Path(path_str).name
    if name in ALLOWLIST:
        return False
    parts = Path(path_str).parts
    for pattern in JUNK_PATTERNS:
        if fnmatch.fnmatch(name, pattern):
            return True
        if any(fnmatch.fnmatch(part, pattern) for part in parts):
            return True
    return False


def bucket(path_str):
    ext = Path(path_str).suffix.lower()
    if ext in SOURCE_EXT:
        return "source"
    if ext in CONFIG_EXT:
        return "config"
    if ext in DOCS_EXT:
        return "docs"
    return "other"


def main():
    toplevel = run(["git", "rev-parse", "--show-toplevel"])
    if toplevel is None:
        print("Not inside a git repository (or git isn't installed).")
        sys.exit(0)

    # Untracked files, respecting whatever .gitignore already exists.
    untracked_visible = run(
        ["git", "ls-files", "--others", "--exclude-standard"]
    )
    untracked_visible = untracked_visible.splitlines() if untracked_visible else []

    # All tracked files.
    tracked = run(["git", "ls-files"])
    tracked = tracked.splitlines() if tracked else []

    junk_not_ignored = [f for f in untracked_visible if is_junk(f)]
    junk_but_tracked = [f for f in tracked if is_junk(f)]

    print(f"Repo: {toplevel}\n")

    print("=" * 60)
    print("1) Untracked junk NOT yet in .gitignore")
    print("=" * 60)
    if junk_not_ignored:
        for f in junk_not_ignored:
            print(f"  [ADD TO .gitignore]  {f}")
    else:
        print("  None found — .gitignore is catching everything visible.")

    print()
    print("=" * 60)
    print("2) Already-TRACKED junk (needs `git rm --cached`)")
    print("=" * 60)
    if junk_but_tracked:
        for f in junk_but_tracked:
            print(f"  [git rm --cached '{f}']")
    else:
        print("  None found — no junk currently tracked in git history.")

    # Real pending changes: modified + added + untracked (minus junk).
    status = run(["git", "status", "--porcelain", "-uall"])
    status_lines = status.splitlines() if status else []
    pending = []
    for line in status_lines:
        # porcelain format: XY <path>  (path may be quoted if it has spaces)
        path = line[3:].strip().strip('"')
        if path and not is_junk(path):
            pending.append(path)

    print()
    print("=" * 60)
    print("3) Pending real changes, bucketed")
    print("=" * 60)
    if not pending:
        print("  No pending changes outside of junk files.")
    else:
        buckets = {"source": [], "config": [], "docs": [], "other": []}
        for f in pending:
            buckets[bucket(f)].append(f)
        for name, files in buckets.items():
            if files:
                print(f"  {name} ({len(files)}):")
                for f in files:
                    print(f"    - {f}")

    print()
    if junk_not_ignored or junk_but_tracked:
        print("Action needed before committing — see sections 1 and 2 above.")
    else:
        print("Looks clean — safe to stage the files listed in section 3.")


if __name__ == "__main__":
    main()
