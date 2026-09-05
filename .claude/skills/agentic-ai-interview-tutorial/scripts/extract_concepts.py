#!/usr/bin/env python3
"""Inventory what a notebook or folder of notebooks actually teaches.

Usage:
    python extract_concepts.py <path> [<path> ...] [--json] [--quiet]

`<path>` is a folder (crawled recursively for .ipynb) or an individual notebook.
Mixing both is fine.

This is the grounding step for the tutorial skill: it reports the concepts that
are DEMONSTRATED IN THE SOURCE, so the tutorial teaches what the learner's own
notebooks contain rather than what the model assumes they contain.

Per notebook it reports:
  * title       — the first markdown H1, else the filename
  * outline     — every markdown heading, in order
  * imports     — third-party modules, normalized to their top-level package
  * symbols     — classes/functions called, filtered to library-looking names
  * counts      — code cells, markdown cells, lines of code

Aggregated across the input it reports:
  * frameworks  — which libraries appear, and in how many notebooks
  * topics      — matched against TOPIC_SIGNALS below, each with its evidence
  * gaps        — topics an interview expects that the source never demonstrates

Read-only. Never executes a notebook, never writes to the source. Stdlib only.
Exit 0 always (this is a report, not a gate).
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__",
             ".ipynb_checkpoints", ".databricks", "archive", "backup"}

STDLIB_ISH = {
    "os", "sys", "re", "json", "time", "math", "random", "typing", "pathlib",
    "collections", "itertools", "functools", "dataclasses", "datetime", "asyncio",
    "warnings", "logging", "tempfile", "subprocess", "textwrap", "operator",
    "uuid", "copy", "abc", "enum", "io", "glob", "shutil", "pprint", "getpass",
    "typing_extensions", "IPython", "__future__",
}

# A topic is claimed only when the source shows real evidence for it. Each entry
# is (topic, regex over imports+symbols+headings). Keep patterns specific enough
# that an incidental mention does not light up a whole interview section.
TOPIC_SIGNALS: list[tuple[str, str]] = [
    ("Retrieval & RAG",
     r"\b(retriever|vectorstore|vector_store|embed_documents|embed_query|"
     r"OpenAIEmbeddings|Chroma|FAISS|Pinecone|Weaviate|Qdrant|"
     r"TextSplitter|DocumentLoader|similarity_search)\b"),
    ("Chunking & indexing",
     r"\b(RecursiveCharacterTextSplitter|CharacterTextSplitter|chunk_size|"
     r"chunk_overlap|SemanticChunker|ParentDocument)\b"),
    ("Agents & tool calling",
     r"\b(create_agent|AgentExecutor|initialize_agent|create_react_agent|"
     r"bind_tools|ToolNode|@tool|tool_calls|StructuredTool)\b"),
    ("Graph orchestration",
     r"\b(StateGraph|add_conditional_edges|add_edge|Send|compile\(\)|"
     r"START|END|entrypoint|task)\b"),
    ("Workflow patterns",
     r"\b(RunnableParallel|RunnableBranch|RunnablePassthrough|"
     r"orchestrator|evaluator|prompt.chain|parallelization|routing)\b"),
    ("Memory & state",
     r"\b(checkpointer|MemorySaver|InMemorySaver|thread_id|BaseStore|"
     r"ConversationBufferMemory|langmem|get_state|update_state)\b"),
    ("Human-in-the-loop",
     r"\b(interrupt|HumanInTheLoopMiddleware|Command\(resume|"
     r"interrupt_before|interrupt_after|approval)\b"),
    ("Multi-agent",
     r"\b(supervisor|swarm|handoff|subagent|sub_agent|transfer_to|"
     r"create_supervisor|deepagents)\b"),
    ("Structured output",
     r"\b(with_structured_output|response_format|ToolStrategy|ProviderStrategy|"
     r"BaseModel|PydanticOutputParser|JsonOutputParser)\b"),
    ("Middleware & guardrails",
     r"\b(AgentMiddleware|before_model|after_model|wrap_model_call|"
     r"wrap_tool_call|ModelCallLimitMiddleware|PIIMiddleware|"
     r"SummarizationMiddleware|guardrail|moderation)\b"),
    ("Streaming & async",
     r"\b(astream|ainvoke|abatch|stream_events|async def|await |"
     r"stream_mode|AsyncCallbackHandler)\b"),
    ("Evaluation",
     r"\b(ragas|deepeval|GEval|LLMTestCase|evaluate\(|faithfulness|"
     r"answer_relevancy|llm.as.judge|judge)\b"),
    ("Observability & tracing",
     r"\b(langsmith|langfuse|LangChainTracer|callback|CallbackHandler|"
     r"trace|@traceable)\b"),
    ("Caching & cost",
     r"\b(CacheBackedEmbeddings|set_llm_cache|InMemoryCache|SQLiteCache|"
     r"cache|token_usage|max_tokens|get_openai_callback)\b"),
    ("Retries & reliability",
     r"\b(with_retry|with_fallbacks|ToolRetryMiddleware|ModelFallbackMiddleware|"
     r"max_retries|tenacity|fallback)\b"),
    ("Prompting",
     r"\b(ChatPromptTemplate|PromptTemplate|FewShotPromptTemplate|"
     r"MessagesPlaceholder|system_prompt|few.shot)\b"),
    ("Protocols (MCP/A2A)",
     r"\b(mcp|fastmcp|ClientSession|stdio_client|a2a|AgentCard)\b"),
]

# Interview-critical topics. Any of these missing from the source becomes an
# explicit gap the tutorial must cover from first principles rather than silently
# skip -- an interview will ask about them whether or not the notebooks did.
INTERVIEW_CRITICAL = [
    "Retrieval & RAG", "Agents & tool calling", "Memory & state",
    "Evaluation", "Observability & tracing", "Streaming & async",
    "Retries & reliability", "Structured output", "Human-in-the-loop",
    "Multi-agent",
]

HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.*\S)\s*$", re.M)
CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")
# Library-looking: CamelCase, or snake_case with an underscore. Filters out
# ordinary local calls like print/len/range while keeping create_agent, StateGraph.
LIBRARYISH = re.compile(r"^([A-Z][A-Za-z0-9]*[a-z][A-Za-z0-9]*|[a-z]+(?:_[a-z0-9]+)+)$")
NOISE_SYMBOLS = {
    "print", "len", "range", "list", "dict", "set", "str", "int", "float", "type",
    "enumerate", "zip", "sorted", "sum", "open", "format", "input", "isinstance",
    "get_ipython", "display", "load_dotenv", "filterwarnings",
}


def strip_magics(src: str) -> str:
    """Replace notebook magics/shell lines so ast.parse survives them."""
    out = []
    for line in src.split("\n"):
        s = line.lstrip()
        out.append("pass" if s.startswith(("!", "%", "?")) else line)
    return "\n".join(out)


def iter_notebooks(paths: list[Path]) -> list[Path]:
    found: list[Path] = []
    for p in paths:
        if p.is_file() and p.suffix == ".ipynb":
            found.append(p)
        elif p.is_dir():
            for nb in sorted(p.rglob("*.ipynb")):
                if not any(part in SKIP_DIRS for part in nb.parts):
                    found.append(nb)
    # Deduplicate while preserving order.
    seen, uniq = set(), []
    for f in found:
        r = f.resolve()
        if r not in seen:
            seen.add(r)
            uniq.append(f)
    return uniq


def analyse(path: Path) -> dict:
    try:
        nb = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"path": str(path), "error": f"unreadable: {exc}"}

    code_src, md_src, outline = [], [], []
    for cell in nb.get("cells", []):
        src = cell.get("source", "")
        src = "".join(src) if isinstance(src, list) else src
        if cell.get("cell_type") == "code":
            code_src.append(src)
        elif cell.get("cell_type") == "markdown":
            md_src.append(src)
            for hashes, text in HEADING_RE.findall(src):
                outline.append(f"{'  ' * (len(hashes) - 1)}{text}")

    joined_code = "\n".join(code_src)
    imports: set[str] = set()
    symbols: set[str] = set()

    for src in code_src:
        try:
            tree = ast.parse(strip_magics(src))
        except SyntaxError:
            tree = None
        if tree is not None:
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        imports.add(a.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
                    for a in node.names:
                        if LIBRARYISH.match(a.name):
                            symbols.add(a.name)
        # Called names, even in cells that failed to parse.
        for name in CALL_RE.findall(src):
            if name not in NOISE_SYMBOLS and LIBRARYISH.match(name):
                symbols.add(name)

    title = ""
    for src in md_src:
        m = re.search(r"^\s{0,3}#\s+(.*\S)\s*$", src, re.M)
        if m:
            title = m.group(1).strip()
            break

    return {
        "path": str(path),
        "title": title or path.stem,
        "outline": outline,
        "imports": sorted(i for i in imports if i not in STDLIB_ISH),
        "symbols": sorted(symbols),
        "code_cells": len(code_src),
        "markdown_cells": len(md_src),
        "code_lines": sum(1 for ln in joined_code.split("\n") if ln.strip()),
    }


def detect_topics(reports: list[dict]) -> dict[str, list[str]]:
    """Map each topic to the notebooks that provide evidence for it."""
    hits: dict[str, list[str]] = defaultdict(list)
    for r in reports:
        if r.get("error"):
            continue
        blob = " ".join(r["imports"] + r["symbols"] + r["outline"])
        for topic, pattern in TOPIC_SIGNALS:
            if re.search(pattern, blob, re.I):
                hits[topic].append(Path(r["path"]).name)
    return dict(hits)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    ap.add_argument("--quiet", action="store_true", help="omit per-notebook outlines")
    args = ap.parse_args()

    notebooks = iter_notebooks(args.paths)
    if not notebooks:
        print("No .ipynb files found under the given path(s).", file=sys.stderr)
        return 0

    reports = [analyse(p) for p in notebooks]
    topics = detect_topics(reports)
    frameworks = Counter(i for r in reports if not r.get("error") for i in r["imports"])
    gaps = [t for t in INTERVIEW_CRITICAL if t not in topics]

    if args.json:
        print(json.dumps({
            "notebooks": reports,
            "topics": topics,
            "frameworks": frameworks.most_common(),
            "interview_gaps": gaps,
        }, indent=2, ensure_ascii=False))
        return 0

    print(f"# Concept inventory — {len(reports)} notebook(s)\n")
    for r in reports:
        if r.get("error"):
            print(f"  !! {r['path']}: {r['error']}")
            continue
        print(f"## {r['title']}")
        print(f"   {r['path']}")
        print(f"   {r['code_cells']} code / {r['markdown_cells']} md cells, "
              f"{r['code_lines']} lines")
        if r["imports"]:
            print(f"   imports: {', '.join(r['imports'][:14])}")
        if r["symbols"]:
            print(f"   symbols: {', '.join(r['symbols'][:18])}")
        if r["outline"] and not args.quiet:
            print("   outline:")
            for line in r["outline"][:18]:
                print(f"     {line}")
        print()

    print("# Frameworks in use")
    for name, n in frameworks.most_common(20):
        print(f"  {n:3}x  {name}")

    print("\n# Topics demonstrated (with evidence)")
    if topics:
        for topic in sorted(topics):
            files = topics[topic]
            shown = ", ".join(files[:4]) + (f" +{len(files) - 4} more" if len(files) > 4 else "")
            print(f"  [x] {topic:26} <- {shown}")
    else:
        print("  (none matched)")

    print("\n# Interview-critical topics NOT demonstrated in the source")
    if gaps:
        for t in gaps:
            print(f"  [ ] {t}")
        print("\n  Cover these from first principles and label them clearly as")
        print("  'not in your notebooks' so the learner knows to build the gap.")
    else:
        print("  (none — the source covers every interview-critical topic)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
