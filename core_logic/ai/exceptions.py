# ======================================================================
# FILE: core_logic/ai/exceptions.py (PATCH 1 OF 1)
# START: NORMALIZED_AI_PROVIDER_EXCEPTIONS
# ======================================================================


class AIProviderError(RuntimeError):
    """Base exception for normalized AI provider execution failures."""

    def __init__(
        self,
        message: str,
        *,
        provider_name: str | None = None,
    ):
        self.provider_name = provider_name

        if provider_name:
            message = f"{provider_name}: {message}"

        super().__init__(message)


class ProviderUnavailableError(AIProviderError):
    """The selected provider is temporarily unavailable."""


class ProviderTimeoutError(AIProviderError):
    """The selected provider exceeded its execution deadline."""


class ProviderRateLimitError(AIProviderError):
    """The selected provider rejected the request due to rate limits."""


class NetworkUnavailableError(AIProviderError):
    """The local environment cannot reach cloud AI providers."""


class ProviderAuthenticationError(AIProviderError):
    """The provider rejected Aurora's credentials."""


class ProviderRequestError(AIProviderError):
    """The provider rejected an invalid or unsupported request."""


class ProviderExecutionError(AIProviderError):
    """The provider failed for an unclassified execution reason."""


# ======================================================================
# END: NORMALIZED_AI_PROVIDER_EXCEPTIONS (PATCH 1 OF 1)
# ======================================================================

