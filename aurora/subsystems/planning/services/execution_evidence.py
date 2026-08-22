# ======================================================================
# FILE: aurora/subsystems/planning/services/execution_evidence.py
# START: PLANNING_EXECUTION_EVIDENCE_SERVICE
# ======================================================================

from aurora.models import Step, StepFile


class PlanningExecutionEvidenceError(RuntimeError):
    """Raised when execution evidence cannot be recorded safely."""


def record_actual_step_file(
    *,
    step: Step,
    file_path: str,
    user,
    reason: str = "",
) -> StepFile:
    """Record one repository file actually changed during Step execution."""

    if step is None or not step.pk:
        raise PlanningExecutionEvidenceError(
            "A persisted Step is required to record actual file evidence."
        )

    if not user or not getattr(user, "is_authenticated", False):
        raise PlanningExecutionEvidenceError(
            "An authenticated user is required to record actual file evidence."
        )

    normalized_path = str(file_path).strip()

    if not normalized_path:
        raise PlanningExecutionEvidenceError(
            "A repository-relative file path is required."
        )

    step_file, _ = StepFile.objects.update_or_create(
        step=step,
        file_path=normalized_path,
        role=StepFile.Role.ACTUAL,
        defaults={
            "reason": reason.strip(),
            "recorded_by": user,
        },
    )

    return step_file


# ======================================================================
# END: PLANNING_EXECUTION_EVIDENCE_SERVICE
# ======================================================================
