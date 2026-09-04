# -*- coding: utf-8 -*-
"""Run store and trace log (§3.2): "every step, prompt, tool call, and output
persisted for debugging and audit." Renders and persists what `Run.log()`
already accumulated as the run executed."""
from __future__ import annotations

import json
from pathlib import Path

from .config import SETTINGS
from .models import Run


def render_run(run: Run) -> str:
    lines = [f"run {run.run_id}  workflow={run.workflow_id} v{run.workflow_version}  "
             f"state={run.state.value}  cost=${run.total_cost_usd:.2f}"]
    lines.append("-" * 96)
    for ev in run.events:
        kind = ev["kind"]
        if kind == "step_authorize":
            verdict = "OK  " if ev["allowed"] else f"DENY[{ev['rule']}]"
            lines.append(f"  step {ev['step_index']}  {kind:<16}{ev['step']:<16}{verdict:<26}{ev['reason']}")
        elif kind == "step_executed":
            tag = "APPLIED" if ev["side_effect_applied"] else "no-op (idempotent replay)"
            lines.append(f"  step {ev['step_index']}  {kind:<16}{ev['step']:<16}{tag:<26}${ev['cost_usd']:.2f}")
        elif kind == "step_rejected":
            lines.append(f"  step {ev['step_index']}  {kind:<16}{ev['step']:<16}[{ev['rule']}] {ev['reason']}")
        elif kind == "simulated_crash":
            lines.append(f"  step {ev['step_index']}  *** CRASH after '{ev['after_step']}' ***")
        elif kind == "lock_denied":
            lines.append(f"  {kind:<16}target={ev['target']}")
        elif kind == "run_completed":
            lines.append(f"  step {ev['step_index']}  RUN COMPLETE")
        else:
            lines.append(f"  {ev}")
    return "\n".join(lines)


def write(run: Run, settings=SETTINGS) -> Path:
    settings.runs_dir.mkdir(parents=True, exist_ok=True)
    path = settings.runs_dir / f"{run.run_id}.json"
    payload = {
        "run_id": run.run_id, "workflow_id": run.workflow_id, "workflow_version": run.workflow_version,
        "state": run.state.value, "total_cost_usd": run.total_cost_usd, "events": run.events,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
