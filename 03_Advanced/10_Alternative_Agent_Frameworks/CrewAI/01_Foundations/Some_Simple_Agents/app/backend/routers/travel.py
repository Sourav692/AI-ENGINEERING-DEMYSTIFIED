from typing import List

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from crews.travel_advisor import start_travel_crew
from utils import sse_stream, SSE_HEADERS

router = APIRouter()


class TravelRequest(BaseModel):
    names: List[str]
    city: str
    destination: str


@router.post("/run")
async def run(req: TravelRequest):
    q = start_travel_crew(req.names, req.city, req.destination)
    return StreamingResponse(
        sse_stream(q),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )
