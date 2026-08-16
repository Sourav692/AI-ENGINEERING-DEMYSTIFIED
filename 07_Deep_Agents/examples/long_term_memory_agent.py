import json
import os
import re
import uuid
from datetime import datetime
from typing import Literal

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, LocalShellBackend
from langgraph.checkpoint.memory import MemorySaver
from databricks_langchain import ChatDatabricks
from langchain_core.messages import BaseMessage
from tavily import TavilyClient
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

load_dotenv()

# ============ Backend selection ============
USE_SANDBOX = os.environ.get("USE_SANDBOX", "false").lower() == "true"

# Setup directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
SKILLS_DIR = os.path.join(BASE_DIR, "skills")

os.makedirs(PROJECTS_DIR, exist_ok=True)


# ============ Long-Term Memory (JSON file on disk) ============
# Memories are stored in a JSON file so they survive across script restarts.
# The file lives alongside this script at ./long_term_memories.json.
#
# For production, swap this with PostgresStore:
#   from langgraph.store.postgres import PostgresStore

MEMORY_FILE = os.path.join(BASE_DIR, "long_term_memories.json")

# Default user — in production, derive from auth context
CURRENT_USER_ID = "default-user"


def _load_memories() -> dict:
    """Load memories from the JSON file on disk."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_memories(memories: dict) -> None:
    """Flush the full memory dict to the JSON file on disk."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(memories, f, indent=2, ensure_ascii=False)


def _user_namespace_key() -> str:
    """Return the dict key for the current user's memory namespace."""
    return f"memories:{CURRENT_USER_ID}"


# ============ Memory Tools ============

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
    memories = _load_memories()
    ns_key = _user_namespace_key()
    if ns_key not in memories:
        memories[ns_key] = {}

    memory_id = str(uuid.uuid4())
    memories[ns_key][memory_id] = {
        "content": content,
        "category": category,
        "saved_at": datetime.now().isoformat(),
    }
    _save_memories(memories)
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
    memories = _load_memories()
    ns_key = _user_namespace_key()
    user_memories = memories.get(ns_key, {})

    if not user_memories:
        return "No memories found."

    matched = []
    for mem_id, entry in user_memories.items():
        content = entry.get("content", "")
        cat = entry.get("category", "general")
        saved_at = entry.get("saved_at", "unknown")

        # Filter by category if provided
        if category and cat != category:
            continue

        # Filter by query text if provided
        if query and query.lower() not in content.lower():
            continue

        matched.append(f"- [{cat}] {content} (saved: {saved_at})")

    if not matched:
        filter_desc = f"category='{category}'" if category else f"'{query}'"
        return f"No memories matching {filter_desc} found."

    return f"Found {len(matched)} memories:\n" + "\n".join(matched)


def forget_memory(content_substring: str) -> str:
    """Remove a specific memory from long-term storage.

    Use this when the user explicitly asks you to forget something,
    or when stored information is no longer accurate.

    Args:
        content_substring: A substring that uniquely identifies the memory
                           to delete. The first matching memory will be removed.
    """
    memories = _load_memories()
    ns_key = _user_namespace_key()
    user_memories = memories.get(ns_key, {})

    for mem_id, entry in user_memories.items():
        if content_substring.lower() in entry.get("content", "").lower():
            deleted_content = entry["content"]
            del memories[ns_key][mem_id]
            _save_memories(memories)
            return f"Memory deleted: {deleted_content}"

    return f"No memory matching '{content_substring}' found."


# ============ Project folder tool ============

def name_project(project_name: str) -> str:
    """Create a project folder with the given name.

    Call this FIRST before writing any files. The name should be a short,
    descriptive, lowercase slug using hyphens (e.g., 'email-validator',
    'todo-api', 'csv-parser'). The folder will be created under ./projects/.

    Args:
        project_name: A short, lowercase, hyphenated name for the project.
    """
    slug = project_name.lower().strip()
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = slug.strip("-")

    if not slug:
        return "Error: Could not create a valid project name. Try a descriptive name like 'email-validator'"

    project_path = os.path.join(PROJECTS_DIR, slug)
    os.makedirs(project_path, exist_ok=True)

    return (
        f"Project folder created: projects/{slug}/\n"
        f"Write all files into this folder using the folder name as prefix "
        f"- e.g write_file('projects/{slug}/main.py', ...)"
    )


# ============ Tavily search tool ============
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY", ""))


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
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


# ============ Databricks Genie tools ============
databricks_client = WorkspaceClient()

GENIE_SPACES = {
    "customer_analytics": "01f1272d4de1188cac8feeb7e71bdb69",
    "distribution_channels": "01f1272d4d271203ad122e9280470248",
    "policy_underwriting": "01f1272d4c6b1fb49223785ab841befd",
    "claims_analytics": "01f1272d4ba6144ba75d868762f1925d",
}


def _query_genie(space_id: str, question: str) -> dict:
    """Query a Databricks Genie space and return structured results."""
    resp = databricks_client.genie.start_conversation_and_wait(
        space_id=space_id,
        content=question,
    )
    result = {
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
    Data source: aia_multi_agent_catalog.silver.customer_360

    Args:
        question: Natural language question about customers.
    """
    return _query_genie(GENIE_SPACES["customer_analytics"], question)


def ask_distribution_channels(question: str) -> dict:
    """Ask a natural language question about AIA agent performance and distribution channels.

    Covers agent sales, premium volumes, channel comparisons, and top performers.
    Data source: aia_multi_agent_catalog.gold.agent_performance

    Args:
        question: Natural language question about agents or distribution channels.
    """
    return _query_genie(GENIE_SPACES["distribution_channels"], question)


def ask_policy_underwriting(question: str) -> dict:
    """Ask a natural language question about AIA policies and underwriting.

    Covers premium volumes, policy counts, renewal rates, product mix, and underwriting metrics.
    Data sources: aia_multi_agent_catalog.gold.policy_performance, silver.enriched_policies

    Args:
        question: Natural language question about policies or underwriting.
    """
    return _query_genie(GENIE_SPACES["policy_underwriting"], question)


def ask_claims_analytics(question: str) -> dict:
    """Ask a natural language question about AIA insurance claims.

    Covers claim counts, amounts, processing times, fraud scores, and regional breakdowns.
    Data sources: aia_multi_agent_catalog.gold.claims_summary, gold.fraud_analysis, silver.enriched_claims

    Args:
        question: Natural language question about claims or fraud.
    """
    return _query_genie(GENIE_SPACES["claims_analytics"], question)


# ============ Subagents ============

memory_manager = {
    "name": "memory-manager",
    "description": (
        "Manages long-term memory — saving, recalling, and organizing information "
        "the user wants remembered across conversations. Use when the user shares "
        "preferences, asks you to remember something, or when past context would help."
    ),
    "system_prompt": "Follow the memory-manager skill instructions.",
    "skills": ["/skills/"],
    "tools": [save_memory, recall_memories, forget_memory],
}

senior_developer = {
    "name": "senior-developer",
    "description": (
        "Senior Python developer that plans, writes, and delivers complete projects. "
        "Use for any coding task that needs structured implementation."
    ),
    "system_prompt": "Follow the senior-developer skill instructions.",
    "skills": ["/skills/"],
    "tools": [name_project],
}

code_reviewer = {
    "name": "code-reviewer",
    "description": (
        "Reviews Python code for bugs, style issues, and best practices. "
        "Use when code has been written and needs a quality check before delivery."
    ),
    "system_prompt": "Follow the code-reviewer skill instructions.",
    "skills": ["/skills/"],
    "tools": [],
}

research_agent = {
    "name": "research-agent",
    "description": (
        "Conducts in-depth web research on any topic. "
        "Use when current information, background research, or fact-checking is needed."
    ),
    "system_prompt": "Follow the research-agent skill instructions.",
    "skills": ["/skills/"],
    "tools": [internet_search],
}

aia_customer_agent = {
    "name": "aia-customer-analytics",
    "description": (
        "Queries AIA customer data — segmentation, retention, demographics, claim frequency. "
        "Use when the user asks about customers or customer segments."
    ),
    "system_prompt": "Follow the aia-customer-analytics skill instructions.",
    "skills": ["/skills/"],
    "tools": [ask_customer_analytics],
}

aia_distribution_agent = {
    "name": "aia-distribution-channels",
    "description": (
        "Queries AIA agent performance and distribution channel data. "
        "Use when the user asks about agents, sales channels, or distribution performance."
    ),
    "system_prompt": "Follow the aia-distribution-channels skill instructions.",
    "skills": ["/skills/"],
    "tools": [ask_distribution_channels],
}

aia_policy_agent = {
    "name": "aia-policy-underwriting",
    "description": (
        "Queries AIA policy and underwriting data — premiums, policy counts, renewals, product mix. "
        "Use when the user asks about policies, premiums, or underwriting."
    ),
    "system_prompt": "Follow the aia-policy-underwriting skill instructions.",
    "skills": ["/skills/"],
    "tools": [ask_policy_underwriting],
}

aia_claims_agent = {
    "name": "aia-claims-analytics",
    "description": (
        "Queries AIA claims data — claim counts, amounts, processing times, fraud scores. "
        "Use when the user asks about claims, fraud, or claim processing."
    ),
    "system_prompt": "Follow the aia-claims-analytics skill instructions.",
    "skills": ["/skills/"],
    "tools": [ask_claims_analytics],
}

subagents = [
    memory_manager,
    senior_developer,
    code_reviewer,
    research_agent,
    aia_customer_agent,
    aia_distribution_agent,
    aia_policy_agent,
    aia_claims_agent,
]


# ============ Backend factory ============

def _create_backend():
    """Create the appropriate backend based on USE_SANDBOX env var."""
    if USE_SANDBOX:
        return LocalShellBackend(root_dir=PROJECTS_DIR)
    return FilesystemBackend(root_dir=BASE_DIR, virtual_mode=True)


# ============ System prompt with memory awareness ============

SYSTEM_PROMPT = """You are a multi-agent orchestrator with long-term memory.

## Memory Guidelines

You have access to long-term memory tools that persist information across conversations.

**When to save memories:**
- The user shares a preference ("I prefer dark themes", "I like concise answers")
- The user tells you a fact about themselves ("My name is Alice", "I work on the analytics team")
- Important decisions are made ("We decided to use FastAPI for the backend")
- Project context that will be useful later ("The deadline is March 15")
- The user explicitly asks you to remember something

**When to recall memories:**
- At the START of each conversation — proactively check for stored context
- When the user references something from a previous conversation
- When user preferences would improve your response
- Before making recommendations that past context could inform

**When to forget:**
- Only when the user explicitly asks you to forget something
- When information is confirmed to be outdated

**Categories for organizing memories:**
- "preference" — User likes/dislikes, communication style
- "fact" — Personal details, team info, roles
- "decision" — Architectural choices, agreements
- "project" — Deadlines, goals, requirements
- "feedback" — What worked well, what to avoid

Always be transparent about what you remember. When recalling memories, briefly
mention the context so the user knows what information you're working with.
"""


# ============ Agent setup ============

checkpointer = MemorySaver()

model = ChatDatabricks(
    endpoint="databricks-claude-opus-4-6",
    temperature=0.1,
)

agent = create_deep_agent(
    model=model,
    tools=[
        name_project,
        internet_search,
        save_memory,
        recall_memories,
        forget_memory,
        ask_customer_analytics,
        ask_distribution_channels,
        ask_policy_underwriting,
        ask_claims_analytics,
    ],
    system_prompt=SYSTEM_PROMPT,
    skills=["/skills/"],
    subagents=subagents,
    backend=_create_backend(),
    checkpointer=checkpointer,
)


def main():
    banner = r"""
   __                         ______
  / /   ____  ____  ____ _   /_  __/__  _________ ___
 / /   / __ \/ __ \/ __ `/    / / / _ \/ ___/ __ `__ \
/ /___/ /_/ / / / / /_/ /    / / /  __/ /  / / / / / /
\____/\____/_/ /_/\__, /    /_/  \___/_/  /_/ /_/ /_/
                 /____/
    __  ___                                 ___                    __
   /  |/  /__  ____ ___  ____  _______  __/   | ____ ____  ____  / /_
  / /|_/ / _ \/ __ `__ \/ __ \/ ___/ / / / /| |/ __ `/ _ \/ __ \/ __/
 / /  / /  __/ / / / / / /_/ / /  / /_/ / ___ / /_/ /  __/ / / / /_
/_/  /_/\___/_/ /_/ /_/\____/_/   \__, /_/  |_\__, /\___/_/ /_/\__/
                                 /____/      /____/
"""
    print(banner)
    print("Multi-Agent Orchestrator with Long-Term Memory")
    print("=" * 60)
    print()

    backend_label = (
        "LocalShell (code execution enabled)"
        if USE_SANDBOX
        else "Filesystem (virtual, no code execution)"
    )
    print(f"Backend  : {backend_label}")
    print(f"Memory   : {MEMORY_FILE}")
    print(f"Projects : {PROJECTS_DIR}/")
    print()
    print("Your agent remembers across threads within this session.")
    print("Type 'quit' to exit, 'new' to start a new thread.")
    print()

    task_count = 0
    thread_id = 1

    while True:
        user_input = input(f"[thread-{thread_id}] > ").strip()

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if user_input.lower() == "new":
            thread_id += 1
            print(f"\n--- Started new thread: thread-{thread_id} ---")
            print("(Long-term memories carry over to this thread)\n")
            continue

        if not user_input:
            continue

        task_count += 1
        config = {"configurable": {"thread_id": f"thread-{thread_id}"}}

        print()
        print("-" * 60)
        print("Agent is Working...")
        print("-" * 60)
        print()

        for step in agent.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config,
            stream_mode="updates",
        ):
            for node_name, update in step.items():
                if update and (messages := update.get("messages")):
                    for message in (
                        messages if isinstance(messages, list) else [messages]
                    ):
                        if isinstance(message, BaseMessage):
                            message.pretty_print()

        print()


if __name__ == "__main__":
    main()
