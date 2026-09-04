# -*- coding: utf-8 -*-
"""Put `src/` on sys.path so the scripts run without an editable install."""
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
