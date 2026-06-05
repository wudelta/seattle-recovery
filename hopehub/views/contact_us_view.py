# hopehub/views/contact_us_view.py
from django.views.generic import TemplateView

class ContactUsView(TemplateView):
    template_name = "hopehub/contact_us.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Contact Us"
        context["return_path"] = "/hopehub/" if "hopehub" == "hopehub" else "/aurora/"
        return context
