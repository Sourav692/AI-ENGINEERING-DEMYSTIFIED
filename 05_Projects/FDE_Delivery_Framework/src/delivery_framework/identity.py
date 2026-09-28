# -*- coding: utf-8 -*-
"""The four roles that can sign off a gate. Resolved by lookup, never assumed."""
from __future__ import annotations

from typing import Dict, List

from .models import Principal

_PRINCIPALS: Dict[str, Principal] = {
    "u_fda_sourav": Principal("u_fda_sourav", "Sourav (Forward Deployed Architect)", "fda"),
    "u_sec_priya": Principal("u_sec_priya", "Priya (Security Reviewer)", "security_reviewer"),
    "u_sme_northwind": Principal("u_sme_northwind", "Alex (Northwind Customer SME)", "customer_sme"),
    "u_sponsor_northwind": Principal("u_sponsor_northwind", "Jordan (Northwind Exec Sponsor)", "sponsor"),
    # A negative control, same idea as u_attacker_other_tenant in the RAG project:
    # right person, wrong hat - proves role-checking isn't decorative.
    "u_fda_wrong_hat": Principal("u_fda_wrong_hat", "Sourav, attempting a security sign-off", "fda"),
}


def get_principal(user_id: str) -> Principal:
    if user_id not in _PRINCIPALS:
        raise KeyError(f"unknown principal '{user_id}'")
    return _PRINCIPALS[user_id]


def list_principals() -> List[Principal]:
    return list(_PRINCIPALS.values())
