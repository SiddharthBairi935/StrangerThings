from dataclasses import dataclass


@dataclass(frozen=True)
class SpecialistTask:
    agent: str
    responsibility: str


SPECIALISTS = {
    "frontend": "Own end-to-end web frontend delivery across HTML/CSS/JavaScript/TypeScript, all major web frameworks, UI systems, accessibility, APIs, performance, and frontend quality.",
    "mobile": "Own native, cross-platform, and hybrid mobile delivery across Flutter, React Native, Android, iOS, .NET MAUI, Ionic, device capabilities, app security, testing, and store releases.",
    "backend": "Own server-side delivery across Java, Python, PHP, .NET/C#, Node.js, Go, Ruby, C/C++, APIs, distributed systems, security, integrations, and deployment.",
    "database": "Own data architecture and operations across SQL, relational, NoSQL, cache, search, graph, time-series, and cloud data platforms, including modeling, reliability, security, and performance.",
    "testing": "Own quality engineering across manual and automated testing, web/mobile/API/database layers, unit through end-to-end tests, performance, security, accessibility, release validation, and reporting.",
}


def create_lucas_plan(task: str) -> dict[str, object]:
    """Create a transparent deterministic work plan; does not execute code."""
    normalized = " ".join(task.lower().split())
    selected: list[str] = []

    keyword_groups = {
        "frontend": (
            "react frontend", "react.js", "react component", "next.js", "nextjs",
            "html", "css", "javascript", "typescript", "web page", "website ui",
            "web ui", "frontend", "angular", "vue", "nuxt", "svelte", "astro",
            "bootstrap", "tailwind", "sass", "scss", "vite", "webpack",
            "accessibility", "responsive design",
        ),
        "mobile": (
            "flutter", "dart", "android", "ios", "mobile", "app screen",
            "react native", "swift", "swiftui", "kotlin", "jetpack compose",
            "ionic", "capacitor", ".net maui", "xamarin", "kotlin multiplatform",
        ),
        "backend": (
            "api", "backend", "server", "python", "java", "authentication",
            "endpoint", "fastapi", "django", "flask", "php", "laravel",
            "asp.net", ".net", "spring", "node.js", "nestjs", "express",
            "golang", "rust", "ruby", "c++", "c#", "microservice", "grpc",
        ),
        "database": (
            "database", "postgres", "postgresql", "sql", "schema", "migration",
            "query", "sqlite", "mongodb", "redis", "oracle", "dynamodb",
            "mysql", "cassandra", "firestore", "snowflake", "bigquery",
            "elasticsearch", "neo4j", "database index",
        ),
    }
    for agent, keywords in keyword_groups.items():
        matched = any(keyword in normalized for keyword in keywords)
        if agent == "frontend" and "react native" in normalized and "react frontend" not in normalized:
            matched = any(
                keyword in normalized for keyword in keyword_groups["frontend"]
                if keyword not in {"react frontend", "react.js", "react component"}
            )
        if matched:
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
