import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Literal
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app.agents import list_agents
from app.brain import extract_max_health_logs, generate_reply, select_agent
from app.config import get_settings
from app.coding_workspace import execute_lucas_coding_task
from app.database import (
    delete_memory,
    delete_health_entry,
    get_memories,
    init_db,
    save_health_entry,
    get_health_entries,
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


class MaxHealthLogRequest(BaseModel):
    entry_type: Literal["food", "workout", "weight", "measurement", "activity", "note"]
    data: dict[str, object] = Field(min_length=1)
    logged_at: str | None = Field(default=None, max_length=40)


class LucasDelegationRequest(BaseModel):
    task: str = Field(min_length=1, max_length=12000)


class LucasCodingRequest(BaseModel):
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


@app.get("/api/max/summary")
async def max_health_summary(
    days: int = 30,
    profile_id: str = Depends(require_owner),
) -> dict[str, object]:
    """Return transparent summaries of explicitly logged nutrition and progress data."""
    safe_days = max(1, min(days, 365))
    entries = get_health_entries(settings.database_path, profile_id, limit=2000)
    today = datetime.now(timezone.utc).date()
    start = today.fromordinal(today.toordinal() - safe_days + 1)
    daily: dict[str, dict[str, float | int]] = {}
    weight_series: list[dict[str, object]] = []
    measurements: list[dict[str, object]] = []
    workout_sessions = 0
    for entry in entries:
        logged = str(entry.get("logged_at") or "")
        try:
            day = datetime.fromisoformat(logged.replace("Z", "+00:00")).date()
        except ValueError:
            continue
        if day < start or day > today:
            continue
        day_key = day.isoformat()
        bucket = daily.setdefault(day_key, {
            "food_entries": 0, "calories": 0.0, "protein_g": 0.0,
            "carbs_g": 0.0, "fat_g": 0.0, "workouts": 0,
        })
        data = entry.get("data") if isinstance(entry.get("data"), dict) else {}
        kind = entry.get("entry_type")
        if kind == "food":
            bucket["food_entries"] += 1
            nutrition = data.get("nutrition") if isinstance(data.get("nutrition"), dict) else data
            for output, keys in {
                "calories": ("calories", "kcal"),
                "protein_g": ("protein_g", "protein"),
                "carbs_g": ("carbs_g", "carbs"),
                "fat_g": ("fat_g", "fat"),
            }.items():
                for key in keys:
                    value = nutrition.get(key)
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        bucket[output] += float(value)
                        break
        elif kind == "workout":
            bucket["workouts"] += 1
            workout_sessions += 1
        elif kind == "weight":
            value = data.get("kg")
            unit = "kg"
            if not isinstance(value, (int, float)):
                value = data.get("value")
                unit = str(data.get("unit") or "")
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                weight_series.append({"date": day_key, "value": float(value), "unit": unit})
        elif kind == "measurement":
            measurements.append({"date": day_key, **data})
    ordered_days = sorted(daily)
    totals = {
        key: round(sum(float(daily[day][key]) for day in ordered_days), 2)
        for key in ("calories", "protein_g", "carbs_g", "fat_g")
    }
    return {
        "period_days": safe_days,
        "from": start.isoformat(),
        "to": today.isoformat(),
        "totals": totals,
        "daily": [{"date": day, **daily[day]} for day in ordered_days],
        "weight_series": sorted(weight_series, key=lambda item: str(item["date"])),
        "latest_weight": max(weight_series, key=lambda item: str(item["date"])) if weight_series else None,
        "measurements": measurements[:50],
        "workout_sessions": workout_sessions,
        "note": "Nutrition totals include only numeric values explicitly stored in food log entries; missing values are not estimated or treated as zero intake.",
    }


@app.get("/api/max/logs")
async def max_health_logs(
    limit: int = 50,
    entry_type: Literal["food", "workout", "weight", "measurement", "activity", "note"] | None = None,
    profile_id: str = Depends(require_owner),
) -> dict[str, object]:
    return {
        "entries": get_health_entries(
            settings.database_path, profile_id, limit=limit, entry_type=entry_type
        )
    }


@app.post("/api/max/logs")
async def max_add_health_log(
    payload: MaxHealthLogRequest,
    profile_id: str = Depends(require_owner),
) -> dict[str, object]:
    entry_id = save_health_entry(
        settings.database_path,
        profile_id,
        payload.entry_type,
        payload.data,
        payload.logged_at,
    )
    return {"saved": True, "id": entry_id}


@app.delete("/api/max/logs/{entry_id}")
async def max_delete_health_log(
    entry_id: int,
    profile_id: str = Depends(require_owner),
) -> dict[str, bool]:
    deleted = delete_health_entry(settings.database_path, profile_id, entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Health log not found.")
    return {"deleted": True}


@app.post("/api/lucas/delegate")
async def lucas_delegate(
    payload: LucasDelegationRequest,
    _: str = Depends(require_owner),
) -> dict[str, object]:
    return create_lucas_plan(payload.task)


@app.post("/api/lucas/code")
async def lucas_code(
    payload: LucasCodingRequest,
    _: str = Depends(require_owner),
) -> dict[str, object]:
    if not settings.llm_api_key or not settings.llm_model:
        raise HTTPException(status_code=503, detail="AI provider is not configured.")
    return await execute_lucas_coding_task(settings, payload.task)


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
    if agent_name == "max" and settings.llm_api_key and settings.llm_model:
        extracted_logs = await extract_max_health_logs(settings, payload.message)
        for entry in extracted_logs:
            save_health_entry(
                settings.database_path,
                profile_id,
                entry["entry_type"],
                entry["data"],
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
