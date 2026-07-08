# ======================================================================
# FILE: core_logic/ai/providers/openai.py (PATCH 1 OF 1)
# START: OPENAI_PROVIDER_IMPLEMENTATION
# ======================================================================

from openai import OpenAI
from django.conf import settings

from core_logic.ai.base import AIProvider, AIResponse


class OpenAIProvider(AIProvider):
    """
    Provider implementation for the OpenAI Responses API.

    This class is responsible only for translating between Aurora's
    provider interface and the OpenAI SDK.
    """

    @property
    def name(self) -> str:
        return "openai"

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
        )

    def _normalize_usage(self, usage):
        """
        Normalize SDK-specific usage objects into Aurora's
        standard usage dictionary.
        """

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

    def chat(
        self,
        prompt: str,
        directive,
    ) -> AIResponse:

        constraints = directive.constraints or {}

        model = constraints.get(
            "model",
            getattr(settings, "OPENAI_MODEL", "gpt-5.5"),
        )

        response = self.client.responses.create(
            model=model,
            instructions=directive.instructions,
            input=prompt,
            temperature=constraints.get(
                "temperature",
                0.2,
            ),
            max_output_tokens=constraints.get(
                "max_output_tokens",
            ),
        )

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
        prompt: str,
        directive,
    ):
        """
        Stream response fragments while preserving a normalized
        final AIResponse.
        """

        constraints = directive.constraints or {}

        model = constraints.get(
            "model",
            getattr(settings, "OPENAI_MODEL", "gpt-5.5"),
        )

        stream = self.client.responses.create(
            model=model,
            instructions=directive.instructions,
            input=prompt,
            temperature=constraints.get(
                "temperature",
                0.2,
            ),
            max_output_tokens=constraints.get(
                "max_output_tokens",
            ),
            stream=True,
        )

        accumulated = ""
        usage = None

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