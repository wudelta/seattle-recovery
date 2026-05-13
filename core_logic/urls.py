from django.contrib import admin
from django.urls import path, include
from delta_chat import views  # Import the views module
from interface import views as interface_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', interface_views.index, name='index'),
    path('documents/', views.DocumentView.as_view()),
    path('metadata/', views.MetadataView.as_view()),
    path('content/', views.ContentView.as_view()),
    path('delta/', include('delta_chat.urls')),
]
