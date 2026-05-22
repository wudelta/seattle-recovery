from django.urls import path
from . import views

app_name = 'hopehub' 

urlpatterns = [
    path('journal_entries/', views.JournalView.as_view(), name='journal_entries'),
    path('create_journal_entry/', views.CreateJournalEntryView.as_view(), name='create_journal_entry'),
    path('update_journal_entry/<pk>/', views.UpdateJournalEntryView.as_view(), name='update_journal_entry'),
    path('delete_journal_entry/<pk>/', views.DeleteJournalEntryView.as_view(), name='delete_journal_entry'),
]