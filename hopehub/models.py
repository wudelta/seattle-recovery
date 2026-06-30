# ======================================================================
# FILE: hopehub/models.py (PATCH 1 OF 3)
# START: RUNTIME_IMPORTS_AND_ENCRYPTION_LOGIC
# ======================================================================
import os
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet

# HIPAA & 42 CFR PART 2 SECURITY INVARIANT: Isolate encryption keys entirely from source code files.
ENCRYPTION_KEY = os.getenv('HOPEHUB_FIELD_ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    # Fail-secure hard stop: Block application boot to prevent data leakage or fallback weaknesses
    raise SystemError(
        "\n======================================================================\n"
        "🚨 [SECURITY CRITICAL] HOPEHUB_FIELD_ENCRYPTION_KEY IS NOT CONFIGURED!\n"
        " To prevent data corruption and maintain clinical confidentiality,\n"
        " you must export a valid 32-byte URL-safe base64 key into your environment.\n"
        "======================================================================\n"
    )

cipher_suite = Fernet(ENCRYPTION_KEY.encode('utf-8'))

class EncryptedTextField(models.TextField):
    """Custom TextField wrapper that handles transparent database encryption."""
    def get_prep_value(self, value):
        """Encrypts plain text into an opaque token before database write."""
        value = super().get_prep_value(value)
        if value and not value.startswith('gAAAA'):
            return cipher_suite.encrypt(value.encode('utf-8')).decode('utf-8')
        return value

    def from_db_value(self, value, expression, connection):
        """Decrypts tokens into readable strings using the primary production environment key."""
        if value:
            if value.startswith('gAAAA'):
                try:
                    return cipher_suite.decrypt(value.encode('utf-8')).decode('utf-8')
                except Exception:
                    return f"[DECRYPTION ERROR: KEY MISMATCH] - Raw Data: {value[:15]}..."
            return value
        return value
# ======================================================================
# END: RUNTIME_IMPORTS_AND_ENCRYPTION_LOGIC (PATCH 1 OF 3)
# ======================================================================

# ======================================================================
# FILE: hopehub/models.py (PATCH 2 OF 3)
# START: JOURNAL_ENTRY_AND_TAGGING_METADATA_SCHEMAS
# ======================================================================
class JournalEntry(models.Model):
    # Fix: Point relation to the active swapped settings custom user model
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Targeted Encryption Field (Protects clinical texts while allowing metadata analytics indexing)
    text = EncryptedTextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    emotion = models.CharField(max_length=50, choices=[
        ('joyful', 'Joyful'),
        ('peaceful', 'Peaceful'),
        ('grateful', 'Grateful'),
        ('hopeful', 'Hopeful'),
        ('balanced', 'Balanced'),
        ('reflective', 'Reflective'),
        ('anxious', 'Anxious'),
        ('sad', 'Sad'),
        ('frustrated', 'Frustrated'),
        ('angry', 'Angry'),
        ('tired', 'Tired'),
        ('overwhelmed', 'Stressed'),
    ])
    mood_rating = models.IntegerField(choices=[
        (1, 'Crisis / Extremely Low'),
        (2, 'Very Low / Severe Distress'),
        (3, 'Low / Visibly Struggling'),
        (4, 'Mildly Low / Flat'),
        (5, 'Neutral / Baseline'),
        (6, 'Mildly Good / Stable'),
        (7, 'Good / Positive'),
        (8, 'Very Good / High Energy'),
        (9, 'Excellent / Vibrant'),
        (10, 'Peak Joy / Triumphant'),
    ])
    tags = models.ManyToManyField('Tag', blank=True)
    categories = models.ManyToManyField('Category', blank=True)
    image = models.ImageField(upload_to='journal_images', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Journal Entries"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
# ======================================================================
# END: JOURNAL_ENTRY_AND_TAGGING_METADATA_SCHEMAS (PATCH 2 OF 3)
# ======================================================================

# ======================================================================
# FILE: hopehub/models.py (PATCH 3 OF 3)
# START: DATA_DRIVEN_GOVERNANCE_AND_AI_CONSTRAINTS
# ======================================================================
class GovernanceSection(models.Model):
    """Stores human-readable regulatory compliance text blocks for state/federal auditors."""
    regulation_type = models.CharField(
        max_length=50, choices=[
            ('HIPAA_SECURITY', 'HIPAA Security Rule'),
            ('42_CFR_PART_2', '42 CFR Part 2 (SUD Privacy)'),
            ('DATA_MINIMIZATION', 'Data Retention & Minimization Policy'),
        ], unique=True
    )
    title = models.CharField(max_length=150)
    body_text = models.TextField(help_text="Preserves line breaks and explicit paragraph spaces.")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Governance Policy Section"
        ordering = ['regulation_type']

    def __str__(self) -> str:
        return f"[{self.regulation_type}] {self.title}"

class TechnicalConstraint(models.Model):
    """Stores machine-readable JSON blocks to guide automated AI development loops."""
    rule_key = models.CharField(max_length=100, unique=True, help_text="e.g., 'encryption_invariants'")
    description = models.CharField(max_length=150)
    constraint_data = models.JSONField(help_text="Valid JSON structural guidelines parsed by AI agents.")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "AI Development Constraint"

    def __str__(self) -> str:
        return f"Constraint Group: {self.rule_key}"
# ======================================================================
# END: DATA_DRIVEN_GOVERNANCE_AND_AI_CONSTRAINTS (PATCH 3 OF 3)
# ======================================================================
