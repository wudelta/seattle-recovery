from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), 
    path('aurora/', include('aurora.urls', namespace='aurora')),
    path('hopehub/', include('hopehub.urls', namespace='hopehub')),
    #path('documents/', aurora_views.DocumentView.as_view()),
    #path('metadata/', aurora_views.MetadataView.as_view()),
    #path('content/', aurora_views.ContentView.as_view()),
]

# Append media tracking using inline addition. Linters love this syntax.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
