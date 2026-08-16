import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import StreamingResponse

from crews.doc_summarizer import start_summarizer_crew
from utils import sse_stream, SSE_HEADERS

router = APIRouter()

UPLOADS_DIR = Path(__file__).parent.parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


@router.post("/run")
async def run(
    file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None),
):
    if file and file.filename:
        # Save uploaded file
        suffix = Path(file.filename).suffix or ".txt"
        upload_path = UPLOADS_DIR / f"{uuid.uuid4()}{suffix}"
        contents = await file.read()
        upload_path.write_bytes(contents)
        path_to_file = str(upload_path)
    elif text_content:
        # Write pasted text to a temp file
        upload_path = UPLOADS_DIR / f"{uuid.uuid4()}.txt"
        upload_path.write_text(text_content, encoding="utf-8")
        path_to_file = str(upload_path)
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Provide a file or text_content.")

    q = start_summarizer_crew(path_to_file)
    return StreamingResponse(
        sse_stream(q),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )
