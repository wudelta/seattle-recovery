# ======================================================================
# FILE: aurora/subsystems/wu_chat/services/execution_context.py
# START: EXECUTION_CONTEXT_RESOLVER
# ======================================================================
"""Resolve the current Initiative, Phase, and Step execution state."""

from dataclasses import dataclass
from typing import Optional

from django.contrib.auth import get_user_model

from aurora.models import (
    ExecutionStatus,
    Initiative,
    Phase,
    Step,
)


@dataclass(frozen=True)
class ExecutionContext:
    """Immutable snapshot of Aurora's current execution position."""

    initiative: Optional[Initiative] = None
    phase: Optional[Phase] = None
    step: Optional[Step] = None

    @property
    def is_active(self) -> bool:
        """Return whether a complete active execution path exists."""
        return all(
            (
                self.initiative is not None,
                self.phase is not None,
                self.step is not None,
            )
        )

    def as_prompt_block(self) -> str:
        """Serialize the active execution state for AI prompt context."""
        if not self.is_active:
            return ""

        lines = [
            "=== ACTIVE AURORA EXECUTION CONTEXT ===",
            f"Initiative: {self.initiative.title}",
            f"Initiative description: {self.initiative.description or 'Not provided.'}",
            f"Phase: {self.phase.title}",
            f"Phase description: {self.phase.description or 'Not provided.'}",
            f"Step: {self.step.title}",
            f"Step description: {self.step.description or 'Not provided.'}",
            (
                "Validation requirement: "
                f"{self.step.validation_description or 'Not provided.'}"
            ),
        ]

        if self.step.estimated_minutes is not None:
            lines.append(
                f"Estimated effort: {self.step.estimated_minutes} minutes"
            )

        if self.step.estimate_confidence:
            lines.append(
                "Estimate confidence: "
                f"{self.step.get_estimate_confidence_display()}"
            )

        lines.append(
            "Treat this execution context as authoritative project state. "
            "The user's current instruction remains the immediate request."
        )

        return "\n".join(lines)


class ExecutionContextResolver:
    """Build the current user-scoped execution context."""

    @classmethod
    def build(cls, user) -> ExecutionContext:
        """Return the active Initiative → Phase → Step path for a user."""
        user_model = get_user_model()

        if not isinstance(user, user_model) or not user.is_authenticated:
            return ExecutionContext()

        initiative = (
            Initiative.objects.filter(
                created_by=user,
                status=ExecutionStatus.ACTIVE,
            )
            .order_by("position", "created_at")
            .first()
        )

        if initiative is None:
            return ExecutionContext()

        phase = (
            Phase.objects.filter(
                initiative=initiative,
                status=ExecutionStatus.ACTIVE,
            )
            .order_by("position", "created_at")
            .first()
        )

        if phase is None:
            return ExecutionContext(
                initiative=initiative,
            )

        step = (
            Step.objects.filter(
                phase=phase,
                status=ExecutionStatus.ACTIVE,
            )
            .order_by("position", "created_at")
            .first()
        )

        return ExecutionContext(
            initiative=initiative,
            phase=phase,
            step=step,
        )

# ======================================================================
# END: EXECUTION_CONTEXT_RESOLVER
# ======================================================================