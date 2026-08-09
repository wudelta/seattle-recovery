# ======================================================================
# FILE: aurora/subsystems/delta_directives/admin.py
# START: DELTA_DIRECTIVES_ADMIN
# ======================================================================

from django.contrib import admin

from aurora.subsystems.delta_directives.models import DeltaDirectives


@admin.register(DeltaDirectives)
class DeltaDirectivesAdmin(admin.ModelAdmin):
    """Management grid for AI directive and constraint configuration."""

    list_display = (
        "directive_name",
        "is_active",
        "display_user_uuid",
        "date_created",
        "date_modified",
    )
    search_fields = (
        "directive_name",
        "instructions",
        "created_by__username",
    )
    list_filter = (
        "is_active",
        "date_created",
        "date_modified",
    )
    readonly_fields = (
        "id",
        "display_user_uuid",
        "date_created",
        "date_modified",
    )
    ordering = ("directive_name",)
    list_select_related = ("created_by",)

    fieldsets = (
        (
            "Minion Core Identity",
            {
                "fields": (
                    "id",
                    "directive_name",
                    "is_active",
                ),
            },
        ),
        (
            "Dense AI Prompt Instructions",
            {
                "fields": ("instructions",),
            },
        ),
        (
            "Structured Parameter Boundaries & Rules",
            {
                "fields": (
                    "constraints",
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
        """Exposes the immutable UUID token of the author."""
        return obj.created_by_id or "-"

    display_user_uuid.short_description = "Author UUID Token"


# ======================================================================
# END: DELTA_DIRECTIVES_ADMIN
# ======================================================================