import os
from dataclasses import dataclass, field
from urllib.parse import urlparse

from dotenv import load_dotenv

from backend.database.connection import PROJECT_ROOT
from backend.utils.errors import AppError


class AIConfigurationError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=503)


@dataclass(frozen=True)
class AISettings:
    api_key: str = field(repr=False)
    base_url: str = "https://api.openai.com/v1"
    response_format: str = "json_schema"
    timeout_seconds: float = 30.0
    max_retries: int = 1

    @classmethod
    def from_env(cls) -> "AISettings":
        load_dotenv(PROJECT_ROOT / ".env", override=False)
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise AIConfigurationError(
                "AI is not configured. Missing environment variable: OPENAI_API_KEY"
            )

        response_format = os.getenv(
            "OPENAI_RESPONSE_FORMAT",
            "json_schema",
        ).strip()
        if response_format not in {"json_schema", "json_object"}:
            raise AIConfigurationError(
                "OPENAI_RESPONSE_FORMAT must be json_schema or json_object"
            )

        try:
            timeout_seconds = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "30"))
            max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "1"))
        except ValueError as exc:
            raise AIConfigurationError(
                "OPENAI_TIMEOUT_SECONDS and OPENAI_MAX_RETRIES must be numeric"
            ) from exc
        if timeout_seconds <= 0 or max_retries < 0:
            raise AIConfigurationError(
                "OPENAI_TIMEOUT_SECONDS must be positive and "
                "OPENAI_MAX_RETRIES cannot be negative"
            )

        base_url = os.getenv(
            "OPENAI_BASE_URL",
            "https://api.openai.com/v1",
        ).strip()
        if not base_url:
            raise AIConfigurationError("OPENAI_BASE_URL cannot be empty")
        parsed_base_url = urlparse(base_url)
        if parsed_base_url.scheme not in {"http", "https"} or not parsed_base_url.netloc:
            raise AIConfigurationError("OPENAI_BASE_URL must be a valid HTTP(S) URL")

        return cls(
            api_key=api_key,
            base_url=base_url.rstrip("/"),
            response_format=response_format,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )

    @classmethod
    def is_configured(cls) -> bool:
        try:
            cls.from_env()
        except AIConfigurationError:
            return False
        return True
