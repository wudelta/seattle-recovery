# filepath: hopehub/urls.py
from django.urls import path
from . import views

app_name = 'hopehub'

urlpatterns = [
    # 1. Main Journal Dashboard View
    path('journal/', views.JournalView.as_view(), name='journal_entries'),
    
    # 2. Dual-Purpose Entry View (Create Action: No Primary Key argument provided)
    path('journal/new/', views.ProcessJournalEntryView.as_view(), name='journal_entry_create'),
    
    # 3. Dual-Purpose Entry View (Update Action: Primary Key integer mapped to self.kwargs)
    path('journal/<int:pk>/edit/', views.ProcessJournalEntryView.as_view(), name='journal_entry_edit'),
    
    # 4. Entry Deletion View
    path('journal/<int:pk>/delete/', views.DeleteJournalEntryView.as_view(), name='journal_entry_delete'),

    # Anchor Signature for Aurora Forge Automation Engine (Step 4 Target)
    # Network Routing Minion will append paths directly below this line
]
