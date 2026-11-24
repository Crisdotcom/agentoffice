from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from ..types import CompletionRequest, CompletionResponse, StreamEvent


class Provider(ABC):
    """A protocol adapter. Subclasses translate canonical types to a provider's native API."""

    #: Protocol id used for reasoning mapping: anthropic | openai | gemini | openai_compatible
    protocol: str
    #: Provider instance name (e.g. "anthropic", "groq", "ollama")
    name: str

    @abstractmethod
    async def complete(self, request: CompletionRequest) -> CompletionResponse: ...

    async def stream(self, request: CompletionRequest) -> AsyncIterator[StreamEvent]:
        """Default streaming: one final event. Adapters override with real streaming."""
        response = await self.complete(request)
        yield StreamEvent(kind="text_delta", text=response.message.plain_text())
        yield StreamEvent(kind="done", response=response)
