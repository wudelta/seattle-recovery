# ======================================================================
# FILE: aurora/admin.py (PATCH 1 OF 1)
# START: COMPONENT_REGISTRY_ADMIN_REGISTRATION
# ======================================================================
from django.contrib import admin
from aurora.models import ComponentRegistry, StaticContent, DeltaDirectives

class StaticContentInline(admin.StackedInline):
    """Allows editing child HTML informational content directly inside the parent Component Profile."""
    model = StaticContent
    extra = 1
    fields = ('title', 'html_content')


@admin.register(ComponentRegistry)
class ComponentRegistryAdmin(admin.ModelAdmin):
    """Exposes the tracked system assets visually for manual documentation."""
    # Column views visible directly on your master list index page
    list_display = ('name', 'file_path', 'persona', 'status', 'locked', 'date_modified')
    
    # Active search bar matching your key system fields
    search_fields = ('name', 'file_path', 'description')
    
    # Right-hand sidebar filter clusters for fast layout drilling
    list_filter = ('persona', 'status', 'locked')
    
    # Inline management layout injection for parent-child relationship control
    inlines = [StaticContentInline]
    
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


@admin.register(StaticContent)
class StaticContentAdmin(admin.ModelAdmin):
    """Dedicated management grid for standalone informational content modifications."""
    list_display = ('title', 'component_registry', 'created_at', 'updated_at')
    search_fields = ('title', 'html_content', 'component_registry__name')
    list_filter = ('created_at', 'updated_at')


@admin.register(DeltaDirectives)
class DeltaDirectivesAdmin(admin.ModelAdmin):
    """
    Dedicated management grid for standalone AI constraint rule modifications.
    Gives you a clean interface to tweak prompts and rules for later expansions.
    """
    list_display = ('directive_name', 'is_active', 'created_at', 'updated_at')
    search_fields = ('directive_name', 'instructions')
    list_filter = ('is_active', 'created_at')
    
    # Organizes your dense prompt layouts cleanly within the edit form
    fieldsets = (
        ('Minion Core Identity', {
            'fields': ('directive_name', 'is_active')
        }),
        ('Dense AI Prompt Instructions', {
            'fields': ('instructions',)
        }),
        ('Structured Parameter Boundaries & Rules', {
            'fields': ('constraints',)
        }),
    )
# ======================================================================
# END: COMPONENT_REGISTRY_ADMIN_REGISTRATION (PATCH 1 OF 1)
# ======================================================================
