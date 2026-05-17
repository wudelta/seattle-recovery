# FILE: aurora/admin.py
"""
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T20:22:45.329031+00:00
 PROJECT ECOSYSTEM: AURORA
 FILE PATH: aurora/admin.py
 TECHNICAL MATRIX: Python Module. Exported Logic Components: get_formset

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[admin.py] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[AURORA]
 ```
"""
# aurora/admin.py
from django.contrib import admin
from .models import Document, Metadata, Content

class MetadataInline(admin.TabularInline):
    model = Metadata
    extra = 1
    fields = ('key', 'value', 'criticality', 'status', 'type')

class ContentInline(admin.StackedInline):
    model = Content
    extra = 0
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Apply fixed monospace font styling directly to the document editor area
        formset.form.base_fields['content'].widget.attrs['style'] = 'font-family: monospace; font-size: 13px; rows: 20; width: 100%;'
        return formset

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)
    inlines = [MetadataInline, ContentInline]