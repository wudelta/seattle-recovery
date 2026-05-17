# FILE: aurora/serializers.py
"""
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T21:12:26.674973+00:00
 PROJECT ECOSYSTEM: AURORA
 FILE PATH: aurora/serializers.py
 TECHNICAL MATRIX: Python Module. Exported Logic Components: 

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[serializers.py] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[AURORA]
 ```
"""
from rest_framework import serializers
from .models import Document, Metadata, Content

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

class MetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metadata
        fields = '__all__'

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__'