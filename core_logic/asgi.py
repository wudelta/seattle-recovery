# ======================================================================
# FILE: core_logic/asgi.py (PATCH 1 OF 1)
# START: PROTOCOL ASYNC GATEWAY ROUTER
# ======================================================================
import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core_logic.settings")

# 1. Boot up Django app configurations completely first
django.setup()

# 2. Extract the core ASGI applications
django_asgi_app = get_asgi_application()

# 3. Import channels infrastructure safely now that the registry is ready
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from django.conf import settings

# 4. Wrap HTTP endpoints inside the development asset styling serve handler
django_static_asgi_app = ASGIStaticFilesHandler(django_asgi_app)

# 5. Dynamically isolate WebSocket routing tables based on active configurations
websocket_routes = []

if 'aurora' in settings.INSTALLED_APPS:
    import aurora.routing
    websocket_routes = aurora.routing.websocket_urlpatterns
elif 'hopehub' in settings.INSTALLED_APPS:
    try:
        import hopehub.routing
        websocket_routes = hopehub.routing.websocket_urlpatterns
    except ImportError:
        pass  # Gracefully fall back if Hopehub has no custom sockets yet

# 6. Lock in the unified protocol routing gateway table
application = ProtocolTypeRouter({
    "http": django_static_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_routes
        )
    ),
})
# ======================================================================
# END: PROTOCOL ASYNC GATEWAY ROUTER
# ======================================================================
