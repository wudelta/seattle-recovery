# aurora/urls.py
from django.urls import path
from . import views  # Just one import!

urlpatterns = [
    # We use views.<function_name> to keep it clean
    path('process/', views.wu_director, name='wu_director'),
    path('', views.dashboard, name='aurora_dashboard'),
    path('api/', views.chat_api, name='chat_api'),
    path('end_session/', views.end_session_view, name='end_session'),  # Registered
    path('manual_log/', views.manual_time_log_view, name='manual_log'),
]
