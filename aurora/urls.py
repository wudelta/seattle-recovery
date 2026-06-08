# ======================================================================
# FILE: aurora/urls.py (PATCH 1 OF 1)
# START: SYSTEM DISPATCH ROUTING MATRIX & LOGIN ENTRIES
# ======================================================================
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from aurora import api as api_commands  # Renamed package alias to match architectural standard

app_name = 'aurora'

urlpatterns = [
    # 1. ROOT VIEW: Typing '/aurora/' MUST hit the clean visual matrix landing page node
    path('', views.aurora_landing, name='landing'),
    
    # 2. THE COCKPIT: Your primary working environment that replaces Spyder tools
    path('console/', views.ConsoleView.as_view(), name='console'),
    
    # 3. AI PIPELINES: Background endpoints handling asynchronous communication with Wu
    path('api/command/', api_commands.execute_blueprint_api, name='api_command'),
    
    # 6. DJANGO AUTH URLS
    path('login/', auth_views.LoginView.as_view(
        template_name='aurora/login.html',
        success_url='/aurora/'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='aurora:landing'), name='logout'),
    
    path('delta_notes/', views.DeltaNotesView.as_view(), name='delta_notes'),
    path('api/delta_notes/', api_commands.delta_notes_endpoint, name='delta_notes_endpoint'),
]
# ======================================================================
# END: SYSTEM DISPATCH ROUTING MATRIX & LOGIN ENTRIES
# ======================================================================
