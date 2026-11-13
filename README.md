# StrangerThings — Eleven Personal AI Assistant

**StrangerThings** is the private project repository. **Eleven (11), alias L**, is the overall personal AI assistant and central coordinator.

## Confirmed agent hierarchy

- **Eleven (11) / L** — overall assistant, central brain, planning and coordination.
  - **Max** — diet, fitness, workouts, physical activity, weight, measurements and progress.
  - **Will** — LinkedIn, career, jobs, freelancing, networking and resume support.
  - **Mike** — Google Drive files, folders and documents (requires Drive connection and permissions).
  - **Dustin** — day-to-day general research, comparisons, fact-checking and learning.
  - **Lucas** — head of the Coding Department.
    - **Frontend Agent** — full-spectrum web development: HTML5, CSS3, JavaScript, TypeScript, Bootstrap, Tailwind, Sass/SCSS, Less, React, Next.js, Angular, Vue, Nuxt, Svelte, SvelteKit, Astro, jQuery, state management, UI libraries, responsive UX, accessibility, API integration, tooling, performance and frontend testing.
    - **Mobile Agent** — native, cross-platform and hybrid apps: Flutter/Dart, React Native, Android/Kotlin/Java, iOS/Swift/SwiftUI, .NET MAUI, Xamarin, Ionic, Capacitor, Kotlin Multiplatform, device APIs, offline storage, notifications, mobile security, testing and store releases.
    - **Backend Agent** — Java/Spring, Python/Django/Flask/FastAPI, PHP/Laravel, C#/.NET/ASP.NET, Node.js/Express/NestJS, Go, Ruby, Rust, C/C++, APIs, distributed systems, authentication, security, integrations and deployment.
    - **Database Agent** — relational, NoSQL, cache, search, graph, time-series and cloud data platforms including PostgreSQL, MySQL, SQL Server, Oracle, SQLite, MongoDB, Redis, Cassandra, DynamoDB, Firebase/Firestore, schema design, optimization, migrations, backup, replication and security.
    - **Testing Agent** — manual and automated QA across web, mobile, API and database layers; unit, integration, system, end-to-end, regression, performance, load, security, accessibility and release testing; Selenium, Playwright, Cypress, Appium, Jest, Vitest, Pytest, JUnit, Postman, JMeter and k6.

Lucas's five coding specialists are peers at the same level. Lucas coordinates their work and reports to Eleven.

## Specialist skill policy

Each specialist is expected to cover the broad, end-to-end skill set of its own domain rather than being limited to one framework or language. The capability registry is intentionally broad and can be extended as technologies evolve. For each project, Lucas should select technologies that fit the existing codebase, requirements, platform and operational constraints—not force every listed technology into one project. A declared skill means it is in the specialist's knowledge scope; it does not prove that a runtime, license, external account, device, or tool is installed or connected.

## Current implementation

- FastAPI backend and responsive chat interface.
- Authenticated chat and owner-scoped SQLite conversation history.
- Configurable OpenAI-compatible model provider.
- Agent hierarchy registry at `GET /api/agents`.
- Top-level department routing for Max, Will, Mike, Dustin, Lucas, or Eleven.
- Broad capability registries and role instructions for all five Lucas coding specialists.
- Lucas delegation planner at `POST /api/lucas/delegate`, which selects specialists from task keywords and always includes Testing.
- User-approved memory endpoints.
- GitHub Actions test workflow.

**Important:** Lucas now performs multi-specialist LLM orchestration: relevant domain specialists produce proposals, Testing reviews them, and Lucas synthesizes a final response. These are role-separated calls to the configured model, not separate independently hosted models. This is not yet an autonomous software execution environment: the agents cannot run shell commands, edit repository files from the running app, execute tests, or deploy. GitHub write access, command execution, Drive/LinkedIn connections, live research tools, voice, vision, approvals UI and scheduled tasks still need implementation. A registered capability describes knowledge scope; it does not mean a runtime, external account, or tool is connected.

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
- `LLM_BASE_URL`: optional provider API base URL.\n- `GITHUB_TOKEN`: optional fine-grained GitHub token with repository Contents (read/write) and Pull requests (read/write) permissions. Keep it server-side only.\n- `GITHUB_REPOSITORY`: repository in `owner/name` form.\n- `GITHUB_BASE_BRANCH`: base branch for coding pull requests (default `main`).

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
\n\n## Lucas coding workspace\n\nThe authenticated `POST /api/lucas/code` endpoint accepts `{"task":"Add a profile settings screen"}`. When `GITHUB_TOKEN`, `GITHUB_REPOSITORY`, and LLM credentials are configured, Lucas reads a bounded set of `app/`, `tests/`, and root documentation/dependency files and generates a focused patch. The server validates every path, limits patch size and changed-file count, requires a test-file change, creates a dedicated `lucas/task-*` branch, commits the patch, and opens a draft pull request. The default branch is not modified. GitHub Actions runs the configured test workflow for the PR. The app itself does not execute shell commands or claim that CI passed; review the PR checks before merging. Never grant this token more permissions than required, and do not expose it to the browser.\n