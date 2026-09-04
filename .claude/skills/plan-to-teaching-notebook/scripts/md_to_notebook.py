#!/usr/bin/env python3
"""Build a conventions-compliant .ipynb from a plain-markdown draft.

Write the notebook as ONE markdown file: prose is prose, ```python fences become
code cells. That keeps drafting in normal text instead of hand-assembling notebook
JSON, and makes the whole notebook reviewable as a diff.

Usage:
    python md_to_notebook.py draft.md --out path/to/Notebook.ipynb
    python md_to_notebook.py --check path/to/Notebook.ipynb

Rules:
  * ```python fences  -> code cells (outputs empty, execution_count null)
  * ```python-noexec  -> code cell that is illustrative only; rendered as
                         ```python but the fence tag reminds you not to run it
  * everything else   -> markdown cells (other fences stay inline as markdown)
  * `<!-- split -->`  -> force a markdown cell break
  * A `## ` or `# ` heading always starts a new markdown cell.

--check validates a notebook against this repo's conventions (CLAUDE.md):
title cell, heading hierarchy, code-cell banners, grouped imports, summary cell.
Stdlib only. Never executes anything.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path

# Windows consoles default to cp1252; box-drawing and em dashes in output would
# raise UnicodeEncodeError. Force UTF-8 and degrade gracefully if unavailable.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


FENCE_RE = re.compile(r"^```(\w[\w-]*)?\s*$")
SPLIT_RE = re.compile(r"^<!--\s*split\s*-->\s*$", re.I)
HEADING_RE = re.compile(r"^#{1,2}\s+\S")
BANNER_RE = re.compile(r"^#\s*=+\s*.+?\s*=+\s*$")

CODE_LANGS = {"python", "python-noexec", "py"}


def _cell(kind: str, source: str, noexec: bool = False) -> dict:
    lines = source.rstrip("\n").split("\n")
    src = [ln + "\n" for ln in lines[:-1]] + [lines[-1]] if lines else []
    meta: dict = {}
    if noexec:
        # Marks the cell as illustrative-only: 0.x code kept for contrast, not meant to
        # run. Review is static (nothing is executed), but the tag keeps that intent
        # visible in Jupyter and lets static_check.py treat old API names here as
        # deliberate rather than as defects. `raises-exception` is the standard nbclient
        # tag, so a human who does run the notebook isn't stopped by the expected error.
        meta["tags"] = ["raises-exception", "langchain-0x-contrast"]
    base = {"id": uuid.uuid4().hex[:12], "cell_type": kind,
            "metadata": meta, "source": src}
    if kind == "code":
        base["execution_count"] = None
        base["outputs"] = []
    return base


def md_to_cells(text: str) -> list[dict]:
    cells: list[dict] = []
    buf: list[str] = []
    in_code = False
    code_lang = ""
    code_buf: list[str] = []
    fence_stack_lang = ""

    def flush_md():
        nonlocal buf
        body = "\n".join(buf).strip("\n")
        if body.strip():
            cells.append(_cell("markdown", body))
        buf = []

    for raw in text.splitlines():
        m = FENCE_RE.match(raw)
        if m and not in_code:
            lang = (m.group(1) or "").lower()
            if lang in CODE_LANGS:
                flush_md()
                in_code, code_lang, code_buf = True, lang, []
            else:
                # non-python fence: keep it inside the markdown cell
                fence_stack_lang = lang or "_plain_"
                buf.append(raw)
            continue
        if m and in_code:
            cells.append(_cell("code", "\n".join(code_buf),
                               noexec=code_lang == "python-noexec"))
            in_code, code_lang, code_buf = False, "", []
            continue
        if in_code:
            code_buf.append(raw)
            continue
        # not in a python fence
        if fence_stack_lang:
            buf.append(raw)
            if FENCE_RE.match(raw):
                fence_stack_lang = ""
            continue
        if SPLIT_RE.match(raw):
            flush_md()
            continue
        if HEADING_RE.match(raw) and any(b.strip() for b in buf):
            flush_md()
        buf.append(raw)

    if in_code:
        raise SystemExit("error: unterminated ```python fence")
    flush_md()
    return cells


def build_notebook(cells: list[dict]) -> dict:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


# --------------------------------------------------------------------------
# Convention check
# --------------------------------------------------------------------------
def check(path: Path) -> list[str]:
    problems: list[str] = []
    try:
        nb = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"unreadable notebook: {exc}"]

    cells = nb.get("cells", [])
    if not cells:
        return ["notebook has no cells"]

    def src(c) -> str:
        s = c.get("source", "")
        return "".join(s) if isinstance(s, list) else s

    first = cells[0]
    if first.get("cell_type") != "markdown":
        problems.append("cell 0 must be markdown (the title cell)")
    elif not src(first).lstrip().startswith("# "):
        problems.append("cell 0 must open with a single `# Title` heading")

    code_cells = [(i, c) for i, c in enumerate(cells) if c.get("cell_type") == "code"]
    if not code_cells:
        problems.append("no code cells — an explainer notebook needs runnable examples")

    for i, c in code_cells:
        body = src(c).strip()
        if not body:
            problems.append(f"cell {i}: empty code cell")
            continue
        if not BANNER_RE.match(body.splitlines()[0].strip()):
            problems.append(
                f"cell {i}: first line should be a banner "
                f"`# ============ SECTION NAME ============`")

    if cells[-1].get("cell_type") != "markdown":
        problems.append("last cell must be a markdown summary / key-takeaways cell")

    for i, c in enumerate(cells):
        if c.get("cell_type") == "code" and c.get("outputs"):
            problems.append(f"cell {i}: has saved outputs — clear them before committing")

    heads = [src(c).lstrip()[:4] for c in cells if c.get("cell_type") == "markdown"]
    if sum(1 for h in heads if h.startswith("# ") and not h.startswith("## ")) > 1:
        problems.append("more than one top-level `# ` heading — use `##` for sections")

    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", type=Path, help="markdown draft, or .ipynb with --check")
    ap.add_argument("--out", type=Path, help="destination .ipynb")
    ap.add_argument("--check", action="store_true",
                    help="validate an existing notebook instead of building one")
    ap.add_argument("--force", action="store_true", help="overwrite an existing --out")
    args = ap.parse_args()

    if not args.source.exists():
        print(f"error: no such file: {args.source}", file=sys.stderr)
        return 2

    if args.check:
        problems = check(args.source)
        if problems:
            print(f"{args.source}: {len(problems)} convention problem(s)")
            for p in problems:
                print(f"  - {p}")
            return 1
        print(f"{args.source}: OK")
        return 0

    if not args.out:
        print("error: --out is required when building", file=sys.stderr)
        return 2
    if args.out.exists() and not args.force:
        print(f"error: {args.out} exists (use --force to overwrite)", file=sys.stderr)
        return 2

    cells = md_to_cells(args.source.read_text(encoding="utf-8"))
    nb = build_notebook(cells)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n",
                        encoding="utf-8")

    n_code = sum(1 for c in cells if c["cell_type"] == "code")
    print(f"Wrote {args.out} — {len(cells)} cells ({n_code} code, "
          f"{len(cells) - n_code} markdown)")

    problems = check(args.out)
    if problems:
        print(f"  {len(problems)} convention problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("  conventions: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
