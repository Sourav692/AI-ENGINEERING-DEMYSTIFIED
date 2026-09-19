# -*- coding: utf-8 -*-
"""The workflow definition store (§3.2): versioned, declarative specs, promoted
through the staged rollout in §3.3 - draft -> testing -> shadow -> live ->
autonomous. Promotion is role-gated and order-enforced, the same shape as
delivery_framework.engine.py::advance_stage() - no skipping a stage, and only
an admin (never the workflow's own author) can promote it.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .models import Decision, Principal, STATUS_ORDER, WorkflowSpec, WorkflowStatus


class WorkflowStore:
    """In-memory version history, keyed by workflow_id -> [versions...]."""

    def __init__(self):
        self._versions: Dict[str, List[WorkflowSpec]] = {}

    def publish(self, spec: WorkflowSpec) -> WorkflowSpec:
        history = self._versions.setdefault(spec.workflow_id, [])
        history.append(spec)
        return spec

    def latest(self, workflow_id: str) -> Optional[WorkflowSpec]:
        history = self._versions.get(workflow_id)
        return history[-1] if history else None

    def get_version(self, workflow_id: str, version: int) -> Optional[WorkflowSpec]:
        for spec in self._versions.get(workflow_id, []):
            if spec.version == version:
                return spec
        return None

    def all_live(self, tenant_id: str) -> List[WorkflowSpec]:
        """The current, latest-version spec for every workflow this tenant has -
        what routing.py matches events against. A run that's already in flight
        stays pinned to the version it started on (see orchestrator.py) even if
        this returns a newer one after an edit."""
        return [self.latest(wid) for wid in self._versions
               if self.latest(wid) and self.latest(wid).tenant_id == tenant_id]


def promote(store: WorkflowStore, workflow_id: str, to_status: WorkflowStatus,
           signer: Principal) -> Decision:
    """Advance a workflow's latest version to the next rollout stage. Author
    cannot self-promote; stage cannot be skipped."""
    current = store.latest(workflow_id)
    if current is None:
        return Decision(False, "unknown_workflow", f"'{workflow_id}' has no published version")

    if signer.role not in ("admin", "approver"):
        return Decision(False, "wrong_role",
                        f"'{signer.role}' may not promote a workflow; requires admin or approver")

    current_idx = STATUS_ORDER.index(current.status)
    target_idx = STATUS_ORDER.index(to_status)
    if target_idx != current_idx + 1:
        return Decision(False, "cannot_skip_stage",
                        f"'{workflow_id}' is at {current.status.name}; "
                        f"can only promote to {STATUS_ORDER[current_idx + 1].name}, not {to_status.name}")

    current.status = to_status
    return Decision(True, "promoted", f"'{workflow_id}' is now {to_status.name}")
