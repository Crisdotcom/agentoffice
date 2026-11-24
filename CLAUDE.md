# AgentOffice

Open-source (AGPL-3.0) office of AI agents: each agent has a role, its own LLM provider/model and
reasoning level, and agents collaborate through a provider-neutral message format.

## Layout
- `backend/` — Python 3.12, FastAPI, managed with `uv` (workspace).
  - `backend/app/` — the API application.
  - `backend/packages/llm_gateway/` — our own provider-agnostic LLM layer (no LiteLLM).
    Adapters: `anthropic`, `openai`, `gemini`, `openai_compatible`. Canonical types in `types.py`.
  - `backend/roles/` — YAML role templates.
- `frontend/` — React + Vite + TypeScript.
- `docs/` — architecture and roadmap.

## Commands
- Backend tests: `cd backend && uv run pytest`
- Backend lint: `cd backend && uv run ruff check . && uv run ruff format --check .`
- Backend dev server: `cd backend && uv run uvicorn app.main:app --reload`
- Frontend: `cd frontend && npm run dev` / `npm run build` / `npm run lint`
- Full stack: `docker compose up --build`

## Conventions
- Frontend UI work must follow the project skill `.claude/skills/modern-web-guidance`
  (search the guidance before writing HTML/CSS/client JS).
- Provider API keys are encrypted at rest and never returned to the frontend.
- Thinking/reasoning blocks are provider-specific: drop them when context crosses providers.
