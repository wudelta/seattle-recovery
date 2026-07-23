# ======================================================================
# FILE: core_logic/ai/base.py (PATCH 1 OF 1)
# START: AI_PROVIDER_INTERFACE
# ======================================================================

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class AIResponse:
    """
    Normalized response returned by every AI provider.

    All provider implementations translate their native SDK responses
    into this structure before returning control to Aurora.
    """

    text: str
    provider: str
    model: str
    usage: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class AIProvider(ABC):
    """
    Abstract interface implemented by every AI provider.

    Provider implementations are responsible only for translating
    between Aurora's normalized interface and the underlying vendor SDK.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Unique provider identifier (e.g. "openai", "gemini").
        """
        raise NotImplementedError

    @abstractmethod
    def chat(
        self,
        *,
        model: str,
        prompt: str,
        directive,
        timeout_seconds: float | None = None,
    ) -> AIResponse:
        """
        Execute a complete request and return a normalized response.

        Every provider implementation must guarantee one of three outcomes:

        - return a normalized AIResponse;
        - raise a normalized AIProviderError subclass;
        - terminate because the supplied execution timeout expired.

        Provider implementations are responsible for translating Aurora's
        timeout contract into the underlying SDK.
        """
        raise NotImplementedError

    @abstractmethod
    async def stream(
        self,
        *,
        model: str,
        prompt: str,
        directive,
        timeout_seconds: float | None = None,
    ) -> AsyncIterator[str | AIResponse]:
        """
        Stream response fragments asynchronously.

        Providers may yield either:

        - string fragments during generation;
        - a final normalized AIResponse.

        Every provider implementation must honor the same execution
        guarantees defined by chat().
        """
        raise NotImplementedError


# ======================================================================
# END: AI_PROVIDER_INTERFACE (PATCH 1 OF 1)
# ======================================================================