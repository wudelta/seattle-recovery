# ======================================================================
# FILE: aurora/urls.py (PATCH 1 OF 1)
# START: SYSTEM DISPATCH ROUTING MATRIX & LOGIN ENTRIES
# ======================================================================
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from aurora import api as api_commands

app_name = 'aurora'

urlpatterns = [
    # 1. ROOT VIEW: Typing '/aurora/' MUST hit the clean visual matrix landing page node
    path('', views.aurora_landing, name='landing'),
    
    # 2. THE COCKPIT: Your primary working environment that replaces Spyder tools
    path('console/', views.ConsoleView.as_view(), name='console'),
    
    # NEW ENDPOINT: Route target pointing directly to your new dev_streamer_api module
    path('console/run/', api_commands.trigger_pipeline, name='trigger_pipeline'),
    
    # 3. AI PIPELINES: Background endpoints handling asynchronous communication with Wu
    path('api/command/', api_commands.execute_blueprint_api, name='api_command'),
    
    # FIXED: Direct standalone path for the unlocked components tracking matrix registry endpoint
    path('api/components/unlocked/', api_commands.unlocked_components_endpoint, name='unlocked_components_registry'),
    
    # 4. LIGHTWEIGHT EMBEDDED IDE & DOCKER SANDBOX ENDPOINTS
    path('api/files/tree/', views.file_tree_api, name='ide_file_tree'),
    path('api/files/op/', views.file_operation_api, name='ide_file_operations'),
    path('api/sandbox/run/', views.run_code_api, name='ide_sandbox_run'),
    path('api/sandbox/lint/', views.lint_code_api, name='ide_sandbox_lint'),
    
    # 6. DJANGO AUTH URLS
    path('login/', auth_views.LoginView.as_view(
        template_name='aurora/login.html',
        success_url='/aurora/'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='aurora:landing'), name='logout'),
    path('api/delta_notes/', api_commands.delta_notes_endpoint, name='delta_notes_endpoint'),
    path('api/content/', api_commands.content_endpoint, name='content_endpoint'),
    path('api/directives/', api_commands.directives_endpoint, name='directives_endpoint'),
    path('api/wu_chat/', api_commands.wu_chat_endpoint, name='wu_chat_endpoint'),
]
# ======================================================================
# END: SYSTEM DISPATCH ROUTING MATRIX & LOGIN ENTRIES (PATCH 1 OF 1)
# ======================================================================
