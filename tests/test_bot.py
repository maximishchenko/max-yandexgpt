"""Tests for MaxYandexGPT handlers."""

from collections.abc import AsyncIterator
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest

from max_yandexgpt import Config, LLMResponse, MaxYandexGPT

ERROR_MARK = "ошибка"


@pytest.fixture
def bot(config: Config) -> MaxYandexGPT:
    """Bot with mocked LLM and Max client."""
    instance = MaxYandexGPT(config=config)
    instance.llm = AsyncMock()
    instance.bot = AsyncMock()
    return instance


def _event(text: str | None) -> Any:
    body = (
        SimpleNamespace(text=text, mid="mid-1") if text is not None else None
    )
    sent = SimpleNamespace(message=SimpleNamespace(body=body))
    message = SimpleNamespace(body=body, answer=AsyncMock(return_value=sent))
    return SimpleNamespace(message=message)


def test_init_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Credentials fall back to environment variables."""
    monkeypatch.setenv("MAX_TOKEN", "t")
    monkeypatch.setenv("YANDEX_API_KEY", "k")
    monkeypatch.setenv("YANDEX_FOLDER_ID", "f")

    cfg = MaxYandexGPT().config

    assert (cfg.max_token, cfg.yandex_api_key, cfg.yandex_folder_id) == (
        "t",
        "k",
        "f",
    )


def test_init_without_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing credentials raise ValueError."""
    for name in ("MAX_TOKEN", "YANDEX_API_KEY", "YANDEX_FOLDER_ID"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(ValueError, match="required"):
        MaxYandexGPT()


def test_init_overrides(config: Config) -> None:
    """Keyword overrides are applied to the config."""
    cfg = MaxYandexGPT(
        config=config,
        model="yandexgpt-5-pro/latest",
        system_prompt="sp",
        stream=False,
        temperature=0.9,
        max_tokens=10,
    ).config

    assert cfg.model == "yandexgpt-5-pro/latest"
    assert cfg.system_prompt == "sp"
    assert cfg.stream is False
    assert cfg.temperature == 0.9
    assert cfg.max_tokens == 10


async def test_on_start(bot: MaxYandexGPT) -> None:
    """Greeting is sent on bot start."""
    event: Any = SimpleNamespace(bot=AsyncMock(), chat_id=42)

    await bot._on_start(event)

    event.bot.send_message.assert_awaited_once()
    assert event.bot.send_message.call_args.kwargs["chat_id"] == 42


async def test_on_start_without_bot(bot: MaxYandexGPT) -> None:
    """No bot on the event means nothing to do."""
    event: Any = SimpleNamespace(bot=None, chat_id=1)
    await bot._on_start(event)


@pytest.mark.parametrize("text", [None, ""])
async def test_on_message_ignores_empty(
    bot: MaxYandexGPT, text: str | None
) -> None:
    """Messages without text are ignored."""
    event = _event(text)

    await bot._on_message(event)

    event.message.answer.assert_not_awaited()


async def test_on_message_sync(bot: MaxYandexGPT) -> None:
    """Non-streaming mode answers with the full LLM text."""
    bot.config.stream = False
    complete: Any = bot.llm.complete
    complete.return_value = LLMResponse(text="ok")
    event = _event("hello")

    await bot._on_message(event)

    complete.assert_awaited_once_with("hello")
    event.message.answer.assert_awaited_once_with("ok")


async def test_sync_error(bot: MaxYandexGPT) -> None:
    """LLM failure produces an apology message."""
    bot.config.stream = False
    complete: Any = bot.llm.complete
    complete.side_effect = RuntimeError("boom")
    event = _event("hello")

    await bot._on_message(event)

    event.message.answer.assert_awaited_once()
    assert ERROR_MARK in event.message.answer.call_args.args[0]


async def test_streaming(bot: MaxYandexGPT) -> None:
    """Streaming mode edits the placeholder and ends with full text."""
    bot.config.stream_interval = 0.0

    async def fake_stream(_: str) -> AsyncIterator[str]:
        for part in ("Hel", "lo"):
            yield part

    bot.llm.stream = fake_stream  # type: ignore[method-assign]
    event = _event("hi")

    await bot._on_message(event)

    event.message.answer.assert_awaited_once_with("...")
    edit: Any = bot.bot.edit_message
    assert edit.call_args.kwargs == {"message_id": "mid-1", "text": "Hello"}


async def test_streaming_error(bot: MaxYandexGPT) -> None:
    """Failure while streaming produces an apology message."""

    async def broken(_: str) -> AsyncIterator[str]:
        raise RuntimeError("boom")
        yield ""  # pragma: no cover

    bot.llm.stream = broken  # type: ignore[method-assign]
    event = _event("hi")

    await bot._on_message(event)

    assert ERROR_MARK in event.message.answer.call_args.args[0]
