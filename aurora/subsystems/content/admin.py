# ======================================================================
# FILE: aurora/subsystems/content/admin.py
# START: STATIC_CONTENT_ADMIN
# ======================================================================

from django.contrib import admin

from aurora.subsystems.content.models import StaticContent


@admin.register(StaticContent)
class StaticContentAdmin(admin.ModelAdmin):
    """Management grid for standalone informational content."""

    list_display = (
        "title",
        "application",
        "created_by",
        "display_user_uuid",
        "date_created",
        "date_modified",
    )
    search_fields = (
        "title",
        "html_content",
        "created_by__username",
    )
    list_filter = (
        "application",
        "date_created",
        "date_modified",
        "created_by",
    )
    readonly_fields = (
        "id",
        "display_user_uuid",
        "date_created",
        "date_modified",
    )
    ordering = ("-date_created",)
    list_select_related = ("created_by",)

    fieldsets = (
        (
            "Content Identity",
            {
                "fields": (
                    "id",
                    "application",
                    "title",
                ),
            },
        ),
        (
            "HTML Content",
            {
                "fields": ("html_content",),
            },
        ),
        (
            "Ownership",
            {
                "fields": (
                    "created_by",
                    "display_user_uuid",
                ),
            },
        ),
        (
            "Record History",
            {
                "fields": (
                    "date_created",
                    "date_modified",
                ),
            },
        ),
    )

    def display_user_uuid(self, obj):
        """Exposes the immutable UUID token of the content creator."""
        return obj.created_by_id or "-"

    display_user_uuid.short_description = "Creator UUID Token"


# ======================================================================
# END: STATIC_CONTENT_ADMIN
# ======================================================================