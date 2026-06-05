# hopehub/views/about_hopehub_view.py
from django.views.generic import TemplateView

class AboutHopehubView(TemplateView):
    template_name = "hopehub/about_hopehub.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "About Hopehub"
        context["return_path"] = "/hopehub/" if "hopehub" == "hopehub" else "/aurora/"
        return context
