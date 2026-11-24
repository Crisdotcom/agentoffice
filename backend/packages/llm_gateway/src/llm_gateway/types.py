"""Canonical, provider-neutral types. Every adapter translates to and from these."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field


class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ReasoningLevel(StrEnum):
    OFF = "off"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TextBlock(BaseModel):
    type: Literal["text"] = "text"
    text: str


class ImageBlock(BaseModel):
    type: Literal["image"] = "image"
    media_type: str
    data_base64: str | None = None
    url: str | None = None


class ToolCallBlock(BaseModel):
    type: Literal["tool_call"] = "tool_call"
    id: str
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolResultBlock(BaseModel):
    type: Literal["tool_result"] = "tool_result"
    tool_call_id: str
    content: str
    is_error: bool = False


class ThinkingBlock(BaseModel):
    """Provider-specific reasoning. Only valid when sent back to the same provider."""

    type: Literal["thinking"] = "thinking"
    provider: str
    text: str = ""
    signature: str | None = None


ContentBlock = Annotated[
    TextBlock | ImageBlock | ToolCallBlock | ToolResultBlock | ThinkingBlock,
    Field(discriminator="type"),
]


class Message(BaseModel):
    role: Role
    content: list[ContentBlock]

    @classmethod
    def text(cls, role: Role, text: str) -> Message:
        return cls(role=role, content=[TextBlock(text=text)])

    def plain_text(self) -> str:
        return "".join(b.text for b in self.content if isinstance(b, TextBlock))


class ToolSpec(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=lambda: {"type": "object", "properties": {}})


class Usage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    cached_input_tokens: int = 0


class CompletionRequest(BaseModel):
    model: str
    messages: list[Message]
    system: str | None = None
    tools: list[ToolSpec] = Field(default_factory=list)
    reasoning: ReasoningLevel = ReasoningLevel.OFF
    max_output_tokens: int = 4096
    temperature: float | None = None


class StopReason(StrEnum):
    END = "end"
    TOOL_USE = "tool_use"
    MAX_TOKENS = "max_tokens"
    ERROR = "error"


class CompletionResponse(BaseModel):
    provider: str
    model: str
    message: Message
    stop_reason: StopReason
    usage: Usage = Field(default_factory=Usage)


class StreamEvent(BaseModel):
    kind: Literal["text_delta", "thinking_delta", "tool_call", "done"]
    text: str = ""
    tool_call: ToolCallBlock | None = None
    response: CompletionResponse | None = None


def strip_foreign_thinking(messages: list[Message], target_provider: str) -> list[Message]:
    """Drop other providers' thinking blocks before sending context to `target_provider`."""
    cleaned: list[Message] = []
    for msg in messages:
        blocks = [
            b
            for b in msg.content
            if not (isinstance(b, ThinkingBlock) and b.provider != target_provider)
        ]
        if blocks:
            cleaned.append(msg.model_copy(update={"content": blocks}))
    return cleaned
