#!/usr/bin/env python3
"""Scan notebooks/scripts for LangChain 0.x patterns that break or are legacy on 1.x.

Usage:
    python scan_langchain_v1.py <path> [<path> ...] [--json] [--out FILE]
                                [--min-severity {BLOCKING,BREAKING,MODERNIZE,INFO}]
                                [--include-archive]

Emits a markdown migration plan on stdout (or JSON with --json).
Pure stdlib — no LangChain import, no notebook execution, read-only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# Windows consoles default to cp1252; box-drawing and em dashes in output would
# raise UnicodeEncodeError. Force UTF-8 and degrade gracefully if unavailable.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


# --------------------------------------------------------------------------
# Severity model
# --------------------------------------------------------------------------
# BLOCKING   -> raises ImportError / AttributeError on langchain 1.x. Must fix.
# BREAKING   -> imports fine but behaviour/signature changed. Silent wrongness.
# MODERNIZE  -> still works (often via langchain-classic) but is the old idiom;
#               teaching material should show the 1.x way.
# INFO       -> worth a look, not necessarily a change.
SEVERITY_ORDER = {"BLOCKING": 0, "BREAKING": 1, "MODERNIZE": 2, "INFO": 3}
SEVERITY_WEIGHT = {"BLOCKING": 3.0, "BREAKING": 2.0, "MODERNIZE": 1.0, "INFO": 0.25}


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    category: str
    pattern: re.Pattern
    what: str
    fix: str


def R(rid, sev, cat, pat, what, fix, flags=0):
    return Rule(rid, sev, cat, re.compile(pat, flags), what, fix)


# --------------------------------------------------------------------------
# Rules
# --------------------------------------------------------------------------
RULES: list[Rule] = [
    # ---- 1. Imports that moved to langchain-classic (hard ImportError) ----
    R("IMP-chains", "BLOCKING", "Imports moved to langchain-classic",
      r"\bfrom\s+langchain\.chains\b|\bimport\s+langchain\.chains\b",
      "`langchain.chains` no longer exists in the 1.x `langchain` package.",
      "`pip install langchain-classic`, then `from langchain_classic.chains import ...` — "
      "or better, rewrite the chain as LCEL / `create_agent`."),
    R("IMP-retrievers", "BLOCKING", "Imports moved to langchain-classic",
      r"\bfrom\s+langchain\.retrievers\b|\bimport\s+langchain\.retrievers\b",
      "`langchain.retrievers` moved to `langchain-classic`.",
      "`from langchain_classic.retrievers... import ...` (vector-store-native retrievers "
      "via `vectorstore.as_retriever()` are unaffected)."),
    R("IMP-indexes", "BLOCKING", "Imports moved to langchain-classic",
      r"\bfrom\s+langchain\.indexes\b|\bimport\s+langchain\.indexes\b",
      "The indexing API moved to `langchain-classic`.",
      "`from langchain_classic.indexes import index, SQLRecordManager`."),
    R("IMP-hub", "BLOCKING", "Imports moved to langchain-classic",
      r"\bfrom\s+langchain\s+import\s+hub\b|\bfrom\s+langchain\.hub\b",
      "`langchain.hub` moved to `langchain-classic`.",
      "`from langchain_classic import hub` — or inline the prompt so the notebook has no "
      "network dependency."),
    R("IMP-memory", "BLOCKING", "Imports moved to langchain-classic",
      r"\bfrom\s+langchain\.memory\b|\bimport\s+langchain\.memory\b",
      "`langchain.memory` is gone from the 1.x package.",
      "`langchain_classic.memory` still exports every class, so a repoint compiles. Prefer "
      "the real replacement though: a LangGraph checkpointer + `thread_id`, or "
      "`SummarizationMiddleware`. See §5 of the differences doc."),
    R("IMP-schema", "BLOCKING", "Imports moved to langchain-core",
      r"\bfrom\s+langchain\.schema\b",
      "`langchain.schema` was the 0.1-era home for messages/documents/parsers.",
      "`from langchain_core.messages import ...` / `langchain_core.documents` / "
      "`langchain_core.output_parsers` — or the 1.x re-export `langchain.messages`."),
    R("IMP-llms", "BLOCKING", "Imports moved to partner packages",
      r"\bfrom\s+langchain\.(llms|chat_models\.\w+|embeddings\.\w+)\b",
      "0.1-era provider imports off the root `langchain` package.",
      "Use partner packages: `langchain_openai`, `langchain_groq`, `langchain_anthropic`, "
      "or `langchain.chat_models.init_chat_model` for provider-agnostic init."),
    R("IMP-community", "BREAKING", "Imports moved to langchain-community",
      r"\bfrom\s+langchain\.(document_loaders|vectorstores|utilities|tools\.\w+|callbacks\.\w+)\b",
      "Integration import off the root `langchain` package (moved out in 0.2, absent in 1.x).",
      "`from langchain_community.<same path> import ...`, or the dedicated partner package "
      "(`langchain_chroma`, `langchain_tavily`, ...)."),
    R("IMP-textsplitter", "BLOCKING", "Imports moved out of langchain",
      r"\bfrom\s+langchain\.text_splitter\b",
      "`langchain.text_splitter` moved to its own package.",
      "`from langchain_text_splitters import RecursiveCharacterTextSplitter, ...`"),
    R("IMP-prompts", "BLOCKING", "Imports moved to langchain-core",
      r"\bfrom\s+langchain\.(prompts|docstore)\b|\bimport\s+langchain\.(prompts|docstore)\b",
      "`langchain.prompts` / `langchain.docstore` no longer exist in the 1.x package.",
      "`from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, ...` "
      "(docstore -> `langchain_classic.docstore`). Verified gone on langchain 1.4.0."),
    R("IMP-parsers", "MODERNIZE", "Imports moved to langchain-classic",
      r"\bfrom\s+langchain\.output_parsers\b",
      "`langchain.output_parsers` moved; the core ones live in `langchain_core`.",
      "`from langchain_core.output_parsers import ...` for Str/JSON/Pydantic parsers; "
      "the rest are in `langchain_classic.output_parsers`."),
    R("IMP-evaluation", "BLOCKING", "Imports moved to langchain-classic",
      r"\bfrom\s+langchain\.(evaluation|smith|globals)\b",
      "Evaluation / smith / globals helpers moved to `langchain-classic`.",
      "`from langchain_classic.<same path> import ...`, or move evaluation to LangSmith / "
      "DeepEval (see Phase 7)."),

    # ---- 2. Agent construction ----
    R("AGT-executor", "BLOCKING", "Agent construction",
      r"\bAgentExecutor\b",
      "`AgentExecutor` is removed from the 1.x agent surface.",
      "Rewrite with `from langchain.agents import create_agent`; the executor loop is now "
      "the compiled LangGraph agent itself."),
    R("AGT-initialize", "BLOCKING", "Agent construction",
      r"\binitialize_agent\s*\(|\bAgentType\.",
      "`initialize_agent` / `AgentType` are the pre-0.2 agent API.",
      "`create_agent(model, tools, system_prompt=...)`."),
    R("AGT-constructors", "BLOCKING", "Agent construction",
      r"\bcreate_(tool_calling|openai_functions|openai_tools|structured_chat|json_chat|"
      r"self_ask_with_search|xml)_agent\s*\(",
      "0.x per-flavour agent constructors are all replaced by one function.",
      "`create_agent(...)` — tool-calling is the default loop; flavour-specific behaviour "
      "goes in middleware."),
    R("AGT-react-prebuilt", "BREAKING", "Agent construction",
      r"from\s+langgraph\.prebuilt\s+import[^\n]*\bcreate_react_agent\b|\bcreate_react_agent\s*\(",
      "`langgraph.prebuilt.create_react_agent` is superseded by `langchain.agents.create_agent`.",
      "Swap the import AND rename `prompt=` to `system_prompt=`. Also check: state must be a "
      "TypedDict, no pre-bound `.bind_tools()` model, stream node renamed `agent`->`model`."),
    R("AGT-hooks", "BLOCKING", "Agent construction",
      r"\bpre_model_hook\b|\bpost_model_hook\b",
      "`pre_model_hook` / `post_model_hook` were removed.",
      "Use middleware: `@before_model` / `@after_model`, passed via `middleware=[...]`."),
    R("AGT-toolkit-agents", "MODERNIZE", "Agent construction",
      r"\bcreate_(sql|pandas_dataframe|csv|python|json|spark_dataframe)_agent\s*\(",
      "Toolkit agent factories live in `langchain-classic` / `langchain-experimental` now.",
      "Either import from `langchain_classic.agents...`, or rebuild as `create_agent` + the "
      "toolkit's `.get_tools()`."),
    R("AGT-prompt-kwarg", "BREAKING", "Agent construction",
      r"create_(react_)?agent\s*\([^)]*\bprompt\s*=",
      "`prompt=` was renamed on the 1.x agent factory.",
      "Rename to `system_prompt=`."),

    # ---- 3. Chains ----
    R("CHN-llmchain", "BLOCKING", "Legacy chains",
      r"\bLLMChain\b|\bConversationChain\b|\bSimpleSequentialChain\b|\bSequentialChain\b|"
      r"\bTransformChain\b",
      "Core legacy chain classes moved to `langchain-classic` and are deprecated.",
      "Rewrite as LCEL: `prompt | model | StrOutputParser()`. `ConversationChain` -> "
      "`create_agent` + checkpointer."),
    R("CHN-retrieval", "BLOCKING", "Legacy chains",
      r"\bRetrievalQA\b|\bConversationalRetrievalChain\b|\bRetrievalQAWithSourcesChain\b|"
      r"\bVectorDBQA\b",
      "Legacy RAG chain classes moved to `langchain-classic`.",
      "Rewrite as LCEL retrieval chain, or `create_agent` with a retriever tool (agentic RAG). "
      "See Phase 4 / Phase 8."),
    R("CHN-loaders", "MODERNIZE", "Legacy chains",
      r"\bload_qa_chain\b|\bload_summarize_chain\b|\bload_qa_with_sources_chain\b|"
      r"\bStuffDocumentsChain\b|\bMapReduceDocumentsChain\b|\bRefineDocumentsChain\b",
      "Document-combining chain loaders are legacy.",
      "`from langchain.chains.combine_documents import create_stuff_documents_chain` is the "
      "0.3 bridge; on 1.x prefer explicit LCEL or a map-reduce LangGraph graph "
      "(see Phase 5 orchestrator-worker)."),
    R("CHN-lcel-helpers", "MODERNIZE", "Legacy chains",
      r"\bcreate_retrieval_chain\b|\bcreate_history_aware_retriever\b|"
      r"\bcreate_stuff_documents_chain\b",
      "0.3 LCEL-helper constructors now live in `langchain-classic`.",
      "Import from `langchain_classic.chains...`, or inline the LCEL they build "
      "(usually 5-10 lines and clearer for teaching)."),
    R("CHN-misc", "MODERNIZE", "Legacy chains",
      r"\bLLMMathChain\b|\bAPIChain\b|\bSQLDatabaseChain\b|\bcreate_extraction_chain\b|"
      r"\bcreate_tagging_chain\b|\bLLMRouterChain\b|\bMultiPromptChain\b",
      "Utility/router chains are legacy.",
      "Extraction/tagging -> `model.with_structured_output(Schema)`. Routers -> LangGraph "
      "conditional edges or `create_agent` tool choice. Others -> `langchain_classic`."),

    # ---- 4. Memory ----
    R("MEM-classes", "BLOCKING", "Memory",
      r"\bConversation(Buffer|BufferWindow|Summary|SummaryBuffer|Entity|KG)Memory\b|"
      r"\bVectorStoreRetrieverMemory\b|\bCombinedMemory\b|\bReadOnlySharedMemory\b",
      "All `*Memory` classes were removed from the 1.x package.",
      "Short-term: LangGraph checkpointer (`InMemorySaver`/`PostgresSaver`) + "
      "`config={'configurable': {'thread_id': ...}}`. Summarizing: `SummarizationMiddleware`. "
      "Long-term: LangGraph `Store`."),
    R("MEM-kwarg", "BREAKING", "Memory",
      r"\bmemory\s*=\s*(memory|conversation|buffer|window|summary)",
      "A `memory=` kwarg being threaded into a chain/agent — the 0.x memory contract.",
      "Replace with checkpointer + thread_id; there is no `memory=` parameter on `create_agent`."),
    R("MEM-history", "INFO", "Memory",
      r"\bRunnableWithMessageHistory\b|\bChatMessageHistory\b",
      "Still importable on 1.x, but the recommended path changed.",
      "Fine to keep for a pure-LCEL lesson; for agents prefer a checkpointer."),

    # ---- 5. Message / content API ----
    R("MSG-text-method", "BREAKING", "Message API",
      r"\.text\s*\(\s*\)",
      "`message.text()` became a property in 1.x.",
      "Use `message.text` (no parentheses)."),
    R("MSG-example-kwarg", "BREAKING", "Message API",
      r"AIMessage\s*\([^)]*\bexample\s*=",
      "The `example=` parameter was removed from `AIMessage`.",
      "Delete the kwarg; use few-shot prompt templates instead."),
    R("MSG-raw-content", "MODERNIZE", "Message API",
      r"\.additional_kwargs\b|\.response_metadata\[|\.content\[\s*0\s*\]\[",
      "Reading provider-shaped fields off a message.",
      "Use the provider-agnostic `message.content_blocks` (typed `text` / `reasoning` / "
      "`citation` / `tool_call` blocks). See §6 of the differences doc."),
    R("MSG-func-call", "BREAKING", "Message API",
      r"\bfunction_call\b|\bFunctionMessage\b",
      "OpenAI `function_call` era API.",
      "Use `tool_calls` / `ToolMessage`, and `model.bind_tools(...)`."),
    R("MOD-direct-call", "BREAKING", "Model invocation",
      r"^\s*\w+\s*=\s*(llm|chat|chat_model|model|chat_llm)\s*\(",
      "Calling a chat model directly (`llm(messages)`). `BaseChatModel.__call__` was "
      "removed in 1.x — verified absent on langchain-core 1.6.1, so this raises "
      "`TypeError: '<Model>' object is not callable`.",
      "Use `llm.invoke(messages)` (or `.batch()` / `.stream()`). Deliberately narrow: it "
      "only matches assignment from a variable literally named llm/chat/model, so a "
      "constructor call like `llm = ChatGroq(...)` is not flagged."),

    # ---- 6. Agent state / streaming / runtime ----
    R("ST-pydantic-state", "BREAKING", "Agent state",
      r"class\s+\w*(State|AgentState)\w*\s*\(\s*BaseModel\s*\)",
      "1.x `create_agent` accepts TypedDict state only — Pydantic/dataclass state is rejected.",
      "Convert to `class MyState(AgentState): ...` using `TypedDict` semantics. "
      "(A Pydantic model is still fine for a hand-built LangGraph `StateGraph`.)"),
    R("ST-stream-agent-node", "BREAKING", "Streaming",
      r"[\[\(]\s*[\"']agent[\"']\s*[\]\)]|==\s*[\"']agent[\"']|chunk\[[\"']agent[\"']\]",
      "The agent's model node was renamed `agent` -> `model` in 1.x.",
      "Update any stream filter / node-name check to `\"model\"`."),
    R("ST-configurable-ctx", "MODERNIZE", "Runtime context",
      r"config\s*\[\s*[\"']configurable[\"']\s*\]",
      "Runtime values passed through `config['configurable']`.",
      "`thread_id` still goes there, but user/app context should move to the "
      "`context=` parameter + `Runtime[ContextSchema]`."),
    R("ST-bound-model", "BREAKING", "Agent construction",
      r"create_(react_)?agent\s*\(\s*\w+\.bind_tools\(",
      "Passing a pre-bound model into the agent factory is no longer supported.",
      "Pass the plain model and the `tools=[...]` list separately."),

    # ---- 7. Misc ----
    R("MSC-globals", "BLOCKING", "Misc",
      r"\blangchain\.debug\s*=|\blangchain\.verbose\s*=|from\s+langchain\.globals\b",
      "Global debug/verbose flags moved.",
      "`from langchain_core.globals import set_debug, set_verbose`."),
    R("MSC-pip-pin", "INFO", "Environment",
      r"pip\s+install[^\n]*\blangchain\s*[=<>]{0,2}\s*0\.|langchain==0\.",
      "A notebook cell pins langchain 0.x.",
      "Drop the pin (repo pins 1.x in pyproject.toml) or update it."),
    R("MSC-pip-install", "INFO", "Environment",
      r"^\s*[!%]\s*pip\s+install",
      "In-notebook pip install.",
      "Repo convention is `uv pip install -e \".[dev]\"` from pyproject.toml; check the "
      "package list still matches 1.x names (add `langchain-classic` if needed)."),
]

# Signals that a file is already written against 1.x.
MODERN_SIGNALS = [
    ("create_agent", re.compile(r"from\s+langchain\.agents\s+import[^\n]*\bcreate_agent\b")),
    ("middleware", re.compile(r"langchain\.agents\.middleware|middleware\s*=\s*\[")),
    ("content_blocks", re.compile(r"\.content_blocks\b")),
    ("langchain_classic", re.compile(r"\blangchain_classic\b")),
    ("checkpointer", re.compile(r"\bcheckpointer\s*=")),
    ("init_chat_model", re.compile(r"\binit_chat_model\b")),
]

SKIP_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".ipynb_checkpoints",
    ".databricks", ".mypy_cache", ".ruff_cache", "dist", "build", ".next",
}


# --------------------------------------------------------------------------
# Scanning
# --------------------------------------------------------------------------
@dataclass
class Hit:
    rule: Rule
    loc: str       # "cell 4, line 12" or "line 12"
    snippet: str


@dataclass
class FileReport:
    path: Path
    kind: str
    hits: list[Hit] = field(default_factory=list)
    modern: list[str] = field(default_factory=list)
    cells: int = 0

    @property
    def score(self) -> float:
        return sum(SEVERITY_WEIGHT[h.rule.severity] for h in self.hits)

    @property
    def worst(self) -> str:
        if not self.hits:
            return "CLEAN"
        return min((h.rule.severity for h in self.hits), key=lambda s: SEVERITY_ORDER[s])

    @property
    def effort(self) -> str:
        """Coarse rewrite-effort bucket, used to order the plan."""
        n_block = sum(1 for h in self.hits if h.rule.severity == "BLOCKING")
        cats = {h.rule.category for h in self.hits}
        if not self.hits:
            return "none"
        if n_block == 0 and self.score <= 3:
            return "S"           # a few find/replace edits
        if n_block <= 3 and len(cats) <= 2:
            return "M"           # mechanical, one concept touched
        if "Legacy chains" in cats or "Agent construction" in cats or "Memory" in cats:
            return "L"           # needs a conceptual rewrite, not just imports
        return "M"


def iter_sources(root: Path, include_archive: bool):
    if root.is_file():
        yield root
        return
    for p in sorted(root.rglob("*")):
        if p.is_dir():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if not include_archive and any(part.lower() == "archive" for part in p.parts):
            continue
        if p.suffix in (".ipynb", ".py"):
            yield p


def notebook_segments(path: Path):
    """Return (segments, error, n_code_cells); segments are (label, source_text)."""
    try:
        nb = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (json.JSONDecodeError, OSError) as exc:
        return [], str(exc), 0
    segs, n = [], 0
    for i, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        tags = set(cell.get("metadata", {}).get("tags", []) or [])
        if "langchain-0x-contrast" in tags:
            # Deliberate 0.x contrast in a teaching notebook -- showing the old
            # import IS the lesson, so it is not migration debt.
            continue
        n += 1
        src = cell.get("source", "")
        if isinstance(src, list):
            src = "".join(src)
        segs.append((f"cell {i}", src))
    return segs, None, n


def scan_file(path: Path) -> FileReport:
    if path.suffix == ".ipynb":
        segs, err, ncells = notebook_segments(path)
        if err:
            return FileReport(path, "notebook")
        rep = FileReport(path, "notebook", cells=ncells)
    else:
        try:
            segs = [("", path.read_text(encoding="utf-8", errors="replace"))]
        except OSError:
            return FileReport(path, "python")
        rep = FileReport(path, "python")

    seen: set[tuple[str, str]] = set()
    for label, src in segs:
        if not src:
            continue
        for name, pat in MODERN_SIGNALS:
            if pat.search(src) and name not in rep.modern:
                rep.modern.append(name)
        for lineno, line in enumerate(src.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#") and "pip install" not in stripped:
                continue
            for rule in RULES:
                if not rule.pattern.search(line):
                    continue
                key = (rule.id, stripped[:120])
                if key in seen:                    # dedupe identical repeats
                    continue
                seen.add(key)
                loc = f"{label}, line {lineno}" if label else f"line {lineno}"
                rep.hits.append(Hit(rule, loc, stripped[:160]))
    return rep


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------
def render_markdown(reports: list[FileReport], roots: list[Path], min_sev: str) -> str:
    cutoff = SEVERITY_ORDER[min_sev]
    flagged = [r for r in reports if any(SEVERITY_ORDER[h.rule.severity] <= cutoff
                                         for h in r.hits)]
    clean = [r for r in reports if r not in flagged]

    sev_counts = Counter(h.rule.severity for r in flagged for h in r.hits)
    cat_counts = Counter(h.rule.category for r in flagged for h in r.hits)
    rule_counts = Counter(h.rule.id for r in flagged for h in r.hits)

    out: list[str] = []
    A = out.append
    A("# LangChain 1.x Migration Plan")
    A("")
    A("Scanned: " + ", ".join(f"`{p}`" for p in roots))
    A("")
    A(f"- Files scanned: **{len(reports)}**")
    A(f"- Files needing work: **{len(flagged)}**")
    A(f"- Files already clean / already on 1.x: **{len(clean)}**")
    A("")
    A("| Severity | Findings | Meaning |")
    A("| --- | --- | --- |")
    for sev, meaning in [
        ("BLOCKING", "raises ImportError/AttributeError on 1.x — notebook will not run"),
        ("BREAKING", "imports fine, behaviour or signature changed — silently wrong"),
        ("MODERNIZE", "works (often via `langchain-classic`) but teaches the old idiom"),
        ("INFO", "worth a look"),
    ]:
        A(f"| {sev} | {sev_counts.get(sev, 0)} | {meaning} |")
    A("")

    if cat_counts:
        A("## What's driving the work")
        A("")
        A("| Theme | Findings | Files |")
        A("| --- | --- | --- |")
        for cat, n in cat_counts.most_common():
            nf = sum(1 for r in flagged if any(h.rule.category == cat for h in r.hits))
            A(f"| {cat} | {n} | {nf} |")
        A("")

    # ---- Waves ----
    A("## Suggested order of work")
    A("")
    A("Do these as waves — each wave is internally uniform, so a single decision "
      "(e.g. \"rewrite RetrievalQA as LCEL, don't just repoint to langchain-classic\") "
      "applies across every file in it.")
    A("")

    waves = [
        ("Wave 1 — unblock: imports only",
         "Pure find/replace. Nothing conceptual. Get notebooks importing again.",
         lambda h: h.rule.category.startswith("Imports") or h.rule.id.startswith("MSC-globals")),
        ("Wave 2 — agents",
         "Rewrite to `create_agent`; rename `prompt=`, fix state/stream/hook fallout.",
         lambda h: h.rule.category in ("Agent construction", "Agent state", "Streaming")),
        ("Wave 3 — memory",
         "Swap `*Memory` classes for checkpointer + `thread_id` / `SummarizationMiddleware`.",
         lambda h: h.rule.category == "Memory"),
        ("Wave 4 — chains",
         "Decide per notebook: repoint to `langchain-classic` (if the lesson IS the legacy "
         "chain) vs rewrite as LCEL (if the lesson is the task).",
         lambda h: h.rule.category == "Legacy chains"),
        ("Wave 5 — polish",
         "Message API, model invocation, content blocks, runtime context, pip cells.",
         lambda h: h.rule.category in ("Message API", "Model invocation", "Runtime context",
                                       "Misc", "Environment")),
    ]
    for title, why, pred in waves:
        files = sorted(
            {r.path for r in flagged for h in r.hits if pred(h)},
        )
        if not files:
            continue
        A(f"### {title}  ({len(files)} files)")
        A("")
        A(why)
        A("")
        for f in files:
            A(f"- `{_rel(f, roots)}`")
        A("")

    # ---- Per-file detail ----
    A("## Per-file findings")
    A("")
    by_dir: dict[Path, list[FileReport]] = defaultdict(list)
    for r in flagged:
        by_dir[r.path.parent].append(r)

    for d in sorted(by_dir):
        A(f"### `{_rel(d, roots)}/`")
        A("")
        for r in sorted(by_dir[d], key=lambda x: (-x.score, x.path.name)):
            tag = f"effort **{r.effort}**" if r.effort != "none" else ""
            modern = (" · already uses: " + ", ".join(f"`{m}`" for m in r.modern)) if r.modern else ""
            A(f"#### `{r.path.name}` — worst: **{r.worst}** · {len(r.hits)} findings · {tag}{modern}")
            A("")
            A("| Sev | Where | Rule | Found | Fix |")
            A("| --- | --- | --- | --- | --- |")
            for h in sorted(r.hits, key=lambda x: SEVERITY_ORDER[x.rule.severity]):
                if SEVERITY_ORDER[h.rule.severity] > cutoff:
                    continue
                snippet = h.snippet.replace("|", "\\|").replace("`", "'")
                fix = h.rule.fix.replace("|", "\\|")
                A(f"| {h.rule.severity} | {h.loc} | `{h.rule.id}` | `{snippet}` | {fix} |")
            A("")

    if clean:
        A("## Files with no 0.x patterns detected")
        A("")
        for r in sorted(clean, key=lambda x: str(x.path)):
            note = (" — uses " + ", ".join(f"`{m}`" for m in r.modern)) if r.modern else ""
            A(f"- `{_rel(r.path, roots)}`{note}")
        A("")

    if rule_counts:
        A("## Rule hit counts")
        A("")
        for rid, n in rule_counts.most_common():
            rule = next(x for x in RULES if x.id == rid)
            A(f"- `{rid}` ({rule.severity}) × {n} — {rule.what}")
        A("")

    A("---")
    A("")
    A("_Regex-based static scan. It cannot see dynamically-built imports, `%run`-included "
      "files, or a pattern that only appears in prose. Treat it as a worklist to verify, "
      "not as proof._")
    return "\n".join(out)


def _rel(p: Path, roots: list[Path]) -> str:
    for root in roots:
        base = root if root.is_dir() else root.parent
        try:
            return str(p.relative_to(base)).replace("\\", "/")
        except ValueError:
            continue
    return str(p).replace("\\", "/")


def to_json(reports: list[FileReport], roots: list[Path]) -> str:
    payload = []
    for r in reports:
        payload.append({
            "path": _rel(r.path, roots),
            "kind": r.kind,
            "cells": r.cells,
            "worst_severity": r.worst,
            "score": round(r.score, 2),
            "effort": r.effort,
            "modern_signals": r.modern,
            "findings": [{
                "rule": h.rule.id,
                "severity": h.rule.severity,
                "category": h.rule.category,
                "location": h.loc,
                "snippet": h.snippet,
                "what": h.rule.what,
                "fix": h.rule.fix,
            } for h in r.hits],
        })
    return json.dumps({"scanned": len(reports), "files": payload}, indent=2)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    ap.add_argument("--out", type=Path, help="write to this file instead of stdout")
    ap.add_argument("--min-severity", default="INFO",
                    choices=list(SEVERITY_ORDER), help="hide findings below this severity")
    ap.add_argument("--include-archive", action="store_true",
                    help="also scan archive/ folders (skipped by default)")
    args = ap.parse_args()

    roots = [p.resolve() for p in args.paths]
    for r in roots:
        if not r.exists():
            print(f"error: no such path: {r}", file=sys.stderr)
            return 2

    reports: list[FileReport] = []
    for root in roots:
        for f in iter_sources(root, args.include_archive):
            reports.append(scan_file(f))

    text = (to_json(reports, roots) if args.json
            else render_markdown(reports, roots, args.min_severity))

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        n_flagged = sum(1 for r in reports if r.hits)
        print(f"Wrote {args.out} — {len(reports)} files scanned, {n_flagged} need work.")
    else:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
