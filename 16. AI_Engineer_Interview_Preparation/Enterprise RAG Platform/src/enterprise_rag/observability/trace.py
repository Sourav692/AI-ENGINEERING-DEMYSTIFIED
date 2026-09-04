# -*- coding: utf-8 -*-
"""Run tracing.

A trace here is not "logging". It is a complete, replayable record of one request:
who asked, what the policy decided, which queries were generated, which chunks were
retrieved and why, what was denied, what the model was shown, what it produced, what
it cost, and how long each stage took.

Three audiences, one artefact:
  - the engineer debugging a bad answer,
  - the auditor asking "did this user ever see the contract?",
  - the finance team asking "which tenant is burning the budget?".

Traces land in `runs/` as JSONL - one file per run, greppable, diffable, and
replayable without the vector store.
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import SETTINGS


@dataclass
class Step:
    name: str
    started_at: float
    duration_ms: float = 0.0
    detail: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RunTrace:
    """One request, end to end."""

    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    tenant_id: str = ""
    user_id: str = ""
    role: str = ""
    question: str = ""
    strategy: str = ""
    prompt_version: str = ""
    started_at: float = field(default_factory=time.time)
    steps: List[Step] = field(default_factory=list)

    # access control
    prefilter: Dict[str, Any] = field(default_factory=dict)
    prefilter_explained: str = ""
    denied: List[Dict[str, Any]] = field(default_factory=list)
    redacted_count: int = 0
    audit_events: List[Dict[str, Any]] = field(default_factory=list)
    security_events: List[Dict[str, Any]] = field(default_factory=list)

    # retrieval
    generated_queries: List[str] = field(default_factory=list)
    hyde_passage: Optional[str] = None
    subquestions: List[str] = field(default_factory=list)
    candidates: List[Dict[str, Any]] = field(default_factory=list)
    context_chunk_ids: List[str] = field(default_factory=list)

    # outcome
    answer_preview: str = ""
    citations: List[str] = field(default_factory=list)
    refused: bool = False
    refusal_reason: Optional[str] = None
    degraded: bool = False
    degraded_reason: Optional[str] = None
    groundedness: Optional[float] = None

    # cost
    tokens_in: int = 0
    tokens_out: int = 0
    embedding_tokens: int = 0
    llm_calls: int = 0
    cost_usd: float = 0.0
    total_ms: float = 0.0

    _open: Dict[str, Step] = field(default_factory=dict, repr=False)

    # -- step timing -------------------------------------------------------
    def start(self, name: str, **detail):
        self._open[name] = Step(name=name, started_at=time.time(), detail=detail)

    def end(self, name: str, **detail):
        step = self._open.pop(name, None)
        if step is None:
            return
        step.duration_ms = (time.time() - step.started_at) * 1000.0
        step.detail.update(detail)
        self.steps.append(step)

    def finish(self, usage=None):
        self.total_ms = (time.time() - self.started_at) * 1000.0
        if usage is not None:
            self.tokens_in = usage.prompt_tokens
            self.tokens_out = usage.completion_tokens
            self.embedding_tokens = usage.embedding_tokens
            self.llm_calls = usage.calls
            self.cost_usd = round(usage.cost_usd, 6)

    # -- output ------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d.pop("_open", None)
        return d

    def write(self, settings=SETTINGS) -> Optional[Path]:
        if not settings.trace_enabled:
            return None
        settings.runs_dir.mkdir(parents=True, exist_ok=True)
        path = settings.runs_dir / f"run_{self.run_id}.json"
        path.write_text(json.dumps(self.to_dict(), indent=2, default=str), encoding="utf-8")
        return path

    def timeline(self) -> str:
        """Human-readable stage timings - the first thing you look at for latency."""
        lines = [f"run {self.run_id}  |  {self.total_ms:7.0f} ms total  |  "
                 f"${self.cost_usd:.5f}  |  {self.llm_calls} llm calls"]
        for s in self.steps:
            bar = "#" * max(1, int(s.duration_ms / max(self.total_ms, 1) * 40))
            lines.append(f"  {s.name:<14} {s.duration_ms:7.0f} ms  {bar}")
        return "\n".join(lines)
