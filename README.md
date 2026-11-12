# StrangerThings — Eleven Personal AI Assistant

**StrangerThings** is the project repository. **Eleven (L)** is the personal AI assistant being built inside it.

Eleven is designed around one central brain, specialist agents, approved personal memory, and a private interface for chat and voice. This repository is under active development and is not yet production-ready.

## Current foundation

- FastAPI backend and health endpoint.
- Responsive Eleven chat workspace served at `/` (desktop and mobile layouts).
- Browser chat connects to the private API using a tab-only owner token; it is not persisted in local storage.
- Chat API with SQLite conversation history.
- Configurable OpenAI-compatible model provider.
- General, coding, and research prompt roles with basic routing.
- Agent registry at `GET /api/agents`.
- Explicit user-approved memory endpoints.
- Private owner-token authentication for chat and memory APIs.
- Conversation history and memories are scoped to the authenticated owner profile.
- GitHub Actions test workflow.

## Agent status

| Agent | Status | Notes |
|---|---|---|
| General | Active | Uses configured LLM |
| Coding | Active | Prompt-specialized role; no shell or repository write tools yet |
| Research | Active | Prompt-specialized role; no live web search tool yet |
| GitHub | Planned | Needs scoped integration and approval checks |
| Google Drive | Planned | Needs OAuth and Drive API integration |
| Voice | Planned | Speech-to-text and text-to-speech |
| Vision | Planned | Image understanding; face recognition needs additional safeguards |
| Tasks | Planned | Background worker and scheduler |

"Active" means a prompt role can be selected by the model. It does not mean external tools or autonomous task execution are connected.

## Requirements and local setup

- Python 3.11+
- pip

```bash
python -m venv .venv
pip install -r requirements.txt
cp .env.example .env
```

Set these values in your private `.env` file:
- `ELEVEN_API_TOKEN`: a long, random secret used by your private client.
- `LLM_API_KEY` and `LLM_MODEL`: credentials and model name for your chosen OpenAI-compatible provider.
- `LLM_BASE_URL`: change only if your provider uses a different API base URL.

Generate a token locally with `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Never commit the real `.env` file or share the token in chat.

Start the API:

```bash
uvicorn app.main:app --reload
```

- Eleven interface: `http://127.0.0.1:8000/`
- Health: `http://127.0.0.1:8000/health`
- API docs: `http://127.0.0.1:8000/docs`
- Agent registry: `GET /api/agents` (public capability metadata)

## Eleven chat interface

Open `http://127.0.0.1:8000/` after starting the server. Paste the `ELEVEN_API_TOKEN` value from your private server `.env` into the connection field. The browser keeps the token in memory for the current tab only; refreshing or closing the tab clears it. The interface currently supports text chat and displays the selected prompt role. Voice, real integrations, agent delegation, and task approvals are not connected yet.

## Authenticated API

Send the owner token on private endpoints:

```http
Authorization: Bearer YOUR_ELEVEN_API_TOKEN
```

Chat: `POST /api/chat`

```json
{
  "message": "Help me plan the next development milestone",
  "conversation_id": null
}
```

Reuse the returned `conversation_id` to continue the same conversation. The server assigns the owner profile; clients cannot choose another profile.

Memory: `POST /api/memory`

```json
{
  "content": "The user prefers concise answers in Hindi."
}
```

List memories with `GET /api/memory`; delete one with `DELETE /api/memory/{memory_id}`. All these endpoints require the owner token and use the server-configured owner profile.

If `ELEVEN_API_TOKEN` is not configured, private endpoints fail closed with HTTP 503. Missing or incorrect tokens receive HTTP 401.

## Deployment warning

Do not expose this API publicly yet. Authentication is now present for the single-owner development setup, but production still needs HTTPS/reverse-proxy configuration, rate limiting, stricter operational controls, backups, monitoring, frontend-origin configuration, and end-to-end security testing. The provider key and owner token must live only in server-side secrets.

## Roadmap

1. Finish backend security and API tests.
2. Add actual task delegation and safe tool execution.
3. Connect GitHub, Google Drive, and live research with least-privilege permissions and approvals.
4. Build the Eleven chat interface and voice pipeline.
5. Add vision and background tasks.
6. Build the responsive iPhone-friendly PWA.
7. Complete end-to-end tests and production hardening.
8. Deploy to Hostinger only after the security checks pass.
