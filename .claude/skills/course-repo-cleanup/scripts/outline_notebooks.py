#!/usr/bin/env python3
"""Outline notebooks to spot duplicated concepts: headings, tools, model/API usage, graph shape.

Usage: outline_notebooks.py DIR_OR_NOTEBOOK [...] [--code]
       (--code also prints the first line of every code cell)
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SIGNALS = [
    r"@tool", r"bind_tools", r"ToolNode", r"tools_condition", r"StateGraph", r"create_agent",
    r"create_react_agent", r"AgentExecutor", r"with_structured_output", r"\.stream\(",
    r"add_conditional_edges", r"Send\(", r"interrupt\(", r"Checkpoint|MemorySaver|InMemorySaver",
    r"responses\.create", r"chat\.completions\.create", r"input\(", r"get_\w+_llm\(|get_llm\(",
    r"Chat[A-Z]\w+\(", r"RunnableParallel|RunnableBranch|RunnableLambda", r"\.batch\(|\.map\(\)",
]


def src(cell) -> str:
    s = cell.get("source", "")
    return "".join(s) if isinstance(s, list) else s


def notebooks(paths):
    for p in map(Path, paths):
        if p.is_dir():
            yield from sorted(x for x in p.rglob("*.ipynb") if ".ipynb_checkpoints" not in x.parts)
        else:
            yield p


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--code", action="store_true")
    a = ap.parse_args()
    for p in notebooks(a.paths):
        nb = json.loads(p.read_text(encoding="utf-8"))
        cells = nb.get("cells", [])
        code = "\n".join(src(c) for c in cells if c.get("cell_type") == "code")
        md_n = sum(c.get("cell_type") == "markdown" for c in cells)
        print(f"\n#### {p}  ({md_n} md / {len(cells) - md_n} code)")
        tools = re.findall(r"@tool[^\n]*\n\s*def (\w+)", code)
        if tools:
            print(f"  tools: {tools}")
        found = sorted({m.group(0)[:40] for s in SIGNALS for m in re.finditer(s, code)})
        print(f"  uses: {found}")
        edges = re.findall(r"add_edge\(([^)]*)\)", code)
        if edges:
            print(f"  edges: {[e.replace(' ', '') for e in edges][:12]}")
        for n, c in enumerate(cells, 1):  # cell numbers are 1-based over all cells
            if c.get("cell_type") == "markdown":
                for line in src(c).splitlines():
                    if line.startswith("#"):
                        print(f"   [c{n}] {line[:120]}")
            elif a.code and src(c).strip():
                print(f"     [c{n}] [code] {src(c).strip().splitlines()[0][:100]}")


if __name__ == "__main__":
    main()
