from dataclasses import dataclass


@dataclass(frozen=True)
class AgentInfo:
    name: str
    description: str
    status: str
    capabilities: tuple[str, ...]


AGENTS: tuple[AgentInfo, ...] = (
    AgentInfo(
        name="general",
        description="Conversation, explanation, planning, and everyday assistance.",
        status="active",
        capabilities=("chat", "explain", "plan"),
    ),
    AgentInfo(
        name="coding",
        description="Code reasoning, debugging guidance, and software design through the configured model.",
        status="active",
        capabilities=("code", "debug", "architecture"),
    ),
    AgentInfo(
        name="research",
        description="Structured research and synthesis; live web access is not connected yet.",
        status="active",
        capabilities=("research", "summarize", "compare"),
    ),
    AgentInfo(
        name="github",
        description="Repository operations; GitHub API tools and scoped permissions are not connected to Eleven yet.",
        status="planned",
        capabilities=("repository", "issues", "pull_requests"),
    ),
    AgentInfo(
        name="drive",
        description="Google Drive search and file operations; connector is not configured yet.",
        status="planned",
        capabilities=("files", "documents"),
    ),
    AgentInfo(
        name="voice",
        description="Speech input and speech output pipeline.",
        status="planned",
        capabilities=("speech_to_text", "text_to_speech"),
    ),
    AgentInfo(
        name="vision",
        description="Image understanding and optional face recognition.",
        status="planned",
        capabilities=("image_understanding", "face_recognition"),
    ),
    AgentInfo(
        name="tasks",
        description="Scheduled and background task execution.",
        status="planned",
        capabilities=("automation", "scheduling"),
    ),
)


def list_agents() -> list[dict[str, object]]:
    return [
        {
            "name": agent.name,
            "description": agent.description,
            "status": agent.status,
            "capabilities": list(agent.capabilities),
        }
        for agent in AGENTS
    ]


def route_agent(message: str) -> str:
    text = message.lower()
    if any(word in text for word in ("python", "dart", "flutter", "javascript", "code", "bug", "debug", "api", "function", "program")):
        return "coding"
    if any(word in text for word in ("research", "compare", "investigate", "sources", "अध्ययन", "तुलना")):
        return "research"
    return "general"


AGENT_INSTRUCTIONS = {
    "general": "Be a thoughtful personal assistant. Answer clearly and ask only necessary questions.",
    "coding": "Act as a senior software engineer. Explain assumptions, provide correct code, and never claim code was executed unless it was.",
    "research": "Act as a careful research analyst. Separate known facts from uncertainty. Do not claim live browsing or citations unless available.",
}
