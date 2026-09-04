#!/usr/bin/env python3
"""Statically inspect a notebook: syntax, imports, and symbol inventory.

Usage:
    python static_check.py <notebook.ipynb> [--json]

Parses every code cell with `ast` / `compile()` — the code is NEVER executed, no
kernel is started, no API key is read, nothing costs money. Reports:

  * syntax errors, with the cell index and line within that cell
  * an inventory of imports (module -> names), so the reviewer can check them
    against the pinned versions without running anything
  * called symbols that look like LangChain API surface, and the keyword
    arguments used on them — this is the raw material for the API-correctness
    gate, where a reviewer verifies each kwarg actually exists
  * cells tagged `raises-exception` / `langchain-0x-contrast` (the 0.x contrast
    cells), listed separately since old-API names there are intentional

Exit codes: 0 = parses clean, 1 = at least one syntax error, 2 = unreadable.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

# Windows consoles default to cp1252; box-drawing and em dashes in output would
# raise UnicodeEncodeError. Force UTF-8 and degrade gracefully if unavailable.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


CONTRAST_TAGS = {"raises-exception", "langchain-0x-contrast"}

# Magics/shell lines are not Python; blank them out before parsing rather than
# reporting them as syntax errors.
def strip_magics(src: str) -> str:
    out = []
    for line in src.split("\n"):
        s = line.lstrip()
        if s.startswith(("!", "%", "?")) or s.endswith("?"):
            out.append("pass  # (magic/shell line removed for parsing)")
        else:
            out.append(line)
    return "\n".join(out)


def cell_source(cell: dict) -> str:
    s = cell.get("source", "")
    return "".join(s) if isinstance(s, list) else s


class Collector(ast.NodeVisitor):
    """Gather imports and call signatures — what a reviewer needs to verify."""

    def __init__(self) -> None:
        self.imports: list[dict] = []
        self.calls: list[dict] = []

    def visit_Import(self, node: ast.Import):
        for a in node.names:
            self.imports.append({"module": a.name, "name": None,
                                 "asname": a.asname, "line": node.lineno})

    def visit_ImportFrom(self, node: ast.ImportFrom):
        for a in node.names:
            self.imports.append({"module": node.module or "", "name": a.name,
                                 "asname": a.asname, "line": node.lineno})

    def visit_Call(self, node: ast.Call):
        func = node.func
        if isinstance(func, ast.Name):
            name = func.id
        elif isinstance(func, ast.Attribute):
            name = func.attr
        else:
            name = None
        if name:
            self.calls.append({
                "callee": name,
                "kwargs": sorted({kw.arg for kw in node.keywords if kw.arg}),
                "line": node.lineno,
            })
        self.generic_visit(node)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("notebook", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        nb = json.loads(args.notebook.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read notebook: {exc}", file=sys.stderr)
        return 2

    syntax_errors: list[dict] = []
    imports: list[dict] = []
    calls: list[dict] = []
    contrast_cells: list[int] = []

    for i, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        tags = set(cell.get("metadata", {}).get("tags", []) or [])
        is_contrast = bool(tags & CONTRAST_TAGS)
        if is_contrast:
            contrast_cells.append(i)

        src = strip_magics(cell_source(cell))
        if not src.strip():
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError as exc:
            syntax_errors.append({
                "cell": i,
                "line": exc.lineno,
                "offset": exc.offset,
                "msg": exc.msg,
                "text": (exc.text or "").strip()[:160],
                "contrast_cell": is_contrast,
            })
            continue

        c = Collector()
        c.visit(tree)
        for imp in c.imports:
            imports.append({"cell": i, "contrast_cell": is_contrast, **imp})
        for call in c.calls:
            calls.append({"cell": i, "contrast_cell": is_contrast, **call})

    # Collapse calls to a per-symbol kwarg inventory: the reviewer checks each
    # (callee, kwarg) pair against the real 1.x signature.
    surface: dict[str, dict] = {}
    for call in calls:
        key = call["callee"]
        entry = surface.setdefault(key, {"cells": set(), "kwargs": set(),
                                         "contrast_only": True})
        entry["cells"].add(call["cell"])
        entry["kwargs"].update(call["kwargs"])
        if not call["contrast_cell"]:
            entry["contrast_only"] = False
    surface_out = {
        k: {"cells": sorted(v["cells"]), "kwargs": sorted(v["kwargs"]),
            "contrast_only": v["contrast_only"]}
        for k, v in sorted(surface.items())
    }

    result = {
        "notebook": str(args.notebook),
        "ok": not syntax_errors,
        "syntax_errors": syntax_errors,
        "contrast_cells": contrast_cells,
        "imports": imports,
        "call_surface": surface_out,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{args.notebook.name}: "
              f"{'PARSES CLEAN' if result['ok'] else 'SYNTAX ERRORS'} "
              f"({len(syntax_errors)} error(s), {len(imports)} imports, "
              f"{len(surface_out)} distinct call sites)")
        for e in syntax_errors:
            tag = " [contrast cell]" if e["contrast_cell"] else ""
            print(f"  [FAIL] cell {e['cell']} line {e['line']}: {e['msg']}{tag}")
            if e["text"]:
                print(f"         {e['text']}")
        if imports:
            print("  imports:")
            seen = set()
            for imp in imports:
                label = (f"{imp['module']}.{imp['name']}" if imp["name"]
                         else imp["module"])
                if label in seen:
                    continue
                seen.add(label)
                mark = " (contrast)" if imp["contrast_cell"] else ""
                print(f"    - {label}{mark}")
        if surface_out:
            print("  call surface (verify these kwargs against the real 1.x API):")
            for name, info in surface_out.items():
                if info["contrast_only"]:
                    continue
                kw = ", ".join(info["kwargs"]) or "-"
                print(f"    - {name}({kw})  cells {info['cells']}")

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
