# -*- coding: utf-8 -*-
"""Identity resolution.

This module stands in for the identity provider. The important property is not how
it loads personas but *when* it is called: attributes are resolved fresh on every
request, never cached in a session and never read from anything the user controls.

That is what makes live revocation work. Remove someone from a group in the IdP and
the very next query enforces it, without touching the index.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .config import SETTINGS
from .models import Principal

_CACHE: Optional[Dict[str, Principal]] = None


def _load(path: Optional[Path] = None) -> Dict[str, Principal]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    path = Path(path or SETTINGS.identity_file)
    data = json.loads(path.read_text(encoding="utf-8"))
    _CACHE = {}
    for row in data["principals"]:
        row = {k: v for k, v in row.items() if not k.startswith("_")}
        p = Principal.from_dict(row)
        _CACHE[p.user_id] = p
    return _CACHE


def list_principals() -> List[Principal]:
    return list(_load().values())


def get_principal(user_id: str) -> Principal:
    principals = _load()
    if user_id not in principals:
        raise KeyError(f"unknown principal '{user_id}'. "
                       f"Known: {', '.join(sorted(principals))}")
    # Return a copy so a caller mutating groups (as the revocation demo does)
    # cannot corrupt the directory for other requests.
    p = principals[user_id]
    return Principal(user_id=p.user_id, display_name=p.display_name, tenant_id=p.tenant_id,
                     role=p.role, groups=list(p.groups), clearance=p.clearance,
                     region=p.region, projects=list(p.projects),
                     can_view_pii=p.can_view_pii, is_external=p.is_external)
