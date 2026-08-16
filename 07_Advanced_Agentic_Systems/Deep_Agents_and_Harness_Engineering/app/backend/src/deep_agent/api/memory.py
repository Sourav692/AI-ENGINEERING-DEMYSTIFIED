"""Memory CRUD endpoints — direct access to the long-term memory store."""

from fastapi import APIRouter, HTTPException

from deep_agent.api.schemas import MemorySave
from deep_agent.runtime import get_memory_store

router = APIRouter(prefix="/api/memories", tags=["memories"])


@router.get("")
async def list_memories():
    db = get_memory_store()
    if not db:
        return []
    return db.list_all()


@router.post("")
async def save_memory(request: MemorySave):
    db = get_memory_store()
    if not db:
        raise HTTPException(status_code=503, detail="Memory store not available")
    return db.save(request.content, request.category)


@router.delete("/{content_substring}")
async def delete_memory(content_substring: str):
    db = get_memory_store()
    if not db:
        raise HTTPException(status_code=503, detail="Memory store not available")
    result = db.forget(content_substring)
    if not result:
        raise HTTPException(status_code=404, detail="Memory not found")
    return result
