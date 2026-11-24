import pytest
from llm_gateway import (
    CompletionRequest,
    Message,
    ReasoningLevel,
    Role,
    TextBlock,
    ThinkingBlock,
    reasoning_params,
    strip_foreign_thinking,
)
from llm_gateway.providers import FakeProvider


def test_reasoning_off_is_empty_except_gemini():
    assert reasoning_params("openai", ReasoningLevel.OFF) == {}
    assert reasoning_params("anthropic", ReasoningLevel.OFF) == {}
    assert reasoning_params("gemini", ReasoningLevel.OFF) == {
        "thinkingConfig": {"thinkingBudget": 0}
    }


@pytest.mark.parametrize("level", [ReasoningLevel.LOW, ReasoningLevel.MEDIUM, ReasoningLevel.HIGH])
def test_reasoning_maps_per_protocol(level):
    assert reasoning_params("openai", level) == {"reasoning_effort": level.value}
    assert reasoning_params("anthropic", level)["thinking"]["type"] == "enabled"
    assert reasoning_params("gemini", level)["thinkingConfig"]["thinkingBudget"] > 0


def test_unknown_protocol_raises():
    with pytest.raises(ValueError):
        reasoning_params("nope", ReasoningLevel.LOW)


def test_strip_foreign_thinking_keeps_own_provider():
    msgs = [
        Message(
            role=Role.ASSISTANT,
            content=[
                ThinkingBlock(provider="anthropic", text="hmm", signature="sig"),
                TextBlock(text="hello"),
            ],
        ),
        Message(role=Role.ASSISTANT, content=[ThinkingBlock(provider="anthropic", text="only")]),
    ]
    to_openai = strip_foreign_thinking(msgs, "openai")
    assert len(to_openai) == 1
    assert to_openai[0].content == [TextBlock(text="hello")]

    to_anthropic = strip_foreign_thinking(msgs, "anthropic")
    assert len(to_anthropic) == 2


def test_message_round_trips_through_json():
    msg = Message(role=Role.ASSISTANT, content=[TextBlock(text="hi"), ThinkingBlock(provider="x")])
    assert Message.model_validate_json(msg.model_dump_json()) == msg


async def test_fake_provider_echoes():
    provider = FakeProvider()
    resp = await provider.complete(
        CompletionRequest(model="fake-1", messages=[Message.text(Role.USER, "ping")])
    )
    assert resp.message.plain_text() == "echo: ping"
    assert provider.requests[0].model == "fake-1"
