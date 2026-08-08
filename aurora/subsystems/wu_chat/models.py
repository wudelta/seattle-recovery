# ======================================================================
# FILE: aurora/subsystems/wu_chat/models.py
# START: WU_CHAT_MODELS
# ======================================================================

import uuid

from django.conf import settings
from django.db import models


class ChatLedgerEntry(models.Model):
    """
    Lightweight, index-optimized conversational transaction table.
    Enforces a low-footprint sliding history window to prevent context bloat.
    """

    ROLE_CHOICES = (
        ("user", "User Input Prompt"),
        ("model", "Model Assistant Response"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_ledger_entries",
        help_text=(
            "The authenticated user operating the active workspace "
            "session thread."
        ),
    )
    session_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Unique workspace thread isolation tracker token.",
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        db_index=True,
    )
    text = models.TextField(
        help_text="Raw conversational data chunk payload."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = "Chat Ledger Entry"
        verbose_name_plural = "Chat Ledger Entries"
        indexes = [
            models.Index(
                fields=["session_id", "created_at"],
                name="aurora_chat_ledger_idx",
            ),
        ]

    def __str__(self):
        return (
            f"[{self.session_id}] {self.role.upper()} - "
            f"{self.created_at.strftime('%Y-%m-%d %H:%M')}"
        )

    def save(self, *args, **kwargs):
        """
        Database-level Self-Pruning Guard: Captures table mutations and
        surgically deletes surplus old rows past the 20-row history limit.
        """
        super().save(*args, **kwargs)

        excess_entries = ChatLedgerEntry.objects.filter(
            session_id=self.session_id
        ).order_by("-created_at")[20:]

        if excess_entries:
            ChatLedgerEntry.objects.filter(
                id__in=[entry.id for entry in excess_entries]
            ).delete()


class PendingCodeChange(models.Model):
    """Stores one validated Wu code proposal awaiting developer review."""

    STATUS_CHOICES = [
        ("PENDING", "Pending Developer Review"),
        ("APPLIED", "Approved and Applied"),
        ("REJECTED", "Rejected by Developer"),
        ("CONFLICT", "Source Changed Before Approval"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pending_code_changes",
    )
    file_path = models.CharField(
        max_length=500,
        db_index=True,
        help_text=(
            "Validated repository-relative path targeted by the proposal."
        ),
    )
    original_content = models.TextField(
        help_text="Source content loaded when the proposal was generated.",
    )
    proposed_content = models.TextField(
        help_text="Replacement content returned by Wu and shown for review.",
    )
    original_sha256 = models.CharField(
        max_length=64,
        help_text="Checksum used to detect source changes before approval.",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        db_index=True,
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_reviewed = models.DateTimeField(null=True, blank=True)
    date_applied = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Pending Code Change"
        verbose_name_plural = "Pending Code Changes"
        ordering = ["-date_created"]

    def __str__(self):
        return f"{self.file_path} [{self.status}]"


# ======================================================================
# END: WU_CHAT_MODELS
# ======================================================================