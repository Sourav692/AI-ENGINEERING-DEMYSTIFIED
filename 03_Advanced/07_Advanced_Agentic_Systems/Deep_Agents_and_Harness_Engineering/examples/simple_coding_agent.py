import os
import re
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
# Set USE_SANDBOX=true in .env to use LangSmith sandbox (cloud code execution).
# Default: FilesystemBackend (virtual mode, no code execution).
USE_SANDBOX = os.environ.get("USE_SANDBOX", "false").lower() == "true"

# Setup directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
SKILLS_DIR = os.path.join(BASE_DIR, "skills")

os.makedirs(PROJECTS_DIR, exist_ok=True)

# Project folder naming tool
def name_project(project_name: str) -> str:

    """Create a project folder with the given name.

    Call this FIRST before writing any files. The name should be a short,
    descriptive, lowercase slug using hyphens (e.g., 'email-validator',
    'todo-api', 'csv-parser'). The folder will be created under ./projects/.

    Args:
        project_name: A short, lowercase, hyphenated name for the project.
    """

    # Sanitize
    slug = project_name.lower().strip()
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = slug.strip("-")

    if not slug:
        return "Error: Could not create a valid project name. Try a descriptive name like 'email-validator'"
    
    project_path = os.path.join(PROJECTS_DIR, slug)
    os.makedirs(project_path, exist_ok=True)

    return f"Project folder created: projects/{slug}/\nWrite all files into this folder using the folder name as prefix - e.g write_file('projects/{slug}/main.py', ...)"


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

# Genie space IDs are workspace-specific: set these in the project-root .env.
GENIE_SPACE_ENV = {
    "customer_analytics": "GENIE_SPACE_CUSTOMER_ANALYTICS",
    "distribution_channels": "GENIE_SPACE_DISTRIBUTION_CHANNELS",
    "policy_underwriting": "GENIE_SPACE_POLICY_UNDERWRITING",
    "claims_analytics": "GENIE_SPACE_CLAIMS_ANALYTICS",
}


def _query_genie(domain: str, question: str) -> dict:
    """Query a Databricks Genie space and return structured results."""
    space_id = os.environ.get(GENIE_SPACE_ENV[domain], "").strip()
    if not space_id:
        return {"error": f"Genie space for '{domain}' is not configured — set {GENIE_SPACE_ENV[domain]} in .env."}
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
    """Ask a natural language question about Acme Life customer data.

    Covers customer segmentation, retention, demographics, and claim frequency.
    Data source: acme_life_multi_agent_catalog.silver.customer_360

    Args:
        question: Natural language question about customers.
    """
    return _query_genie("customer_analytics", question)


def ask_distribution_channels(question: str) -> dict:
    """Ask a natural language question about Acme Life agent performance and distribution channels.

    Covers agent sales, premium volumes, channel comparisons, and top performers.
    Data source: acme_life_multi_agent_catalog.gold.agent_performance

    Args:
        question: Natural language question about agents or distribution channels.
    """
    return _query_genie("distribution_channels", question)


def ask_policy_underwriting(question: str) -> dict:
    """Ask a natural language question about Acme Life policies and underwriting.

    Covers premium volumes, policy counts, renewal rates, product mix, and underwriting metrics.
    Data sources: acme_life_multi_agent_catalog.gold.policy_performance, silver.enriched_policies

    Args:
        question: Natural language question about policies or underwriting.
    """
    return _query_genie("policy_underwriting", question)


def ask_claims_analytics(question: str) -> dict:
    """Ask a natural language question about Acme Life insurance claims.

    Covers claim counts, amounts, processing times, fraud scores, and regional breakdowns.
    Data sources: acme_life_multi_agent_catalog.gold.claims_summary, gold.fraud_analysis, silver.enriched_claims

    Args:
        question: Natural language question about claims or fraud.
    """
    return _query_genie("claims_analytics", question)


# ============ Subagents ============
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

acme_life_customer_agent = {
    "name": "insurer-customer-analytics",
    "description": (
        "Queries Acme Life customer data — segmentation, retention, demographics, claim frequency. "
        "Use when the user asks about customers or customer segments."
    ),
    "system_prompt": "Follow the insurer-customer-analytics skill instructions.",
    "skills": ["/skills/"],
    "tools": [ask_customer_analytics],
}

acme_life_distribution_agent = {
    "name": "insurer-distribution-channels",
    "description": (
        "Queries Acme Life agent performance and distribution channel data. "
        "Use when the user asks about agents, sales channels, or distribution performance."
    ),
    "system_prompt": "Follow the insurer-distribution-channels skill instructions.",
    "skills": ["/skills/"],
    "tools": [ask_distribution_channels],
}

acme_life_policy_agent = {
    "name": "insurer-policy-underwriting",
    "description": (
        "Queries Acme Life policy and underwriting data — premiums, policy counts, renewals, product mix. "
        "Use when the user asks about policies, premiums, or underwriting."
    ),
    "system_prompt": "Follow the insurer-policy-underwriting skill instructions.",
    "skills": ["/skills/"],
    "tools": [ask_policy_underwriting],
}

acme_life_claims_agent = {
    "name": "insurer-claims-analytics",
    "description": (
        "Queries Acme Life claims data — claim counts, amounts, processing times, fraud scores. "
        "Use when the user asks about claims, fraud, or claim processing."
    ),
    "system_prompt": "Follow the insurer-claims-analytics skill instructions.",
    "skills": ["/skills/"],
    "tools": [ask_claims_analytics],
}

subagents = [
    senior_developer,
    code_reviewer,
    research_agent,
    acme_life_customer_agent,
    acme_life_distribution_agent,
    acme_life_policy_agent,
    acme_life_claims_agent,
]

# ============ Backend factory ============
def _create_backend():
    """Create the appropriate backend based on USE_SANDBOX env var."""
    if USE_SANDBOX:
        return LocalShellBackend(root_dir=PROJECTS_DIR)
    return FilesystemBackend(root_dir=BASE_DIR, virtual_mode=True)


# ============ Agent setup ============
checkpointer = MemorySaver()

model = ChatDatabricks(
    endpoint="databricks-claude-opus-4-6",
    temperature=0.1,
)

agent = create_deep_agent(
    model = model,
    tools = [
        name_project,
        internet_search,
        ask_customer_analytics,
        ask_distribution_channels,
        ask_policy_underwriting,
        ask_claims_analytics,
    ],
    skills = ["/skills/"],
    subagents = subagents,
    backend = _create_backend(),
    checkpointer = checkpointer,
)

def main():
    banner = r"""
   _____ _                 __        ______          ___
  / ___/(_)___ ___  ____  / /__     / ____/___  ____/ (_)___  ____ _
  \__ \/ / __ `__ \/ __ \/ / _ \   / /   / __ \/ __  / / __ \/ __ `/
 ___/ / / / / / / / /_/ / /  __/  / /___/ /_/ / /_/ / / / / / /_/ /
/____/_/_/ /_/ /_/ .___/_/\___/   \____/\____/\__,_/_/_/ /_/\__, /
                /_/                                        /____/
    ___                    __
   /   | ____ ____  ____  / /_
  / /| |/ __ `/ _ \/ __ \/ __/
 / ___ / /_/ /  __/ / / / /_
/_/  |_\__, /\___/_/ /_/\__/
      /____/
"""
    print(banner)
    print("Plan -> Write -> Review -> Fix -> Deliver")
    print("="* 60)
    print()
    backend_label = "LocalShell (code execution enabled)" if USE_SANDBOX else "Filesystem (virtual, no code execution)"
    print(f"Backend                   : {backend_label}")
    print(f"Projects will be saved to : {PROJECTS_DIR}/")
    print()
    print("Describe a coding task. Type 'quit' to exit")
    print()

    task_count = 0

    while True:

        user_input = input("> ").strip()

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if not user_input:
            continue
        
        task_count += 1
        config = {"configurable": {"thread_id": f"task-{task_count}"}}

        print()
        print("-" * 60)
        print("Agent is Working...")
        print("-" * 60)
        print()

        for step in agent.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config,
            stream_mode="updates"
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