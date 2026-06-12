# ======================================================================
# FILE: aurora/api/dev_streamer_api.py (PATCH 1 OF 1)
# START: DEV STREAMER THREADED VIEW AND PROCESS ENGINE
# ======================================================================
import time
import threading
import traceback
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class ConsoleConsumer(AsyncWebsocketConsumer):
    """
    Handles live browser WebSocket lifecycles with strict NoneType channel guards
    to prevent dynamic AJAX template reloads from crashing the Daphne process.
    """
    async def connect(self):
        self.group_name = "dev_console"
        if self.channel_layer is not None:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            # Reject the connection cleanly if the memory registry layer isn't reachable
            await self.close()

    async def disconnect(self, close_code):
        if self.channel_layer is not None:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def task_update(self, event):
        # Receives the broadcast event group packet and forces transmission to the UI
        await self.send(text_data=json.dumps({"message": event["message"]}))

def send_to_console(message):
    """
    Broadcasts a string line directly to the dev_console WebSocket group.
    Falls back gracefully to standard stdout printing if the channel layer
    is temporarily unreachable in memory.
    """
    try:
        channel_layer = get_channel_layer()
        if channel_layer is not None:
            async_to_sync(channel_layer.group_send)(
                "dev_console", 
                {
                    "type": "task_update", 
                    "message": message
                }
            )
        else:
            print(f"[FALLBACK-STDOUT] {message}")
    except Exception as e:
        print(f"[CHANNEL-ERROR] Failed to stream: {e}. Message: {message}")

def run_development_pipeline():
    """
    Long-running execution module pipeline. Wrap your core logic steps 
    here to stream state checkpoints and tracebacks directly to the web.
    """
    try:
        send_to_console("[INFO] Initializing system nodes...")
        time.sleep(1)  # Simulate target processing work
        
        send_to_console("[INFO] Connecting to Neo4j tandem layer...")
        time.sleep(1)
        
        send_to_console("[INFO] Querying development dataset entries...")
        time.sleep(1)
        
        send_to_console("[INFO] Executing matrix transformations...")
        # Simulating a math / runtime crash for interface verification
        result = 100 / 0
        
        send_to_console("[SUCCESS] Execution completed flawlessly.")
        
    except Exception as e:
        # Pushes terminal format crashes straight to your browser layout
        error_trace = f"[FAIL] Exception Intercepted:\n{traceback.format_exc()}"
        send_to_console(error_trace)

@login_required
def trigger_pipeline(request):
    """
    API endpoint that receives the AJAX POST call and launches the module 
    inside an isolated background thread to keep your UI alive.
    """
    if request.method == "POST":
        task_thread = threading.Thread(target=run_development_pipeline)
        task_thread.start()
        return JsonResponse({"status": "started"})
        
    return JsonResponse({"error": "Invalid request method"}, status=400)
# ======================================================================
# END: DEV STREAMER THREADED VIEW AND PROCESS ENGINE
# ======================================================================
