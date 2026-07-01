# ======================================================================
# FILE: core_logic/urls.py (PATCH 1 OF 1)
# START: GLOBAL ROUTING DISPATCH MATRIX ENTRIES
# ======================================================================
import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Baseline global infrastructure pathways
urlpatterns = [
    path('admin/', admin.site.urls),
]

# Identify which container network node is booting up
CURRENT_CONTAINER_TARGET = os.getenv('DB_NAME')

if CURRENT_CONTAINER_TARGET == 'aurora_db':
    # Only load the builder url definitions on the Aurora container node
    urlpatterns.append(path('aurora/', include('aurora.urls', namespace='aurora')))

elif CURRENT_CONTAINER_TARGET == 'hopehub_db':
    # Only load the application url definitions on the Hopehub container node
    urlpatterns.append(path('hopehub/', include('hopehub.urls', namespace='hopehub')))

else:
    # Fallback pathing safety matrix for local terminal shell calls
    urlpatterns.append(path('hopehub/', include('hopehub.urls', namespace='hopehub')))
    urlpatterns.append(path('aurora/', include('aurora.urls', namespace='aurora')))

# Append media tracking using inline addition. Linters love this syntax.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ======================================================================
# END: GLOBAL ROUTING DISPATCH MATRIX ENTRIES
# ======================================================================
