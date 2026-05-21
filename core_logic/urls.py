from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('aurora/', include('aurora.urls', namespace='aurora')),
    path('hopehub/', include('hopehub.urls', namespace='hopehub')),
    #path('documents/', aurora_views.DocumentView.as_view()),
    #path('metadata/', aurora_views.MetadataView.as_view()),
    #path('content/', aurora_views.ContentView.as_view()),
]