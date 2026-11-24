# llm_gateway

AgentOffice's own provider-agnostic LLM layer. One canonical set of types, four protocol adapters:
`anthropic`, `openai`, `gemini`, `openai_compatible`.

Phase 0 ships the canonical types, reasoning normalization, the `Provider` interface and a
`FakeProvider` for tests. Real adapters land in Phase 1.
