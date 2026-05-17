# FILE: aurora/apps.py
"""
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T21:12:26.630692+00:00
 PROJECT ECOSYSTEM: AURORA
 FILE PATH: aurora/apps.py
 TECHNICAL MATRIX: Python Module. Exported Logic Components: 

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[apps.py] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[AURORA]
 ```
"""
from django.apps import AppConfig

class AuroraConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aurora'