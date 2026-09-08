# -*- coding: utf-8 -*-
"""Channel adapters - normalise inbound events from every channel into one
canonical Event schema (§3.2). Nothing downstream ever branches on "which
channel did this come from" again; it only ever sees an Event.

Each adapter's real job, same instinct as the RAG project's loader translating a
source system's permission model: read a wildly different payload shape and
extract the same three things every workflow trigger actually needs - what kind
of thing happened, what tenant it belongs to, and what entity it's about.
"""
from __future__ import annotations

from typing import Any, Dict

from .models import Channel, Event


def from_webhook(payload: Dict[str, Any]) -> Event:
    """A Zendesk-shaped webhook payload."""
    return Event(
        channel=Channel.WEBHOOK,
        event_type=payload["type"],
        tenant_id=payload["tenant_id"],
        target_entity_id=str(payload["ticket_id"]),
        payload=payload,
        raw_ref=f"webhook:{payload.get('id', 'unknown')}",
    )


def from_slack(payload: Dict[str, Any]) -> Event:
    """A Slack message-event-shaped payload - very differently shaped from a
    webhook, on purpose, to prove the adapters are actually doing translation
    work and not just relabeling the same dict."""
    text = payload.get("text", "")
    event_type = "urgent_message" if payload.get("is_urgent") else "message"
    return Event(
        channel=Channel.SLACK,
        event_type=event_type,
        tenant_id=payload["team_id"],
        target_entity_id=payload.get("thread_ref", payload["ts"]),
        payload={"text": text, "channel_name": payload.get("channel_name", "")},
        raw_ref=f"slack:{payload['ts']}",
    )


def from_email(payload: Dict[str, Any]) -> Event:
    return Event(
        channel=Channel.EMAIL,
        event_type="email_received",
        tenant_id=payload["tenant_id"],
        target_entity_id=payload.get("thread_id", payload["message_id"]),
        payload={"subject": payload.get("subject", ""), "body": payload.get("body", "")},
        raw_ref=f"email:{payload['message_id']}",
    )
