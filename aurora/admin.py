# ======================================================================
# FILE: aurora/admin.py (PATCH 1 OF 1)
# START: COMPONENT_REGISTRY_ADMIN_REGISTRATION
# ======================================================================
from django.contrib import admin
from aurora.models import ComponentRegistry

@admin.register(ComponentRegistry)
class ComponentRegistryAdmin(admin.ModelAdmin):
    """Exposes the 65 tracked system assets visually for manual documentation."""
    
    # Column views visible directly on your master list index page
    list_display = ('name', 'file_path', 'persona', 'status', 'locked', 'date_modified')
    
    # Active search bar matching your key system fields
    search_fields = ('name', 'file_path', 'description')
    
    # Right-hand sidebar filter clusters for fast layout drilling
    list_filter = ('persona', 'status', 'locked')
    
    # Organize fields inside your visual editor form panel layout cleanly
    fieldsets = (
        ('System Identity Parity Anchors', {
            'fields': ('name', 'file_path', 'persona')
        }),
        ('Safety Locks & Deployment Status', {
            'fields': ('status', 'locked', 'created_by')
        }),
        ('Multi-Audience Documentation Assets', {
            'fields': ('description', 'description_audiences')
        }),
    )
# ======================================================================
# END: COMPONENT_REGISTRY_ADMIN_REGISTRATION
# ======================================================================
