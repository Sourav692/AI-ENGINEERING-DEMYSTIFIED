from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from crews.book_recommender import start_book_crew
from utils import sse_stream, SSE_HEADERS

router = APIRouter()


class BookRequest(BaseModel):
    user_id: str
    user_preferences: str


@router.post("/run")
async def run(req: BookRequest):
    q = start_book_crew(req.user_id, req.user_preferences)
    return StreamingResponse(
        sse_stream(q),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )
