from typing import List

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from crews.fitness_tracker import start_fitness_crew
from utils import sse_stream, SSE_HEADERS

router = APIRouter()


class FitnessRequest(BaseModel):
    fitness_goal: str
    nutrition_preference: str
    historical_weight_data: List[str]


@router.post("/run")
async def run(req: FitnessRequest):
    q = start_fitness_crew(
        req.fitness_goal,
        req.nutrition_preference,
        req.historical_weight_data,
    )
    return StreamingResponse(
        sse_stream(q),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )
