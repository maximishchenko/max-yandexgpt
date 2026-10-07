"""Configuration for max-yandexgpt."""

from dataclasses import dataclass

MODELS: set[str] = {
    "yandexgpt-5.1/latest",
    "yandexgpt-5-pro/latest",
    "yandexgpt-5-lite/latest",
    "aliceai-llm/latest",
}
"""AI models available in Yandex Cloud.
Keys are user-friendly names, values are model URIs.
"""

DEFAULT_MODEL: str = "yandexgpt-5-lite/latest"
"""Default AI model."""


@dataclass
class Config:
    """Bot configuration."""

    max_token: str = ""
    """Max messenger bot token."""

    yandex_api_key: str = ""
    """YandexGPT API key."""

    yandex_folder_id: str = ""
    """Yandex Cloud folder ID."""

    model: str = DEFAULT_MODEL
    """YandexGPT model name."""

    system_prompt: str = "Ты — полезный ассистент."
    """System prompt for the LLM."""

    temperature: float = 0.3
    """temperature: Generation temperature (0.0 - 1.0)."""

    max_tokens: int = 2000
    """max_tokens: Maximum tokens in LLM response."""

    stream: bool = True
    """stream: Enable streaming responses with message editing."""

    stream_interval: float = 1.0
    """stream_interval: Seconds between message edits during streaming."""

    def __post_init__(self) -> None:  # noqa: D105
        self._validate()

    def _validate(self) -> None:
        """Validate that required fields are set."""
        self.__validate_required_fields()
        self.__validate_model()
        self.__validate_temperature()

    def __validate_model(self) -> None:
        """Validate that the model is supported.
        
        Raises:
            ValueError: If the model is not supported

        """
        if self.model not in MODELS:
            available_models: str = ", ".join(map(str, MODELS))
            raise ValueError(
                f"Unsupported model: {self.model}. "
                f"Supported models: {available_models}"
            )

    def __validate_temperature(self) -> None:
        """Validate that the temperature is in the valid range.
        
        Raises:
            ValueError: If the temperature is not between 0.0 and 1.0

        """
        if not (0.0 <= self.temperature <= 1.0):
            raise ValueError("temperature must be between 0.0 and 1.0")

    def __validate_required_fields(self) -> None:
        """Validate that required fields are set.
        
        Raises:
            ValueError: If any required field is not set

        """
        if not self.max_token:
            raise ValueError("max_token is required")
        if not self.yandex_api_key:
            raise ValueError("yandex_api_key is required")
        if not self.yandex_folder_id:
            raise ValueError("yandex_folder_id is required")
