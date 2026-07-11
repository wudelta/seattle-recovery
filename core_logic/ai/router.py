# ======================================================================
# FILE: core_logic/ai/router.py (PATCH 1 OF 1)
# START: PROVIDER_ROUTER
# ======================================================================

from core_logic.ai.registry import registry
from core_logic.settings import AI_PROVIDER


class ProviderRouter:
    """
    Centralized AI provider routing.

    The router owns provider selection and, eventually:

      • model resolution
      • retry policy
      • failover
      • cost-aware routing
      • quota enforcement

    Provider implementations remain focused solely on translating
    between Aurora's provider interface and vendor SDKs.
    """

    _MODEL_MAP = {
        "openai": {
            "small": "gpt-5.6-luna",
            "medium": "gpt-5.6-terra",
            "large": "gpt-5.6-sol",
        },
        "gemini": {
            "small": "gemini-2.5-flash-lite",
            "medium": "gemini-2.5-flash",
            "large": "gemini-2.5-pro",
        },
    }

    def get_provider(
        self,
        provider_name: str | None,
    ):
        """
        Resolve the requested provider.

        Explicit provider requests take precedence. Otherwise, use the
        configured default provider.
        """

        provider_name = (
            provider_name or AI_PROVIDER
        ).lower()

        return registry.get(provider_name)

    def resolve_model(
        self,
        provider_name: str,
        constraints: dict | None,
        default_model: str,
    ) -> str:
        """
        Resolve a provider-independent model profile into a concrete
        provider model.

        If no model_profile is supplied, preserve the existing baseline
        behavior by honoring an explicit model value before falling back
        to the provider default.
        """

        constraints = constraints or {}

        profile = constraints.get("model_profile")
        if profile:
            return self._MODEL_MAP.get(
                provider_name,
                {},
            ).get(
                profile.lower(),
                default_model,
            )

        return constraints.get(
            "model",
            default_model,
        )


provider_router = ProviderRouter()

# ======================================================================
# END: PROVIDER_ROUTER (PATCH 1 OF 1)
# ======================================================================