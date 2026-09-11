"""
The API.

Wraps the team and the evaluation behind three HTTP endpoints, so anything --
a web page, a script, another service -- can use them without importing Python.

  GET  /health     is it up
  POST /run        run one task through the team
  POST /evaluate   run the whole test set and score it
"""

from fastapi import FastAPI
from pydantic import BaseModel

from .agents import run
from .evaluation import evaluate

api = FastAPI(title="Multi-Agent Demo")


class TaskIn(BaseModel):
    task: str


@api.get("/health")
def health():
    return {"status": "ok"}


@api.post("/run")
def run_task(payload: TaskIn):
    """Run one task. Returns the answer plus the path the team took to get it."""
    return run(payload.task)


@api.post("/evaluate")
def run_evaluation():
    """Run every test case and return per-case scores and the averages."""
    return evaluate()
