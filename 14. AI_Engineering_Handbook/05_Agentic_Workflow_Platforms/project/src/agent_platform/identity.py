# -*- coding: utf-8 -*-
"""The three roles that matter to guardrails: authoring a workflow is not the
same authority as approving what it's about to do, which is not the same
authority as promoting it to a more trusted rollout stage."""
from __future__ import annotations

from typing import Dict, List

from .models import Principal

_PRINCIPALS: Dict[str, Principal] = {
    "u_author_dana": Principal("u_author_dana", "Dana (Ops, workflow author)", "author"),
    "u_approver_raj": Principal("u_approver_raj", "Raj (Support Lead, approver)", "approver"),
    "u_admin_lee": Principal("u_admin_lee", "Lee (Platform Admin)", "admin"),
    # A negative control: an author trying to approve or promote their own workflow.
    "u_author_wrong_hat": Principal("u_author_wrong_hat", "Dana, attempting self-approval", "author"),
}


def get_principal(user_id: str) -> Principal:
    if user_id not in _PRINCIPALS:
        raise KeyError(f"unknown principal '{user_id}'")
    return _PRINCIPALS[user_id]


def list_principals() -> List[Principal]:
    return list(_PRINCIPALS.values())
