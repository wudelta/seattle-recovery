# ======================================================================
# FILE: core_logic/urls_hopehub.py (PATCH 1 OF 1)
# START: ISO_HOPEHUB_ROUTING_MATRIX
# ======================================================================
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hopehub/', include('hopehub.urls', namespace='hopehub')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ======================================================================
# END: ISO_HOPEHUB_ROUTING_MATRIX (PATCH 1 OF 1)
# ======================================================================
