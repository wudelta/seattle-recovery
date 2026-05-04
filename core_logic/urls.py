from django.contrib import admin
from django.urls import path
from delta_chat.views import dashboard, chat_api  # <--- MUST HAVE BOTH HERE

urlpatterns = [
    path('admin/', admin.site.urls),
    path('delta/', dashboard, name='delta_dashboard'),
    path('delta/api/', chat_api, name='chat_api'),
]