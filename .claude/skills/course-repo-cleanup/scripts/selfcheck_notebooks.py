#!/usr/bin/env python3
"""Static self-containment check: flag names a notebook uses but never defines.

Joins each notebook's code cells (IPython magics/shell lines blanked) into one module and runs
ruff's undefined-name rule (F821). A notebook that silently relies on another notebook's
variables shows up here without executing anything.

Usage: selfcheck_notebooks.py DIR_OR_NOTEBOOK [...]     (needs `ruff`; run via `uv run`)
Exit 1 if any notebook uses an undefined name.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def notebooks(paths):
    for p in map(Path, paths):
        if p.is_dir():
            yield from sorted(x for x in p.rglob("*.ipynb") if ".ipynb_checkpoints" not in x.parts)
        else:
            yield p


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        mapping = {}
        for i, nb_path in enumerate(notebooks(sys.argv[1:])):
            nb = json.loads(nb_path.read_text(encoding="utf-8"))
            lines = []
            for c in nb.get("cells", []):
                if c.get("cell_type") != "code":
                    continue
                src = c.get("source", "")
                src = "".join(src) if isinstance(src, list) else src
                for line in src.splitlines():
                    stripped = line.lstrip()
                    lines.append("" if stripped.startswith(("!", "%", "?")) else line)
                lines.append("")
            out = Path(tmp) / f"nb{i:03d}.py"
            out.write_text("\n".join(lines))
            mapping[out.name] = nb_path
        r = subprocess.run(
            ["ruff", "check", "--isolated", "--no-cache", "--select", "F821",
             "--output-format", "concise", tmp],
            capture_output=True, text=True,
        )
        bad = set()
        for line in r.stdout.splitlines():
            if "F821" in line:
                fname = Path(line.split(":", 1)[0]).name
                bad.add(fname)
                print(f"{mapping.get(fname, fname)}: {line.split(':', 3)[-1].strip()}")
        print(f"{len(mapping)} notebooks checked, {len(bad)} with undefined names")
        return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
