import asyncio
import uuid
from pathlib import Path

from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import StreamingResponse

from crews.data_analyst import start_data_analyst_crew
from utils import safe_sse, SSE_HEADERS

router = APIRouter()

UPLOADS_DIR = Path(__file__).parent.parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


@router.post("/run")
async def run(
    file: UploadFile = File(...),
    user_instruction: str = Form(...),
):
    # Save uploaded file to uploads/
    suffix = Path(file.filename or "upload.csv").suffix or ".csv"
    upload_path = UPLOADS_DIR / f"{uuid.uuid4()}{suffix}"
    contents = await file.read()
    upload_path.write_bytes(contents)

    q = start_data_analyst_crew(str(upload_path), user_instruction)

    async def event_stream():
        loop = asyncio.get_event_loop()
        while True:
            item = await loop.run_in_executor(None, q.get)
            if item.startswith("[DOWNLOAD] "):
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
