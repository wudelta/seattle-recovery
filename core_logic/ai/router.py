# ======================================================================
# FILE: core_logic/ai/router.py (PATCH 1 OF 1)
# START: PROVIDER_ROUTER
# ======================================================================

from core_logic.ai.registry import registry


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

    def get_provider(
        self,
        provider_name: str | None,
    ):
        """
        Resolve the requested provider.

        For the baseline implementation this is a direct lookup in the
        provider registry. Future revisions will centralize routing,
        model resolution, retry, and failover here.
        """

        provider_name = (
            provider_name or "simulated"
        ).lower()

        return registry.get(provider_name)


provider_router = ProviderRouter()


# ======================================================================
# END: PROVIDER_ROUTER (PATCH 1 OF 1)
# ======================================================================