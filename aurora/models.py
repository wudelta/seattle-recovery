# ======================================================================
# FILE: aurora/models.py (PATCH 1 OF 7)
# START: RUNTIME_IMPORTS_AND_DEPENDENCIES
# ======================================================================
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
# ======================================================================
# END: RUNTIME_IMPORTS_AND_DEPENDENCIES (PATCH 1 OF 7)
# ======================================================================

# ======================================================================
# FILE: aurora/models.py (PATCH 2 OF 7)
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_path = models.CharField(max_length=500, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    persona = models.CharField(max_length=30, choices=PERSONA_CHOICES, default='COMPILER_MODULE')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='ACTIVE')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='PRIVATE')
    locked = models.BooleanField(default=False)

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
# END: COMPONENT_REGISTRY_CORE_SCHEMA (PATCH 2 OF 7)
# ======================================================================

# ======================================================================
# FILE: aurora/models.py (PATCH 3 OF 7)
# START: STATIC_CONTENT_SCHEMA
# ======================================================================
class StaticContent(models.Model):
    """Stores the HTML content for informational pages."""
    class ApplicationChoices(models.TextChoices):
        AURORA = 'aurora', 'Aurora'
        HOPEHUB = 'hopehub', 'HopeHub'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.CharField(
        max_length=10, choices=ApplicationChoices.choices, default=ApplicationChoices.AURORA
    )
    title = models.CharField(max_length=255)
    html_content = models.TextField()
    
    # Fix: Point relation to the active swapped settings model
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"StaticContent: {self.title} [{self.application}] (ID: {self.id})"
# ======================================================================
# END: STATIC_CONTENT_SCHEMA (PATCH 3 OF 7)
# ======================================================================

# ======================================================================
# FILE: aurora/models.py (PATCH 4 OF 7)
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
    session_id = models.CharField(max_length=255, db_index=True, help_text="Unique workspace thread isolation tracker token.")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, db_index=True)
    text = models.TextField(help_text="Raw conversational data chunk payload.")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "Chat Ledger Entry"
        verbose_name_plural = "Chat Ledger Entries"
        # FIXED: Upgraded legacy index_together syntax to modern Django 5.x indices array blocks
        indexes = [
            models.Index(fields=['session_id', 'created_at'], name='aurora_chat_ledger_idx')
        ]

    def __str__(self):
        return f"[{self.session_id}] {self.role.upper()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        """
        Database-level Self-Pruning Guard: Captures table mutations and
        surgically deletes surplus old rows past the 20-row history limit.
        """
        super().save(*args, **kwargs)
        
        # Pull entry ID list past the rolling 20-message row buffer limit
        excess_entries = ChatLedgerEntry.objects.filter(
            session_id=self.session_id
        ).order_by('-created_at')[20:]
        
        if excess_entries:
            # Batch erase old records inside a single SQL deletion execution pass
            ChatLedgerEntry.objects.filter(id__in=[entry.id for entry in excess_entries]).delete()
# ======================================================================
# END: PERSISTENT_CHAT_LEDGER_SCHEMA (PATCH 4 OF 7)
# ======================================================================

# ======================================================================
# FILE: aurora/models.py (PATCH 5 OF 7)
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

    @classmethod
    def provision_standard_minions(cls, author_user) -> int:
        """Programmatically seeds the database with default settings for the core minion fleet."""
        minion_fleet = {
            "minion_wu": {
                "instructions": "Act as the master project orchestrator. Parse complex multi-step tasks, evaluate repo requirements, and delegate isolated tasks down to the specialized 8B fleet.",
                "constraints": {"model": "llama-3.3-70b-versatile", "temperature": 0.1}
            },
            "minion_UI_layout": {
                "instructions": "Generate structural layouts. Produce clean, well-formed HTML skeleton layout blocks based on context.",
                "constraints": {"model": "llama-3.1-8b-instant", "temperature": 0.4}
            },
            "minion_UI_style": {
                "instructions": "Generate interface style themes. Output clean utility or custom CSS styling rules.",
                "constraints": {"model": "llama-3.1-8b-instant", "temperature": 0.3}
            },
            "minion_UI_logic": {
                "instructions": "Generate client interactivity. Output pure modern JavaScript block strings code blocks.",
                "constraints": {"model": "llama-3.1-8b-instant", "temperature": 0.2}
            },
            "minion_anamod": {
                "instructions": "Analyze existing repository code modules. Propose clean code modifications or file patches safely.",
                "constraints": {"model": "llama-3.1-8b-instant", "temperature": 0.1}
            },
            "minion_AI_writer": {
                "instructions": "Refactor raw text blocks. Polish clarity, style, documentation records, and structural layout phrasing.",
                "constraints": {"model": "llama-3.1-8b-instant", "temperature": 0.6}
            }
        }
        seeded_count = 0
        for name, data in minion_fleet.items():
            obj, created = cls.objects.get_or_create(
                directive_name=name,
                defaults={
                    "instructions": data["instructions"],
                    "constraints": data["constraints"],
                    "is_active": True,
                    "created_by": author_user
                }
            )
            if created:
                seeded_count += 1
        return seeded_count

    def __str__(self):
        return f"{self.directive_name} [Active: {self.is_active}]"
# ======================================================================
# END: DIRECTIVES_SCHEMA (PATCH 5 OF 7)
# ======================================================================

# ======================================================================
# FILE: aurora/models.py (PATCH 6 OF 7)
# START: DELTA_NOTES_SCHEMA
# ======================================================================
class DeltaNotesEntry(models.Model):
    """
    Tracks daily developer intentions, active task execution blocks, and 
    accumulated focus time per session window.
    """
    # Fix: Point relation to the active swapped settings model
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
        default=0, help_text="Total accumulated active focus time recorded in seconds."
    )
    last_started_at = models.DateTimeField(
        null=True, blank=True, help_text="Timestamp when the active session timer toggle was engaged."
    )

    class Meta:
        verbose_name = "Delta Notes Entry"
        verbose_name_plural = "Delta Notes Entries"
        ordering = ['-created_at']

    def __str__(self):
        return f"DeltaNote {self.id} - User: {self.user.username} ({self.created_at.strftime('%Y-%m-%d')})"
# ======================================================================
# END: DELTA_NOTES_SCHEMA (PATCH 6 OF 7)
# ======================================================================

# ======================================================================
# FILE: aurora/models.py (PATCH 7 OF 7)
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
# END: CODE_CHANGE_REVIEW_SCHEMA (PATCH 7 OF 7)
# ======================================================================