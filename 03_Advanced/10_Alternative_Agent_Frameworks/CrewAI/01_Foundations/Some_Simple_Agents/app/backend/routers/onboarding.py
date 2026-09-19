from typing import List

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from crews.employee_onboarding import start_onboarding_crew
from utils import sse_stream, SSE_HEADERS

router = APIRouter()


class Employee(BaseModel):
    name: str
    start_date: str
    department: str


class OnboardingRequest(BaseModel):
    employees: List[Employee]


@router.post("/run")
async def run(req: OnboardingRequest):
    employees = [e.model_dump() for e in req.employees]
    q = start_onboarding_crew(employees)
    return StreamingResponse(
        sse_stream(q),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )
