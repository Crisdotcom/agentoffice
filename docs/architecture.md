# Architecture

```
Frontend (React + Vite)  ── REST + WebSocket ──  Backend (FastAPI)
                                                   ├─ Orchestrator / message bus / shared memory
                                                   ├─ llm_gateway (own provider-agnostic LLM layer)
                                                   ├─ Tools + MCP client
                                                   └─ Cost control & guardrails
                                    Postgres + pgvector · Redis (pub/sub + queue) · workers
```

## llm_gateway

A small, auditable package (`backend/packages/llm_gateway`) instead of a large third-party proxy.
Four protocol adapters cover almost every provider:

| Adapter | Covers |
|---|---|
| `anthropic` | Claude (Messages API) |
| `openai` | GPT / o-series |
| `gemini` | Gemini |
| `openai_compatible` | Groq, DeepSeek, Mistral, xAI, Together, OpenRouter, Ollama, LM Studio, vLLM… |

Canonical types (`types.py`): `Message`, content blocks (`TextBlock`, `ImageBlock`, `ToolCallBlock`,
`ToolResultBlock`, `ThinkingBlock`), `ToolSpec`, `CompletionRequest/Response`, `StreamEvent`, `Usage`.

Reasoning is normalized to `off | low | medium | high` and translated per provider.

**Cross-provider rule:** thinking blocks are provider-specific (Anthropic signs them). When context moves
between agents on different providers, thinking blocks are dropped and only text, tool calls and results
are passed on.

## Agent communication

Agents communicate through tools (`send_message`, `delegate_task`, `ask`, `write_shared`, `read_shared`),
never free text parsing. A manager agent decomposes goals; a shared blackboard holds artifacts; each agent
gets a relevant context summary instead of other agents' full history. Every action emits an event that
streams to the UI over WebSocket.

See [plan.es.md](plan.es.md) for the full plan (Spanish).
