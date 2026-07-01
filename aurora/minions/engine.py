# ====================================================================== #
# FILE: aurora/minions/engine.py (PATCH 1 OF 1)                          #
# START: ASYNC_STREAMING_GEMINI_FLEET_ENGINE                             #
# ====================================================================== #
import os
import sys
import asyncio
from django.conf import settings
from google import genai
from google.genai import types
from google.genai.errors import APIError
from aurora.models import DeltaDirectives
from asgiref.sync import async_to_sync

class MinionRunner:
    """Universal Cloud-Driven AI Execution Engine built on the official modern Google GenAI SDK."""
    
    def __init__(self):
        # Extract token from Django settings or fallback straight to host environment maps
        self.api_key = getattr(settings, "GEMINI_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
        
        # Initialize tracking variables to update web user interface metrics gauges
        self.last_tokens_consumed = 0
        self.last_rpm_remaining = 14

        # Initialize the official SDK client
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = genai.Client()

    async def query_gemini_llm_stream(self, model_tag: str, system_directive: str, user_prompt: str, temperature: float = 0.3):
        """
        Asynchronously streams completion tokens natively from the Google Cloud models, 
        calculating metrics from chunks without overloading local system threads.
        """
        # Remap legacy Groq models out to efficient, cloud-hosted Gemini equivalents
        if "llama" in model_tag.lower():
            model_tag = "gemini-2.5-flash"

        sys.stdout.write(f"📡 [ENGINE] Initializing official Async Gemini transaction stream using: {model_tag}\n")
        sys.stdout.flush()

        # Build clean configuration entities wrapping instructions to point to the cloud provider
        config = types.GenerateContentConfig(
            system_instruction=system_directive,
            temperature=temperature,
        )

        try:
            # FIXED: Explicitly await the stream creation coroutine object before iterating chunks
            response_stream = await self.client.aio.models.generate_content_stream(
                model=model_tag,
                contents=user_prompt,
                config=config
            )

            # Process the active, initialized stream iterator smoothly
            async for response_chunk in response_stream:
                # Update usage tracking records dynamically if returned within chunk objects
                if hasattr(response_chunk, 'usage_metadata') and response_chunk.usage_metadata:
                    self.last_tokens_consumed = response_chunk.usage_metadata.total_token_count

                # Yield structural token chunks out to the calling async consumer stream loop
                if response_chunk.text:
                    yield response_chunk.text

            # Decrement local tracking RPM meter down safely to drive frontend fuel meters
            self.last_rpm_remaining = max(1, self.last_rpm_remaining - 1)

        except APIError as api_err:
            yield f"\n🛑 [GEMINI GATEWAY REJECTION] The Cloud SDK caught an operational API error!\nDETAILS: {str(api_err)}\n"
            return
        except Exception as system_err:
            yield f"\n💥 [ENGINE FAULT] Unexpected local exception caught during execution: {str(system_err)}\n"
            return

    async def run_minion_task_stream(self, minion_name: str, task_input: str):
        """Loads operational presets asynchronously out of database rows and yields the SDK stream."""
        from asgiref.sync import sync_to_async
        try:
            directive = await sync_to_async(DeltaDirectives.objects.get)(directive_name=minion_name, is_active=True)
        except DeltaDirectives.DoesNotExist:
            yield f"💥 [REGISTRY ERROR]: Minion configuration '{minion_name}' is missing or inactive in your database!"
            return

        model_tag = directive.constraints.get("model", "gemini-2.5-flash")
        temperature = directive.constraints.get("temperature", 0.3)
        system_instructions = directive.instructions

        async for token in self.query_gemini_llm_stream(
            model_tag=model_tag,
            system_directive=system_instructions,
            user_prompt=task_input,
            temperature=temperature
        ):
            yield token

    def run_minion_task(self, minion_name: str, task_input: str) -> str:
        """
        Synchronous interface wrapper for pytest execution blocks and legacy code blocks. 
        Stitches tokens from the async stream into a completed output string.
        """
        async def _gather_stream_tokens():
            tokens = []
            async for token in self.run_minion_task_stream(minion_name, task_input):
                tokens.append(token)
            return "".join(tokens)
        return async_to_sync(_gather_stream_tokens)()
# ====================================================================== #
# END: ASYNC_STREAMING_GEMINI_FLEET_ENGINE (PATCH 1 OF 1)               #
# ====================================================================== #
