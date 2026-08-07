# ======================================================================
# FILE: aurora/urls.py (PATCH 1 OF 1)
# START: SYSTEM_DISPATCH_ROUTING_MATRIX_AND_LOGIN_ENTRIES
# ======================================================================

from django.contrib.auth import views as auth_views
from django.urls import path

from aurora import api as api_endpoints

from . import views

app_name = "aurora"

urlpatterns = [
# 1. ROOT VIEW
path(
"",
views.aurora_landing,
name="landing",
),

# 2. AURORA CONSOLE
path(
    "console/",
    views.ConsoleView.as_view(),
    name="console",
),

# 4. ANAMOD AND SANDBOX ENDPOINTS
path(
    "api/files/tree/",
    api_endpoints.file_tree_api,
    name="ide_file_tree",
),
path(
    "api/files/op/",
    api_endpoints.file_operation_api,
    name="ide_file_operations",
),
path(
    "api/sandbox/run/",
    api_endpoints.run_code_api,
    name="ide_sandbox_run",
),
path(
    "api/sandbox/lint/",
    api_endpoints.lint_code_api,
    name="ide_sandbox_lint",
),

# 5. DJANGO AUTH
path(
    "login/",
    auth_views.LoginView.as_view(
        template_name="aurora/login.html",
        success_url="/aurora/",
    ),
    name="login",
),
path(
    "logout/",
    auth_views.LogoutView.as_view(
        next_page="aurora:landing",
    ),
    name="logout",
),

# 6. AURORA CONSOLE SUBSYSTEM ENDPOINTS
path(
    "api/delta_notes/",
    api_endpoints.delta_notes_endpoint,
    name="delta_notes_endpoint",
),
path(
    "api/content/",
    api_endpoints.content_endpoint,
    name="content_endpoint",
),
path(
    "api/directives/",
    api_endpoints.directives_endpoint,
    name="directives_endpoint",
),
path(
    "api/planning/",
    api_endpoints.planning_endpoint,
    name="planning_endpoint",
),
path(
    "api/wu_chat/",
    api_endpoints.wu_chat_endpoint,
    name="wu_chat_endpoint",
),

# 7. WU STRUCTURED REVIEW WORKFLOW
path(
    "api/wu_chat/approve/",
    api_endpoints.approve_pending_code_change,
    name="approve_pending_code_change",
),
path(
    "api/wu_chat/reject/",
    api_endpoints.reject_pending_code_change,
    name="reject_pending_code_change",
),
]

# ======================================================================
# END: SYSTEM_DISPATCH_ROUTING_MATRIX_AND_LOGIN_ENTRIES (PATCH 1 OF 1)
# ======================================================================
