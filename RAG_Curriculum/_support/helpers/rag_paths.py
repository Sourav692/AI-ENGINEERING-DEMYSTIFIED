"""Depth-independent resource resolution for the RAG curriculum.

Why this exists
---------------
`RAG_CURRICULUM.md` section 7C requires lesson notebooks to stop depending on
fragile ``../../`` paths and on which directory the kernel happened to start in.
Section 7B requires the shared corpora to stay where they are during the first
migration passes, so lessons must be able to reach assets that still live under
``04_Retrieval_and_RAG/shared_data/`` and friends.

This module reconciles the two: notebooks ask for a resource by name, and the
resolver finds it relative to the repository root regardless of notebook depth
or kernel working directory.

Usage
-----
    from rag_paths import repo_root, asset, ASSET_ROOTS

    repo_root()                    # -> Path to the "AI ENGINEERING" root
    asset("Transformer.pdf")       # -> resolved Path, searched across roots
    asset("bella_vista.txt")

Bootstrapping from a notebook (the module is not an installed package)::

    import sys, pathlib
    p = pathlib.Path.cwd()
    while not (p / "RAG_Curriculum").is_dir() and p != p.parent:
        p = p.parent
    sys.path.insert(0, str(p / "RAG_Curriculum" / "_support" / "helpers"))

Note on module-name collisions
------------------------------
Section 7C also warns about local ``utils.py`` / ``helpers`` shadowing. This
module is deliberately named ``rag_paths`` rather than ``utils`` or ``helpers``
so it can never shadow, or be shadowed by, the repository's installed
``helpers`` package or the several per-folder ``utils.py`` files under
``04_Retrieval_and_RAG/``.
"""

from __future__ import annotations

from pathlib import Path

__all__ = ["repo_root", "asset", "curriculum_root", "ASSET_ROOTS", "find_all"]

# A directory is the repository root if it contains all of these.
_ROOT_MARKERS = ("RAG_Curriculum", "pyproject.toml")


def repo_root(start: Path | str | None = None) -> Path:
    """Walk upward from *start* (default: cwd) until the repository root is found.

    Falls back to this file's own location, which is always four levels below
    the root, so the resolver still works if the kernel is started somewhere
    unexpected.
    """
    candidates = []
    if start is not None:
        candidates.append(Path(start).resolve())
    candidates.append(Path.cwd().resolve())
    candidates.append(Path(__file__).resolve())

    for candidate in candidates:
        current = candidate if candidate.is_dir() else candidate.parent
        while True:
            if all((current / marker).exists() for marker in _ROOT_MARKERS):
                return current
            if current == current.parent:
                break
            current = current.parent

    # __file__ is <root>/RAG_Curriculum/_support/helpers/rag_paths.py
    return Path(__file__).resolve().parents[3]


def curriculum_root(start: Path | str | None = None) -> Path:
    """Return the ``RAG_Curriculum/`` directory."""
    return repo_root(start) / "RAG_Curriculum"


# Search order for `asset()`. The curriculum's own `_support/shared_data/` wins,
# so a lesson-local copy can later supersede a stationary source without
# editing any notebook. The remaining roots are the existing homes that
# section 7B says to leave in place for now.
ASSET_ROOTS: tuple[str, ...] = (
    "RAG_Curriculum/_support/shared_data",
    "04_Retrieval_and_RAG/shared_data",
    "04_Retrieval_and_RAG/09_RAG_with_LangChain",
    "04_Retrieval_and_RAG/01_Introduction_to_RAG",
    "04_Retrieval_and_RAG/02_Embeddings_and_Vector_Databases/data",
    "04_Retrieval_and_RAG/06_RAG_Naive_to_Production/02_Splitting_and_Chunking",
    "08_Advanced_RAG/Comprehensive_RAG_Techniques/data",
    "08_Advanced_RAG/Comprehensive_RAG_Techniques/images",
)


def find_all(name: str, start: Path | str | None = None) -> list[Path]:
    """Return every match for *name* across ``ASSET_ROOTS``, in search order.

    Useful when two roots hold same-named files: section 7B forbids assuming
    that a filename match means the files are interchangeable, so a lesson that
    cares can inspect all candidates before choosing.
    """
    root = repo_root(start)
    return [p for r in ASSET_ROOTS if (p := root / r / name).exists()]


def asset(name: str, start: Path | str | None = None) -> Path:
    """Resolve a shared input asset by filename.

    Raises ``FileNotFoundError`` listing the roots that were searched, rather
    than silently substituting a different document (section 7B).
    """
    matches = find_all(name, start)
    if matches:
        return matches[0]
    root = repo_root(start)
    searched = "\n".join(f"  - {root / r}" for r in ASSET_ROOTS)
    raise FileNotFoundError(
        f"Asset {name!r} not found. Searched these roots:\n{searched}\n"
        "Add its directory to rag_paths.ASSET_ROOTS or copy the file into "
        "RAG_Curriculum/_support/shared_data/."
    )
