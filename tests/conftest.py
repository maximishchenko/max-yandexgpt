"""Shared fixtures."""

import pytest

from max_yandexgpt import Config


@pytest.fixture
def config() -> Config:
    """Return a valid config."""
    return Config(
        max_token="max-token",
        yandex_api_key="api-key",
        yandex_folder_id="folder",
    )
