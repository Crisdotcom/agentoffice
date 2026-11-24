"""llm_gateway: AgentOffice's provider-agnostic LLM layer."""

from .reasoning import reasoning_params
from .types import (
    CompletionRequest,
    CompletionResponse,
    Message,
    ReasoningLevel,
    Role,
    StopReason,
    StreamEvent,
    TextBlock,
    ThinkingBlock,
    ToolCallBlock,
    ToolResultBlock,
    ToolSpec,
    Usage,
    strip_foreign_thinking,
)

__all__ = [
    "CompletionRequest",
    "CompletionResponse",
    "Message",
    "ReasoningLevel",
    "Role",
    "StopReason",
    "StreamEvent",
    "TextBlock",
    "ThinkingBlock",
    "ToolCallBlock",
    "ToolResultBlock",
    "ToolSpec",
    "Usage",
    "reasoning_params",
    "strip_foreign_thinking",
]
