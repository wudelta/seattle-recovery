# ======================================================================
# FILE: core_logic/ai/registry.py (PATCH 1 OF 1)
# START: PROVIDER_REGISTRY
# ======================================================================

from core_logic.ai.base import AIProvider
from core_logic.ai.providers import (
    GeminiProvider,
    OpenAIProvider,
    SimulatedProvider,
)


class ProviderRegistry:
    """
    Registry of available AI providers.

    The registry owns provider registration and singleton instance
    management. It performs no routing, model resolution, retry, or
    failover decisions.
    """

    def __init__(self):
        self._provider_classes = {}
        self._provider_instances = {}

    def register(
        self,
        provider_class: type[AIProvider],
    ) -> None:
        """
        Register a provider implementation.
        """

        provider = provider_class()

        self._provider_classes[provider.name] = provider_class

    def get(
        self,
        provider_name: str,
    ) -> AIProvider:
        """
        Return a singleton provider instance.
        """

        provider_name = provider_name.lower()

        if provider_name not in self._provider_classes:
            raise ValueError(
                f"Unknown AI provider '{provider_name}'. "
                f"Available providers: "
                f"{', '.join(sorted(self.names()))}"
            )

        if provider_name not in self._provider_instances:
            provider_class = self._provider_classes[
                provider_name
            ]
            self._provider_instances[
                provider_name
            ] = provider_class()

        return self._provider_instances[
            provider_name
        ]

    def names(self) -> list[str]:
        """
        Return registered provider names.
        """

        return sorted(self._provider_classes.keys())


registry = ProviderRegistry()

registry.register(SimulatedProvider)
registry.register(OpenAIProvider)
registry.register(GeminiProvider)


# ======================================================================
# END: PROVIDER_REGISTRY (PATCH 1 OF 1)
# ======================================================================