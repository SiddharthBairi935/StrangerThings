import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
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
from app.delegation import create_lucas_plan

settings = get_settings()
bearer_scheme = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db(settings.database_path)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.5.0",
    description="Private personal AI assistant brain API.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


async def require_owner(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    expected = settings.api_access_token
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="Private API access is not configured. Set ELEVEN_API_TOKEN on the server.",
        )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="A valid Eleven access token is required.")
    if not secrets.compare_digest(credentials.credentials, expected):
        raise HTTPException(status_code=401, detail="A valid Eleven access token is required.")
    return settings.owner_profile_id


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    conversation_id: str | None = Field(default=None, min_length=1, max_length=100)


class ChatResponse(BaseModel):
    conversation_id: str
    assistant: str
    status: str
    agent: str


class MemoryRequest(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class LucasDelegationRequest(BaseModel):
    task: str = Field(min_length=1, max_length=12000)


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/api/agents")
async def agents() -> dict[str, object]:
    return {"agents": list_agents()}


@app.post("/api/lucas/delegate")
async def lucas_delegate(
    payload: LucasDelegationRequest,
    _: str = Depends(require_owner),
) -> dict[str, object]:
    return create_lucas_plan(payload.task)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    profile_id: str = Depends(require_owner),
) -> ChatResponse:
    conversation_id = payload.conversation_id or str(uuid4())
    agent_name = select_agent(payload.message)
    save_message(
        settings.database_path, conversation_id, "user", payload.message, profile_id
    )
    answer = await generate_reply(
        settings,
        settings.database_path,
        profile_id,
        conversation_id,
        agent_name,
    )
    save_message(
        settings.database_path, conversation_id, "assistant", answer, profile_id
    )
    return ChatResponse(
        conversation_id=conversation_id,
        assistant=answer,
        status="ok",
        agent=agent_name,
    )


@app.get("/api/memory")
async def memories(profile_id: str = Depends(require_owner)) -> dict[str, object]:
    return {"memories": get_memories(settings.database_path, profile_id, limit=100)}


@app.post("/api/memory")
async def remember(
    payload: MemoryRequest,
    profile_id: str = Depends(require_owner),
) -> dict[str, object]:
    created = save_memory(settings.database_path, profile_id, payload.content)
    return {
        "saved": created,
        "memories": get_memories(settings.database_path, profile_id),
    }


@app.delete("/api/memory/{memory_id}")
async def forget(
    memory_id: int,
    profile_id: str = Depends(require_owner),
) -> dict[str, bool]:
    deleted = delete_memory(settings.database_path, profile_id, memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found.")
    return {"deleted": True}
