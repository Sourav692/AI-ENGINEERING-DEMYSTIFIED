"""Databricks Genie analytics tools — natural-language Q&A over AIA data."""

import logging

from deep_agent.clients import get_workspace_client
from deep_agent.config import GENIE_SPACES

logger = logging.getLogger("deep-agent")


def _query_genie(space_id: str, question: str) -> dict:
    # Tool exceptions kill the parent agent's stream. Catch here so a single
    # bad Genie space (trashed, permissions, transient API error) doesn't
    # crash the whole multi-step run — the agent gets an error string back
    # and can synthesise around it.
    try:
        resp = get_workspace_client().genie.start_conversation_and_wait(
            space_id=space_id, content=question,
        )
    except Exception as e:
        logger.warning(f"Genie query failed (space={space_id}): {e}")
        return {"error": str(e), "space_id": space_id}

    result: dict = {
        "status": str(resp.status),
        "conversation_id": resp.conversation_id,
    }
    for att in resp.attachments or []:
        if att.query:
            result["sql"] = att.query.query
            result["description"] = att.query.description
            if att.query.query_result_metadata:
                result["row_count"] = att.query.query_result_metadata.row_count
        if att.text:
            result["answer"] = att.text.content
        if att.suggested_questions:
            result["suggested_questions"] = att.suggested_questions.questions
    return result


def ask_customer_analytics(question: str) -> dict:
    """Ask a natural language question about AIA customer data.
    Covers customer segmentation, retention, demographics, and claim frequency.
    Args:
        question: Natural language question about customers.
    """
    return _query_genie(GENIE_SPACES["customer_analytics"], question)


def ask_distribution_channels(question: str) -> dict:
    """Ask a natural language question about AIA agent performance and distribution channels.
    Covers agent sales, premium volumes, channel comparisons, and top performers.
    Args:
        question: Natural language question about agents or distribution channels.
    """
    return _query_genie(GENIE_SPACES["distribution_channels"], question)


def ask_policy_underwriting(question: str) -> dict:
    """Ask a natural language question about AIA policies and underwriting.
    Covers premium volumes, policy counts, renewal rates, product mix, and underwriting metrics.
    Args:
        question: Natural language question about policies or underwriting.
    """
    return _query_genie(GENIE_SPACES["policy_underwriting"], question)


def ask_claims_analytics(question: str) -> dict:
    """Ask a natural language question about AIA insurance claims.
    Covers claim counts, amounts, processing times, fraud scores, and regional breakdowns.
    Args:
        question: Natural language question about claims or fraud.
    """
    return _query_genie(GENIE_SPACES["claims_analytics"], question)
