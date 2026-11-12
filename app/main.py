from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Private personal AI assistant backend.",
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    language: Literal["auto", "en", "hi", "hinglish"] = "auto"


class ChatResponse(BaseModel):
    assistant: str
    status: Literal["model_not_configured", "ok"]
    agent: str = "orchestrator"


@app.get("/")
async def root() -> dict[str, str]:
    return {"name": settings.app_name, "status": "running", "stage": "foundation"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    # The model adapter is intentionally not faked. It will be added once
    # the provider and model are selected and configured securely.
    if not settings.ai_provider or not settings.ai_api_key or not settings.ai_model:
        return ChatResponse(
            assistant=(
                "Eleven का backend चालू है, लेकिन AI model अभी configure नहीं हुआ है. "
                "अगले चरण में सुरक्षित तरीके से model provider जोड़ेंगे."
            ),
            status="model_not_configured",
        )

    return ChatResponse(
        assistant=(
            "AI provider की settings मिल गई हैं. वास्तविक model adapter अभी "
            "अगले development चरण में जोड़ा जाएगा."
        ),
        status="model_not_configured",
    )
