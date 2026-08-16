"""Web search tool — Tavily."""

from typing import Literal

from tavily import TavilyClient

from deep_agent.config import TAVILY_API_KEY


_tavily_client: TavilyClient | None = None


def _get_tavily() -> TavilyClient:
    global _tavily_client
    if _tavily_client is None:
        if not TAVILY_API_KEY:
            raise RuntimeError("TAVILY_API_KEY not set — web search unavailable")
        _tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    return _tavily_client


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
) -> dict:
    """Run a web search using Tavily.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return.
        topic: Search topic category — "general", "news", or "finance".
        include_raw_content: Whether to include full page content in results.
    """
    try:
        return _get_tavily().search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic,
        )
    except RuntimeError as e:
        return {"error": str(e), "results": []}
