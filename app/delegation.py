from dataclasses import dataclass


@dataclass(frozen=True)
class SpecialistTask:
    agent: str
    responsibility: str


SPECIALISTS = {
    "frontend": "Implement or review web UI, React/Next.js components, styling, accessibility, and responsive behavior.",
    "mobile": "Implement or review Flutter/Dart mobile screens, navigation, state, and platform-specific behavior.",
    "backend": "Implement or review API endpoints, server logic, authentication, validation, and integrations.",
    "database": "Design or review schemas, SQL queries, migrations, indexes, and data integrity.",
    "testing": "Create and run appropriate unit, integration, and regression tests; report failures and coverage gaps.",
}


def create_lucas_plan(task: str) -> dict[str, object]:
    """Create a transparent deterministic work plan; does not execute code."""
    normalized = " ".join(task.lower().split())
    selected: list[str] = []

    keyword_groups = {
        "frontend": ("react", "next.js", "nextjs", "html", "css", "web page", "frontend", "ui", "ux"),
        "mobile": ("flutter", "dart", "android", "ios", "mobile", "app screen"),
        "backend": ("api", "backend", "server", "python", "java", "authentication", "endpoint", "fastapi"),
        "database": ("database", "postgres", "postgresql", "sql", "schema", "migration", "query", "sqlite"),
    }
    for agent, keywords in keyword_groups.items():
        if any(keyword in normalized for keyword in keywords):
            selected.append(agent)

    # For a broad coding request with no stack clues, Lucas starts with backend
    # analysis and Testing, then asks for missing technical context if required.
    if not selected:
        selected.append("backend")
    selected.append("testing")

    tasks = [
        {"agent": agent, "role": SPECIALISTS[agent]}
        for agent in selected
    ]
    return {
        "coordinator": "lucas",
        "task": task,
        "status": "planned",
        "execution_started": False,
        "specialists": selected,
        "workflow": tasks,
        "sequence": [
            "Lucas reviews the request and confirms scope and constraints.",
            "Selected specialists prepare their implementation or review work.",
            "Lucas integrates the proposed changes and resolves conflicts.",
            "Testing Agent verifies the result and reports failures or gaps.",
            "Lucas sends the verified report to Eleven.",
        ],
        "approval_note": (
            "This endpoint creates a delegation plan only. Repository edits, command execution, "
            "deployment, and external actions require separate connected tools and authorization."
        ),
    }
