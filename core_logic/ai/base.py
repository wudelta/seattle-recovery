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
        prompt: str,
        directive,
    ) -> AIResponse:
        """
        Execute a complete request and return a normalized response.
        """
        raise NotImplementedError

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        directive,
    ) -> AsyncIterator[str | AIResponse]:
        """
        Stream response fragments asynchronously.

        Providers may yield either:

        - string fragments during generation
        - a final AIResponse containing normalized metadata
        """
        raise NotImplementedError


# ======================================================================
# END: AI_PROVIDER_INTERFACE (PATCH 1 OF 1)
# ======================================================================