# StrangerThings — Eleven Personal AI Assistant

**StrangerThings** is the project repository. **Eleven** is the personal AI assistant being built inside it.

Eleven is designed around a central brain/orchestrator, specialist agents, user-approved memory, and a private self-hosted backend. This repository is under active development; it is not yet a production-ready assistant.

## Current brain foundation

- FastAPI backend with health endpoint.
- Chat API with conversation IDs and SQLite conversation history.
- Configurable OpenAI-compatible chat-completions provider.
- Central brain prompt with relevant user-approved memories.
- Basic routing between general, coding, and research model roles.
- Agent registry endpoint: `GET /api/agents`.
- Memory endpoints: `GET/POST /api/memory` and `DELETE /api/memory/{memory_id}`.
- Tests for memory isolation, conversation ordering, prompt context, and basic routing.

## Agent status

| Agent | Status | Notes |
|---|---|---|
| General | Active | Uses configured LLM |
| Coding | Active | Prompt-specialized LLM role; no shell or repository write tools yet |
| Research | Active | Prompt-specialized LLM role; no live web search tool yet |
| GitHub | Planned | Needs scoped GitHub integration and approval checks |
| Google Drive | Planned | Needs OAuth and Drive API integration |
| Voice | Planned | Speech-to-text and text-to-speech pipeline |
| Vision | Planned | Image understanding; face recognition requires extra privacy safeguards |
| Tasks | Planned | Background worker and scheduler not connected |

"Active" means the role can be selected and handled by the configured language model. It does not mean external tools are connected.

## Requirements

- Python 3.11+
- pip

## Run locally

```bash
python -m venv .venv
# Activate the virtual environment for your operating system
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Set `LLM_API_KEY`, `LLM_MODEL`, and if required `LLM_BASE_URL` in your private `.env` file. Never commit real credentials.

- Health: `http://127.0.0.1:8000/health`
- API documentation: `http://127.0.0.1:8000/docs`
- Agent registry: `GET /api/agents`

## Chat

`POST /api/chat`

```json
{
  "message": "Help me plan the next development milestone",
  "conversation_id": null,
  "profile_id": "default"
}
```

Reuse the returned `conversation_id` to continue the same conversation. Use a stable profile ID for memory across conversations.

## Memory

`POST /api/memory`

```json
{
  "profile_id": "default",
  "content": "The user prefers concise answers in Hindi."
}
```

Memory is explicitly saved through the memory endpoint. Do not store sensitive information. List with `GET /api/memory?profile_id=default`; delete an entry with `DELETE /api/memory/{memory_id}?profile_id=default`.

## Important security limitations before deployment

- The current API has no user authentication or authorization. Do not expose it publicly yet.
- The default profile ID is a development convenience, not a secure identity boundary.
- Configure HTTPS, authentication, per-user data isolation, rate limiting, CORS for the real frontend origin, backups, and secret management before public use.
- Never commit `.env`, API keys, SSH keys, database files, or personal data.
- Face recognition must never be the only factor authorizing sensitive actions.

## Roadmap

1. Complete and test brain foundation.
2. Add secure user accounts and memory ownership.
3. Connect GitHub and Google Drive agents with least-privilege scopes and approvals.
4. Add live research tools and controlled coding execution.
5. Add voice and vision services.
6. Build a responsive iPhone-friendly web app/PWA.
7. Add background jobs, monitoring, backups, and production hardening.
8. Deploy to the Hostinger VPS only after security and integration tests pass.
