# ======================================================================
# FILE: aurora/minions/engine.py (PATCH 1 OF 1)
# START: ASYNC_STREAMING_GROQ_FLEET_ENGINE
# ======================================================================
import os
import sys
import asyncio
from django.conf import settings
from groq import AsyncGroq, GroqError
from aurora.models import DeltaDirectives
from asgiref.sync import async_to_sync

class MinionRunner:
    """Universal Cloud-Driven AI Execution Engine built on the official Groq SDK."""

    def __init__(self):
        # Extract token from Django settings or fallback straight to host environment maps
        self.api_key = getattr(settings, "GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")
        # Initialize the official SDK client asynchronously
        if self.api_key:
            self.client = AsyncGroq(api_key=self.api_key)
        else:
            # Fallback will let the SDK look for the environment variable automatically
            self.client = AsyncGroq()

    async def query_groq_llm_stream(self, model_tag: str, system_directive: str, user_prompt: str, temperature: float = 0.3):
        """
        Asynchronously streams completion tokens natively from the Groq SDK engine.
        Guarantees that any server rejections or validation faults bubble straight up to the UI.
        """
        sys.stdout.write(f"📡 [ENGINE] Initializing official AsyncGroq transaction stream using: {model_tag}\n")
        sys.stdout.flush()
        try:
            # Native SDK async stream completion loop configuration
            stream = await self.client.chat.completions.create(
                model=model_tag,
                messages=[
                    {"role": "system", "content": system_directive},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                stream=True
            )
            # FIX: Ensure streaming chunks are parsed via the choices list index format 
            # safely to align with actual Groq SDK real-time iterator models.
            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    token = chunk.choices[0].delta.content
                    if token:
                        yield token
        except GroqError as groq_err:
            # Surgically catch and print exact cloud API parameter or endpoint authentication faults
            yield f"\n🛑 [GROQ GATEWAY REJECTION] The SDK caught an operational error!\nDETAILS: {str(groq_err)}\n"
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

        model_tag = directive.constraints.get("model", "llama-3.3-70b-versatile")
        temperature = directive.constraints.get("temperature", 0.3)
        system_instructions = directive.instructions

        async for token in self.query_groq_llm_stream(
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
# ======================================================================
# END: ASYNC_STREAMING_GROQ_FLEET_ENGINE (PATCH 1 OF 1)
# ======================================================================
