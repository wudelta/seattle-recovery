# ======================================================================
# FILE: aurora/models.py 
# START: RUNTIME_IMPORTS_AND_DEPENDENCIES
# ======================================================================
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
# ======================================================================
# END: RUNTIME_IMPORTS_AND_DEPENDENCIES 
# ======================================================================

# ======================================================================
# FILE: aurora/models.py 
# START: COMPONENT_REGISTRY_CORE_SCHEMA
# ======================================================================
class ComponentRegistry(models.Model):
    """Tabular schema tracking application metadata, safety locks, and audience visibility rules."""

    PERSONA_CHOICES = [
        ('Core Vectors', [
            ('ENTRY_POINT', 'Entry Point / Execution Vector'),
            ('COMPILER_MODULE', 'Standard Codebase Module'),
        ]),
        ('Web Assets & Client Interface', [
            ('UI_LAYOUT', 'UI Layout (.html)'),
            ('UI_STYLE', 'UI Style (.css)'),
            ('UI_LOGIC', 'UI Logic (.js)'),
            ('UI_MEDIA', 'UI Media (.jpeg, .png, etc.)'),
        ]),
        ('System Config & Documentation', [
            ('DOCUMENTATION', 'Documentation (.md, .txt)'),
            ('CONFIGURATION', 'Configuration Registry (.ini, .yaml, .json)'),
        ]),
        ('Logs & Diagnostics', [
            ('DIAGNOSTIC_LOG', 'System Execution Log (.log)'),
        ]),
    ]
    STATUS_CHOICES = [
        ('ACTIVE', 'Active Component'),
        ('STAGED_FOR_DELETION', 'Quarantined / Pending Deletion Review'),
    ]
    VISIBILITY_CHOICES = [
        ('PUBLIC', 'Public Access Node'),
        ('PRIVATE', 'Private Protected Node'),
    ]
    ANALYSIS_STATUS_CHOICES = [
        ('PENDING', 'Pending Analysis'),
        ('COMPLETE', 'Analysis Complete'),
        ('FAILED', 'Analysis Failed'),
    ]
    GRAPH_SYNC_STATUS_CHOICES = [
        ('PENDING', 'Pending Graph Synchronization'),
        ('COMPLETE', 'Graph Synchronization Complete'),
        ('FAILED', 'Graph Synchronization Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_path = models.CharField(max_length=500, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    persona = models.CharField(max_length=30, choices=PERSONA_CHOICES, default='COMPILER_MODULE')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='ACTIVE')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='PRIVATE')
    locked = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='forged_assets',
        help_text="The authenticated developer who authorized the execution string."
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    source_hash = models.CharField(
        max_length=64,
        blank=True,
        default='',
        help_text="SHA-256 digest from the most recently observed source content.",
    )
    last_observed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Most recent reconciliation timestamp at which the file was observed.",
    )
    last_analyzed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Most recent successful or failed AI enrichment attempt.",
    )
    analysis_status = models.CharField(
        max_length=20,
        choices=ANALYSIS_STATUS_CHOICES,
        default='PENDING',
        help_text="Current incremental documentation analysis state.",
    )
    analysis_version = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="Analyzer contract version used for the stored documentation.",
    )
    graph_sync_status = models.CharField(
        max_length=20,
        choices=GRAPH_SYNC_STATUS_CHOICES,
        default='PENDING',
        db_index=True,
        help_text="Current PostgreSQL-to-Neo4j projection state.",
    )
    graph_sync_hash = models.CharField(
        max_length=64,
        blank=True,
        default='',
        help_text="Source hash most recently projected successfully into Neo4j.",
    )
    graph_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Most recent successful Neo4j projection timestamp.",
    )
    graph_sync_error = models.TextField(
        blank=True,
        default='',
        help_text="Most recent graph synchronization failure details.",
    )
    description = models.TextField(
        blank=True, help_text="Primary unified summary of what this component module executes."
    )
    description_audiences = models.JSONField(
        default=dict, blank=True, help_text="Stores segregated documentation data blocks: developer_docs, stakeholder_docs, end_user_docs."
    )

    class Meta:
        verbose_name = "Component Asset Profile"
        verbose_name_plural = "Component Asset Profiles"

    def update_audience_docs(self, track: str, content: str):
        """Helper loop to safely write or update a specific audience documentation block."""
        if not isinstance(self.description_audiences, dict):
            self.description_audiences = {}
        self.description_audiences[track] = content
        self.save()

    def __str__(self):
        return f"{self.name} [{self.persona}] - Locked: {self.locked}"
# ======================================================================
# END: COMPONENT_REGISTRY_CORE_SCHEMA 
# ======================================================================

# ======================================================================
# FILE: aurora/models.py 
# START: STATIC_CONTENT_SCHEMA
# ======================================================================
class StaticContent(models.Model):
    """Stores the HTML content for informational pages."""

    class ApplicationChoices(models.TextChoices):
        AURORA = 'aurora', 'Aurora'
        HOPEHUB = 'hopehub', 'HopeHub'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.CharField(
        max_length=10,
        choices=ApplicationChoices.choices,
        default=ApplicationChoices.AURORA,
    )
    title = models.CharField(max_length=255)
    html_content = models.TextField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"StaticContent: {self.title} [{self.application}] (ID: {self.id})"
# ======================================================================
# END: STATIC_CONTENT_SCHEMA 
# ======================================================================

# ======================================================================
# FILE: aurora/models.py 
# START: PERSISTENT_CHAT_LEDGER_SCHEMA
# ======================================================================
class ChatLedgerEntry(models.Model):
    """
    Lightweight, index-optimized conversational transaction table.
    Enforces a low-footprint sliding history window to prevent context bloat.
    """

    ROLE_CHOICES = (
        ('user', 'User Input Prompt'),
        ('model', 'Model Assistant Response'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_ledger_entries',
        help_text="The authenticated user operating the active workspace session thread."
    )
    session_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Unique workspace thread isolation tracker token.",
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, db_index=True)
    text = models.TextField(help_text="Raw conversational data chunk payload.")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Chat Ledger Entry"
        verbose_name_plural = "Chat Ledger Entries"
        indexes = [
            models.Index(
                fields=['session_id', 'created_at'],
                name='aurora_chat_ledger_idx',
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
        ).order_by('-created_at')[20:]

        if excess_entries:
            ChatLedgerEntry.objects.filter(
                id__in=[entry.id for entry in excess_entries]
            ).delete()
# ======================================================================
# END: PERSISTENT_CHAT_LEDGER_SCHEMA 
# ======================================================================

# ======================================================================
# FILE: aurora/models.py 
# START: DIRECTIVES_SCHEMA
# ======================================================================
class DeltaDirectives(models.Model):
    """
    Standalone configuration engine storing system instructions, prompts, and 
    model processing boundaries for your AI minion fleet.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    directive_name = models.CharField(max_length=255, unique=True, db_index=True)
    instructions = models.TextField()
    constraints = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    # Fix: Point relation to the active swapped settings model
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Delta Directive Profile"
        verbose_name_plural = "Delta Directive Profiles"

    def __str__(self):
        return f"{self.directive_name} [Active: {self.is_active}]"
# ======================================================================
# END: DIRECTIVES_SCHEMA 
# ======================================================================

# ======================================================================
# FILE: aurora/models.py 
# START: DELTA_NOTES_SCHEMA
# ======================================================================
class DeltaNotesEntry(models.Model):
    """
    Tracks daily developer intentions, active task execution blocks, and
    accumulated focus time per session window.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='delta_notes',
        help_text="The developer compiling this active workspace iteration note."
    )
    text = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed = models.BooleanField(default=False)
    total_seconds_logged = models.PositiveIntegerField(
        default=0,
        help_text="Total accumulated active focus time recorded in seconds."
    )
    last_started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the active session timer toggle was engaged."
    )

    class Meta:
        verbose_name = "Delta Notes Entry"
        verbose_name_plural = "Delta Notes Entries"
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"DeltaNote {self.id} - "
            f"User: {self.user.username} "
            f"({self.created_at.strftime('%Y-%m-%d')})"
        )
# ======================================================================
# END: DELTA_NOTES_SCHEMA 
# ======================================================================

# ======================================================================
# FILE: aurora/models.py 
# START: CODE_CHANGE_REVIEW_SCHEMA
# ======================================================================
class PendingCodeChange(models.Model):
    """Stores one validated Wu code proposal awaiting developer review."""

    STATUS_CHOICES = [
        ('PENDING', 'Pending Developer Review'),
        ('APPLIED', 'Approved and Applied'),
        ('REJECTED', 'Rejected by Developer'),
        ('CONFLICT', 'Source Changed Before Approval'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pending_code_changes',
    )
    file_path = models.CharField(
        max_length=500,
        db_index=True,
        help_text="Validated repository-relative path targeted by the proposal.",
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
        default='PENDING',
        db_index=True,
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_reviewed = models.DateTimeField(null=True, blank=True)
    date_applied = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Pending Code Change"
        verbose_name_plural = "Pending Code Changes"
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.file_path} [{self.status}]"
# ======================================================================
# END: CODE_CHANGE_REVIEW_SCHEMA 
# ======================================================================

# ======================================================================
# FILE: aurora/models.py
# START: EXECUTION_PLAN_SCHEMA
# ======================================================================
class ExecutionStatus(models.TextChoices):
    """Shared lifecycle states for execution planning."""

    PLANNED = "PLANNED", "Planned"
    ACTIVE = "ACTIVE", "Active"
    PAUSED = "PAUSED", "Paused"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class EstimateConfidence(models.TextChoices):
    """Confidence levels for implementation effort estimates."""

    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"


class RiskLevel(models.TextChoices):
    """Potential implementation impact associated with a planning step."""

    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"
    CRITICAL = "CRITICAL", "Critical"


class Project(models.Model):
    """A product, application, or engineering domain containing initiatives."""

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    color = models.CharField(
        max_length=32,
        blank=True,
        help_text="Optional presentation color for planning interfaces.",
    )

    icon = models.CharField(
        max_length=64,
        blank=True,
        help_text="Optional icon identifier for planning interfaces.",
    )

    status = models.CharField(
        max_length=20,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.PLANNED,
        db_index=True,
    )

    position = models.PositiveIntegerField(default=0)

    active = models.BooleanField(
        default=True,
        db_index=True,
        help_text=(
            "Whether this project remains available for normal engineering work."
        ),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="projects_created",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="projects_assigned",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["position", "title"]

    def __str__(self):
        return self.title


class Initiative(models.Model):
    """A top-level engineering objective within a Project."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="initiatives",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.PLANNED,
        db_index=True,
    )

    position = models.PositiveIntegerField(default=0)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="initiatives_created",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="initiatives_assigned",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["position", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "position"],
                name="unique_initiative_position_per_project",
            ),
        ]

    def __str__(self):
        return f"{self.project} / {self.title}"


class Phase(models.Model):
    """A milestone within an Initiative."""

    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name="phases",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.PLANNED,
        db_index=True,
    )

    position = models.PositiveIntegerField(default=0)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="phases_created",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="phases_assigned",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["position", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["initiative", "position"],
                name="unique_phase_position_per_initiative",
            ),
        ]

    def __str__(self):
        return f"{self.initiative} / {self.title}"


class Step(models.Model):
    """A single validated implementation task within a Phase."""

    phase = models.ForeignKey(
        Phase,
        on_delete=models.CASCADE,
        related_name="steps",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.PLANNED,
        db_index=True,
    )

    position = models.PositiveIntegerField(default=0)

    estimated_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated implementation effort in minutes.",
    )

    estimate_confidence = models.CharField(
        max_length=10,
        choices=EstimateConfidence.choices,
        null=True,
        blank=True,
        help_text="Confidence in the current implementation estimate.",
    )

    risk_level = models.CharField(
        max_length=10,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW,
        db_index=True,
        help_text="Potential impact if this implementation step fails.",
    )

    risk_description = models.TextField(
        blank=True,
        help_text="Reason this step carries implementation or operational risk.",
    )

    validation_description = models.TextField(
        blank=True,
        help_text="Deterministic evidence required to validate this step.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="steps_created",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="steps_assigned",
    )

    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="validated_steps",
    )

    validation_notes = models.TextField(
        blank=True,
        help_text="Observed validation results and supporting evidence.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["position", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["phase", "position"],
                name="unique_step_position_per_phase",
            ),
        ]

    def __str__(self):
        return f"{self.phase} / {self.title}"


class UserPosition(models.Model):
    """The current planning hierarchy position selected by a user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="planning_position",
    )

    project = models.ForeignKey(
        Project,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_positions",
    )

    initiative = models.ForeignKey(
        Initiative,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_positions",
    )

    phase = models.ForeignKey(
        Phase,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_positions",
    )

    step = models.ForeignKey(
        Step,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_positions",
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} planning position"


class TimeEntry(models.Model):
    """A period of time spent by a user working on a planning step."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="planning_time_entries",
    )

    step = models.ForeignKey(
        Step,
        on_delete=models.PROTECT,
        related_name="time_entries",
    )

    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user} / {self.step} / {self.started_at}"
# ======================================================================
# END: EXECUTION_PLAN_SCHEMA
# ======================================================================