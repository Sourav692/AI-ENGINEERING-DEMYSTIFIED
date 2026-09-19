from typing import List

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from crews.fraud_detector import start_fraud_crew
from utils import sse_stream, SSE_HEADERS

router = APIRouter()


class FraudRequest(BaseModel):
    transaction_list: List[str]


@router.post("/run")
async def run(req: FraudRequest):
    q = start_fraud_crew(req.transaction_list)
    return StreamingResponse(
        sse_stream(q),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )
