# ======================================================================
# FILE: aurora/admin.py (PATCH 1 OF 1)
# START: READABLE_ADMIN_DOCUMENTATION_VIEWS
# ======================================================================
from django.contrib import admin
from django.utils.safestring import mark_safe
from aurora.models import ComponentRegistry, StaticContent, DeltaDirectives, DeltaNotesEntry


@admin.register(ComponentRegistry)
class ComponentRegistryAdmin(admin.ModelAdmin):
    """Exposes the tracked system assets visually for manual documentation."""
    list_display = ('name', 'file_path', 'persona', 'status', 'locked', 'date_modified')
    search_fields = ('name', 'file_path', 'description')
    list_filter = ('persona', 'status', 'locked')
    inlines = []  # REMOVED: StaticContentInline completely

    # Register our custom display fields as read-only admin elements
    readonly_fields = ('display_developer_docs', 'display_stakeholder_docs')
    fieldsets = (
        ('System Identity Parity Anchors', {
            'fields': ('name', 'file_path', 'persona')
        }),
        ('Safety Locks & Deployment Status', {
            'fields': ('status', 'locked', 'created_by')
        }),
        ('Unified Summary String', {
            'fields': ('description',)
        }),
        ('🔍 Detailed Multi-Audience AI Documentation (Formatted View)', {
            'fields': ('display_developer_docs', 'display_stakeholder_docs'),
        }),
    )

    def display_developer_docs(self, obj):
        """Extracts and safely formats the developer track text with HTML breaks."""
        docs = obj.description_audiences or {}
        text = docs.get("developer_docs", "No documentation generated yet.")
        formatted_text = text.replace('\n', '<br>')
        return mark_safe(f'<div style="background:#f8f9fa; padding:15px; border-left:4px solid #007bff; border-radius:4px; max-width:800px; font-family:sans-serif; line-height:1.5;">{formatted_text}</div>')
    display_developer_docs.short_description = "Developer Architecture Overview"

    def display_stakeholder_docs(self, obj):
        """Extracts and safely formats the stakeholder track text with HTML breaks."""
        docs = obj.description_audiences or {}
        text = docs.get("stakeholder_docs", "No documentation generated yet.")
        formatted_text = text.replace('\n', '<br>')
        return mark_safe(f'<div style="background:#f8f9fa; padding:15px; border-left:4px solid #28a745; border-radius:4px; max-width:800px; font-family:sans-serif; line-height:1.5;">{formatted_text}</div>')
    display_stakeholder_docs.short_description = "Stakeholder Business Translation"


@admin.register(StaticContent)
class StaticContentAdmin(admin.ModelAdmin):
    """Dedicated management grid for standalone informational content modifications."""
    list_display = ('title', 'application', 'created_by', 'date_created', 'date_modified')
    search_fields = ('title', 'html_content')
    list_filter = ('application', 'date_created', 'date_modified', 'created_by')
    ordering = ('-date_created',)


@admin.register(DeltaDirectives)
class DeltaDirectivesAdmin(admin.ModelAdmin):
    """Dedicated management grid for standalone AI constraint rule modifications."""
    list_display = ('directive_name', 'is_active', 'created_at', 'updated_at')
    search_fields = ('directive_name', 'instructions')
    list_filter = ('is_active', 'created_at')
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


@admin.register(DeltaNotesEntry)
class DeltaNotesEntryAdmin(admin.ModelAdmin):
    """Dedicated management grid for daily developer intentions and active session logs."""
    list_display = ('user', 'short_text', 'processed', 'display_focus_time', 'created_at')
    search_fields = ('text', 'user__username')
    list_filter = ('processed', 'created_at', 'user')
    fieldsets = (
        ('Developer Context Anchor', {
            'fields': ('user', 'processed')
        }),
        ('Active Intention / Task Blocks', {
            'fields': ('text',)
        }),
        ('🎛️ Session Focus Timer Metrics', {
            'fields': ('total_seconds_logged', 'last_started_at'),
        }),
    )

    def short_text(self, obj):
        """Truncates long logs for clean display rows in the index registry."""
        return obj.text[:60] + "..." if len(obj.text) > 60 else obj.text
    short_text.short_description = "Logged Intention Statement"

    def display_focus_time(self, obj):
        """Translates raw logged seconds fields into a readable HH:MM:SS format string."""
        total_seconds = obj.total_seconds_logged or 0
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"⏱️ {hours:02d}h {minutes:02d}m {seconds:02d}s"
    display_focus_time.short_description = "Total Accumulated Focus Time"

# ======================================================================
# END: READABLE_ADMIN_DOCUMENTATION_VIEWS (PATCH 1 OF 1)
# ======================================================================
