# AgentOffice

**Build an office of AI agents for your business.** Bring any LLM with your own API key, hire agents for
different jobs (marketing, developer, lead prospector, legal reviewer…), pick the model and reasoning
level for each one, and watch them collaborate as a team.

> 🇪🇸 [Leer en español](README.es.md)

> **Status:** early development (Phase 0). Nothing is usable yet — star/watch the repo to follow along.

## Why AgentOffice

- **Any LLM, per agent.** Use Anthropic for your developer, OpenAI for marketing, Gemini for legal review,
  or a local model via Ollama — in the same team.
- **Real teamwork.** Agents talk through a provider-neutral message format and a shared workspace, so
  context flows between agents even when they run on different models.
- **You stay in control.** Per-agent model and reasoning level, token/cost budgets, turn limits and
  human approval for external actions.
- **See your office.** A live dashboard today, a 3D office where you watch agents work on the roadmap.
- **Your keys, your data.** Self-host it; provider API keys are encrypted at rest.

## Architecture (short)

| Layer | Tech |
|---|---|
| Frontend | React + Vite + TypeScript (3D office with React Three Fiber in Phase 2) |
| API | Python 3.12 + FastAPI, WebSockets for live events |
| LLM layer | [`llm_gateway`](backend/packages/llm_gateway) — our own adapter layer: Anthropic, OpenAI, Gemini and any OpenAI-compatible API |
| Data | Postgres + pgvector, Redis |

More in [docs/architecture.md](docs/architecture.md) and the [roadmap](docs/roadmap.md).

## Quick start (development)

Requirements: Docker, or Python 3.12 + [uv](https://docs.astral.sh/uv/) and Node 22.

```bash
cp .env.example .env
docker compose up --build
```

- Web: http://localhost:5173
- API: http://localhost:8000/api/health

Without Docker:

```bash
cd backend && uv sync && uv run uvicorn app.main:app --reload
cd frontend && npm install && npm run dev
```

## Open source and hosted

AgentOffice is open source under the **AGPL-3.0**. A hosted cloud edition with extra features
(managed hosting, multi-user teams, SSO, always-on agents, included LLM credits) is planned and will fund
development of the open-source core.

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). New role templates and provider
adapters are a great place to start.

## License

[GNU Affero General Public License v3.0](LICENSE)
