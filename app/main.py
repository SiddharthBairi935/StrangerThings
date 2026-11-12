from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.agents import list_agents
from app.brain import generate_reply, select_agent
from app.config import get_settings
from app.database import (
    delete_memory,
    get_memories,
    init_db,
    save_memory,
    save_message,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db(settings.database_path)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.3.0",
    description="Eleven personal AI assistant brain API.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    conversation_id: str | None = None
    profile_id: str = Field(default="default", min_length=1, max_length=100)


class ChatResponse(BaseModel):
    conversation_id: str
    assistant: str
    status: str
    agent: str


class MemoryRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)
    profile_id: str = Field(default="default", min_length=1, max_length=100)


@app.get("/")
async def root() -> dict[str, str]:
    return {"name": settings.app_name, "status": "running", "stage": "brain-foundation"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/agents")
async def agents() -> dict[str, object]:
    return {"agents": list_agents()}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    conversation_id = payload.conversation_id or str(uuid4())
    agent_name = select_agent(payload.message)

    # Store the user turn first. If the model call fails, it remains available for retry/debug.
    save_message(settings.database_path, conversation_id, "user", payload.message)
    try:
        answer = await generate_reply(
            settings,
            settings.database_path,
            payload.profile_id,
            conversation_id,
            agent_name,
        )
    except HTTPException:
        raise
    save_message(settings.database_path, conversation_id, "assistant", answer)
    return ChatResponse(
        conversation_id=conversation_id,
        assistant=answer,
        status="ok",
        agent=agent_name,
    )


@app.get("/api/memory")
async def memories(profile_id: str = "default") -> dict[str, object]:
    return {"memories": get_memories(settings.database_path, profile_id, limit=100)}


@app.post("/api/memory")
async def remember(payload: MemoryRequest) -> dict[str, object]:
    created = save_memory(settings.database_path, payload.profile_id, payload.content)
    return {"saved": created, "memories": get_memories(settings.database_path, payload.profile_id)}


@app.delete("/api/memory/{memory_id}")
async def forget(memory_id: int, profile_id: str = "default") -> dict[str, bool]:
    deleted = delete_memory(settings.database_path, profile_id, memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found.")
    return {"deleted": True}
