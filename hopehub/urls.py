# ======================================================================
# FILE: hopehub/urls.py
# START: HOPEHUB_URL_CONFIGURATION
# ======================================================================
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.urls import path

from hopehub import api as api_commands
from hopehub import views


app_name = "hopehub"


def superuser_required(view):
    """Restrict a view to authenticated Django superusers."""

    return user_passes_test(
        lambda user: user.is_authenticated and user.is_superuser,
        login_url="hopehub:login",
    )(view)


urlpatterns = [
    path("", views.hopehub_landing, name="landing"),

    path(
        "journal/",
        superuser_required(views.JournalView.as_view()),
        name="journal_entries",
    ),
    path(
        "journal/new/",
        superuser_required(views.ProcessJournalEntryView.as_view()),
        name="journal_entry_create",
    ),
    path(
        "journal/<int:pk>/edit/",
        superuser_required(views.ProcessJournalEntryView.as_view()),
        name="journal_entry_edit",
    ),
    path(
        "journal/<int:pk>/delete/",
        superuser_required(views.DeleteJournalEntryView.as_view()),
        name="journal_entry_delete",
    ),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="hopehub/login.html",
            success_url="/hopehub/",
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="hopehub:landing"),
        name="logout",
    ),

    # Anchor Signature for Aurora Forge Automation Engine
    # Network Routing Minion will append paths directly below this line.
    path(
        "api/get_content/",
        api_commands.get_content_endpoint,
        name="get_content_endpoint",
    ),
]
# ======================================================================
# FILE: hopehub/urls.py
# END: HOPEHUB_URL_CONFIGURATION
# ======================================================================