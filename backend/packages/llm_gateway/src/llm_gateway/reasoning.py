"""Translate the normalized reasoning level into each provider's native parameters."""

from __future__ import annotations

from typing import Any

from .types import ReasoningLevel

# Token budgets for providers that take an explicit thinking budget.
THINKING_BUDGETS: dict[ReasoningLevel, int] = {
    ReasoningLevel.LOW: 2_048,
    ReasoningLevel.MEDIUM: 8_192,
    ReasoningLevel.HIGH: 24_576,
}


def reasoning_params(protocol: str, level: ReasoningLevel) -> dict[str, Any]:
    """Return request parameters to merge into a provider call for the given reasoning level."""
    if level is ReasoningLevel.OFF:
        if protocol == "gemini":
            return {"thinkingConfig": {"thinkingBudget": 0}}
        return {}

    match protocol:
        case "openai" | "openai_compatible":
            return {"reasoning_effort": level.value}
        case "anthropic":
            return {"thinking": {"type": "enabled", "budget_tokens": THINKING_BUDGETS[level]}}
        case "gemini":
            return {"thinkingConfig": {"thinkingBudget": THINKING_BUDGETS[level]}}
        case _:
            raise ValueError(f"Unknown protocol: {protocol}")
