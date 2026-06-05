from django.views.generic import TemplateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from hopehub.models import JournalEntry
from .forms import JournalEntryForm

# Keep your main dashboard view as-is...
class JournalView(LoginRequiredMixin, TemplateView):
    template_name = 'hopehub/journal_entries.html'
    login_url = 'hopehub:login'  # <-- Enforces HopeHub login layout

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['journal_entries'] = JournalEntry.objects.filter(user=self.request.user).order_by('-created_at')
        return context

# NEW: Combined View for both Create and Update operations
class ProcessJournalEntryView(LoginRequiredMixin, UpdateView):
    model = JournalEntry
    form_class = JournalEntryForm
    template_name = 'hopehub/journal_entry_form.html'
    success_url = reverse_lazy('hopehub:journal_entries')
    login_url = 'hopehub:login'  # <-- Enforces HopeHub login layout

    # This method allows this class to double as a CreateView if no pk is provided
    def get_object(self, queryset=None):
        if 'pk' in self.kwargs:
            return super().get_object(queryset)
        return None  # Returning None tells Django to initialize a brand new empty model instance

    # Auto-assign the logged-in user when creating a brand new record
    def form_valid(self, form):
        if not form.instance.pk:
            form.instance.user = self.request.user
        return super().form_valid(form)

    # Security constraint: Restrict editing access to the entry's true owner
    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)

# Keep your delete view as-is...
class DeleteJournalEntryView(LoginRequiredMixin, DeleteView):
    model = JournalEntry
    template_name = 'hopehub/delete_journal_entry.html'
    success_url = reverse_lazy('hopehub:journal_entries')
    login_url = 'hopehub:login'  # <-- Enforces HopeHub login layout

    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)
