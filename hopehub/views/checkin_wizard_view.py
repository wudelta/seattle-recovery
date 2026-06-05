# hopehub/views/checkin_wizard_view.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class CheckinWizardView(LoginRequiredMixin, TemplateView):
    template_name = "hopehub/checkin_wizard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Checkin Wizard"
        context["return_path"] = "/hopehub/" if "hopehub" == "hopehub" else "/aurora/"
        return context
