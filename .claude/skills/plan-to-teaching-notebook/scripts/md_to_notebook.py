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
  * a standalone `---` -> starts a new markdown cell, keeping the `---` at its top
                          (the format's major-section separator). Headings do NOT
                          split, so the title cell keeps its H1 + Learning
                          Objectives + Prerequisites together.
  * `<!-- split -->`  -> force a markdown cell break anywhere else

--check validates the notebook against the Format_Python_Notebook skill
(.claude/skills/format-notebook/SKILL.md): title cell (rule 1), section
separators and heading emoji (rule 2), the 3-line code banner (rule 3),
summary + next steps (rule 6), cleared outputs (rule 7). Each message names
the rule it breaks. Stdlib only. Never executes anything.
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
HR_RE = re.compile(r"^---\s*$")   # thematic break = major-section boundary
# Format_Python_Notebook's 3-line banner:
#   # ==========...
#   # SECTION_NAME: Brief description
#   # ==========...
BANNER_RULE_RE = re.compile(r"^#\s*={10,}\s*$")
BANNER_NAME_RE = re.compile(r"^#\s+[A-Z0-9][A-Z0-9 ._/&()+-]*(:.*)?$")

CODE_LANGS = {"python", "python-noexec", "py"}

# Optional leading emoji on a fixed heading. Deliberately narrow: an earlier
# version used `(?:\S+\s+)?`, which matched ANY token, so `## Optional
# Prerequisites` and `## Draft Summary` would have passed. The range matches
# _has_emoji's own threshold.
EMOJI_PREFIX = r"(?:[℁-🫿]\S*\s+)?"  # 2101, not 2100: _has_emoji uses `> 0x2100` (exclusive)

# Headings the Format_Python_Notebook templates show without an emoji.
FIXED_HEADINGS = {
    "Learning Objectives", "Prerequisites", "Key Concepts", "Key Concepts:",
    "Next Steps", "Summary", "Recap",
}


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
    in_code = False          # inside a ```python / ```python-noexec fence
    in_plain_fence = False   # inside any other fence (bash, text, json, ...)
    code_lang = ""
    code_buf: list[str] = []

    def flush_md():
        nonlocal buf
        body = "\n".join(buf).strip("\n")
        if body.strip():
            cells.append(_cell("markdown", body))
        buf = []

    for raw in text.splitlines():
        fence = FENCE_RE.match(raw)

        # --- inside a python fence: everything is code until the closer ---
        if in_code:
            if fence:
                cells.append(_cell("code", "\n".join(code_buf),
                                   noexec=code_lang == "python-noexec"))
                in_code, code_lang, code_buf = False, "", []
            else:
                code_buf.append(raw)
            continue

        # --- inside a non-python fence: passthrough until the closer ---
        # This branch MUST come before the "open a fence" branch below. A
        # closing ``` also matches FENCE_RE, and treating it as an opening
        # fence leaves the parser stuck in fence mode forever, silently
        # swallowing every later `<!-- split -->` and `---`.
        if in_plain_fence:
            buf.append(raw)
            if fence:
                in_plain_fence = False
            continue

        # --- not in any fence ---
        if fence:
            lang = (fence.group(1) or "").lower()
            if lang in CODE_LANGS:
                flush_md()
                in_code, code_lang, code_buf = True, lang, []
            else:
                in_plain_fence = True
                buf.append(raw)
            continue
        if SPLIT_RE.match(raw):
            flush_md()
            continue
        if HR_RE.match(raw) and any(b.strip() for b in buf):
            # A `---` opens a new major section: close the previous cell and
            # start the next one WITH the separator, per format rule 2.
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
# Convention check — enforces the Format_Python_Notebook skill's rules
# (.claude/skills/format-notebook/SKILL.md). Keep the two in sync: if that
# skill's rules change, change these checks and say so in its Reference section.
# --------------------------------------------------------------------------
def _has_emoji(text: str) -> bool:
    """Any non-ASCII pictograph counts — the formatter wants one per heading."""
    return any(ord(ch) > 0x2100 for ch in text)


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

    # ---- 1. Title cell: H1 + emoji + Learning Objectives + Prerequisites ----
    first = cells[0]
    if first.get("cell_type") != "markdown":
        problems.append("cell 0 must be markdown (the title cell)")
    else:
        head = src(first)
        title_line = head.lstrip().split("\n")[0]
        if not title_line.startswith("# "):
            problems.append("cell 0 must open with a single `# <emoji> Title` heading")
        elif not _has_emoji(title_line):
            problems.append("cell 0: the H1 title needs one leading emoji "
                            "(format rule 1)")
        # Allow an optional emoji: rule 2 asks for one emoji per heading, so
        # `## 🎯 Learning Objectives` is at least as conformant as the bare form.
        # A literal substring check rejected it -- that was a checker bug.
        if not re.search(rf"^##\s+{EMOJI_PREFIX}Learning Objectives\s*$", head, re.M):
            problems.append("cell 0: missing `## Learning Objectives` "
                            "(3-5 bolded items) — format rule 1")
        if not re.search(rf"^##\s+{EMOJI_PREFIX}Prerequisites\s*$", head, re.M):
            problems.append("cell 0: missing `## Prerequisites` — format rule 1")

    # ---- 2. Code cells: 3-line banner ----
    code_cells = [(i, c) for i, c in enumerate(cells) if c.get("cell_type") == "code"]
    if not code_cells:
        problems.append("no code cells — an explainer notebook needs runnable examples")

    for i, c in code_cells:
        body = src(c).strip()
        if not body:
            problems.append(f"cell {i}: empty code cell")
            continue
        lines = [ln.rstrip() for ln in body.splitlines()]
        ok = (len(lines) >= 3
              and BANNER_RULE_RE.match(lines[0])
              and BANNER_NAME_RE.match(lines[1])
              and BANNER_RULE_RE.match(lines[2]))
        if not ok:
            problems.append(
                f"cell {i}: needs the 3-line banner (format rule 3):\n"
                f"        # {'=' * 74}\n"
                f"        # SECTION_NAME: Brief description\n"
                f"        # {'=' * 74}")

    # ---- 3. Summary cell ----
    last = cells[-1]
    if last.get("cell_type") != "markdown":
        problems.append("last cell must be the markdown summary cell (format rule 6)")
    else:
        tail = src(last)
        if not re.search(rf"^##\s+{EMOJI_PREFIX}Summary\s*$", tail, re.M):
            problems.append("last cell: missing `## 📝 Summary` heading (format rule 6)")
        if not re.search(rf"^###\s+{EMOJI_PREFIX}Next Steps\s*$", tail, re.M):
            problems.append("last cell: missing `### Next Steps` (format rule 6)")

    # ---- 4. Markdown section hygiene ----
    h1_count = 0
    for i, c in enumerate(cells):
        if c.get("cell_type") != "markdown":
            continue
        body = src(c).strip()
        if not body:
            continue
        lines = body.split("\n")
        if lines[0].startswith("# ") and not lines[0].startswith("## "):
            h1_count += 1
        # Major `##` sections open with a `---` separator (format rule 2).
        if lines[0].startswith("## ") and i != 0:
            problems.append(f"cell {i}: `##` section should open with a `---` "
                            f"separator line above it (format rule 2)")
        for ln in lines:
            # Emoji is required on `##` CONTENT sections only. The formatter's
            # own fixed headings appear without one in its templates, and `###`
            # / `####` sub-headings are left to the author's judgment.
            if re.match(r"^##\s+\S", ln) and not re.match(r"^###", ln)                     and not _has_emoji(ln)                     and ln.strip("# ").strip() not in FIXED_HEADINGS:
                problems.append(f"cell {i}: `##` heading has no emoji — "
                                f"`{ln[:60]}` (format rule 2)")
                break
    if h1_count > 1:
        problems.append("more than one top-level `# ` heading — use `##` for sections")

    # ---- 5. Outputs cleared ----
    for i, c in enumerate(cells):
        if c.get("cell_type") != "code":
            continue
        if c.get("outputs"):
            problems.append(f"cell {i}: has saved outputs — clear them (format rule 7)")
        if c.get("execution_count") is not None:
            problems.append(f"cell {i}: execution_count must be null (format rule 7)")
        if "application/vnd.databricks.v1+cell" in json.dumps(c.get("metadata", {})):
            problems.append(f"cell {i}: strip Databricks cell metadata (format rule 7)")

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
    # newline="" keeps Windows from translating \n to \r\n. Every other notebook
    # in this repo is LF; emitting CRLF here inflates every future diff on the
    # file and was caught in review twice.
    with open(args.out, "w", encoding="utf-8", newline="") as fh:
        fh.write(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")

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
