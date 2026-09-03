# ======================================================================
# FILE: aurora/subsystems/wu_chat/services/execution_context.py
# START: EXECUTION_CONTEXT_RESOLVER
# ======================================================================
"""Resolve Wu prompt context from Planning-owned execution state."""

from dataclasses import dataclass
from typing import Optional

from aurora.subsystems.planning.api.worker_resources import (
    get_current_execution_worker_resource,
)


@dataclass(frozen=True)
class ExecutionContext:
    """Immutable Wu-facing snapshot of Planning's current execution position."""

    initiative: Optional[dict[str, object]] = None
    phase: Optional[dict[str, object]] = None
    step: Optional[dict[str, object]] = None

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
            f"Initiative: {self.initiative['title']}",
            (
                "Initiative description: "
                f"{self.initiative['description'] or 'Not provided.'}"
            ),
            f"Phase: {self.phase['title']}",
            (
                "Phase description: "
                f"{self.phase['description'] or 'Not provided.'}"
            ),
            f"Step: {self.step['title']}",
            (
                "Step description: "
                f"{self.step['description'] or 'Not provided.'}"
            ),
            (
                "Validation requirement: "
                f"{self.step['validation_description'] or 'Not provided.'}"
            ),
        ]

        estimated_minutes = self.step.get("estimated_minutes")
        if estimated_minutes is not None:
            lines.append(
                f"Estimated effort: {estimated_minutes} minutes"
            )

        estimate_confidence = self.step.get("estimate_confidence_label")
        if estimate_confidence:
            lines.append(
                f"Estimate confidence: {estimate_confidence}"
            )

        lines.append(
            "Treat this execution context as authoritative project state. "
            "The user's current instruction remains the immediate request."
        )

        return "\n".join(lines)


class ExecutionContextResolver:
    """Build Wu context from Planning's worker-facing execution resource."""

    @classmethod
    def build(cls, user) -> ExecutionContext:
        """Return Planning's authoritative executable path for Wu."""
        resource = get_current_execution_worker_resource(user=user)

        return ExecutionContext(
            initiative=resource["initiative"],
            phase=resource["phase"],
            step=resource["step"],
        )


# ======================================================================
# END: EXECUTION_CONTEXT_RESOLVER
# ======================================================================
