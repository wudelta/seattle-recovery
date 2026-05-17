# FILE: hopehub/urls.py
"""
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T21:12:27.281086+00:00
 PROJECT ECOSYSTEM: HOPEHUB
 FILE PATH: hopehub/urls.py
 TECHNICAL MATRIX: Python Module. Exported Logic Components: 

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[urls.py] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[HOPEHUB]
 ```
"""
from django.urls import path
from . import views

urlpatterns = [
    # This is the "landing page" for the interface app
    # If you have a function named 'index' in views.py, uncomment the line below:
    # path('', views.index, name='index'),
]