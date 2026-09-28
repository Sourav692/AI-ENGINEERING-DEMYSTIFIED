# -*- coding: utf-8 -*-
"""Central configuration."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_here = Path(__file__).resolve()
PACKAGE_ROOT = _here.parents[1]              # src/
PROJECT_ROOT = _here.parents[2]              # delivery_framework_platform/


@dataclass
class Settings:
    data_dir: Path = PROJECT_ROOT / "data"
    runs_dir: Path = PROJECT_ROOT / "runs"

    # The hard gate: escalate if data access isn't granted by this day (§5.4 -
    # "data access delays: start day 1, escalate day 3").
    data_access_escalation_day: int = 3

    # A run is refused at intake if success metrics aren't measurable, or no
    # customer SME is assigned - see pipeline.py::intake().
    require_measurable_metrics: bool = True
    require_customer_sme: bool = True


SETTINGS = Settings()
