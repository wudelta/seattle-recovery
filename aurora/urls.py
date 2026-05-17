# FILE: aurora/urls.py
"""
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T20:22:45.293161+00:00
 PROJECT ECOSYSTEM: AURORA
 FILE PATH: aurora/urls.py
 TECHNICAL MATRIX: Python Module. Exported Logic Components: 

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[urls.py] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[AURORA]
 ```
"""
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
    path('commit_file/', views.commit_file_view, name='aurora_commit_file'),
]