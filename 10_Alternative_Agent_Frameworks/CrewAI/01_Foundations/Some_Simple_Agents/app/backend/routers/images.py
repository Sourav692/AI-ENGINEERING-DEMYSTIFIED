import asyncio

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from crews.image_generator import start_image_crew
from utils import safe_sse, SSE_HEADERS

router = APIRouter()


class ImageRequest(BaseModel):
    initial_prompt: str


@router.post("/run")
async def run(req: ImageRequest):
    q = start_image_crew(req.initial_prompt)

    async def event_stream():
        loop = asyncio.get_event_loop()
        image_path = None
        while True:
            item = await loop.run_in_executor(None, q.get)
            if item.startswith("[IMAGE] "):
                image_path = item[8:]
                yield f"data: {item}\n\n"
                continue
            if item == "__DONE__":
                final = await loop.run_in_executor(None, q.get)
                yield f"data: [FINAL] {safe_sse(final)}\n\n"
                break
            yield f"data: {safe_sse(item)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )
