# ======================================================================
# FILE: aurora/subsystems/wu_chat/admin.py
# START: WU_CHAT_ADMIN
# ======================================================================

from django.contrib import admin

from aurora.subsystems.wu_chat.models import (
    ChatLedgerEntry,
    PendingCodeChange,
)


@admin.register(ChatLedgerEntry)
class ChatLedgerEntryAdmin(admin.ModelAdmin):
    """Read-oriented view of persisted Wu conversation history."""

    list_display = (
        "session_id",
        "role",
        "user",
        "short_text",
        "created_at",
    )
    search_fields = (
        "session_id",
        "text",
        "user__username",
        "user__email",
    )
    list_filter = (
        "role",
        "created_at",
        "user",
    )
    readonly_fields = (
        "id",
        "user",
        "session_id",
        "role",
        "text",
        "created_at",
    )
    ordering = ("-created_at",)
    list_select_related = ("user",)
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def short_text(self, obj):
        """Provides a compact preview of the persisted message."""
        normalized_text = " ".join(obj.text.split())
        return (
            normalized_text[:80] + "..."
            if len(normalized_text) > 80
            else normalized_text
        )

    short_text.short_description = "Message Preview"


@admin.register(PendingCodeChange)
class PendingCodeChangeAdmin(admin.ModelAdmin):
    """Read-oriented inspection view for Wu code-review transactions."""

    list_display = (
        "file_path",
        "status",
        "user",
        "date_created",
        "date_reviewed",
        "date_applied",
    )
    search_fields = (
        "file_path",
        "original_sha256",
        "user__username",
        "user__email",
    )
    list_filter = (
        "status",
        "date_created",
        "date_reviewed",
        "date_applied",
        "user",
    )
    readonly_fields = (
        "id",
        "user",
        "file_path",
        "original_sha256",
        "original_content",
        "proposed_content",
        "status",
        "date_created",
        "date_reviewed",
        "date_applied",
    )
    ordering = ("-date_created",)
    list_select_related = ("user",)
    date_hierarchy = "date_created"

    fieldsets = (
        (
            "Review Transaction",
            {
                "fields": (
                    "id",
                    "user",
                    "file_path",
                    "status",
                    "original_sha256",
                ),
            },
        ),
        (
            "Current Source Snapshot",
            {
                "fields": ("original_content",),
            },
        ),
        (
            "Wu Proposed Replacement",
            {
                "fields": ("proposed_content",),
            },
        ),
        (
            "Review Timeline",
            {
                "fields": (
                    "date_created",
                    "date_reviewed",
                    "date_applied",
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ======================================================================
# END: WU_CHAT_ADMIN
# ======================================================================