# -*- coding: utf-8 -*-
"""The reusable accelerator library (§5.3) - connectors, prompt templates, an
eval harness, guardrail policies, dashboard templates. A stage pulls from here
first; only what genuinely doesn't exist yet gets custom-built. The ratio of
pulled:custom is `metrics.py::accelerator_reuse_rate()` - the actual measure of
whether a delivery is "productised" or "bespoke heroics"."""
from __future__ import annotations

from typing import List

from .models import AcceleratorAsset, Engagement, Pull

LIBRARY: List[AcceleratorAsset] = [
    AcceleratorAsset("zendesk_connector", "connector", "Zendesk ticket + KB ingestion"),
    AcceleratorAsset("confluence_connector", "connector", "Confluence space + page ingestion"),
    AcceleratorAsset("salesforce_connector", "connector", "Salesforce object + record ingestion"),
    AcceleratorAsset("support_triage_prompt", "prompt_template", "Tier-1 support triage synthesis prompt"),
    AcceleratorAsset("groundedness_prompt", "prompt_template", "Standard groundedness-judge prompt"),
    AcceleratorAsset("golden_set_harness", "eval_harness", "recall@k / MRR / groundedness / leak-rate harness"),
    AcceleratorAsset("pii_redaction_policy", "guardrail_policy", "Standard PII detection + redaction ruleset"),
    AcceleratorAsset("destructive_action_gate", "guardrail_policy", "Confirmation-gate policy for write actions"),
    AcceleratorAsset("eval_baseline_dashboard", "dashboard_template", "Eval-score-over-time dashboard"),
    AcceleratorAsset("cost_attribution_dashboard", "dashboard_template", "Per-tenant token/cost dashboard"),
]


def pull_or_build(engagement: Engagement, kind: str, name: str) -> Pull:
    """Try to reuse a named accelerator asset; fall back to marking it custom-built."""
    reused = any(a.kind == kind and a.name == name for a in LIBRARY)
    pull = Pull(kind=kind, name=name, reused=reused, day=engagement.day)
    engagement.pulls.append(pull)
    engagement.log("accelerator_pull", asset_kind=kind, name=name, reused=reused)
    return pull
