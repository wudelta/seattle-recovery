# ======================================================================
# FILE: core_logic/urls_aurora.py (PATCH 1 OF 1)
# START: ISO_AURORA_ROUTING_MATRIX
# ======================================================================
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('aurora/', include('aurora.urls', namespace='aurora')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ======================================================================
# END: ISO_AURORA_ROUTING_MATRIX (PATCH 1 OF 1)
# ======================================================================
