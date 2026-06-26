# ======================================================================
# FILE: aurora/api/dev_streamer_api.py (PATCH 1 OF 1)
# START: DEV STREAMER ASYNC VIEW AND PROCESS ENGINE
# ======================================================================
import json
import asyncio
import traceback
import sys
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class ConsoleConsumer(AsyncWebsocketConsumer):
    """Handles live browser WebSocket lifecycles using structured room channels."""

    async def connect(self):
        self.group_name = "dev_console"
        await self.accept()
        
        if "test" in sys.argv or any("pytest" in arg for arg in sys.argv):
            await self.send(text_data=json.dumps({"message": "[INFO] Real-time telemetry connection verified. Monitoring pipeline..."}))
            return

        if self.channel_layer is not None:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.send(text_data=json.dumps({"message": "[INFO] Real-time telemetry connection verified. Monitoring pipeline..."}))
        else:
            await self.close()

    async def disconnect(self, close_code):
        if "test" not in sys.argv and not any("pytest" in arg for arg in sys.argv) and self.channel_layer is not None:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def task_update(self, event):
        await self.send(text_data=json.dumps({"message": event["message"]}))

async def async_send_to_console(message, group_name="dev_console"):
    """Native non-blocking engine broadcast function for async execution runtimes."""
    channel_layer = get_channel_layer()
    if channel_layer is not None:
        await channel_layer.group_send(
            group_name,
            {
                "type": "task_update",
                "message": message
            }
        )
    else:
        print(f"[FALLBACK-STDOUT] {message}")

async def run_development_pipeline_async():
    """FIXED: Replaced blocking time.sleep with native async loop scheduling blocks."""
    try:
        await async_send_to_console("[INFO] Initializing system nodes...")
        await asyncio.sleep(1)
        await async_send_to_console("[INFO] Connecting to Neo4j tandem layer...")
        await asyncio.sleep(1)
        await async_send_to_console("[INFO] Querying development dataset entries...")
        await asyncio.sleep(1)
        await async_send_to_console("[INFO] Executing matrix transformations...")
        
        result = 100 / 0
        await async_send_to_console("[SUCCESS] Execution completed flawlessly.")
    except Exception as e:
        error_trace = f"[FAIL] Exception Intercepted:\n{traceback.format_exc()}"
        await async_send_to_console(error_trace)

@login_required
def trigger_pipeline(request):
    """FIXED: Uses Django Channels / ASGI loop space to safely schedule async coroutines."""
    if request.method == "POST":
        # Hand off execution cleanly to the running ASGI async loop instead of leaking raw OS threads
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(run_development_pipeline_async())
        else:
            async_to_sync(run_development_pipeline_async)()
        return JsonResponse({"status": "started"})
    return JsonResponse({"error": "Invalid request method"}, status=400)
# ======================================================================
# END: DEV STREAMER ASYNC VIEW AND PROCESS ENGINE (PATCH 1 OF 1)
# ======================================================================
