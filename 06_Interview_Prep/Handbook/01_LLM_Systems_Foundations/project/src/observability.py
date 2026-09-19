"""Observability — record every tool call so you can see exactly what the agent did.

In production this is where you'd emit spans/metrics (OpenTelemetry, LangSmith).
Here it's a simple in-memory log with a pretty-printed trace table.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class ToolCall:
    step: int
    tool: str
    args: dict
    status: str                     # ok | cache_hit | retry | error | blocked
    result: Any = None
    error: Optional[str] = None
    ms: float = 0.0                 # latency in milliseconds


class ToolCallLogger:
    """Collects ToolCall records and can print them as a trace."""
    def __init__(self) -> None:
        self.records: List[ToolCall] = []
        self._step = 0

    def log(self, tool: str, args: dict, status: str,
            result: Any = None, error: Optional[str] = None, ms: float = 0.0) -> None:
        self._step += 1
        self.records.append(ToolCall(self._step, tool, dict(args), status, result, error, ms))

    def trace(self) -> str:
        """Return a human-readable table of every tool call, in order."""
        if not self.records:
            return "(no tool calls)"
        lines = [f"{'#':>2}  {'tool':<16} {'status':<10} {'ms':>6}  args -> result/error",
                 "-" * 78]
        for r in self.records:
            outcome = (r.error if r.error else _short(r.result))
            lines.append(f"{r.step:>2}  {r.tool:<16} {r.status:<10} {r.ms:>6.1f}  {_short(r.args)} -> {outcome}")
        return "\n".join(lines)

    # convenience counters for tests / assertions
    def count(self, status: str) -> int:
        return sum(1 for r in self.records if r.status == status)


def _short(x: Any, limit: int = 40) -> str:
    s = str(x)
    return s if len(s) <= limit else s[:limit - 1] + "…"
