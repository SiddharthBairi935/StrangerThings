# Eleven — Personal AI Assistant

Eleven is a private, self-hosted personal AI assistant. The first milestone is a reliable API with persistent conversation history and a provider-neutral LLM connection. The architecture can grow into a multi-agent system, integrations, voice, and a mobile-friendly interface.

## Implemented in the current foundation

- FastAPI backend with root and health endpoints.
- Chat endpoint at `POST /api/chat`.
- SQLite storage for user and assistant messages.
- Conversation IDs so a client can continue an existing conversation.
- Optional OpenAI-compatible chat-completions provider.
- Environment-based configuration aligned with `.env.example`.
- No real credentials committed to this repository.

**Important:** Without `LLM_API_KEY` and `LLM_MODEL`, the API saves messages and returns a clear configuration message instead of pretending an AI model is connected. This is a development foundation, not yet the complete multi-agent assistant. Do not expose it publicly until authentication, HTTPS, rate limits, and deployment secrets are configured.

## Requirements

- Python 3.11+
- pip

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env`.
4. To enable model replies, set `LLM_API_KEY`, `LLM_MODEL`, and (if needed) `LLM_BASE_URL` in your private `.env` file. Never commit real keys.
5. Start the API:

   ```bash
   uvicorn app.main:app --reload
   ```

6. Open:
   - Health: http://127.0.0.1:8000/health
   - API docs: http://127.0.0.1:8000/docs

## Chat API

Send a request to `POST /api/chat`:

```json
{
  "message": "Hello, Eleven",
  "conversation_id": null
}
```

The response includes a conversation ID, assistant reply, and status. Send the returned `conversation_id` with the next message to continue that conversation.

## Environment

See `.env.example`. Never commit `.env`, API keys, SSH keys, production database files, or personal data.

## Planned milestones

1. Secure foundation and verified VPS deployment.
2. Main brain and agent registry.
3. User-controlled persistent memory and preferences.
4. GitHub and Google Drive integrations with least-privilege permissions.
5. Voice pipeline and optional face-based convenience features.
6. Responsive iPhone-friendly web app/PWA.
7. Authentication, audit logs, backups, monitoring, and production hardening.

## Security principles

- Secrets belong in environment variables or a secret manager, never source control.
- Face recognition must never be the only authorization factor for sensitive actions.
- External actions require explicit permissions and audit logging.
- Personal memory must be inspectable and deletable by its owner.
