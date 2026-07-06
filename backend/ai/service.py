from threading import Lock
from typing import Any

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    OpenAIError,
)
from pydantic import ValidationError

from backend.ai.config import AISettings
from backend.ai.prompts import build_messages
from backend.ai.schemas import AIChatResult
from backend.utils.errors import AppError


class AIProviderError(AppError):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message, status_code=status_code)


class AIService:
    def __init__(self, settings: AISettings, client: Any | None = None) -> None:
        self.settings = settings
        if client is not None:
            self.client = client
            return
        self.client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
            timeout=settings.timeout_seconds,
            max_retries=settings.max_retries,
        )

    @classmethod
    def from_env(cls) -> "AIService":
        return cls(AISettings.from_env())

    def close(self) -> None:
        self.client.close()

    def generate_reply(
        self,
        *,
        model: str,
        context: dict,
        message: str,
    ) -> AIChatResult:
        response_format: dict[str, Any]
        if self.settings.response_format == "json_schema":
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": "copath_learning_assistant_response",
                    "strict": True,
                    "schema": AIChatResult.model_json_schema(),
                },
            }
        else:
            response_format = {"type": "json_object"}

        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=build_messages(context, message),
                response_format=response_format,
            )
        except (APIConnectionError, APITimeoutError) as exc:
            raise AIProviderError(
                "AI provider is temporarily unavailable",
                status_code=503,
            ) from exc
        except APIStatusError as exc:
            raise AIProviderError(
                f"AI provider request failed with HTTP {exc.status_code}"
            ) from exc
        except OpenAIError as exc:
            raise AIProviderError("AI provider request failed") from exc

        if not completion.choices:
            raise AIProviderError("AI provider returned no choices")
        content = completion.choices[0].message.content
        if not isinstance(content, str) or not content.strip():
            raise AIProviderError("AI provider returned an empty response")

        try:
            return AIChatResult.model_validate_json(content)
        except ValidationError as exc:
            raise AIProviderError(
                "AI provider returned invalid structured output"
            ) from exc


_service: AIService | None = None
_service_lock = Lock()


def get_ai_service() -> AIService:
    global _service
    if _service is None:
        with _service_lock:
            if _service is None:
                _service = AIService.from_env()
    return _service


def close_ai_service() -> None:
    global _service
    with _service_lock:
        if _service is not None:
            _service.close()
            _service = None
