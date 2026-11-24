from __future__ import annotations

from collections.abc import Callable

from ..types import (
    CompletionRequest,
    CompletionResponse,
    Message,
    Role,
    StopReason,
    Usage,
)


class FakeProvider:
    """Deterministic provider for tests and demos: replies with a scripted function or an echo."""

    protocol = "openai_compatible"

    def __init__(
        self,
        name: str = "fake",
        reply: Callable[[CompletionRequest], str] | None = None,
    ) -> None:
        self.name = name
        self._reply = reply or (lambda req: f"echo: {req.messages[-1].plain_text()}")
        self.requests: list[CompletionRequest] = []

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        self.requests.append(request)
        text = self._reply(request)
        return CompletionResponse(
            provider=self.name,
            model=request.model,
            message=Message.text(Role.ASSISTANT, text),
            stop_reason=StopReason.END,
            usage=Usage(
                input_tokens=sum(len(m.plain_text()) for m in request.messages),
                output_tokens=len(text),
            ),
        )
