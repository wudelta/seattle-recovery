# hopehub/views/my_account_view.py
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class MyAccountView(LoginRequiredMixin, TemplateView):
    template_name = "hopehub/my_account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "My Account"
        context["return_path"] = "/hopehub/" if "hopehub" == "hopehub" else "/aurora/"
        return context
