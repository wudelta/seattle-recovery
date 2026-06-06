# ======================================================================
# FILE: core_logic/urls.py (PATCH 1 OF 1)
# START: GLOBAL ROUTING DISPATCH MATRIX ENTRIES
# ======================================================================
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hopehub/', include('hopehub.urls', namespace='hopehub')),
    path('aurora/', include('aurora.urls', namespace='aurora')),
]

# Append media tracking using inline addition. Linters love this syntax.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ======================================================================
# END: GLOBAL ROUTING DISPATCH MATRIX ENTRIES
# ======================================================================
