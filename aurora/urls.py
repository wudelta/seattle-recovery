# FILE: aurora/urls.py
"""
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T21:12:26.697206+00:00
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
from . import views

app_name = 'aurora' 

urlpatterns = [
    path('', views.aurora_landing, name='landing'), 
    path('process/', views.wu_director, name='wu_director'),
    path('dashboard/', views.console_dashboard, name='aurora_dashboard'),
    path('save_brief/', views.save_daily_brief, name='save_daily_brief'),
    path('api/', views.chat_api, name='chat_api'),
    path('end_session/', views.end_session_view, name='end_session'), 
    path('manual_log/', views.manual_time_log_view, name='manual_log'),
    path('commit_file/', views.commit_file_view, name='aurora_commit_file'),
    path('api/session/start/', views.start_online_session, name='start_online_session'),
]
