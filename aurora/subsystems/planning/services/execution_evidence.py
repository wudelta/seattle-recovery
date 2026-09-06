# ======================================================================
# FILE: aurora/subsystems/planning/services/execution_evidence.py
# START: PLANNING_EXECUTION_EVIDENCE_SERVICE
# ======================================================================

from django.db import transaction

from aurora.models import Step, StepFile, StepRepositoryBaseline
from aurora.subsystems.component_registry.services.component_policy import (
    CLASSIFICATION_EXCLUDE,
    CLASSIFICATION_REVIEW,
)
from aurora.subsystems.component_registry.services.reconciler import WorkspaceReconciler


class PlanningExecutionEvidenceError(RuntimeError):
    """Raised when execution evidence cannot be recorded safely."""


def _repository_snapshot() -> dict[str, str]:
    """Return the deterministic eligible repository state used for Step evidence."""
    discovered = WorkspaceReconciler().discover_workspace_files()
    snapshot: dict[str, str] = {}

    for path, item in sorted(discovered.items()):
        if item.get("classification") in {
            CLASSIFICATION_EXCLUDE,
            CLASSIFICATION_REVIEW,
        }:
            continue

        source_hash = item.get("source_hash")
        if source_hash is None:
            raise PlanningExecutionEvidenceError(
                "Cannot establish deterministic Step repository evidence because "
                f"the source hash is unavailable: {path}"
            )

        snapshot[path] = str(source_hash)

    return snapshot


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


def open_step_repository_baseline(
    *,
    step: Step,
    user,
    snapshot: dict[str, str] | None = None,
) -> StepRepositoryBaseline:
    """Open the repository baseline for the Step's current execution segment."""
    if step is None or not step.pk:
        raise PlanningExecutionEvidenceError(
            "A persisted Step is required to open repository evidence."
        )

    if not user or not getattr(user, "is_authenticated", False):
        raise PlanningExecutionEvidenceError(
            "An authenticated user is required to open repository evidence."
        )

    baseline_snapshot = snapshot if snapshot is not None else _repository_snapshot()

    with transaction.atomic():
        locked_step = Step.objects.select_for_update().get(pk=step.pk)

        existing = (
            StepRepositoryBaseline.objects
            .select_for_update()
            .filter(step=locked_step)
            .first()
        )
        if existing is not None:
            return existing

        return StepRepositoryBaseline.objects.create(
            step=locked_step,
            snapshot=baseline_snapshot,
            opened_by=user,
        )


def finalize_step_repository_baseline(
    *,
    step: Step,
) -> list[StepFile]:
    """Close one execution segment and persist only changes made in that segment."""
    if step is None or not step.pk:
        raise PlanningExecutionEvidenceError(
            "A persisted Step is required to finalize repository evidence."
        )

    current_snapshot = _repository_snapshot()

    with transaction.atomic():
        baseline = (
            StepRepositoryBaseline.objects
            .select_for_update()
            .select_related("step", "opened_by")
            .filter(step_id=step.pk)
            .first()
        )
        if baseline is None:
            raise PlanningExecutionEvidenceError(
                "The Step has no open repository baseline. Repository changes "
                "cannot be attributed safely."
            )

        before = {
            str(path): str(source_hash)
            for path, source_hash in baseline.snapshot.items()
        }
        after = current_snapshot
        recorded: list[StepFile] = []

        for path in sorted(set(before) | set(after)):
            before_hash = before.get(path)
            after_hash = after.get(path)

            if before_hash is None and after_hash is not None:
                reason = (
                    "Repository file was created while this Step held executable "
                    "authority."
                )
            elif before_hash is not None and after_hash is None:
                reason = (
                    "Repository file was deleted while this Step held executable "
                    "authority."
                )
            elif before_hash != after_hash:
                reason = (
                    "Repository file content changed while this Step held "
                    "executable authority."
                )
            else:
                continue

            recorded.append(
                record_actual_step_file(
                    step=baseline.step,
                    file_path=path,
                    user=baseline.opened_by,
                    reason=reason,
                )
            )

        baseline.delete()
        return recorded


# ======================================================================
# END: PLANNING_EXECUTION_EVIDENCE_SERVICE
# ======================================================================
