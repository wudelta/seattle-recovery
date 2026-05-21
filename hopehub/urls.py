from django.urls import path
from . import views

app_name = 'hopehub' 

urlpatterns = [
    path('journal/', views.JournalView.as_view(), name='journal'),
]