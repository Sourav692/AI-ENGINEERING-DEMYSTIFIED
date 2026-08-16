"""Pydantic request/response models for the API."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    thread_id: str


class ThreadCreate(BaseModel):
    title: str = "New Chat"


class ThreadRename(BaseModel):
    title: str


class MemorySave(BaseModel):
    content: str
    category: str = "general"
