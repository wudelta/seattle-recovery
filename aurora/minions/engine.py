# ======================================================================
# FILE: aurora/minions/engine.py (PATCH 1 OF 1)
# START: PROVIDER_ROUTED_MINION_EXECUTION_ENGINE
# ======================================================================

import os
import time

from asgiref.sync import async_to_sync, sync_to_async
from django.conf import settings

from aurora.models import DeltaDirectives
from core_logic.ai.router import provider_router


class MinionRunner:
    """
    Universal AI execution engine.

    All model execution is delegated through the shared ProviderRouter.
    Provider-specific behavior belongs exclusively to provider classes.
    """

    def __init__(self):
        self.last_provider_name = None
        self.last_model_name = None
        self.last_input_tokens = 0
        self.last_output_tokens = 0
        self.last_tokens_consumed = 0
        self.last_latency_ms = 0
        self.last_provider_error = None
        self.last_rpm_remaining = 14
        self._provider_router = provider_router

    def _resolve_provider(self, directive):
        """
        Resolve the active provider.

        Resolution order:

        1. Directive constraints
        2. Environment configuration
        3. Django settings
        4. Simulated provider fallback
        """

        constraints = directive.constraints or {}

        provider_name = (
            constraints.get("provider")
            or os.getenv("AI_PROVIDER")
            or getattr(settings, "AI_PROVIDER", None)
            or "simulated"
        )

        return self._provider_router.get_provider(provider_name)

    async def query_provider_stream(
        self,
        directive: DeltaDirectives,
        user_prompt: str,
    ):
        """Stream output from the selected AI provider."""

        provider = self._resolve_provider(directive)
        constraints = directive.constraints or {}

        model = self._provider_router.resolve_model(
            provider_name=provider.name,
            constraints=constraints,
            default_model=getattr(
                settings,
                f"{provider.name.upper()}_MODEL",
            ),
        )

        self.last_provider_name = provider.name
        self.last_model_name = model
        self.last_input_tokens = 0
        self.last_output_tokens = 0
        self.last_tokens_consumed = 0
        self.last_provider_error = None

        started_at = time.perf_counter()

        try:
            async for response_chunk in provider.stream(
                model=model,
                prompt=user_prompt,
                directive=directive,
            ):
                if isinstance(response_chunk, str):
                    yield response_chunk
                    continue

                usage = getattr(response_chunk, "usage", None)

                if isinstance(usage, dict):
                    self.last_input_tokens = usage.get(
                        "input_tokens",
                        0,
                    )
                    self.last_output_tokens = usage.get(
                        "output_tokens",
                        0,
                    )
                    self.last_tokens_consumed = usage.get(
                        "total_tokens",
                        (
                            self.last_input_tokens
                            + self.last_output_tokens
                        ),
                    )

            self.last_rpm_remaining = max(
                1,
                self.last_rpm_remaining - 1,
            )

        except Exception as exc:
            self.last_provider_error = (
                f"{type(exc).__name__}: {exc}"
            )
            yield (
                "\n"
                f"💥 [AI PROVIDER ERROR] "
                f"{self.last_provider_error}\n"
            )

        finally:
            self.last_latency_ms = round(
                (time.perf_counter() - started_at) * 1000,
                2,
            )

    async def run_minion_task_stream(
        self,
        minion_name: str,
        task_input: str,
    ):
        """Load a directive and execute through the provider layer."""

        try:
            directive = await sync_to_async(
                DeltaDirectives.objects.get
            )(
                directive_name=minion_name,
                is_active=True,
            )

        except DeltaDirectives.DoesNotExist:
            yield (
                f"💥 [REGISTRY ERROR]: "
                f"Minion configuration "
                f"'{minion_name}' "
                f"is missing or inactive."
            )
            return

        async for token in self.query_provider_stream(
            directive=directive,
            user_prompt=task_input,
        ):
            yield token

    def run_minion_task(
        self,
        minion_name: str,
        task_input: str,
    ) -> str:
        """Synchronous compatibility wrapper."""

        async def _gather_stream_tokens():
            tokens = []

            async for token in self.run_minion_task_stream(
                minion_name=minion_name,
                task_input=task_input,
            ):
                tokens.append(token)

            return "".join(tokens)

        return async_to_sync(
            _gather_stream_tokens
        )()

# ======================================================================
# END: PROVIDER_ROUTED_MINION_EXECUTION_ENGINE (PATCH 1 OF 1)
# ======================================================================