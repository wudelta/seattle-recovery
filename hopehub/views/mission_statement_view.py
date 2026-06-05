# hopehub/views/mission_statement_view.py
from django.views.generic import TemplateView

class MissionStatementView(TemplateView):
    template_name = "hopehub/mission_statement.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Mission Statement"
        context["return_path"] = "/hopehub/" if "hopehub" == "hopehub" else "/aurora/"
        return context
