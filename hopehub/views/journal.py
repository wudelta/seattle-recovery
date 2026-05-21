from django.views.generic import TemplateView

class JournalView(TemplateView):
    template_name = 'hopehub/journal_entries.html'