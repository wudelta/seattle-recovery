from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError

# --- 0. EXTENSIBLE MODEL VALIDATION RUNTIME GUARDRAIL ---
def validate_active_minion_profile(value):
    """
    Data Quality Gate: Validates incoming assignments against the runtime configuration.
    Enables dynamic agent addition without requiring database schema alterations.
    """
    allowed_profiles = getattr(settings, 'ACTIVE_MINIONS', ['NONE', 'CORE_PY', 'UI_CSS', 'DOM_JS', 'DB_SQL', 'SYS_GIT', 'MINION_ADD'])
    if value not in allowed_profiles:
        raise ValidationError(f"❌ '{value}' is not a currently registered minion agent profile matrix.")


# --- 1. EXISTING PLATFORM MODELS (RETAINED VERBATIM) ---
class Document(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'aurora'

    def __str__(self):
        return self.title


class Metadata(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    phase = models.CharField(max_length=255, blank=True, null=True)
    criticality = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    threats = models.TextField(blank=True, null=True)
    mitigations = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        app_label = 'aurora'

    def __str__(self):
        return f"{self.document.title} - {self.key}"


class Content(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        app_label = 'aurora'

    def __str__(self):
        return f"{self.document.title} - Content"


# --- 2. NEW STRATEGIC PROCESS FLOW MODELS (APPENDED) ---
class DeltaNote(models.Model):
    """
    Captures Delta's raw, unstructured human brain dumps offline.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delta_notes')
    raw_text = models.TextField()
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'aurora'

    def __str__(self):
        return f"DeltaNote {self.pk} - User: {self.user.username} (Processed: {self.is_processed})"


class DeltaChange(models.Model):
    """
    Tracks precise code alterations, specialized workers, and state histories.
    """
    ASSIGNMENT_CHOICES = [
        ('WU', 'Wu Core Architect (70B)'),
        ('MINION', 'Mechanical Worker Array (8B)'),
    ]

    STATUS_CHOICES = [
        ('PENDING_REVIEW', 'Pending Human Review Gate'),
        ('APPROVED', 'Approved for Execution'),
        ('EXECUTED', 'Executed - Awaiting Acceptance'),
        ('ACCEPTED', 'Changes Accepted and Committed'),
        ('ROLLED_BACK', 'Changes Rolled Back Safely'),
    ]

    APP_CHOICES = [
        ('AURORA', 'Aurora Core Framework'),
        ('HOPEHUB', 'HopeHub UI Management'),
        ('CORE_LOGIC', 'Core Logic System Systems'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delta_changes')
    app_affected = models.CharField(max_length=20, choices=APP_CHOICES, default='AURORA')
    assigned_to = models.CharField(max_length=10, choices=ASSIGNMENT_CHOICES, default='MINION')
    minion_type = models.CharField(max_length=30, default='NONE', validators=[validate_active_minion_profile])
    dense_instructions = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING_REVIEW')
    
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    executed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'aurora'

    def save(self, *args, **kwargs):
        self.minion_type = self.minion_type.strip().upper().replace(' ', '_')
        if self.assigned_to == 'WU':
            self.minion_type = 'NONE'
        super().save(*args, **kwargs)

    def __str__(self):
        worker = f"Minion ({self.minion_type})" if self.assigned_to == 'MINION' else "Wu Core"
        return f"DeltaChange {self.pk} [{self.app_affected}] -> Worker: {worker} | Status: {self.status}"


class DeltaDirective(models.Model):
    """
    Persistent systemic boundary guardrails (e.g., DOCUMENTATION, CONSTRAINTS)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delta_directives')
    directive_name = models.CharField(max_length=100)
    assigned_to = models.CharField(max_length=30, default='BOTH')
    dense_instructions = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'aurora'

    def save(self, *args, **kwargs):
        self.directive_name = self.directive_name.strip().upper().replace(' ', '_')
        self.assigned_to = self.assigned_to.strip().upper().replace(' ', '_')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"DeltaDirective: {self.directive_name} (Assigned: {self.assigned_to})"


class AutomatedBuildStep(models.Model):
    """
    Relational tracking state machine managing the sequential build parameters
    and automation payloads executed by Aurora's minion worker array.
    """
    STAGE_CHOICES = [
        ('SETUP_TEST', '1. Write Failing Test'),
        ('BUILD_HTML', '2. Generate HTML Template'),
        ('BUILD_VIEW', '3. Implement View Class'),
        ('BUILD_ROUTER', '4. Register URL Path'),
        ('VERIFY_TDD', '5. Run Verification Suite'),
    ]

    APPROVAL_CHOICES = [
        ('PENDING_REVIEW', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    # Core Metadata & Sequence Management
    feature_name = models.CharField(
        max_length=100,
        help_text="Unique lowercase identifier for the target feature group (e.g., 'under_construction_page')."
    )
    step_order = models.PositiveIntegerField(
        help_text="Strict sequential order for pipeline execution (e.g., 1, 2, 3, 4)."
    )
    stage = models.CharField(
        max_length=20, 
        choices=STAGE_CHOICES,
        help_text="The explicit system development lifecycle phase."
    )
    title = models.CharField(
        max_length=150,
        help_text="Short, human-readable title describing this specific automation step."
    )
    
    # Target File System Targeting Parameters
    target_file_path = models.CharField(
        max_length=255,
        help_text="Relative directory file path to modify (e.g., 'hopehub/tests/test_views.py')."
    )
    
    # Automation Payloads & Code Mutation Signatures
    code_payload = models.TextField(
        blank=True,
        help_text="The raw Python code or HTML snippet text to inject or write to disk."
    )
    anchor_signature = models.CharField(
        max_length=255,
        blank=True,
        help_text="The string or regex token used to position code insertion inside an existing file."
    )
    
    # Human-in-the-Loop Workflow Tracking States
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_CHOICES,
        default='PENDING_REVIEW',
        help_text="Controls if a worker minion has authorization to run file updates."
    )
    assigned_minion = models.CharField(
        max_length=50,
        help_text="The descriptive identity name of the runner executing this code operation."
    )
    human_notes = models.TextField(
        blank=True,
        help_text="Your personal workspace adjustments, rationale, or design notes."
    )
    
    # Self-Verification Telemetry & Shell Validation Gate Data
    verification_command = models.CharField(
        max_length=255,
        help_text="The shell command run to verify compilation (e.g., 'python manage.py test')."
    )
    expected_exit_code = models.IntegerField(
        default=0,
        help_text="The terminal response code expected. 0 for clean pass, 1 for TDD initial failure."
    )
    execution_logs = models.TextField(
        blank=True,
        help_text="Raw standard output and error telemetry streaming back from the active worker subprocess."
    )
    is_executed = models.BooleanField(
        default=False,
        help_text="Tracks whether the task step has run successfully and cleared validation checkpoints."
    )

    class Meta:
        ordering = ['feature_name', 'step_order']
        # Strict structural block ensuring no matching order entries collide inside a single feature scope
        unique_together = ['feature_name', 'step_order']
        verbose_name = "Automated Build Step"
        verbose_name_plural = "Automated Build Steps"

    def __str__(self):
        return f"{self.feature_name} - Step {self.step_order}: {self.title}"
