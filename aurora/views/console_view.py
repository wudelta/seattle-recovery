# ======================================================================
# FILE: aurora/views/console_view.py (PATCH 1 OF 1)
# START: COCKPIT TERMINAL DISPLAY ENGINE CONFIGURATION
# ======================================================================
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class ConsoleView(LoginRequiredMixin, TemplateView):
    """Renders the high-density fluid 4-panel terminal console cockpit dashboard."""
    template_name = 'aurora/aurora_console.html'
    login_url = 'aurora:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Binds logged-in user and AI profile tokens directly into frontend terminal scope
        context['architect'] = self.request.user.username
        context['ai_lead'] = "Wu"
        return context
# ======================================================================
# END: COCKPIT TERMINAL DISPLAY ENGINE CONFIGURATION
# ======================================================================
