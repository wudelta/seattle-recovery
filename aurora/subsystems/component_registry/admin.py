# ======================================================================
# FILE: aurora/subsystems/component_registry/admin.py
# START: COMPONENT_REGISTRY_ADMIN
# ======================================================================

from django.contrib import admin
from django.utils.safestring import mark_safe

from aurora.subsystems.component_registry.models import ComponentRegistry


@admin.register(ComponentRegistry)
class ComponentRegistryAdmin(admin.ModelAdmin):
    """Exposes the tracked system assets visually for manual documentation."""

    list_display = (
        "name",
        "file_path",
        "persona",
        "status",
        "visibility",
        "locked",
        "display_user_uuid",
        "date_modified",
    )
    search_fields = (
        "name",
        "file_path",
        "description",
        "created_by__username",
    )
    list_filter = (
        "persona",
        "status",
        "visibility",
        "locked",
    )
    readonly_fields = (
        "id",
        "display_developer_docs",
        "display_stakeholder_docs",
        "display_user_uuid",
        "date_created",
        "date_modified",
    )
    list_select_related = ("created_by",)

    fieldsets = (
        (
            "System Identity Parity Anchors",
            {
                "fields": (
                    "id",
                    "name",
                    "file_path",
                    "persona",
                    "visibility",
                ),
            },
        ),
        (
            "Safety Locks & Deployment Status",
            {
                "fields": (
                    "status",
                    "locked",
                    "created_by",
                    "display_user_uuid",
                ),
            },
        ),
        (
            "Unified Summary String",
            {
                "fields": ("description",),
            },
        ),
        (
            "🔍 Detailed Multi-Audience AI Documentation (Formatted View)",
            {
                "fields": (
                    "display_developer_docs",
                    "display_stakeholder_docs",
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
        """Displays the secure, un-incremented UUID token of the owner."""
        return obj.created_by_id or "-"

    display_user_uuid.short_description = "Owner UUID Token"

    def display_developer_docs(self, obj):
        """Extracts and safely formats the developer documentation track."""
        docs = obj.description_audiences or {}
        text = docs.get(
            "developer_docs",
            "No documentation generated yet.",
        )
        formatted_text = text.replace("\n", "<br>")

        return mark_safe(
            '<div style="background:#f8f9fa; padding:15px; '
            'border-left:4px solid #007bff; border-radius:4px; '
            'max-width:800px; font-family:sans-serif; line-height:1.5;">'
            f"{formatted_text}</div>"
        )

    display_developer_docs.short_description = (
        "Developer Architecture Overview"
    )

    def display_stakeholder_docs(self, obj):
        """Extracts and safely formats the stakeholder documentation track."""
        docs = obj.description_audiences or {}
        text = docs.get(
            "stakeholder_docs",
            "No documentation generated yet.",
        )
        formatted_text = text.replace("\n", "<br>")

        return mark_safe(
            '<div style="background:#f8f9fa; padding:15px; '
            'border-left:4px solid #28a745; border-radius:4px; '
            'max-width:800px; font-family:sans-serif; line-height:1.5;">'
            f"{formatted_text}</div>"
        )

    display_stakeholder_docs.short_description = (
        "Stakeholder Business Translation"
    )


# ======================================================================
# END: COMPONENT_REGISTRY_ADMIN
# ======================================================================