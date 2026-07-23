# ======================================================================
# FILE: core_logic/ai/providers/gemini.py (PATCH 1 OF 1)
# START: GEMINI_PROVIDER_IMPLEMENTATION
# ======================================================================

from typing import NoReturn

import httpx
from django.conf import settings
from google import genai
from google.genai import errors, types

from core_logic.ai.base import AIProvider, AIResponse
from core_logic.ai.exceptions import (
    NetworkUnavailableError,
    ProviderAuthenticationError,
    ProviderExecutionError,
    ProviderRateLimitError,
    ProviderRequestError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)


class GeminiProvider(AIProvider):
    """
    Provider implementation for Google Gemini.

    This class translates Aurora requests, timeouts, responses, and
    failures to and from the Gemini SDK.
    """

    @property
    def name(self) -> str:
        return "gemini"

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ProviderAuthenticationError(
                "GEMINI_API_KEY is not configured.",
                provider_name=self.name,
            )

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
        )

    def _build_config(
        self,
        directive,
        timeout_seconds: float | None,
    ) -> types.GenerateContentConfig:
        """Build Gemini generation and request-level configuration."""

        constraints = directive.constraints or {}

        config = types.GenerateContentConfig(
            system_instruction=directive.instructions,
            temperature=constraints.get(
                "temperature",
                0.2,
            ),
        )

        response_format = constraints.get(
            "response_format",
        )

        if response_format == "json":
            config.response_mime_type = (
                "application/json"
            )

        http_options = {
            "retry_options": types.HttpRetryOptions(
                attempts=1,
            ),
        }

        if timeout_seconds is not None:
            http_options["timeout"] = int(
                timeout_seconds * 1000
            )

        config.http_options = types.HttpOptions(
            **http_options,
        )

        return config

    def _raise_normalized_error(
        self,
        error: Exception,
    ) -> NoReturn:
        """Translate Gemini SDK failures into Aurora provider failures."""

        if isinstance(error, httpx.TimeoutException):
            raise ProviderTimeoutError(
                "Request exceeded its execution deadline.",
                provider_name=self.name,
            ) from error

        if isinstance(
            error,
            (
                httpx.ConnectError,
                httpx.NetworkError,
            ),
        ):
            raise NetworkUnavailableError(
                "Unable to reach the provider. Check network connectivity.",
                provider_name=self.name,
            ) from error

        if isinstance(error, errors.APIError):
            status_code = getattr(
                error,
                "code",
                None,
            )

            if status_code == 408:
                raise ProviderTimeoutError(
                    "Provider returned a request timeout.",
                    provider_name=self.name,
                ) from error

            if status_code == 429:
                raise ProviderRateLimitError(
                    "Provider rate limit was reached.",
                    provider_name=self.name,
                ) from error

            if status_code in {401, 403}:
                raise ProviderAuthenticationError(
                    f"Provider rejected access with HTTP {status_code}.",
                    provider_name=self.name,
                ) from error

            if status_code is not None and status_code >= 500:
                raise ProviderUnavailableError(
                    f"Provider returned HTTP {status_code}.",
                    provider_name=self.name,
                ) from error

            raise ProviderRequestError(
                (
                    f"Provider rejected the request with HTTP {status_code}."
                    if status_code is not None
                    else "Provider rejected the request."
                ),
                provider_name=self.name,
            ) from error

        raise ProviderExecutionError(
            f"Unexpected provider failure: {error}",
            provider_name=self.name,
        ) from error

    def chat(
        self,
        *,
        model: str,
        prompt: str,
        directive,
        timeout_seconds: float | None = None,
    ) -> AIResponse:
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=self._build_config(
                    directive=directive,
                    timeout_seconds=timeout_seconds,
                ),
            )
        except Exception as error:
            self._raise_normalized_error(error)

        return AIResponse(
            text=response.text,
            provider=self.name,
            model=model,
            metadata={
                "directive": directive.directive_name,
            },
        )

    async def stream(
        self,
        *,
        model: str,
        prompt: str,
        directive,
        timeout_seconds: float | None = None,
    ):
        """
        Temporary streaming implementation.

        Until native Gemini streaming is integrated, this method
        delegates to chat() and yields a single normalized response.
        """

        response = self.chat(
            model=model,
            prompt=prompt,
            directive=directive,
            timeout_seconds=timeout_seconds,
        )

        yield response


# ======================================================================
# END: GEMINI_PROVIDER_IMPLEMENTATION (PATCH 1 OF 1)
# ======================================================================