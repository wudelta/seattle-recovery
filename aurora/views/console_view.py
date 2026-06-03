# aurora/views/console_view.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class ConsoleView(LoginRequiredMixin, TemplateView):
    template_name = 'aurora/aurora_console.html'
    login_url = 'aurora:login' 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['architect'] = self.request.user.username
        context['ai_lead'] = "Wu"
        return context
