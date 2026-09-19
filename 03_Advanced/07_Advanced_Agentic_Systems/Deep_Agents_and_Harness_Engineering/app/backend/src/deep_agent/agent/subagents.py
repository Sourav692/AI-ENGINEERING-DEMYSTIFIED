"""Subagent definitions — each specialized agent's tools, skills, and role."""

from deep_agent.tools.analytics import (
    ask_claims_analytics,
    ask_customer_analytics,
    ask_distribution_channels,
    ask_policy_underwriting,
)
from deep_agent.tools.memory import forget_memory, recall_memories, save_memory
from deep_agent.tools.projects import (
    list_project_files,
    name_project,
    write_project_file,
)
from deep_agent.tools.search import internet_search


_SKILLS = ["/skills/"]


memory_manager = {
    "name": "memory-manager",
    "description": (
        "Manages long-term memory — saving, recalling, and organizing information "
        "the user wants remembered across conversations."
    ),
    "system_prompt": "Follow the memory-manager skill instructions.",
    "skills": _SKILLS,
    "tools": [save_memory, recall_memories, forget_memory],
}

senior_developer = {
    "name": "senior-developer",
    "description": "Senior Python developer that plans, writes, and delivers complete projects.",
    "system_prompt": "Follow the senior-developer skill instructions.",
    "skills": _SKILLS,
    "tools": [name_project, write_project_file, list_project_files],
}

code_reviewer = {
    "name": "code-reviewer",
    "description": "Reviews Python code for bugs, style issues, and best practices.",
    "system_prompt": "Follow the code-reviewer skill instructions.",
    "skills": _SKILLS,
    "tools": [],
}

research_agent = {
    "name": "research-agent",
    "description": "Conducts in-depth web research on any topic.",
    "system_prompt": "Follow the research-agent skill instructions.",
    "skills": _SKILLS,
    "tools": [internet_search],
}

aia_customer_agent = {
    "name": "aia-customer-analytics",
    "description": "Queries AIA customer data — segmentation, retention, demographics, claim frequency.",
    "system_prompt": "Follow the aia-customer-analytics skill instructions.",
    "skills": _SKILLS,
    "tools": [ask_customer_analytics],
}

aia_distribution_agent = {
    "name": "aia-distribution-channels",
    "description": "Queries AIA agent performance and distribution channel data.",
    "system_prompt": "Follow the aia-distribution-channels skill instructions.",
    "skills": _SKILLS,
    "tools": [ask_distribution_channels],
}

aia_policy_agent = {
    "name": "aia-policy-underwriting",
    "description": "Queries AIA policy and underwriting data — premiums, policy counts, renewals.",
    "system_prompt": "Follow the aia-policy-underwriting skill instructions.",
    "skills": _SKILLS,
    "tools": [ask_policy_underwriting],
}

aia_claims_agent = {
    "name": "aia-claims-analytics",
    "description": "Queries AIA claims data — claim counts, amounts, fraud scores.",
    "system_prompt": "Follow the aia-claims-analytics skill instructions.",
    "skills": _SKILLS,
    "tools": [ask_claims_analytics],
}


SUBAGENTS = [
    memory_manager,
    senior_developer,
    code_reviewer,
    research_agent,
    aia_customer_agent,
    aia_distribution_agent,
    aia_policy_agent,
    aia_claims_agent,
]
