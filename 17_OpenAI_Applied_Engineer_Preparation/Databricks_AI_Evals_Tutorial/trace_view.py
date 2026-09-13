"""
Trace rendering: reading an MLflow span tree at a glance
=======================================================

Introduced in Phase 1 and reused wherever a notebook needs to look at a trace's shape
(Phases 1, 3, 9, 10). Pure formatting — no MLflow import, no network call, no cost. It
takes an `mlflow.entities.Trace` and returns text.

Why this is a module and not four copies of a five-line loop
------------------------------------------------------------
The flat indented list this replaces answered one question ("what spans are there?") and
left three unanswered, all of which matter when you are debugging an eval:

**1. Where did the time actually go?** A parent span's duration includes its children, so
`LangGraph 13613.6 ms` tells you nothing — the 13.6 s belongs to whatever leaf is slow.
`SELF` (duration minus the time accounted for by children) is the column that localises
latency; `SHARE` puts every span on the same scale against the root.

**2. Does the trace carry what the scorers need?** Span *type* is a contract in MLflow:
`RetrievalGroundedness()` errors outright on a trace with no RETRIEVER span, and the
Phase 3 tool-correctness judge searches for TOOL spans. The gutter column marks those
span types where you read the tree, and the footer states the readiness verdict, so you
don't discover the problem from a stack trace inside `mlflow.genai.evaluate()`.

**3. What did the model calls cost?** Token usage recorded by `mlflow.langchain.autolog()`
lives in span attributes; summing it here is what makes Phase 5's cost comparison
checkable on a single run.

Nesting order is by start time, not by whatever order the span list came back in — for a
multi-turn trace (Phase 9) the sequence of turns is the thing you're reading for.
"""

import json

# ============================================================================
# WHICH SPAN TYPES AN EVALUATION DEPENDS ON
# ============================================================================
# The gutter marker is not decoration: each of these span types is a hard input to a
# scorer built later in the tutorial. Seeing them in the tree is how you confirm, before
# spending money on judges, that the trace can be scored at all.

SCORER_CRITICAL = {
    "RETRIEVER": ("*", "RetrievalGroundedness() — hard requirement, errors without one"),
    "TOOL": ("+", "Phase 3 tool-call correctness judge"),
    "CHAT_MODEL": ("~", "token usage and latency — Phase 5 cost comparison"),
}

# Tree drawing + column widths. LABEL_WIDTH is the tree prefix *and* the span name, so
# columns stay aligned no matter how deep the nesting goes.
LABEL_WIDTH = 44
TYPE_WIDTH = 11
BAR_WIDTH = 10
_BLOCKS = "▏▎▍▌▋▊▉█"


# ============================================================================
# SPAN ACCESSORS (defensive — span internals differ across MLflow versions)
# ============================================================================

def _duration_ms(span) -> float:
    """Wall-clock duration of a span in milliseconds. 0.0 for an unfinished span."""
    start, end = getattr(span, "start_time_ns", None), getattr(span, "end_time_ns", None)
    if start is None or end is None or end < start:
        return 0.0
    return (end - start) / 1e6


def _span_type(span) -> str:
    return str(getattr(span, "span_type", None) or "UNKNOWN")


def _is_error(span) -> bool:
    status = getattr(span, "status", None)
    code = getattr(status, "status_code", status)
    return "ERROR" in str(code or "").upper()


def _token_usage(span):
    """Return (input_tokens, output_tokens) if autolog recorded them, else None."""
    attrs = getattr(span, "attributes", None) or {}
    usage = attrs.get("mlflow.chat.tokenUsage") or attrs.get("llm.token_count")
    if isinstance(usage, str):
        try:
            usage = json.loads(usage)
        except (ValueError, TypeError):
            return None
    if not isinstance(usage, dict):
        return None
    prompt = usage.get("input_tokens") or usage.get("prompt_tokens") or 0
    completion = usage.get("output_tokens") or usage.get("completion_tokens") or 0
    if not prompt and not completion:
        return None
    return int(prompt), int(completion)


def _bar(fraction: float, width: int = BAR_WIDTH) -> str:
    """A sub-character-resolution bar, so a 2% span is still visibly non-zero."""
    fraction = max(0.0, min(1.0, fraction))
    eighths = round(fraction * width * 8)
    full, remainder = divmod(eighths, 8)
    bar = "█" * full + (_BLOCKS[remainder - 1] if remainder else "")
    return bar.ljust(width)


# ============================================================================
# TREE CONSTRUCTION
# ============================================================================

def _index(spans):
    """Group spans by parent, in start-time order, and identify the roots.

    A span whose `parent_id` is absent from the trace is treated as a root rather than
    dropped — a truncated or partially exported trace should still render.
    """
    by_id = {span.span_id: span for span in spans}
    children, roots = {}, []
    for span in spans:
        parent = getattr(span, "parent_id", None)
        if parent and parent in by_id:
            children.setdefault(parent, []).append(span)
        else:
            roots.append(span)
    for siblings in children.values():
        siblings.sort(key=lambda s: getattr(s, "start_time_ns", 0) or 0)
    roots.sort(key=lambda s: getattr(s, "start_time_ns", 0) or 0)
    return children, roots


def _self_ms(span, children) -> float:
    """Duration minus the time claimed by direct children — where time was really spent."""
    child_total = sum(_duration_ms(c) for c in children.get(span.span_id, []))
    return max(0.0, _duration_ms(span) - child_total)


# ============================================================================
# RENDERING
# ============================================================================

def span_tree_str(trace, show_tokens: bool = True) -> str:
    """Render a trace as an annotated tree. Returns the text; see `print_span_tree`."""
    spans = list(trace.data.spans)
    if not spans:
        return "(trace carries no spans)"

    children, roots = _index(spans)
    total_ms = max(_duration_ms(root) for root in roots) or 1.0

    lines = []
    info = getattr(trace, "info", None)
    if info is not None:
        state = str(getattr(info, "state", "") or "")
        lines.append(
            f"{getattr(info, 'trace_id', '?')}   {state}   "
            f"{total_ms:,.0f} ms   {len(spans)} spans"
        )
        lines.append("")

    header = (
        f"  {'SPAN':<{LABEL_WIDTH}} {'TYPE':<{TYPE_WIDTH}} "
        f"{'TOTAL':>10} {'SELF':>10}  SHARE"
    )
    lines.append(header)
    lines.append("  " + "-" * (len(header) - 2))

    def walk(span, prefix: str, connector: str, child_prefix: str):
        name = f"{prefix}{connector}{span.name}"
        if len(name) > LABEL_WIDTH:
            name = name[: LABEL_WIDTH - 1] + "…"
        span_type = _span_type(span)
        marker = SCORER_CRITICAL.get(span_type, (" ",))[0]
        ms = _duration_ms(span)
        share = ms / total_ms
        if _is_error(span):
            flag = "  <- ERROR"
        elif getattr(span, "end_time_ns", None) is None:
            flag = "  <- unfinished"
        else:
            flag = ""
        lines.append(
            f"{marker} {name:<{LABEL_WIDTH}} {span_type:<{TYPE_WIDTH}} "
            f"{ms:>8,.1f}ms {_self_ms(span, children):>8,.1f}ms  "
            f"{_bar(share)} {share:>6.1%}{flag}"
        )
        # The vertical bar continues under a node only while siblings remain below it.
        kids = children.get(span.span_id, [])
        for i, kid in enumerate(kids):
            last = i == len(kids) - 1
            walk(
                kid,
                child_prefix,
                "└── " if last else "├── ",
                child_prefix + ("    " if last else "│   "),
            )

    for root in roots:
        walk(root, "", "", "")

    lines.append("")
    lines.extend(_footer(spans, children, roots, total_ms, show_tokens))
    return "\n".join(lines)


def _footer(spans, children, roots, total_ms, show_tokens):
    """Counts, token spend, the true latency culprit, and the scorer-readiness verdict."""
    lines = []

    counts = {}
    for span in spans:
        counts[_span_type(span)] = counts.get(_span_type(span), 0) + 1
    lines.append("  spans      : " + "  ".join(f"{t} x{n}" for t, n in sorted(counts.items())))

    if show_tokens:
        usages = [u for u in (_token_usage(s) for s in spans) if u]
        if usages:
            prompt = sum(u[0] for u in usages)
            completion = sum(u[1] for u in usages)
            lines.append(
                f"  tokens     : {prompt:,} in / {completion:,} out "
                f"across {len(usages)} model call(s)"
            )

    # Rank by SELF time: the span that *owns* the latency, not the parent that contains it.
    hot = max(spans, key=lambda s: _self_ms(s, children))
    hot_ms = _self_ms(hot, children)
    lines.append(
        f"  hot span   : {hot.name} ({_span_type(hot)}) — {hot_ms:,.1f} ms of own work, "
        f"{hot_ms / total_ms:.0%} of the trace"
    )

    errors = [s.name for s in spans if _is_error(s)]
    if errors:
        lines.append(f"  errors     : {', '.join(errors)}")

    # "absent" is a statement of fact, not a verdict: a general question that correctly
    # calls no tool has no TOOL span, and that is the right outcome. Only a missing
    # RETRIEVER span is unambiguously a problem, so only that one gets a warning.
    present = set(counts)
    lines.append("  scoreable  : " + "   ".join(
        f"{span_type} {'present' if span_type in present else 'absent'}"
        for span_type in SCORER_CRITICAL
    ))
    if "RETRIEVER" not in present:
        lines.append("               ^ no RETRIEVER span: RetrievalGroundedness() will error")
    if len(roots) > 1:
        lines.append(f"  note       : {len(roots)} root spans (trace may be partial)")

    lines.append("")
    for i, (span_type, (marker, why)) in enumerate(SCORER_CRITICAL.items()):
        label = "  legend     : " if i == 0 else "               "
        lines.append(f"{label}{marker} {span_type:<11} {why}")
    return lines


def print_span_tree(trace, show_tokens: bool = True) -> None:
    """Print a trace's spans as a tree with self-time, share of total, and span-type markers.

    TOTAL is wall clock including children; SELF excludes them — SELF is the column that
    tells you which span is actually slow. The left gutter marks the span types the
    tutorial's scorers require.
    """
    print(span_tree_str(trace, show_tokens=show_tokens))
