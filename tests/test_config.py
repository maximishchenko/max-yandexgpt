"""Tests for Config."""

from typing import Any

import pytest

from max_yandexgpt import Config
from max_yandexgpt.config import DEFAULT_MODEL, MODELS

VALID: dict[str, Any] = {
    "max_token": "a",
    "yandex_api_key": "b",
    "yandex_folder_id": "c",
}


def test_defaults(config: Config) -> None:
    """Defaults are applied for optional fields."""
    assert config.model == DEFAULT_MODEL
    assert config.stream is True
    assert config.temperature == 0.3


@pytest.mark.parametrize("missing", sorted(VALID))
def test_required_fields(missing: str) -> None:
    """Each required field must be non-empty."""
    kwargs: dict[str, Any] = {**VALID, missing: ""}
    with pytest.raises(ValueError, match=missing):
        Config(**kwargs)


@pytest.mark.parametrize("model", sorted(MODELS))
def test_supported_models(model: str) -> None:
    """All listed models are accepted."""
    assert Config(**VALID, model=model).model == model


def test_unsupported_model() -> None:
    """Unknown model is rejected."""
    with pytest.raises(ValueError, match="Unsupported model"):
        Config(**VALID, model="gpt-4")


@pytest.mark.parametrize("temperature", [-0.1, 1.1])
def test_temperature_out_of_range(temperature: float) -> None:
    """Temperature must be within [0, 1]."""
    with pytest.raises(ValueError, match="temperature"):
        Config(**VALID, temperature=temperature)


@pytest.mark.parametrize("temperature", [0.0, 1.0])
def test_temperature_bounds_ok(temperature: float) -> None:
    """Boundary temperatures are valid."""
    assert Config(**VALID, temperature=temperature).temperature == temperature
