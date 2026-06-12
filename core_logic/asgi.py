# ======================================================================
# FILE: core_logic/asgi.py (PATCH 1 OF 1)
# START: PROTOCOL ASYNC GATEWAY ROUTER
# ======================================================================
import os
import django # <-- ADDED: Explicit core initialization engine
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core_logic.settings")

# 1. CRITICAL: Force Django to fully bootstrap configurations inside memory scope
django.setup() # <-- ADDED: Safely boots channel layers before Daphne opens sockets

# 2. Initialize core HTTP ASGI application first
django_asgi_app = get_asgi_application()

# 3. Wrap it so Daphne handles local CSS/JS styling files automatically
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
django_static_asgi_app = ASGIStaticFilesHandler(django_asgi_app)

# 4. SAFE IMPORT: Now that the registry is fully populated, we can pull app paths
import aurora.routing
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

application = ProtocolTypeRouter({
    "http": django_static_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            aurora.routing.websocket_urlpatterns
        )
    ),
})
# ======================================================================
# END: PROTOCOL ASYNC GATEWAY ROUTER
# ======================================================================
