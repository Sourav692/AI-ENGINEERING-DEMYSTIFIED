#!/usr/bin/env python3
"""Remove every in-notebook package install from notebook code cells.

Dependencies belong to the repo root (pyproject.toml -> uv.lock -> requirements.txt), so
notebooks must not install anything themselves: an install cell can downgrade the shared
env (e.g. `!pip install langchain==0.3.14`) or add packages the lock doesn't know about.

Removes, in code cells, active or commented-out:
  !pip install ...   %pip install ...   pip install ...   !uv pip install ...   !pip3 install ...
  (including backslash-continued lines), and a `%%capture` left with nothing to capture.
A cell left with no code becomes a one-line pointer to the root setup; otherwise the pointer
is prepended. JSON indentation is preserved so diffs stay minimal.

Before editing it reports every package those lines installed and flags the ones that are
NOT in uv.lock, so you can `uv add` them first (nothing gets silently dropped).
Markdown cells are only reported (prose needs a human rewrite), never edited.

Usage:
  strip_pip_installs.py [--dry-run] [--lock uv.lock] NOTEBOOK.ipynb [...]
  strip_pip_installs.py [--dry-run] --all [ROOT]      # every tracked-looking .ipynb under ROOT
Exit code 2 if any removed package is missing from the lock (edits are still applied
unless --dry-run; run with --dry-run first).
"""

import argparse
import json
import re
import sys
from pathlib import Path

INSTALL = re.compile(r"^\s*#?\s*[!%]?\s*(?:uv\s+)?pip3?\s+install\b(.*)$")
MD_INSTALL = re.compile(r"\bpip3?\s+install\b")
NOTE = ["# Dependencies are managed at the repo root (pyproject.toml / uv.lock / requirements.txt).\n",
        "# Run `uv sync` in the repo root instead of installing packages here.\n"]
# pointer lines written by earlier versions of this skill; replaced by NOTE so cells don't stack notes
OLD_NOTES = ("# Dependencies (LangChain 1.x) come from the repo root",)
EXCLUDE = {".venv", "venv", ".git", "node_modules", ".ipynb_checkpoints", "site-packages"}


def norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def packages(args: str):
    """Package names from the argument part of a pip install line."""
    out, skip_next = [], False
    for tok in args.split("#")[0].replace("\\", " ").split():
        if skip_next:
            skip_next = False
            continue
        if tok.startswith("-"):
            # flags that take a value
            if tok in {"-r", "-c", "-e", "-i", "--index-url", "--extra-index-url", "-f", "--find-links",
                       "--target", "-t", "--python"}:
                skip_next = True
            continue
        m = re.match(r"^['\"]?([A-Za-z0-9][A-Za-z0-9._-]*)", tok)
        if m:
            out.append(m.group(1))
    return out


def locked(lock: Path):
    if not lock.exists():
        return None
    return {norm(n) for n in re.findall(r'^name = "([^"]+)"', lock.read_text(), re.M)}


def strip_cell(src):
    kept, removed, i = [], [], 0
    while i < len(src):
        line = src[i]
        m = INSTALL.match(line)
        if not m:
            kept.append(line)
            i += 1
            continue
        args = m.group(1)
        while line.rstrip("\n").rstrip().endswith("\\") and i + 1 < len(src):  # continuation
            i += 1
            line = src[i]
            args += " " + line
        removed.append(args)
        i += 1
    return kept, removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--all", action="store_true", help="treat the single path (default .) as a root to scan")
    ap.add_argument("--lock", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if a.all:
        root = Path(a.paths[0] if a.paths else ".").resolve()
        files = [p for p in root.rglob("*.ipynb") if not EXCLUDE & set(p.relative_to(root).parts)]
    else:
        root = Path(".").resolve()
        files = [Path(p) for p in a.paths]
    lock_path = Path(a.lock) if a.lock else next(
        (d / "uv.lock" for d in [root, *root.parents] if (d / "uv.lock").exists()), root / "uv.lock")
    in_lock = locked(lock_path)

    unlocked, md_mentions, total = {}, [], 0
    for p in sorted(files):
        raw = p.read_text(encoding="utf-8")
        nb = json.loads(raw)
        n_removed = 0
        for idx, c in enumerate(nb.get("cells", [])):
            src = c["source"] if isinstance(c["source"], list) else c["source"].splitlines(True)
            if c["cell_type"] == "markdown":
                for l in src:
                    if MD_INSTALL.search(l):
                        md_mentions.append((str(p), idx, l.strip()))
                continue
            if c["cell_type"] != "code":
                continue
            kept, removed = strip_cell(src)
            if not removed:
                continue
            kept = [l for l in kept if not l.startswith(OLD_NOTES) and l not in NOTE
                    and l.rstrip("\n") not in [n.rstrip("\n") for n in NOTE]]
            n_removed += len(removed)
            for args in removed:
                for pkg in packages(args):
                    if in_lock is not None and norm(pkg) not in in_lock:
                        unlocked.setdefault(pkg, set()).add(str(p))
            is_code = lambda l: l.strip() and not l.strip().startswith("#") and not l.strip().startswith("%%capture")
            if any(is_code(l) for l in kept):
                kept = NOTE + kept
            else:
                kept = list(NOTE)
            kept[-1] = kept[-1].rstrip("\n")
            c["source"] = kept
            if c["cell_type"] == "code" and not any(is_code(l) for l in kept):
                c["outputs"], c["execution_count"] = [], None  # install logs no longer match the cell
        if n_removed:
            total += n_removed
            print(f"{n_removed:3d} install line(s)  {p}")
            if not a.dry_run:
                indent = 1 if raw.startswith('{\n "') else 2
                p.write_text(json.dumps(nb, indent=indent, ensure_ascii=False)
                             + ("\n" if raw.endswith("\n") else ""), encoding="utf-8")

    print(f"\n{'Would remove' if a.dry_run else 'Removed'} {total} install line(s).")
    if in_lock is None:
        print(f"WARNING: {lock_path} not found; could not check packages against the lock.")
    if unlocked:
        print("\nPackages installed by removed lines but NOT in uv.lock (uv add them, or confirm unneeded):")
        for pkg, srcs in sorted(unlocked.items()):
            print(f"  {pkg}")
            for s in sorted(srcs):
                print(f"      in {s}")
    if md_mentions:
        print("\nMarkdown cells mentioning pip install (rewrite by hand to point at the root uv setup):")
        for f, idx, line in md_mentions:
            print(f"  {f} [cell {idx}]: {line[:140]}")
    sys.exit(2 if unlocked else 0)


if __name__ == "__main__":
    main()
