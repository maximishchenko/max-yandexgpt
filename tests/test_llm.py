"""Tests for the YandexGPT client."""

from collections.abc import AsyncIterator
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest

from max_yandexgpt import Config, YandexGPT


def _chunk(content: str | None) -> SimpleNamespace:
    delta = SimpleNamespace(content=content)
    return SimpleNamespace(choices=[SimpleNamespace(delta=delta)])


async def _aiter(items: list[Any]) -> AsyncIterator[Any]:
    for item in items:
        yield item


@pytest.fixture
def llm(config: Config) -> YandexGPT:
    """Client with a mocked OpenAI transport."""
    client = YandexGPT(config)
    client._client = AsyncMock()  # type: ignore[assignment]
    return client


def test_model_uri(llm: YandexGPT) -> None:
    """Model URI includes folder id and model name."""
    assert llm._model_uri() == "gpt://folder/yandexgpt-5-lite/latest"


def test_build_messages_without_history(llm: YandexGPT) -> None:
    """System prompt goes first, user text last."""
    assert llm._build_messages("hi") == [
        {"role": "system", "content": llm.config.system_prompt},
        {"role": "user", "content": "hi"},
    ]


def test_build_messages_with_history(llm: YandexGPT) -> None:
    """History is inserted between system prompt and user text."""
    history: Any = [{"role": "assistant", "content": "prev"}]
    messages = llm._build_messages("hi", history)
    assert [m["role"] for m in messages] == ["system", "assistant", "user"]


async def test_complete(llm: YandexGPT) -> None:
    """Non-streaming response is mapped to LLMResponse."""
    create: Any = llm._client.chat.completions.create
    create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="answer"))],
        usage=SimpleNamespace(prompt_tokens=3, completion_tokens=5),
    )

    result = await llm.complete("q")

    assert (result.text, result.tokens_input, result.tokens_output) == (
        "answer",
        3,
        5,
    )
    kwargs = create.call_args.kwargs
    assert kwargs["model"] == "gpt://folder/yandexgpt-5-lite/latest"
    assert kwargs["stream"] is False
    assert kwargs["extra_headers"] == {"x-folder-id": "folder"}


async def test_complete_without_usage_and_content(llm: YandexGPT) -> None:
    """Missing usage/content fall back to defaults."""
    create: Any = llm._client.chat.completions.create
    create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=None))],
        usage=None,
    )

    result = await llm.complete("q")

    assert (result.text, result.tokens_input, result.tokens_output) == (
        "",
        0,
        0,
    )


async def test_stream_yields_non_empty_deltas(llm: YandexGPT) -> None:
    """Empty deltas and chunks without choices are skipped."""
    create: Any = llm._client.chat.completions.create
    create.return_value = _aiter(
        [_chunk("a"), _chunk(None), SimpleNamespace(choices=[]), _chunk("b")]
    )

    assert [d async for d in llm.stream("q")] == ["a", "b"]
    assert create.call_args.kwargs["stream"] is True


async def test_close(llm: YandexGPT) -> None:
    """close() closes the underlying client."""
    client: Any = llm._client
    await llm.close()
    client.close.assert_awaited_once()
