# ======================================================================
# FILE: aurora/routing.py (PATCH 1 OF 1)
# START: WEBSOCKET URL MAPPER
# ======================================================================
from django.urls import re_path
from aurora.api import dev_streamer_api

websocket_urlpatterns = [
    # Binds incoming browser socket handshakes straight to your api consumer module
    re_path(r"ws/console/$", dev_streamer_api.ConsoleConsumer.as_asgi()),
]
# ======================================================================
# END: WEBSOCKET URL MAPPER
# ======================================================================
