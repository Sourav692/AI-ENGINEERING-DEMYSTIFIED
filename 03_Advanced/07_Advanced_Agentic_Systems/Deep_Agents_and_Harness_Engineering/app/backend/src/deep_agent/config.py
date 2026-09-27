"""Centralized configuration — all environment variables and derived paths."""

import os


# ============ Paths ============
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(os.path.dirname(PACKAGE_DIR))  # .../app/backend
APP_DIR = os.path.dirname(BACKEND_DIR)                        # .../app
REPO_ROOT = os.path.dirname(APP_DIR)                          # repo root

PROJECTS_DIR = os.path.join(BACKEND_DIR, "projects")
os.makedirs(PROJECTS_DIR, exist_ok=True)

# Skills dir: deployed location first (alongside backend/), else repo-root /skills
_skills_deployed = os.path.join(APP_DIR, "skills")
_skills_repo = os.path.join(REPO_ROOT, "skills")
SKILLS_DIR = _skills_deployed if os.path.isdir(_skills_deployed) else _skills_repo

# Frontend build (served by the FastAPI app in prod)
FRONTEND_BUILD_DIR = os.path.join(APP_DIR, "frontend", "build")


# ============ Databricks ============
DATABRICKS_HOST = os.environ.get("DATABRICKS_HOST", "")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN", "")
VOLUME_BASE = os.environ.get(
    "VOLUME_BASE", "/Volumes/acme_life_multi_agent_catalog/default/agent_projects"
)


# ============ Lakebase (Postgres long-term memory) ============
LAKEBASE_INSTANCE_NAME = os.environ.get("LAKEBASE_INSTANCE_NAME", "deep-agent-memory")
LAKEBASE_DATABASE = os.environ.get("LAKEBASE_DATABASE", "databricks_postgres")
LAKEBASE_SCHEMA = "public"
LAKEBASE_TABLE = "agent_memories"


# ============ Model ============
MODEL_ENDPOINT = os.environ.get("MODEL_ENDPOINT", "databricks-claude-sonnet-4-6")
MODEL_TEMPERATURE = float(os.environ.get("MODEL_TEMPERATURE", "0.1"))


# ============ Tools ============
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
USE_SANDBOX = os.environ.get("USE_SANDBOX", "false").lower() == "true"

# Genie space IDs are workspace-specific, so they come from the environment, never
# from source: set them in the project-root .env for local runs, and attach the four
# spaces as app resources for a deployed app (see app/app.yaml). Keyed by domain; the
# value is the environment variable that holds that domain's space ID.
GENIE_SPACES = {
    "customer_analytics": "GENIE_SPACE_CUSTOMER_ANALYTICS",
    "distribution_channels": "GENIE_SPACE_DISTRIBUTION_CHANNELS",
    "policy_underwriting": "GENIE_SPACE_POLICY_UNDERWRITING",
    "claims_analytics": "GENIE_SPACE_CLAIMS_ANALYTICS",
}


def genie_space_id(domain: str) -> str:
    """The configured Genie space ID for a domain, or "" if it is not set.

    Read at call time rather than import time, so a .env loaded after this module is
    imported still takes effect.
    """
    return os.environ.get(GENIE_SPACES[domain], "").strip()
