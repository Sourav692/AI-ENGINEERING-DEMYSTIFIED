# -*- coding: utf-8 -*-
"""The per-tenant tool registry (§3.2) and argument validation (§3.4) -
"prefer constrained tool schemas over free-text arguments; validate every tool
argument before execution." A workflow step's args are data (a template with
{field} placeholders resolved from the event), never a free-text instruction to
an LLM about what to do - the LLM never picks the tool's raw arguments.
"""
from __future__ import annotations

from typing import Any, Dict, List

from .models import Decision, ToolDefinition

TYPE_CHECKS = {
    "str": lambda v: isinstance(v, str),
    "int": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "float": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "bool": lambda v: isinstance(v, bool),
}

REGISTRY: Dict[str, ToolDefinition] = {
    "draft_reply": ToolDefinition(
        name="draft_reply", description="Draft a reply for human review or auto-send",
        schema={"ticket_id": "str", "body": "str"}, required=["ticket_id", "body"],
        destructive=False, scopes=["support.write_draft"]),
    "issue_refund": ToolDefinition(
        name="issue_refund", description="Issue a refund against an order",
        schema={"order_id": "str", "amount_usd": "float"}, required=["order_id", "amount_usd"],
        destructive=True, scopes=["billing.refund"]),
    "close_ticket": ToolDefinition(
        name="close_ticket", description="Close a support ticket",
        schema={"ticket_id": "str"}, required=["ticket_id"],
        destructive=True, scopes=["support.close"]),
    "tag_ticket": ToolDefinition(
        name="tag_ticket", description="Add a tag to a ticket - non-destructive",
        schema={"ticket_id": "str", "tag": "str"}, required=["ticket_id", "tag"],
        destructive=False, scopes=["support.write_tag"]),
}


def get_tool(name: str) -> ToolDefinition:
    if name not in REGISTRY:
        raise KeyError(f"unknown tool '{name}'")
    return REGISTRY[name]


def validate_args(tool: ToolDefinition, args: Dict[str, Any]) -> Decision:
    missing = [f for f in tool.required if f not in args]
    if missing:
        return Decision(False, "missing_required_args", f"missing: {missing}")

    for field, value in args.items():
        expected = tool.schema.get(field)
        if expected is None:
            return Decision(False, "unknown_arg", f"'{field}' is not a declared parameter of '{tool.name}'")
        check = TYPE_CHECKS[expected]
        if not check(value):
            return Decision(False, "type_mismatch",
                            f"'{field}' expected {expected}, got {type(value).__name__}")

    return Decision(True, "args_valid", "arguments match the tool's schema")
