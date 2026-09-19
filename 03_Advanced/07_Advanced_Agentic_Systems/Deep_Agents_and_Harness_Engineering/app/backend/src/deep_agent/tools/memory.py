"""Long-term memory tools — exposed to the LLM."""

from deep_agent.stores.lakebase import get_memory_db


def save_memory(content: str, category: str = "general") -> str:
    """Save a piece of information to long-term memory for future recall.

    Use this tool when the user shares preferences, facts about themselves,
    important decisions, project context, or anything that should be
    remembered across conversations.

    Args:
        content: The information to remember. Be specific and concise.
        category: A short label to organize the memory (e.g., "preference",
                  "fact", "decision", "project", "feedback"). Defaults to "general".
    """
    get_memory_db().save(content, category)
    return f"Memory saved (category: {category}): {content}"


def recall_memories(query: str = "", category: str = "") -> str:
    """Search long-term memory for previously saved information.

    Use this tool at the start of conversations or when the user references
    something they told you before. Also use it proactively when context
    about the user's preferences, past decisions, or project details
    would improve your response.

    Args:
        query: A search term to find relevant memories. Leave empty to
               retrieve all memories.
        category: Optional category filter (e.g., "preference", "fact",
                  "decision"). Leave empty to search all categories.
    """
    rows = get_memory_db().recall(query, category)
    if not rows:
        filter_desc = (
            f"category='{category}'" if category
            else f"'{query}'" if query
            else "any"
        )
        return f"No memories matching {filter_desc} found."

    lines = [f"- [{r['category']}] {r['content']} (saved: {r['saved_at']})" for r in rows]
    return f"Found {len(lines)} memories:\n" + "\n".join(lines)


def forget_memory(content_substring: str) -> str:
    """Remove a specific memory from long-term storage.

    Use this when the user explicitly asks you to forget something,
    or when stored information is no longer accurate.

    Args:
        content_substring: A substring that uniquely identifies the memory
                           to delete. The first matching memory will be removed.
    """
    result = get_memory_db().forget(content_substring)
    if result:
        return f"Memory deleted: {result['content']}"
    return f"No memory matching '{content_substring}' found."
