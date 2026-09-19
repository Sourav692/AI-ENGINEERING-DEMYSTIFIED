"""
Automated Candidate Interview & Evaluation System.

A FastAPI + WebSocket application that conducts AI-powered mock interviews
using AutoGen's multi-agent framework. Three agents collaborate in a
round-robin chat: an Interviewer (asks questions), a Candidate (human proxy
via WebSocket), and an Evaluator (provides coaching feedback).
"""

import os
from typing import Optional

from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()

app = FastAPI(title="Automated Interview & Evaluation System")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"

model_client = OpenAIChatCompletionClient(
    model=MODEL_NAME,
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": "unknown",
    },
)



class WebSocketInputHandler:
    """Bridges AutoGen's UserProxyAgent input mechanism with a FastAPI WebSocket."""

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    async def get_input(self, prompt: str, cancellation_token: Optional[object] = None) -> str:
        """Signal the frontend that it's the user's turn, then wait for their reply."""
        try:
            await self.websocket.send_text("SYSTEM_TURN:USER")
            return await self.websocket.receive_text()
        except WebSocketDisconnect:
            return "TERMINATE"


async def create_interview_team(websocket: WebSocket, job_position: str):
    """Create and return a RoundRobinGroupChat team for the given role."""
    handler = WebSocketInputHandler(websocket)

    interviewer = AssistantAgent(
        name="Interviewer",
        model_client=model_client,
        description=f"An AI agent that conducts interviews for a {job_position} position.",
        system_message=(
            f"You are a professional interviewer for a {job_position} position.\n"
            "Ask one clear question at a time and wait for the user to respond.\n"
            "Ignore the career coach's response — your job is only to ask questions.\n"
            "Tailor each follow-up based on the candidate's previous answer.\n"
            "Ask 3 questions total covering: technical skills, problem-solving, and cultural fit.\n"
            "After the 3rd question, say 'TERMINATE'.\n"
            "Keep every question under 50 words."
        ),
    )

    candidate = UserProxyAgent(
        name="Candidate",
        description=f"A human proxy representing the candidate for a {job_position} position.",
        input_func=handler.get_input,
    )

    evaluator = AssistantAgent(
        name="Evaluator",
        model_client=model_client,
        description=f"An AI career coach providing feedback for a {job_position} interview.",
        system_message=(
            f"You are a career coach specializing in {job_position} interviews.\n"
            "Provide constructive feedback on the candidate's responses and suggest improvements.\n"
            "After the interview, summarize performance and give actionable advice.\n"
            "Keep feedback under 100 words."
        ),
    )

    termination_condition = TextMentionTermination(text="TERMINATE")

    return RoundRobinGroupChat(
        participants=[interviewer, candidate, evaluator],
        termination_condition=termination_condition,
        max_turns=20,
    )


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main interview UI page."""
    return templates.TemplateResponse(request, "index.html")


@app.websocket("/ws/interview")
async def websocket_endpoint(websocket: WebSocket, pos: str = Query("AI Engineer")):
    """WebSocket endpoint that streams a full interview session to the client."""
    await websocket.accept()
    try:
        team = await create_interview_team(websocket, pos)
        
        await websocket.send_text(f"SYSTEM_INFO:Starting interview for {pos}...")

        async for message in team.run_stream(
            task="Start the interview with the first question."
        ):
            if isinstance(message, TaskResult):
                await websocket.send_text(f"SYSTEM_END:{message.stop_reason}")
            else:
                await websocket.send_text(f"{message.source}:{message.content}")

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Error: {e}")