# -*- coding: utf-8 -*-
"""Every engagement event - gate sign-offs, stage advances, escalations,
accelerator pulls, artifacts - is already logged onto `Engagement.events` as it
happens (see models.py::Engagement.log()). This module just renders and persists
that record. Mirrors observability/trace.py's role in the RAG project: "every run
produces a complete, replayable record," just for an engagement instead of a
query.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .config import SETTINGS
from .models import Engagement


def render_timeline(engagement: Engagement) -> str:
    lines = [f"engagement: {engagement.customer_name}  "
             f"(day {engagement.day}, stage={engagement.current_stage.label})"]
    lines.append("-" * 88)
    for ev in engagement.events:
        kind = ev["kind"]
        prefix = f"day {ev['day']:>2}  {ev['stage']:<28}{kind:<18}"
        if kind == "gate_signoff":
            verdict = "PASS" if ev["allowed"] else f"DENY[{ev['rule']}]"
            lines.append(f"{prefix}{ev['gate']:<26}{verdict:<20}{ev['reason']}")
        elif kind == "advance_attempt":
            verdict = "OK  " if ev["allowed"] else f"DENY[{ev['rule']}]"
            lines.append(f"{prefix}-> {ev.get('target_stage', ''):<23}{verdict:<20}{ev['reason']}")
        elif kind == "escalation_raised":
            lines.append(f"{prefix}{ev['reason']}")
        elif kind == "escalation_resolved":
            lines.append(f"{prefix}{ev['reason']}")
        elif kind == "accelerator_pull":
            tag = "reused" if ev["reused"] else "CUSTOM-BUILT"
            lines.append(f"{prefix}{ev['asset_kind']:<19}{ev['name']:<28}{tag}")
        elif kind == "artifact_produced":
            lines.append(f"{prefix}{ev['name']} (owner={ev['owner']})")
        elif kind == "eval_score":
            lines.append(f"{prefix}score={ev['score']}")
        elif kind == "human_approval":
            lines.append(f"{prefix}overridden={ev['overridden']}")
        elif kind == "deploy_attempt":
            verdict = "OK  " if ev["allowed"] else f"DENY[{ev['rule']}]"
            lines.append(f"{prefix}{verdict:<20}{ev['reason']}")
        else:
            lines.append(f"{prefix}{ev}")
    return "\n".join(lines)


def write(engagement: Engagement, settings=SETTINGS) -> Path:
    settings.runs_dir.mkdir(parents=True, exist_ok=True)
    safe_name = engagement.customer_name.lower().replace(" ", "_")
    path = settings.runs_dir / f"{safe_name}_day{engagement.day}.json"
    payload = {
        "customer_name": engagement.customer_name,
        "current_stage": engagement.current_stage.label,
        "day": engagement.day,
        "deployed": engagement.deployed,
        "events": engagement.events,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
