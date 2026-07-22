# ====================================================================== #
# FILE: aurora/urls.py (PATCH 1 OF 1)                                    #
# START: SYSTEM_DISPATCH_ROUTING_MATRIX_AND_LOGIN_ENTRIES                #
# ====================================================================== #
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# FIXED: Pull directly from the consolidated initialization package layer
from aurora import api as api_endpoints

app_name = 'aurora'

urlpatterns = [
    # 1. ROOT VIEW: Typing '/aurora/' MUST hit the clean visual matrix landing page node
    path('', views.aurora_landing, name='landing'),

    # 2. THE COCKPIT: Your primary working environment that replaces Spyder tools
    path('console/', views.ConsoleView.as_view(), name='console'),

    # NEW ENDPOINT: Route target pointing directly to your new dev_streamer_api module
    path(
        'console/run/',
        api_endpoints.trigger_pipeline,
        name='trigger_pipeline',
    ),

    # 3. AI PIPELINES: Background endpoints handling asynchronous communication with Wu
    path(
        'api/command/',
        api_endpoints.execute_blueprint_api,
        name='api_command',
    ),

    # FIXED: Direct standalone path for the unlocked components tracking matrix registry endpoint
    path(
        'api/components/unlocked/',
        api_endpoints.unlocked_components_endpoint,
        name='unlocked_components_registry',
    ),

    # 4. LIGHTWEIGHT EMBEDDED IDE & DOCKER SANDBOX ENDPOINTS
    path(
        'api/files/tree/',
        api_endpoints.file_tree_api,
        name='ide_file_tree',
    ),
    path(
        'api/files/op/',
        api_endpoints.file_operation_api,
        name='ide_file_operations',
    ),
    path(
        'api/sandbox/run/',
        api_endpoints.run_code_api,
        name='ide_sandbox_run',
    ),
    path(
        'api/sandbox/lint/',
        api_endpoints.lint_code_api,
        name='ide_sandbox_lint',
    ),

    # 5. DJANGO AUTH URLS
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='aurora/login.html',
            success_url='/aurora/',
        ),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(
            next_page='aurora:landing',
        ),
        name='logout',
    ),

    # 6. AURORA CONSOLE WORKSPACE ENDPOINTS
    path(
        'api/delta_notes/',
        api_endpoints.delta_notes_endpoint,
        name='delta_notes_endpoint',
    ),
    path(
        'api/content/',
        api_endpoints.content_endpoint,
        name='content_endpoint',
    ),
    path(
        'api/directives/',
        api_endpoints.directives_endpoint,
        name='directives_endpoint',
    ),
    path(
        'api/planning/',
        api_endpoints.planning_endpoint,
        name='planning_endpoint',
    ),
    path(
        'api/wu_chat/',
        api_endpoints.wu_chat_endpoint,
        name='wu_chat_endpoint',
    ),

    # Wu structured review workflow
    path(
        'api/wu_chat/approve/',
        api_endpoints.approve_pending_code_change,
        name='approve_pending_code_change',
    ),
    path(
        'api/wu_chat/reject/',
        api_endpoints.reject_pending_code_change,
        name='reject_pending_code_change',
    ),
]
# ====================================================================== #
# END: SYSTEM_DISPATCH_ROUTING_MATRIX_AND_LOGIN_ENTRIES (PATCH 1 OF 1)   #
# ====================================================================== #