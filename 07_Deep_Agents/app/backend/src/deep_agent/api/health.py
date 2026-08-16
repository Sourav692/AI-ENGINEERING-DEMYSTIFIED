"""Health + diagnostic endpoint."""

import os

from fastapi import APIRouter

from deep_agent.runtime import agent_init_status

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health():
    status = agent_init_status()
    return {
        "status": "ok",
        **status,
        "cwd": os.getcwd(),
        "env_keys": [
            k for k in os.environ
            if "DATABRICKS" in k or "TAVILY" in k or "LAKEBASE" in k
        ],
    }
