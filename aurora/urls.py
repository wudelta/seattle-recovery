# aurora/urls.py
from django.urls import path
from . import views

# THE SEEDING FIX: Explicitly declares the app identity boundary for Django's parser
app_name = 'aurora'

urlpatterns = [
    # 1. ROOT VIEW: Typing '/aurora/' MUST hit the clean visual matrix landing page node
    path('', views.aurora_landing, name='landing'),
    
    # 2. CONSOLE DASHBOARD: Typing '/aurora/dashboard/' targets the terminal control panel view
    path('dashboard/', views.console_dashboard, name='aurora_dashboard'),
    
    # 3. CHAT PIPELINES
    path('api/', views.chat_api, name='chat_api'),
    path('api/v1/stream/', views.wu_data_stream, name='wu_data_stream'),
    path('api/session/start/', views.start_online_session, name='start_online_session'),
    
    # 4. OPERATIONAL CHANNELS
    path('process/', views.wu_director, name='wu_director'),
    path('end_session/', views.end_session_view, name='end_session'),
    path('manual_log/', views.manual_time_log_view, name='manual_log'),
    path('commit_file/', views.commit_file_view, name='aurora_commit_file'),
    path('daily_brief/', views.daily_brief_view, name='aurora_daily_brief'),
    path('api/notes/create/', views.create_delta_note_api, name='create_delta_note'),
    path('add_note/', views.add_note_view, name='add_note'),
]
