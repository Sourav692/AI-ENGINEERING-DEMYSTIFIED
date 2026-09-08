# -*- coding: utf-8 -*-
"""Central configuration."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_here = Path(__file__).resolve()
PACKAGE_ROOT = _here.parents[1]
PROJECT_ROOT = _here.parents[2]


@dataclass
class Settings:
    data_dir: Path = PROJECT_ROOT / "data"
    runs_dir: Path = PROJECT_ROOT / "runs"

    # Guardrail defaults - a tenant's policy overrides these, but every tenant
    # gets a cap even if nobody configured one explicitly.
    default_spend_cap_usd: float = 50.0
    default_max_steps: int = 10


SETTINGS = Settings()
