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
