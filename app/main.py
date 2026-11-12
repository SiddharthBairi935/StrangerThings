from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import get_settings
from app.database import get_history, init_db, save_message

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db(settings.database_path)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Private personal AI assistant backend.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    assistant: str
    status: str
    agent: str = "orchestrator"


async def generate_reply(conversation_id: str) -> tuple[str, str]:
    history = get_history(settings.database_path, conversation_id, limit=20)

    if not settings.llm_api_key or not settings.llm_model:
        return (
            "Eleven का backend चालू है और आपकी बातचीत सुरक्षित रूप से सेव हो गई है। "
            "AI जवाब चालू करने के लिए LLM provider की settings configure करनी बाकी हैं।",
            "model_not_configured",
        )

    messages = [
        {
            "role": "system",
            "content": (
                "You are Eleven, a helpful personal AI assistant. "
                "Reply in the language used by the user. Be honest about capabilities "
                "and never claim an action was completed unless it actually was."
            ),
        }
    ]
    messages.extend(
        {"role": item["role"], "content": item["content"]}
        for item in history
        if item["role"] in {"user", "assistant"}
    )

    url = settings.llm_base_url.rstrip("/") + "/v1/chat/completions"
    try:
        async with httpx.AsyncClient(timeout=settings.llm_timeout_seconds) as client:
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json={"model": settings.llm_model, "messages": messages},
            )
            response.raise_for_status()
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError("Provider returned an empty assistant message.")
            return answer.strip(), "ok"
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail="The configured AI provider could not complete the request.",
        ) from exc


@app.get("/")
async def root() -> dict[str, str]:
    return {"name": settings.app_name, "status": "running", "stage": "foundation"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    conversation_id = payload.conversation_id or str(uuid4())
    save_message(settings.database_path, conversation_id, "user", payload.message)
    answer, status = await generate_reply(conversation_id)
    save_message(settings.database_path, conversation_id, "assistant", answer)
    return ChatResponse(
        conversation_id=conversation_id,
        assistant=answer,
        status=status,
    )
