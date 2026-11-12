# Eleven — Personal AI Assistant

Eleven is a private, self-hosted personal AI assistant. The first milestone is a small, reliable API with persistent conversation history and a provider-neutral LLM connection. The architecture is intended to grow into a multi-agent system, integrations, voice, and a mobile-friendly interface.

## Current milestone

- FastAPI backend with a health endpoint.
- Chat endpoint with conversation IDs.
- SQLite persistence for conversation history.
- Optional OpenAI-compatible chat-completions provider.
- Safe configuration through environment variables.
- No credentials committed to this repository.

**Important:** Without an LLM provider key, the API stores messages but returns a clear configuration message instead of pretending to be an intelligent model. This initial backend is for development and must not be exposed publicly until authentication, HTTPS, rate limits, and deployment secrets are configured.

## Requirements

- Python 3.11+
- pip

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and configure a provider key if you have one.
4. Start the API:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Open:
   - Health: http://127.0.0.1:8000/health
   - API docs: http://127.0.0.1:8000/docs

## Chat API

`POST /api/chat`

```json
{
  "message": "Hello, Eleven",
  "conversation_id": null
}
```

The response includes the conversation ID, assistant reply, and whether an LLM provider was used.

## Environment

See `.env.example`. Never commit `.env`, API keys, SSH keys, or production database files.

## Planned milestones

1. Secure foundation and verified VPS deployment.
2. Main brain and agent registry.
3. Persistent user memory with explicit user controls.
4. GitHub and Google Drive integrations with least-privilege permissions.
5. Voice pipeline and optional face-based convenience features.
6. Responsive iPhone-friendly web app/PWA.
7. Authentication, audit logs, backups, monitoring, and production hardening.

## Security principles

- Secrets belong in environment variables or a secret manager, never source control.
- Face recognition must never be the only authorization factor for sensitive actions.
- External actions require explicit permissions and audit logging.
- Personal memory must be inspectable and deletable by its owner.
