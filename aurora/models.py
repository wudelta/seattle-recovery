# ======================================================================
# FILE: aurora/models.py (PATCH 1 OF 3)
# START: RUNTIME_IMPORTS_AND_DEPENDENCIES
# ======================================================================
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# ======================================================================
# END: RUNTIME_IMPORTS_AND_DEPENDENCIES
# ======================================================================

# ======================================================================
# FILE: aurora/models.py (PATCH 2 OF 3)
# START: COMPONENT_REGISTRY_CORE_SCHEMA
# ======================================================================
class ComponentRegistry(models.Model):
    """Tabular schema tracking application metadata, safety locks, and audience visibility rules."""
    PERSONA_CHOICES = [
        ('ENTRY_POINT', 'Entry Point / Execution Vector'),
        ('COMPILER_MODULE', 'Standard Codebase Module'),
    ]
    STATUS_CHOICES = [
        ('ACTIVE', 'Active Component'),
        ('STAGED_FOR_DELETION', 'Quarantined / Pending Deletion Review'),
    ]
    VISIBILITY_CHOICES = [
        ('PUBLIC', 'Public Access Node'),
        ('PRIVATE', 'Private Protected Node'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_path = models.CharField(max_length=500, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    persona = models.CharField(max_length=30, choices=PERSONA_CHOICES, default='COMPILER_MODULE')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='ACTIVE')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='PRIVATE')
    locked = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='forged_assets', 
        help_text="The authenticated developer who authorized the execution string."
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    description_audiences = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = "Component Asset Profile"
        verbose_name_plural = "Component Asset Profiles"

    def __str__(self):
        return f"{self.name} [{self.persona}] - Locked: {self.locked}"
# ======================================================================
# END: COMPONENT_REGISTRY_CORE_SCHEMA
# ======================================================================

# ======================================================================
# FILE: aurora/models.py (PATCH 3 OF 3)
# START: DELTA_NOTES_TIMER_SCHEMA
# ======================================================================
class DeltaNotesEntry(models.Model):
    """
    Tracks daily developer intentions, active task execution blocks, 
    and accumulated focus time per session window.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='delta_notes',
        help_text="The developer compiling this active workspace iteration note."
    )
    text = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed = models.BooleanField(default=False)
    
    # Timer Core Mechanics:
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
        return f"DeltaNote {self.id} - User: {self.user.username} ({self.created_at.strftime('%Y-%m-%d')})"
# ======================================================================
# END: DELTA_NOTES_TIMER_SCHEMA
# ======================================================================
