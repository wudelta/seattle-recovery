# aurora/models.py
import uuid
from django.db import models
from django.contrib.auth.models import User

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
    
    # STRUCTURAL REFACTOR: Replaces the old CharField string text log completely
    created_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT,  # Prevents user deletion from destroying repository logs out-of-band
        related_name='forged_assets',
        help_text="The authenticated developer who authorized the execution string."
    )
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    
    # Stores target audience scopes natively as a JSON layout array (e.g., ["developers", "investors"])
    description_audiences = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = "Component Asset Profile"
        verbose_name_plural = "Component Asset Profiles"

    def __str__(self):
        return f"{self.name} [{self.persona}] - Locked: {self.locked}"
