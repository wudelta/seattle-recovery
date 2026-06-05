# filepath: hopehub/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'hopehub'

urlpatterns = [
    # 1. ROOT VIEW: Typing '/aurora/' MUST hit the clean visual matrix landing page node
    path('', views.hopehub_landing, name='landing'),

    # 2. Main Journal Dashboard View
    path('journal/', views.JournalView.as_view(), name='journal_entries'),
    
    # 3. Dual-Purpose Entry View (Create Action: No Primary Key argument provided)
    path('journal/new/', views.ProcessJournalEntryView.as_view(), name='journal_entry_create'),
    
    # 4. Dual-Purpose Entry View (Update Action: Primary Key integer mapped to self.kwargs)
    path('journal/<int:pk>/edit/', views.ProcessJournalEntryView.as_view(), name='journal_entry_edit'),
    
    # 5. Entry Deletion View
    path('journal/<int:pk>/delete/', views.DeleteJournalEntryView.as_view(), name='journal_entry_delete'),

    # 6. DJANGO AUTH URLS
    path('login/', auth_views.LoginView.as_view(
        template_name='hopehub/login.html',
        success_url='/hopehub/'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='hopehub:landing'), name='logout'),

    # Anchor Signature for Aurora Forge Automation Engine (Step 4 Target)
    # Network Routing Minion will append paths directly below this line
    path('mission_statement/', views.MissionStatementView.as_view(), name='mission_statement'),
    path('my_account/', views.MyAccountView.as_view(), name='my_account'),
    path('contact_us/', views.ContactUsView.as_view(), name='contact_us'),
    path('about_hopehub/', views.AboutHopehubView.as_view(), name='about_hopehub'),
    path('api/bed_locator/', views.bed_locator_endpoint, name='bed_locator_endpoint'),
]
