from django.urls import path
from . import views

app_name = 'hopehub'

urlpatterns = [
    path('under-construction/', views.UnderConstructionView.as_view(), name='under_construction'),
    path('journal_entries/', views.JournalView.as_view(), name='journal_entries'),
    
    # Both paths now route to the exact same combined class
    path('create_journal_entry/', views.ProcessJournalEntryView.as_view(), name='create_journal_entry'),
    path('update_journal_entry/<int:pk>/', views.ProcessJournalEntryView.as_view(), name='update_journal_entry'),
    
    path('delete_journal_entry/<int:pk>/', views.DeleteJournalEntryView.as_view(), name='delete_journal_entry'),
]
