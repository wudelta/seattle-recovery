# FILE: aurora/models.py
"""
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T20:22:45.285954+00:00
 PROJECT ECOSYSTEM: AURORA
 FILE PATH: aurora/models.py
 TECHNICAL MATRIX: Python Module. Exported Logic Components: __str__, __str__, __str__

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[models.py] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[AURORA]
 ```
"""
from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        app_label = 'aurora'
        
    def __str__(self):
        return self.title

class Metadata(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    phase = models.CharField(max_length=255, blank=True, null=True)
    criticality = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    threats = models.TextField(blank=True, null=True)
    mitigations = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    class Meta:
        app_label = 'aurora'
        
    def __str__(self):
        return f"{self.document.title} - {self.key}"

class Content(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    content = models.TextField()
    class Meta:
        app_label = 'aurora'
        
    def __str__(self):
        return f"{self.document.title} - Content"