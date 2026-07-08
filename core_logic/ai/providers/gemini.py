# ======================================================================
# FILE: core_logic/ai/providers/gemini.py (PATCH 1 OF 1)
# START: GEMINI_PROVIDER_IMPLEMENTATION
# ======================================================================

from django.conf import settings
from google import genai
from google.genai import types

from core_logic.ai.base import AIProvider, AIResponse


class GeminiProvider(AIProvider):
    """
    Provider implementation for Google Gemini.

    This class is responsible only for translating between Aurora's
    provider interface and the Gemini SDK.
    """

    @property
    def name(self) -> str:
        return "gemini"

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
        )

    def chat(
        self,
        prompt: str,
        directive,
    ) -> AIResponse:

        constraints = directive.constraints or {}

        model = constraints.get(
            "model",
            getattr(
                settings,
                "GEMINI_MODEL",
                "gemini-2.5-flash",
            ),
        )

        config = types.GenerateContentConfig(
            system_instruction=directive.instructions,
            temperature=constraints.get(
                "temperature",
                0.2,
            ),
        )

        response_format = constraints.get(
            "response_format",
        )

        if response_format == "json":
            config.response_mime_type = (
                "application/json"
            )

        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )

        return AIResponse(
            text=response.text,
            provider=self.name,
            model=model,
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
        Temporary streaming implementation.

        Until native Gemini streaming is integrated, this method
        delegates to chat() and yields a single normalized response.
        """

        response = self.chat(
            prompt=prompt,
            directive=directive,
        )

        yield response


# ======================================================================
# END: GEMINI_PROVIDER_IMPLEMENTATION (PATCH 1 OF 1)
# ======================================================================