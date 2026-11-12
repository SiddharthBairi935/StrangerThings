from dataclasses import dataclass


@dataclass(frozen=True)
class AgentInfo:
    name: str
    description: str
    status: str
    capabilities: tuple[str, ...]


# "active" means the specialist prompt and routing are available inside Eleven.
# It does not imply that an external service or API is connected.
AGENTS: tuple[AgentInfo, ...] = (
    AgentInfo("general", "Eleven's main assistant for conversation, planning, and coordination.", "active", ("chat", "plan", "coordinate")),
    AgentInfo("coding", "Software engineering, code review, debugging, and architecture.", "active", ("code", "debug", "architecture")),
    AgentInfo("research", "Research planning, source evaluation, comparison, and synthesis.", "active", ("research", "summarize", "compare")),
    AgentInfo("workspace", "Documents, spreadsheets, reports, and workspace workflows; Drive connector is not connected.", "planned", ("documents", "spreadsheets", "reports")),
    AgentInfo("linkedin", "Professional profile research, job and freelance opportunity workflows; LinkedIn actions are not connected.", "planned", ("profile_review", "jobs", "freelance")),
    AgentInfo("github", "Repository operations; a runtime GitHub integration for Eleven is not connected.", "planned", ("repository", "issues", "pull_requests")),
    AgentInfo("drive", "Google Drive search and file operations; connector is not configured.", "planned", ("files", "documents")),
    AgentInfo("voice", "Speech input and speech output pipeline.", "planned", ("speech_to_text", "text_to_speech")),
    AgentInfo("vision", "Image understanding and visual analysis.", "planned", ("image_understanding",)),
    AgentInfo("tasks", "Scheduled and background task execution.", "planned", ("automation", "scheduling")),
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
    """Route an incoming request to the best available specialist prompt."""
    text = " ".join(message.lower().split())

    # Strong domain-specific phrases are checked before broad keywords.
    routes = (
        ("coding", ("debug", "bug", "stack trace", "exception", "python", "javascript",
                    "typescript", "flutter", "dart", "react", "next.js", "nextjs",
                    "sql", "database", "api", "code", "program", "function", "github repo")),
        ("workspace", ("spreadsheet", "excel", "google sheets", "google drive", "document",
                       "word file", "powerpoint", "presentation", "report", "pdf")),
        ("linkedin", ("linkedin", "job opening", "job openings", "job search", "job",
                      "freelance", "freelancing", "resume", "cv", "career opportunity")),
        ("research", ("research", "investigate", "compare", "comparison", "sources",
                      "latest information", "market analysis", "competitor", "अध्ययन", "तुलना")),
    )
    for agent_name, phrases in routes:
        if any(phrase in text for phrase in phrases):
            return agent_name
    return "general"


AGENT_INSTRUCTIONS = {
    "general": (
        "You are Eleven's main brain. Understand the user's goal, break complex work into "
        "clear steps, and identify which specialist or external integration would be needed. "
        "Do not pretend planned specialists or disconnected services have performed work."
    ),
    "coding": (
        "Act as a senior software engineer. Inspect requirements carefully, explain assumptions, "
        "provide maintainable code, and never claim code was executed unless it was."
    ),
    "research": (
        "Act as a careful research analyst. Separate verified facts from inference, identify "
        "when current sources are required, and never invent browsing or citations."
    ),
    "workspace": (
        "Act as a document and data specialist. Help structure documents, spreadsheets, and "
        "reports. State clearly that Drive or office-file actions require a connected tool."
    ),
    "linkedin": (
        "Act as a career and professional-network specialist. Help with profile strategy, "
        "job and freelance research, and tailored applications. Never claim to access LinkedIn, "
        "send messages, or apply unless a connected tool confirms it."
    ),
}
