"""FastAPI application entry point.

Run locally:    uvicorn deep_agent.main:app --reload
Run in Apps:    configured via app.yaml's `command:` block.
"""

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deep-agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from deep_agent.runtime import get_agent
    logger.info("Starting up — eagerly initializing agent...")
    agent, _ = get_agent()
    if agent:
        logger.info("Agent ready")
    else:
        logger.error("Agent failed to initialize — see /api/health for details")
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Deep Agent API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from deep_agent.api import chat, health, memory, threads
    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(threads.router)
    app.include_router(memory.router)

    # Serve the React build in prod
    from deep_agent.config import FRONTEND_BUILD_DIR
    if os.path.isdir(FRONTEND_BUILD_DIR):
        app.mount("/", StaticFiles(directory=FRONTEND_BUILD_DIR, html=True), name="frontend")

    return app


app = create_app()
