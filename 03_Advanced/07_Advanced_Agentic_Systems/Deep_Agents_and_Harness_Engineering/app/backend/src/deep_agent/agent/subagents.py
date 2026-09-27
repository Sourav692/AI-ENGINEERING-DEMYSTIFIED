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

acme_life_customer_agent = {
    "name": "insurer-customer-analytics",
    "description": "Queries Acme Life customer data — segmentation, retention, demographics, claim frequency.",
    "system_prompt": "Follow the insurer-customer-analytics skill instructions.",
    "skills": _SKILLS,
    "tools": [ask_customer_analytics],
}

acme_life_distribution_agent = {
    "name": "insurer-distribution-channels",
    "description": "Queries Acme Life agent performance and distribution channel data.",
    "system_prompt": "Follow the insurer-distribution-channels skill instructions.",
    "skills": _SKILLS,
    "tools": [ask_distribution_channels],
}

acme_life_policy_agent = {
    "name": "insurer-policy-underwriting",
    "description": "Queries Acme Life policy and underwriting data — premiums, policy counts, renewals.",
    "system_prompt": "Follow the insurer-policy-underwriting skill instructions.",
    "skills": _SKILLS,
    "tools": [ask_policy_underwriting],
}

acme_life_claims_agent = {
    "name": "insurer-claims-analytics",
    "description": "Queries Acme Life claims data — claim counts, amounts, fraud scores.",
    "system_prompt": "Follow the insurer-claims-analytics skill instructions.",
    "skills": _SKILLS,
    "tools": [ask_claims_analytics],
}


SUBAGENTS = [
    memory_manager,
    senior_developer,
    code_reviewer,
    research_agent,
    acme_life_customer_agent,
    acme_life_distribution_agent,
    acme_life_policy_agent,
    acme_life_claims_agent,
]
