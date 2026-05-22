from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import JournalEntry
from .forms import JournalEntryForm

class JournalView(LoginRequiredMixin, TemplateView):
    template_name = 'hopehub/journal_entries.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fix: Filter entries so users only see their own journal history
        context['journal_entries'] = JournalEntry.objects.filter(user=self.request.user).order_by('-created_at')
        return context

class CreateJournalEntryView(LoginRequiredMixin, CreateView):
    model = JournalEntry
    form_class = JournalEntryForm
    template_name = 'hopehub/create_journal_entry.html'
    # Add the 'hopehub:' namespace prefix here
    success_url = reverse_lazy('hopehub:journal_entries') 

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class UpdateJournalEntryView(LoginRequiredMixin, UpdateView):
    model = JournalEntry
    form_class = JournalEntryForm
    template_name = 'hopehub/update_journal_entry.html'
    # Add the 'hopehub:' namespace prefix here
    success_url = reverse_lazy('hopehub:journal_entries') 

    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)

class DeleteJournalEntryView(LoginRequiredMixin, DeleteView):
    model = JournalEntry
    template_name = 'hopehub/delete_journal_entry.html'
    # Add the 'hopehub:' namespace prefix here
    success_url = reverse_lazy('hopehub:journal_entries') 

    def get_queryset(self):
        return JournalEntry.objects.filter(user=self.request.user)
