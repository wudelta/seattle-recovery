# ======================================================================
# FILE: aurora/views/console_view.py
# START: COCKPIT_TERMINAL_DISPLAY_ENGINE_CONFIGURATION
# ======================================================================

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView

from aurora.access import can_access_aurora


class ConsoleView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Render the Aurora Console for authorized developers."""

    template_name = "aurora/aurora_console.html"
    login_url = "aurora:login"
    raise_exception = True

    def test_func(self):
        """Require explicit Aurora authorization after authentication."""
        return can_access_aurora(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["architect"] = self.request.user.username
        context["ai_lead"] = "Wu"
        return context

# ======================================================================
# END: COCKPIT_TERMINAL_DISPLAY_ENGINE_CONFIGURATION
# ======================================================================