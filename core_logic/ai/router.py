# ======================================================================
# FILE: core_logic/ai/router.py (PATCH 1 OF 1)
# START: PROVIDER_ROUTER
# ======================================================================

from core_logic.ai.exceptions import (
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from core_logic.ai.registry import registry
from core_logic.settings import AI_PROVIDER


class ProviderRouter:
    """
    Centralized AI provider routing.

    The router owns provider selection, model resolution, execution
    deadlines, and provider failover policy.

    Provider implementations remain responsible only for translating
    Aurora requests and normalized failures to and from vendor SDKs.
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
        "simulated": {
            "small": "simulated",
            "medium": "simulated",
            "large": "simulated",
        },
    }

    _TRANSIENT_FAILURES = (
        ProviderUnavailableError,
        ProviderTimeoutError,
        ProviderRateLimitError,
    )

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

    def _provider_candidates(
        self,
        provider_name: str | None,
    ) -> list[str]:
        """
        Return the ordered provider execution candidates.

        Simulated execution is intentionally isolated from production
        failover. Production providers may fail over to one another once.
        """

        primary_name = (
            provider_name or AI_PROVIDER
        ).lower()

        if primary_name == "simulated":
            return [primary_name]

        candidates = [primary_name]

        for fallback_name in ("openai", "gemini"):
            if fallback_name != primary_name:
                candidates.append(fallback_name)

        return candidates

    def _resolve_candidate_model(
        self,
        provider_name: str,
        primary_name: str,
        constraints: dict,
    ) -> str:
        """
        Resolve a valid model for the current provider candidate.

        A provider-specific explicit model is honored only by the primary
        provider. Failover uses the equivalent model profile, or the
        candidate provider's medium model when no profile was supplied.
        """

        default_model = self._MODEL_MAP[
            provider_name
        ]["medium"]

        if provider_name == primary_name:
            return self.resolve_model(
                provider_name=provider_name,
                constraints=constraints,
                default_model=default_model,
            )

        fallback_constraints = {
            "model_profile": constraints.get(
                "model_profile",
                "medium",
            ),
        }

        return self.resolve_model(
            provider_name=provider_name,
            constraints=fallback_constraints,
            default_model=default_model,
        )

    def chat(
        self,
        *,
        prompt: str,
        directive,
        provider_name: str | None = None,
        timeout_seconds: float | None = None,
    ):
        """
        Execute a synchronous request with centralized failover.

        Only normalized transient provider failures permit failover.
        Network, authentication, configuration, request, and unexpected
        execution failures propagate immediately.
        """

        constraints = directive.constraints or {}
        candidates = self._provider_candidates(
            provider_name,
        )
        primary_name = candidates[0]

        for candidate_index, candidate_name in enumerate(
            candidates
        ):
            provider = self.get_provider(
                candidate_name,
            )
            model = self._resolve_candidate_model(
                provider_name=candidate_name,
                primary_name=primary_name,
                constraints=constraints,
            )

            try:
                response = provider.chat(
                    model=model,
                    prompt=prompt,
                    directive=directive,
                    timeout_seconds=timeout_seconds,
                )
            except self._TRANSIENT_FAILURES:
                if candidate_index == len(candidates) - 1:
                    raise

                continue

            if candidate_name != primary_name:
                response.metadata.update({
                    "failover": True,
                    "failover_from": primary_name,
                    "failover_to": candidate_name,
                })

            return response

        raise RuntimeError(
            "Provider routing completed without a response."
        )

    async def stream(
        self,
        *,
        prompt: str,
        directive,
        provider_name: str | None = None,
        timeout_seconds: float | None = None,
    ):
        """
        Stream a request with centralized failover.

        Failover is safe only before a provider has emitted output. Once
        output begins, any later failure propagates to avoid combining
        content from multiple providers in one response.
        """

        constraints = directive.constraints or {}
        candidates = self._provider_candidates(
            provider_name,
        )
        primary_name = candidates[0]

        for candidate_index, candidate_name in enumerate(
            candidates
        ):
            provider = self.get_provider(
                candidate_name,
            )
            model = self._resolve_candidate_model(
                provider_name=candidate_name,
                primary_name=primary_name,
                constraints=constraints,
            )
            emitted_output = False

            try:
                async for item in provider.stream(
                    model=model,
                    prompt=prompt,
                    directive=directive,
                    timeout_seconds=timeout_seconds,
                ):
                    emitted_output = True

                    if (
                        candidate_name != primary_name
                        and hasattr(item, "metadata")
                    ):
                        item.metadata.update({
                            "failover": True,
                            "failover_from": primary_name,
                            "failover_to": candidate_name,
                        })

                    yield item

                return
            except self._TRANSIENT_FAILURES:
                if (
                    emitted_output
                    or candidate_index == len(candidates) - 1
                ):
                    raise

                continue


provider_router = ProviderRouter()

# ======================================================================
# END: PROVIDER_ROUTER (PATCH 1 OF 1)
# ======================================================================