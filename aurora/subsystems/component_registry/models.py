# ======================================================================
# FILE: aurora/subsystems/component_registry/models.py
# START: COMPONENT_REGISTRY_CORE_SCHEMA
# ======================================================================

import uuid

from django.conf import settings
from django.db import models


class ComponentRegistry(models.Model):
    """
    Tabular schema tracking application metadata, safety locks,
    and audience visibility rules.
    """

    PERSONA_CHOICES = [
        (
            "Core Vectors",
            [
                ("ENTRY_POINT", "Entry Point / Execution Vector"),
                ("COMPILER_MODULE", "Standard Codebase Module"),
            ],
        ),
        (
            "Web Assets & Client Interface",
            [
                ("UI_LAYOUT", "UI Layout (.html)"),
                ("UI_STYLE", "UI Style (.css)"),
                ("UI_LOGIC", "UI Logic (.js)"),
                ("UI_MEDIA", "UI Media (.jpeg, .png, etc.)"),
            ],
        ),
        (
            "System Config & Documentation",
            [
                ("DOCUMENTATION", "Documentation (.md, .txt)"),
                (
                    "CONFIGURATION",
                    "Configuration Registry (.ini, .yaml, .json)",
                ),
            ],
        ),
        (
            "Logs & Diagnostics",
            [
                ("DIAGNOSTIC_LOG", "System Execution Log (.log)"),
            ],
        ),
    ]

    STATUS_CHOICES = [
        ("ACTIVE", "Active Component"),
        ("ARCHIVED", "Archived Component"),
    ]

    VISIBILITY_CHOICES = [
        ("PUBLIC", "Public Access Node"),
        ("PRIVATE", "Private Protected Node"),
    ]

    ANALYSIS_STATUS_CHOICES = [
        ("PENDING", "Pending Analysis"),
        ("COMPLETE", "Analysis Complete"),
        ("FAILED", "Analysis Failed"),
    ]

    GRAPH_SYNC_STATUS_CHOICES = [
        ("PENDING", "Pending Graph Synchronization"),
        ("COMPLETE", "Graph Synchronization Complete"),
        ("FAILED", "Graph Synchronization Failed"),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    file_path = models.CharField(
        max_length=500,
        unique=True,
        db_index=True,
    )
    name = models.CharField(max_length=255)
    persona = models.CharField(
        max_length=30,
        choices=PERSONA_CHOICES,
        default="COMPILER_MODULE",
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="ACTIVE",
    )
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default="PRIVATE",
    )
    locked = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="forged_assets",
        help_text=(
            "The authenticated developer who authorized "
            "the execution string."
        ),
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    source_hash = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text=(
            "SHA-256 digest from the most recently observed source content."
        ),
    )
    last_observed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "Most recent reconciliation timestamp at which "
            "the file was observed."
        ),
    )
    last_analyzed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=(
            "Most recent successful or failed AI enrichment attempt."
        ),
    )
    analysis_status = models.CharField(
        max_length=20,
        choices=ANALYSIS_STATUS_CHOICES,
        default="PENDING",
        help_text="Current incremental documentation analysis state.",
    )
    analysis_version = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text=(
            "Analyzer contract version used for the stored documentation."
        ),
    )

    graph_sync_status = models.CharField(
        max_length=20,
        choices=GRAPH_SYNC_STATUS_CHOICES,
        default="PENDING",
        db_index=True,
        help_text="Current PostgreSQL-to-Neo4j projection state.",
    )
    graph_sync_hash = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text=(
            "Source hash most recently projected successfully into Neo4j."
        ),
    )
    graph_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Most recent successful Neo4j projection timestamp.",
    )
    graph_sync_error = models.TextField(
        blank=True,
        default="",
        help_text="Most recent graph synchronization failure details.",
    )

    description = models.TextField(
        blank=True,
        help_text=(
            "Primary unified summary of what this component module executes."
        ),
    )
    description_audiences = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Stores segregated documentation data blocks: "
            "developer_docs, stakeholder_docs, end_user_docs."
        ),
    )

    class Meta:
        verbose_name = "Component Asset Profile"
        verbose_name_plural = "Component Asset Profiles"

    def update_audience_docs(self, track: str, content: str):
        """Safely write or update one audience documentation block."""
        if not isinstance(self.description_audiences, dict):
            self.description_audiences = {}

        self.description_audiences[track] = content
        self.save()

    def __str__(self):
        return f"{self.name} [{self.persona}] - Locked: {self.locked}"


# ======================================================================
# END: COMPONENT_REGISTRY_CORE_SCHEMA
# ======================================================================