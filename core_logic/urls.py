from django.contrib import admin
from django.urls import path, include
from aurora import views  # Import the views module
from hopehub import views as interface_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', interface_views.index, name='index'),
    path('documents/', views.DocumentView.as_view()),
    path('metadata/', views.MetadataView.as_view()),
    path('content/', views.ContentView.as_view()),
    path('aurora/', include('aurora.urls', namespace='aurora')),    
]
