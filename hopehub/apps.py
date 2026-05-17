# FILE: hopehub/apps.py
"""
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T20:22:46.191698+00:00
 PROJECT ECOSYSTEM: HOPEHUB
 FILE PATH: hopehub/apps.py
 TECHNICAL MATRIX: Python Module. Exported Logic Components: 

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[apps.py] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[HOPEHUB]
 ```
"""
from django.apps import AppConfig

class HopehubConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hopehub'