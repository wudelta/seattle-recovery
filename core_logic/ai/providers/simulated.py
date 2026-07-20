# ======================================================================
# FILE: core_logic/ai/providers/simulated.py (PATCH 1 OF 1)
# START: SIMULATED_PROVIDER_IMPLEMENTATION
# ======================================================================

import asyncio

from core_logic.ai.base import AIProvider, AIResponse


class SimulatedProvider(AIProvider):
    """
    Deterministic AI provider used for development and testing.

    This implementation provides a predictable, network-free provider
    that serves as the reference implementation for the AIProvider
    interface.
    """

    @property
    def name(self) -> str:
        return "simulated"

    def chat(
        self,
        *,
        model: str,
        prompt: str,
        directive,
        timeout_seconds: float | None = None,
    ) -> AIResponse:
        """
        Execute a deterministic response without contacting an external
        AI service.

        timeout_seconds is accepted to satisfy the provider contract but
        is not required because simulated execution performs no I/O.
        """

        response_text = (
            "[Simulated Provider]\n\n"
            f"Prompt received:\n{prompt}"
        )

        return AIResponse(
            text=response_text,
            provider=self.name,
            model=model,
            usage={
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            metadata={
                "simulated": True,
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
        Stream a deterministic response.

        This mirrors the production providers while remaining completely
        offline and deterministic.
        """

        response = self.chat(
            model=model,
            prompt=prompt,
            directive=directive,
            timeout_seconds=timeout_seconds,
        )

        # Simulate asynchronous execution so callers exercise the same
        # code path as real providers.
        await asyncio.sleep(0)

        yield response


# ======================================================================
# END: SIMULATED_PROVIDER_IMPLEMENTATION (PATCH 1 OF 1)
# ======================================================================