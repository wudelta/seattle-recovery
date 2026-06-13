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
import aurora.routing

# 4. Wrap HTTP endpoints inside the development asset styling serve handler
django_static_asgi_app = ASGIStaticFilesHandler(django_asgi_app)

# 5. Lock in the unified protocol routing gateway table
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
