# ======================================================================
# FILE: aurora/admin.py (PATCH 1 OF 2)
# START: READABLE_ADMIN_DOCUMENTATION_VIEWS
# ======================================================================
from django.contrib import admin
from django.utils.safestring import mark_safe
from aurora.models import ComponentRegistry, StaticContent, DeltaDirectives, DeltaNotesEntry

@admin.register(ComponentRegistry)
class ComponentRegistryAdmin(admin.ModelAdmin):
    """Exposes the tracked system assets visually for manual documentation."""
    # Added 'display_user_uuid' to inspect your secure developer token inline
    list_display = ('name', 'file_path', 'persona', 'status', 'locked', 'display_user_uuid', 'date_modified')
    search_fields = ('name', 'file_path', 'description')
    list_filter = ('persona', 'status', 'locked')
    inlines = []
    readonly_fields = ('display_developer_docs', 'display_stakeholder_docs', 'display_user_uuid')
    fieldsets = (
        ('System Identity Parity Anchors', {
            'fields': ('name', 'file_path', 'persona')
        }),
        ('Safety Locks & Deployment Status', {
            'fields': ('status', 'locked', 'created_by', 'display_user_uuid')
        }),
        ('Unified Summary String', {
            'fields': ('description',)
        }),
        ('🔍 Detailed Multi-Audience AI Documentation (Formatted View)', {
            'fields': ('display_developer_docs', 'display_stakeholder_docs'),
        }),
    )

    def display_user_uuid(self, obj):
        """Displays the secure, un-incremented UUID token of the owner."""
        return obj.created_by.id if obj.created_by else "-"
    display_user_uuid.short_description = "Owner UUID Token"

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
    list_display = ('title', 'application', 'created_by', 'display_user_uuid', 'date_created', 'date_modified')
    search_fields = ('title', 'html_content')
    list_filter = ('application', 'date_created', 'date_modified', 'created_by')
    readonly_fields = ('display_user_uuid',)
    ordering = ('-date_created',)

    def display_user_uuid(self, obj):
        """Exposes the immutable UUID token of the content creator."""
        return obj.created_by.id if obj.created_by else "-"
    display_user_uuid.short_description = "Creator UUID Token"
# ======================================================================
# END: READABLE_ADMIN_DOCUMENTATION_VIEWS (PATCH 1 OF 2)
# ======================================================================

# ======================================================================
# FILE: aurora/admin.py (PATCH 2 OF 2)
# START: DELTA_DIRECTIVES_AND_NOTES_ADMIN_SHELL
# ======================================================================
@admin.register(DeltaDirectives)
class DeltaDirectivesAdmin(admin.ModelAdmin):
    """Dedicated management grid for standalone AI constraint rule modifications."""
    list_display = ('directive_name', 'is_active', 'display_user_uuid', 'date_created', 'date_modified')
    search_fields = ('directive_name', 'instructions')
    list_filter = ('is_active', 'date_created')
    readonly_fields = ('display_user_uuid',)
    fieldsets = (
        ('Minion Core Identity', {
            'fields': ('directive_name', 'is_active')
        }),
        ('Dense AI Prompt Instructions', {
            'fields': ('instructions',)
        }),
        ('Structured Parameter Boundaries & Rules', {
            'fields': ('constraints', 'created_by', 'display_user_uuid')
        }),
    )

    def display_user_uuid(self, obj):
        """Exposes the immutable UUID token of the author."""
        return obj.created_by.id if obj.created_by else "-"
    display_user_uuid.short_description = "Author UUID Token"

@admin.register(DeltaNotesEntry)
class DeltaNotesEntryAdmin(admin.ModelAdmin):
    """Dedicated management grid for daily developer intentions and active session logs."""
    list_display = ('user', 'display_user_uuid', 'short_text', 'processed', 'display_focus_time', 'created_at')
    search_fields = ('text', 'user__username')
    list_filter = ('processed', 'created_at', 'user')
    readonly_fields = ('display_user_uuid',)
    fieldsets = (
        ('Developer Context Anchor', {
            'fields': ('user', 'display_user_uuid', 'processed')
        }),
        ('Active Intention / Task Blocks', {
            'fields': ('text',)
        }),
        ('🎛️ Session Focus Timer Metrics', {
            'fields': ('total_seconds_logged', 'last_started_at'),
        }),
    )

    def display_user_uuid(self, obj):
        """Exposes the internal developer UUID string entry directly."""
        return obj.user.id if obj.user else "-"
    display_user_uuid.short_description = "Developer UUID Token"

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
# END: DELTA_DIRECTIVES_AND_NOTES_ADMIN_SHELL (PATCH 2 OF 2)
# ======================================================================
