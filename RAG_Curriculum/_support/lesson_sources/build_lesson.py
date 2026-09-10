"""Convert a %%-delimited lesson source into a Jupyter notebook.

Cell format:
    %%markdown [attach=<key>]
    %%code [tags=a,b]

Attachments named by `attach=` are pulled from the donor notebook so the
original diagrams survive consolidation (acceptance checklist: "Notebook
attachments, important metadata, and meaningful tags survive consolidation").

A donor diagram that lives on disk as a file rather than as a notebook
attachment is carried with cell metadata:

    %%markdown attachfile=<filename.png>

The filename is resolved through `rag_paths.asset()`, base64'd, and attached
under its stem, so the cell body references it as
`![alt](attachment:<stem>)`. The build fails if that reference is missing.
PNG rather than inline SVG markup: inline `<svg>` depends on the renderer's
HTML sanitizer and fails silently when stripped, whereas attachments are
Jupyter's own mechanism.
"""

import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "helpers"))
from rag_paths import asset  # noqa: E402

REPO = Path(r"D:\AI ENGINEERING")
# The donor was retired to the archive on 2026-09-10 (its diagrams live on inside
# the built lesson as attachments). Prefer the archive; fall back to the original
# path so this script still works if the archive is restored.
_REL = "04_Retrieval_and_RAG/01_Introduction_to_RAG/1_rag_overview.ipynb"
_ARCHIVED = REPO / "RAG_Curriculum/_archive/source_notebooks_preserved_by_migration_manifest" / _REL
DONOR = _ARCHIVED if _ARCHIVED.exists() else REPO / _REL

# key used in the lesson source -> (donor cell index, attachment name in that cell)
ATTACHMENT_MAP = {
    "four_components": (0, "diagram-export-06-01-2026-00_21_36.png"),
    "rag_from_scratch": (1, "c566957c-a8ef-41a9-9b78-e089d35cf0b7.png"),
    "pipeline_walkthrough": (4, "f9b0e284-58e4-4d33-9594-2dad351c569a.png"),
}


def load_attachments():
    nb = json.loads(DONOR.read_text(encoding="utf-8"))
    out = {}
    for key, (idx, name) in ATTACHMENT_MAP.items():
        att = nb["cells"][idx].get("attachments", {})
        if name not in att:
            raise SystemExit(f"donor cell {idx} has no attachment {name!r}; has {list(att)}")
        out[key] = att[name]
        size = sum(len(v) for v in att[name].values())
        print(f"  carried attachment {key:22s} <- donor cell {idx} ({size} b64 chars)")
    return out


def file_attachment(name):
    """Base64 a PNG on disk into a notebook attachment payload.

    PNG rather than inline SVG markup: an inline `<svg>` in a markdown cell is
    at the mercy of the renderer's HTML sanitizer and silently shows nothing
    when it is stripped. An `image/png` attachment referenced as
    `![alt](attachment:key)` is Jupyter's own mechanism and is what the pilot
    lesson's three diagrams already use here.
    """
    path = asset(name)
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    print(f"  attached diagram {name} ({len(payload)} b64 chars) <- {path}")
    return {"image/png": payload}


def parse(src_text):
    cells, cur_type, cur_meta, buf = [], None, {}, []

    def flush():
        if cur_type is None:
            return
        body = "".join(buf).strip("\n")
        cells.append((cur_type, dict(cur_meta), body))

    for line in src_text.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        if stripped.startswith("%%markdown") or stripped.startswith("%%code"):
            flush()
            parts = stripped.split()
            cur_type = "markdown" if parts[0] == "%%markdown" else "code"
            cur_meta = {}
            for token in parts[1:]:
                key, _, value = token.partition("=")
                cur_meta[key] = value
            buf = []
        else:
            buf.append(line)
    flush()
    return cells


def to_source(text):
    """nbformat stores source as a list of lines, each keeping its newline."""
    lines = text.split("\n")
    return [ln + "\n" for ln in lines[:-1]] + ([lines[-1]] if lines[-1] else [])


def main():
    src = Path(sys.argv[1]).read_text(encoding="utf-8")
    out_path = Path(sys.argv[2])
    attachments = load_attachments()

    cells = []
    for idx, (cell_type, meta, body) in enumerate(parse(src)):
        # nbformat_minor 5 requires a stable per-cell id.
        cell = {
            "cell_type": cell_type,
            "id": f"lesson01-{idx:02d}",
            "metadata": {},
            "source": to_source(body),
        }

        if "tags" in meta:
            cell["metadata"]["tags"] = meta["tags"].split(",")

        if cell_type == "code":
            # nbstripout contract: no saved outputs, null execution_count.
            cell["outputs"] = []
            cell["execution_count"] = None
        elif "attach" in meta:
            key = meta["attach"]
            cell["attachments"] = {key: attachments[key]}
        elif "attachfile" in meta:
            name = meta["attachfile"]
            key = Path(name).stem
            cell["attachments"] = {key: file_attachment(name)}
            if f"attachment:{key}" not in body:
                raise SystemExit(
                    f"cell {idx} attaches {name} but never references "
                    f"![...](attachment:{key}) - the image would not render"
                )

        cells.append(cell)

    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.12",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    n_md = sum(1 for c in cells if c["cell_type"] == "markdown")
    n_code = len(cells) - n_md
    print(f"\nwrote {out_path}")
    print(f"  {len(cells)} cells ({n_md} markdown, {n_code} code)")
    print(f"  {out_path.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
