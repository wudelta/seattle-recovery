# ======================================================================
# FILE: hopehub/views/new_page_view.py
# START: PACKAGED_IMPORTS_AND_DEPENDENCIES
# ======================================================================
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
# ======================================================================
# END: PACKAGED_IMPORTS_AND_DEPENDENCIES
# ======================================================================

# ======================================================================
# START: CLASS_BASED_VIEW_ROUTING
# ======================================================================
class NewPageView(LoginRequiredMixin, TemplateView):
    template_name = "hopehub/new_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "New Page"
        context["return_path"] = "/hopehub/" if "hopehub" == "hopehub" else "/aurora/"
        return context
# ======================================================================
# END: CLASS_BASED_VIEW_ROUTING
# ======================================================================
