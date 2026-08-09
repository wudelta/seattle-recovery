# ======================================================================
# FILE: aurora/routing.py (PATCH 1 OF 1)
# START: WEBSOCKET_URL_MAPPER
# ======================================================================

from django.urls import re_path

from aurora.utils.telemetry_stream import ConsoleConsumer


websocket_urlpatterns = [
    re_path(
        r"ws/console/$",
        ConsoleConsumer.as_asgi(),
    ),
]

# ======================================================================
# END: WEBSOCKET_URL_MAPPER
# ======================================================================