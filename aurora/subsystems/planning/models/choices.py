from django.db import models


# START: EXECUTION_PLAN_CHOICES
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
# ======================================================================
# END: EXECUTION_PLAN_CHOICES
# ======================================================================
