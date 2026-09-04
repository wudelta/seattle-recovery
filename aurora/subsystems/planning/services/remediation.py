# ======================================================================
# FILE: aurora/subsystems/planning/services/remediation.py
# START: PLANNING_BLOCKING_REMEDIATION_WORKFLOW
# ======================================================================

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from django.db import transaction

from aurora.subsystems.planning.io.exceptions import (
    PlanningImportError,
    PlanningSchemaError,
)
from aurora.subsystems.planning.io.updater import update_planning_document
from aurora.subsystems.planning.models import (
    ExecutionStatus,
    Initiative,
    Phase,
    Step,
)
from aurora.subsystems.planning.services.lifecycle import (
    PlanningLifecycleError,
    activate_step_hierarchy,
    reopen_initiative,
)
from aurora.subsystems.planning.services.time_tracking import (
    PlanningTimeTrackingError,
    get_executable_step,
)


class PlanningRemediationError(RuntimeError):
    """Raised when bounded remedial Planning work cannot be established."""


@dataclass(frozen=True)
class PlanningRemediationResult:
    """Identity of one controlled interruption and its remedial work."""

    interrupted_step_id: int
    interrupted_phase_id: int
    initiative_id: int
    remedial_phase_id: int
    remedial_step_id: int


@dataclass(frozen=True)
class PlanningCompletedInitiativeRemediationResult:
    """Identity of one reopened Initiative and its corrective Planning work."""

    initiative_id: int
    remedial_phase_id: int
    remedial_step_id: int


def _require_planned_remedial_phase(
    phase_definition: dict[str, Any],
) -> dict[str, Any]:
    """Validate lifecycle-safe shape before handing data to the Planning updater."""

    if not isinstance(phase_definition, dict):
        raise PlanningRemediationError(
            "remedial_phase must be a Planning Phase dictionary."
        )

    phase = deepcopy(phase_definition)
    title = str(phase.get("title") or "").strip()

    if not title:
        raise PlanningRemediationError(
            "The remedial Phase requires a title."
        )

    phase["title"] = title
    phase_status = str(
        phase.get("status") or ExecutionStatus.PLANNED
    ).strip().upper()

    if phase_status != ExecutionStatus.PLANNED:
        raise PlanningRemediationError(
            "A remedial Phase must enter Planning as PLANNED."
        )

    phase["status"] = ExecutionStatus.PLANNED

    steps = phase.get("steps")
    if not isinstance(steps, list) or not steps:
        raise PlanningRemediationError(
            "A remedial Phase requires at least one bounded Step."
        )

    for step in steps:
        if not isinstance(step, dict):
            raise PlanningRemediationError(
                "Every remedial Step must be a Planning Step dictionary."
            )

        step_status = str(
            step.get("status") or ExecutionStatus.PLANNED
        ).strip().upper()

        if step_status != ExecutionStatus.PLANNED:
            raise PlanningRemediationError(
                "Every remedial Step must enter Planning as PLANNED."
            )

        step["status"] = ExecutionStatus.PLANNED

    return phase


def start_remedial_phase(
    user,
    *,
    blocked_step: Step,
    remedial_phase: dict[str, Any],
) -> PlanningRemediationResult:
    """
    Append and activate one remedial Phase inside the current Initiative.

    The current executable Step is the interruption anchor. The caller may not
    redirect remediation to unrelated Planning work.

    Existing lifecycle behavior preserves the interrupted resume state:
    activating the remedial Phase pauses the previous ACTIVE Phase, and later
    normal Initiative work establishment returns to the earliest unfinished
    Phase and its retained ACTIVE/PAUSED resume Step.
    """

    if not user or not getattr(user, "is_authenticated", False):
        raise PlanningRemediationError(
            "An authenticated user is required to establish remedial work."
        )

    if blocked_step is None or not getattr(blocked_step, "pk", None):
        raise PlanningRemediationError(
            "A persisted blocked Step is required."
        )

    normalized_phase = _require_planned_remedial_phase(remedial_phase)

    try:
        with transaction.atomic():
            current_step = get_executable_step(user)
            locked_step = (
                Step.objects
                .select_for_update()
                .select_related(
                    "phase__initiative__project",
                )
                .get(pk=current_step.pk)
            )

            if locked_step.pk != blocked_step.pk:
                raise PlanningRemediationError(
                    "Remediation may target only the lifecycle-authoritative "
                    "current Step."
                )

            initiative = locked_step.phase.initiative
            project = initiative.project

            document = {
                "schema_version": 1,
                "target": {
                    "project_slug": project.slug,
                },
                "add_projects": [],
                "add_initiatives": [],
                "add_phases": [
                    {
                        "initiative_title": initiative.title,
                        "phases": [
                            normalized_phase,
                        ],
                    },
                ],
                "add_steps": [],
            }

            update_planning_document(
                document,
                user=user,
                apply=True,
            )

            remedial = (
                Phase.objects
                .select_for_update()
                .get(
                    initiative=initiative,
                    title=normalized_phase["title"],
                )
            )

            first_step = (
                remedial.steps
                .order_by("position", "pk")
                .first()
            )

            if first_step is None:
                raise PlanningRemediationError(
                    "The appended remedial Phase has no executable Step."
                )

            activated_step = activate_step_hierarchy(
                first_step,
                user,
            )

            return PlanningRemediationResult(
                interrupted_step_id=locked_step.pk,
                interrupted_phase_id=locked_step.phase_id,
                initiative_id=initiative.pk,
                remedial_phase_id=remedial.pk,
                remedial_step_id=activated_step.pk,
            )

    except PlanningRemediationError:
        raise
    except (
        PlanningImportError,
        PlanningSchemaError,
        PlanningLifecycleError,
        PlanningTimeTrackingError,
    ) as exc:
        raise PlanningRemediationError(
            str(exc)
        ) from exc


def reopen_initiative_with_remedial_phase(
    user,
    *,
    initiative: Initiative,
    remedial_phase: dict[str, Any],
) -> PlanningCompletedInitiativeRemediationResult:
    """
    Reopen one prematurely completed Initiative and establish remedial work.

    The caller owns the evidence establishing that completion is invalid.
    Planning owns the lifecycle correction, remedial hierarchy creation, and
    activation of the new executable path.
    """

    if not user or not getattr(user, "is_authenticated", False):
        raise PlanningRemediationError(
            "An authenticated user is required to establish remedial work."
        )

    if initiative is None or not getattr(initiative, "pk", None):
        raise PlanningRemediationError(
            "A persisted Initiative is required."
        )

    normalized_phase = _require_planned_remedial_phase(
        remedial_phase
    )

    try:
        with transaction.atomic():
            locked_initiative = (
                Initiative.objects
                .select_for_update()
                .select_related("project")
                .get(pk=initiative.pk)
            )

            if locked_initiative.assigned_to_id != user.pk:
                raise PlanningRemediationError(
                    "The Initiative is not assigned to this user."
                )

            reopen_initiative(
                locked_initiative
            )

            document = {
                "schema_version": 1,
                "target": {
                    "project_slug": locked_initiative.project.slug,
                },
                "add_projects": [],
                "add_initiatives": [],
                "add_phases": [
                    {
                        "initiative_title": locked_initiative.title,
                        "phases": [
                            normalized_phase,
                        ],
                    },
                ],
                "add_steps": [],
            }

            update_planning_document(
                document,
                user=user,
                apply=True,
            )

            remedial = (
                Phase.objects
                .select_for_update()
                .get(
                    initiative=locked_initiative,
                    title=normalized_phase["title"],
                )
            )

            first_step = (
                remedial.steps
                .order_by("position", "pk")
                .first()
            )

            if first_step is None:
                raise PlanningRemediationError(
                    "The appended remedial Phase has no executable Step."
                )

            activated_step = activate_step_hierarchy(
                first_step,
                user,
            )

            return PlanningCompletedInitiativeRemediationResult(
                initiative_id=locked_initiative.pk,
                remedial_phase_id=remedial.pk,
                remedial_step_id=activated_step.pk,
            )

    except PlanningRemediationError:
        raise
    except (
        PlanningImportError,
        PlanningSchemaError,
        PlanningLifecycleError,
    ) as exc:
        raise PlanningRemediationError(
            str(exc)
        ) from exc


# ======================================================================
# END: PLANNING_BLOCKING_REMEDIATION_WORKFLOW
# ======================================================================
