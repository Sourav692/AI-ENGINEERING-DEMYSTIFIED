# -*- coding: utf-8 -*-
"""Trigger and routing layer (§3.2): matches an Event to a workflow, and
resolves the case §3.5 asks about directly - two workflows trigger on the same
event and conflict.

Two independent mechanisms, deliberately:
  1. PRIORITY - among workflows whose trigger matches, the highest-priority one
     wins. This is a design-time decision (which workflow SHOULD run).
  2. EXCLUSIVITY LOCK - a target entity (a ticket, an order) can only have one
     workflow actively running against it at a time, regardless of how many
     workflows match. This is a run-time safety property (two workflows must
     never both be mutating the same entity concurrently), and it holds even
     if the priority ordering was misconfigured.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .models import Decision, Event, WorkflowSpec, WorkflowStatus

# In-memory lock: target_entity_id -> run_id currently holding it.
_LOCKS: Dict[str, str] = {}


def matching_workflows(event: Event, workflows: List[WorkflowSpec]) -> List[WorkflowSpec]:
    out = []
    for wf in workflows:
        if wf.tenant_id != event.tenant_id:
            continue
        if wf.status == WorkflowStatus.DRAFT:
            continue   # a draft never fires on real events, even in test channels
        for t in wf.triggers:
            if t.channel == event.channel and t.event_type == event.event_type:
                out.append(wf)
                break
    return out


def route(event: Event, workflows: List[WorkflowSpec]) -> Decision:
    """Pick exactly one workflow for this event, or explain why none ran."""
    candidates = matching_workflows(event, workflows)
    if not candidates:
        return Decision(False, "no_trigger_match", "no live workflow triggers on this event")

    if event.target_entity_id in _LOCKS:
        return Decision(False, "entity_locked",
                        f"'{event.target_entity_id}' already has an active run "
                        f"({_LOCKS[event.target_entity_id]}) - refusing a second concurrent run")

    winner = max(candidates, key=lambda w: max(
        t.priority for t in w.triggers if t.channel == event.channel and t.event_type == event.event_type))
    return Decision(True, "routed", f"routed to '{winner.workflow_id}' v{winner.version}")


def selected_workflow(event: Event, workflows: List[WorkflowSpec]) -> Optional[WorkflowSpec]:
    candidates = matching_workflows(event, workflows)
    if not candidates:
        return None
    return max(candidates, key=lambda w: max(
        t.priority for t in w.triggers if t.channel == event.channel and t.event_type == event.event_type))


def acquire_lock(target_entity_id: str, run_id: str) -> bool:
    if target_entity_id in _LOCKS:
        return False
    _LOCKS[target_entity_id] = run_id
    return True


def release_lock(target_entity_id: str):
    _LOCKS.pop(target_entity_id, None)
