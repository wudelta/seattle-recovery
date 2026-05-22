from django.urls import path
from .views import JournalView, ProcessJournalEntryView, DeleteJournalEntryView

app_name = 'hopehub'

urlpatterns = [
    path('journal_entries/', JournalView.as_view(), name='journal_entries'),
    
    # Both paths now route to the exact same combined class
    path('create_journal_entry/', ProcessJournalEntryView.as_view(), name='create_journal_entry'),
    path('update_journal_entry/<int:pk>/', ProcessJournalEntryView.as_view(), name='update_journal_entry'),
    
    path('delete_journal_entry/<int:pk>/', DeleteJournalEntryView.as_view(), name='delete_journal_entry'),
]
