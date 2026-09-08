# -*- coding: utf-8 -*-
"""Intake - the ACL-validation-style refusal gate at the very start (§5.3, §5.4).

A scoping request with no measurable success metric, or no assigned customer
SME, is refused before day 1 starts - exactly the same instinct as
enterprise_rag_platform's loader.py refusing a document with no usable ACL.
Starting the clock on an engagement you already know can't be measured is a
worse failure than never starting it.
"""
from __future__ import annotations

from typing import List, Optional

from .config import SETTINGS
from .models import Engagement


class ScopingRefused(Exception):
    """Raised when an engagement request cannot be started at all."""


def intake(customer_name: str,
          success_metrics: List[str],
          data_sources: List[str],
          customer_sme: Optional[str],
          settings=SETTINGS) -> Engagement:
    """Validate a scoping request. Refuses to create an Engagement rather than
    starting a 2-week clock on something that was never going to be measurable."""
    reasons = []
    if settings.require_measurable_metrics and not success_metrics:
        reasons.append("no measurable success metrics were agreed")
    if settings.require_customer_sme and not customer_sme:
        reasons.append("no customer SME is assigned - contractual prerequisite")
    if not data_sources:
        reasons.append("no data sources named in the inventory")

    if reasons:
        raise ScopingRefused(
            f"refusing to start '{customer_name}': " + "; ".join(reasons))

    return Engagement(customer_name=customer_name, success_metrics=success_metrics,
                      data_sources=data_sources, customer_sme=customer_sme)
