# ======================================================================
# FILE: aurora/subsystems/planning/services/execution_evidence.py
# START: PLANNING_EXECUTION_EVIDENCE_SERVICE
# ======================================================================

from aurora.models import Step, StepFile
from aurora.subsystems.component_registry.services.component_policy import (
    CLASSIFICATION_ARCHIVE,
    CLASSIFICATION_REGISTER,
    CLASSIFICATION_UPDATE,
)
from aurora.subsystems.component_registry.services.reconciler import ReconciliationItem


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


def record_actual_step_files_from_reconciliation(
    *,
    step: Step,
    items: list[ReconciliationItem],
    user,
) -> list[StepFile]:
    """Record deterministic actual-file evidence from one registry comparison."""
    recorded: list[StepFile] = []

    for item in items:
        if item.classification == CLASSIFICATION_REGISTER:
            if item.source_hash is None:
                raise PlanningExecutionEvidenceError(
                    "Cannot record a newly discovered repository file without "
                    f"a deterministic source hash: {item.path}"
                )
            reason = (
                "Component Registry observed a repository file that was absent "
                "from the Step baseline."
            )

        elif item.classification == CLASSIFICATION_ARCHIVE:
            reason = (
                "Component Registry observed a repository file that was present "
                "in the Step baseline and is now absent."
            )

        elif item.classification == CLASSIFICATION_UPDATE:
            if item.reason == "source_hash_missing":
                raise PlanningExecutionEvidenceError(
                    "Cannot attribute repository history when the Component "
                    f"Registry baseline source hash is missing: {item.path}"
                )
            if item.reason != "source_content_changed":
                continue
            reason = (
                "Component Registry observed a deterministic source-hash change "
                "from the Step baseline."
            )

        else:
            continue

        recorded.append(
            record_actual_step_file(
                step=step,
                file_path=item.path,
                user=user,
                reason=reason,
            )
        )

    return recorded


# ======================================================================
# END: PLANNING_EXECUTION_EVIDENCE_SERVICE
# ======================================================================
