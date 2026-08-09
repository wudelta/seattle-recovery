# ======================================================================
# FILE: aurora/subsystems/delta_notes/admin.py
# START: DELTA_NOTES_ADMIN
# ======================================================================

from django.contrib import admin

from aurora.subsystems.delta_notes.models import DeltaNotesEntry


@admin.register(DeltaNotesEntry)
class DeltaNotesEntryAdmin(admin.ModelAdmin):
    """Management grid for developer intentions and session logs."""

    list_display = (
        "user",
        "display_user_uuid",
        "short_text",
        "processed",
        "display_focus_time",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "text",
        "user__username",
        "user__email",
    )
    list_filter = (
        "processed",
        "created_at",
        "updated_at",
        "user",
    )
    readonly_fields = (
        "display_user_uuid",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    list_select_related = ("user",)

    fieldsets = (
        (
            "Developer Context Anchor",
            {
                "fields": (
                    "user",
                    "display_user_uuid",
                    "processed",
                ),
            },
        ),
        (
            "Active Intention / Task Blocks",
            {
                "fields": ("text",),
            },
        ),
        (
            "🎛️ Session Focus Timer Metrics",
            {
                "fields": (
                    "total_seconds_logged",
                    "last_started_at",
                ),
            },
        ),
        (
            "Record History",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    def display_user_uuid(self, obj):
        """Exposes the internal developer UUID string."""
        return obj.user_id or "-"

    display_user_uuid.short_description = "Developer UUID Token"

    def short_text(self, obj):
        """Truncates long logs for clean display rows."""
        return obj.text[:60] + "..." if len(obj.text) > 60 else obj.text

    short_text.short_description = "Logged Intention Statement"

    def display_focus_time(self, obj):
        """Translates raw logged seconds into a readable duration."""
        total_seconds = obj.total_seconds_logged or 0
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"⏱️ {hours:02d}h {minutes:02d}m {seconds:02d}s"

    display_focus_time.short_description = "Total Accumulated Focus Time"


# ======================================================================
# END: DELTA_NOTES_ADMIN
# ======================================================================