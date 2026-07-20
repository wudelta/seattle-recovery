# ======================================================================
# FILE: core_logic/ai/providers/openai.py (PATCH 1 OF 1)
# START: OPENAI_PROVIDER_IMPLEMENTATION
# ======================================================================

from typing import NoReturn

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

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


class OpenAIProvider(AIProvider):
    """
    Provider implementation for the OpenAI Responses API.

    This class translates Aurora requests, timeouts, responses, and
    failures to and from the OpenAI SDK.
    """

    @property
    def name(self) -> str:
        return "openai"

    def __init__(self):
        from django.conf import settings

        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
        )

    def _normalize_usage(self, usage):
        """Normalize OpenAI usage into Aurora's standard dictionary."""

        if usage is None:
            return {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            }

        return {
            "input_tokens": getattr(usage, "input_tokens", 0),
            "output_tokens": getattr(usage, "output_tokens", 0),
            "total_tokens": getattr(usage, "total_tokens", 0),
        }

    def _build_request(
        self,
        model: str,
        prompt: str,
        directive,
    ) -> dict:
        """
        Build a Responses API request.

        GPT-5.x currently does not support the temperature parameter.
        The provider owns vendor-specific request compatibility.
        """

        constraints = directive.constraints or {}

        request = {
            "model": model,
            "instructions": directive.instructions,
            "input": prompt,
            "max_output_tokens": constraints.get(
                "max_output_tokens",
            ),
        }

        return {
            key: value
            for key, value in request.items()
            if value is not None
        }

    def _request_client(
        self,
        timeout_seconds: float | None,
    ):
        """
        Create request-scoped SDK options.

        SDK retries are disabled because Aurora's central execution layer
        owns retry and provider-failover policy.
        """

        options = {
            "max_retries": 0,
        }

        if timeout_seconds is not None:
            options["timeout"] = timeout_seconds

        return self.client.with_options(**options)

    def _raise_normalized_error(
        self,
        error: Exception,
    ) -> NoReturn:
        """Translate OpenAI SDK failures into Aurora provider failures."""

        if isinstance(error, APITimeoutError):
            raise ProviderTimeoutError(
                "Request exceeded its execution deadline.",
                provider_name=self.name,
            ) from error

        if isinstance(error, APIConnectionError):
            raise NetworkUnavailableError(
                "Unable to reach the provider. Check network connectivity.",
                provider_name=self.name,
            ) from error

        if isinstance(error, AuthenticationError):
            raise ProviderAuthenticationError(
                "Provider credentials were rejected.",
                provider_name=self.name,
            ) from error

        if isinstance(error, RateLimitError):
            raise ProviderRateLimitError(
                "Provider rate limit was reached.",
                provider_name=self.name,
            ) from error

        if isinstance(error, APIStatusError):
            status_code = error.status_code

            if status_code == 408:
                raise ProviderTimeoutError(
                    "Provider returned a request timeout.",
                    provider_name=self.name,
                ) from error

            if status_code >= 500:
                raise ProviderUnavailableError(
                    f"Provider returned HTTP {status_code}.",
                    provider_name=self.name,
                ) from error

            if status_code in {401, 403}:
                raise ProviderAuthenticationError(
                    f"Provider rejected access with HTTP {status_code}.",
                    provider_name=self.name,
                ) from error

            raise ProviderRequestError(
                f"Provider rejected the request with HTTP {status_code}.",
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
            response = self._request_client(
                timeout_seconds,
            ).responses.create(
                **self._build_request(
                    model=model,
                    prompt=prompt,
                    directive=directive,
                )
            )
        except Exception as error:
            self._raise_normalized_error(error)

        return AIResponse(
            text=response.output_text,
            provider=self.name,
            model=model,
            usage=self._normalize_usage(
                getattr(response, "usage", None),
            ),
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
        Stream response fragments while preserving a normalized
        final AIResponse.
        """

        request = self._build_request(
            model=model,
            prompt=prompt,
            directive=directive,
        )
        request["stream"] = True

        accumulated = ""
        usage = None

        try:
            stream = self._request_client(
                timeout_seconds,
            ).responses.create(
                **request,
            )

            for event in stream:
                event_type = getattr(event, "type", "")

                if event_type == "response.output_text.delta":
                    delta = getattr(event, "delta", "")
                    accumulated += delta
                    yield delta

                elif event_type == "response.completed":
                    usage = getattr(
                        event.response,
                        "usage",
                        None,
                    )

        except Exception as error:
            self._raise_normalized_error(error)

        yield AIResponse(
            text=accumulated,
            provider=self.name,
            model=model,
            usage=self._normalize_usage(usage),
            metadata={
                "directive": directive.directive_name,
            },
        )


# ======================================================================
# END: OPENAI_PROVIDER_IMPLEMENTATION (PATCH 1 OF 1)
# ======================================================================