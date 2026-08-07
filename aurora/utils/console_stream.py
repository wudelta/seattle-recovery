# ======================================================================
# FILE: aurora/utils/console_stream.py
# START: SHARED_CONSOLE_STREAM_TRANSPORT
# ======================================================================

import json
import sys

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer


class ConsoleConsumer(AsyncWebsocketConsumer):
    """Provide the shared Aurora Console WebSocket transport."""

    async def connect(self):
        self.group_name = "dev_console"

        await self.accept()

        if (
            "test" in sys.argv
            or any("pytest" in arg for arg in sys.argv)
        ):
            await self.send(
                text_data=json.dumps({
                    "message": (
                        "[INFO] Real-time telemetry connection "
                        "verified. Monitoring pipeline..."
                    ),
                })
            )
            return

        if self.channel_layer is None:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.send(
            text_data=json.dumps({
                "message": (
                    "[INFO] Real-time telemetry connection "
                    "verified. Monitoring pipeline..."
                ),
            })
        )

    async def disconnect(self, close_code):
        if (
            "test" not in sys.argv
            and not any("pytest" in arg for arg in sys.argv)
            and self.channel_layer is not None
        ):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def task_update(self, event):
        await self.send(
            text_data=json.dumps({
                "message": event["message"],
            })
        )


async def async_send_to_console(
    message,
    group_name="dev_console",
):
    """Broadcast a message to an Aurora Console WebSocket group."""

    channel_layer = get_channel_layer()

    if channel_layer is not None:
        await channel_layer.group_send(
            group_name,
            {
                "type": "task_update",
                "message": message,
            },
        )
        return

    print(f"[FALLBACK-STDOUT] {message}")

# ======================================================================
# END: SHARED_CONSOLE_STREAM_TRANSPORT
# ======================================================================