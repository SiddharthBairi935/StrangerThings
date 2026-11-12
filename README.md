# StrangerThings — Eleven Personal AI Assistant

**StrangerThings** is the private project repository. **Eleven (11), alias L**, is the overall personal AI assistant and central coordinator.

## Confirmed agent hierarchy

- **Eleven (11) / L** — overall assistant, central brain, planning and coordination.
  - **Max** — diet, fitness, workouts, physical activity, weight, measurements and progress.
  - **Will** — LinkedIn, career, jobs, freelancing, networking and resume support.
  - **Mike** — Google Drive files, folders and documents (requires Drive connection and permissions).
  - **Dustin** — day-to-day general research, comparisons, fact-checking and learning.
  - **Lucas** — head of the Coding Department.
    - **Frontend Agent** — React, Next.js, HTML, CSS and UI/UX.
    - **Mobile Agent** — Flutter, Dart, Android and iOS.
    - **Backend Agent** — APIs, Python, Java, authentication and integrations.
    - **Database Agent** — SQL, PostgreSQL, schema design and query optimization.
    - **Testing Agent** — unit/integration testing, debugging and quality assurance.

Lucas's five coding specialists are peers at the same level. Lucas coordinates their work and reports to Eleven.

## Current implementation

- FastAPI backend and responsive chat interface.
- Authenticated chat and owner-scoped SQLite conversation history.
- Configurable OpenAI-compatible model provider.
- Agent hierarchy registry at `GET /api/agents`.
- Top-level department routing for Max, Will, Mike, Dustin, Lucas, or Eleven.
- Authenticated Lucas delegation planner at `POST /api/lucas/delegate`; selects relevant coding specialists and always includes Testing.
- Role-specific system instructions for each top-level department.
- User-approved memory endpoints.
- GitHub Actions test workflow.

**Important:** The hierarchy and role-aware routing are implemented. This is not yet a fully autonomous multi-agent system: Lucas currently creates a deterministic delegation plan; specialist agents do not independently execute code or call tools yet. Repository editing, command execution, Drive/LinkedIn connections, live research tools, voice, vision, approvals UI, and scheduled tasks still need implementation. A role marked active means its routing/instructions exist; it does not mean external integrations are connected.

## Local setup

Requirements: Python 3.11+ and pip.

```bash
python -m venv .venv
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Configure these values in the private server-side `.env`:
- `ELEVEN_API_TOKEN`: long random secret for private API access.
- `LLM_API_KEY` and `LLM_MODEL`: provider credentials and model name.
- `LLM_BASE_URL`: optional provider API base URL.

Never commit `.env`, provider keys, or access tokens. The browser keeps the owner token in memory for the current tab only.

- Chat: `http://127.0.0.1:8000/`
- Health: `http://127.0.0.1:8000/health`
- API docs: `http://127.0.0.1:8000/docs`
- Agent hierarchy: `GET /api/agents`

## Safety and deployment

The API is not production-ready. Do not expose it publicly until HTTPS/reverse proxy, rate limiting, backups, monitoring, secret management, and end-to-end security checks are complete. Consequential external actions must require explicit user approval. Fitness guidance must not be presented as medical diagnosis.

Hostinger deployment has not been performed by this repository workflow. Deploy only after integration, security, and operational checks are complete.

## Lucas delegation API

The authenticated `POST /api/lucas/delegate` endpoint accepts a task such as `{"task":"Fix the Flutter dashboard"}` and returns the selected specialist workflow. It always includes Testing as the final verification role. The response explicitly reports `status: planned` and `execution_started: false`; it plans work but does not execute code.
