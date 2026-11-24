# Contributing to AgentOffice

Thanks for your interest! AgentOffice is early, so the best contributions right now are:

- **Role templates** (`backend/roles/*.yaml`) — new agent roles with good system prompts.
- **Provider adapters** (`backend/packages/llm_gateway`) — fixes and tests for LLM providers.
- Bug reports, docs and design feedback.

## Development setup

```bash
cd backend && uv sync && uv run pytest
cd frontend && npm install && npm run dev
```

Before opening a PR:

```bash
cd backend && uv run ruff check . && uv run ruff format --check . && uv run pytest
cd frontend && npm run lint && npm run build
```

## Sign-off and CLA

Every commit must be signed off (`git commit -s`) under the
[Developer Certificate of Origin](https://developercertificate.org/).

Because AgentOffice also has a commercial hosted edition, contributors will be asked to accept a
Contributor License Agreement (CLA) on their first pull request. The CLA lets the project offer the code
under the AGPL-3.0 and in the hosted edition; you keep the copyright of your contribution.

## Code of conduct

This project follows the [Contributor Covenant 2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).
Report unacceptable behavior privately to the maintainers (see SECURITY.md for contact).
