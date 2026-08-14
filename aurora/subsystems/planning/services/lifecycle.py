# ======================================================================
# FILE: aurora/subsystems/planning/services/lifecycle.py
# START: PLANNING_LIFECYCLE_SERVICE
# ======================================================================

from django.db import transaction

from aurora.models import (
    ExecutionStatus,
    Initiative,
    Phase,
    Step,
)


class PlanningLifecycleError(RuntimeError):
    """Raised when a Planning lifecycle transition is invalid."""


def activate_initiative(initiative: Initiative) -> Initiative:
    """
    Make one Initiative the current ACTIVE Initiative for its assignee.

    Any other ACTIVE Initiative assigned to the same user is PAUSED.

    Child Phase and Step statuses are intentionally preserved so a paused
    Initiative retains its internal resume position.
    """

    if initiative is None or not initiative.pk:
        raise PlanningLifecycleError(
            "A persisted Initiative is required."
        )

    if initiative.status == ExecutionStatus.COMPLETED:
        raise PlanningLifecycleError(
            "A completed Initiative cannot be activated."
        )

    if initiative.status == ExecutionStatus.CANCELLED:
        raise PlanningLifecycleError(
            "A cancelled Initiative cannot be activated."
        )

    with transaction.atomic():
        locked = (
            Initiative.objects
            .select_for_update()
            .select_related("assigned_to")
            .get(pk=initiative.pk)
        )

        conflicts = (
            Initiative.objects
            .select_for_update()
            .filter(
                assigned_to=locked.assigned_to,
                status=ExecutionStatus.ACTIVE,
            )
            .exclude(pk=locked.pk)
        )

        conflicts.update(
            status=ExecutionStatus.PAUSED,
        )

        if locked.status != ExecutionStatus.ACTIVE:
            locked.status = ExecutionStatus.ACTIVE
            locked.save(
                update_fields=[
                    "status",
                ]
            )

    return locked


def pause_initiative(initiative: Initiative) -> Initiative:
    """
    Pause one Initiative without changing its child lifecycle state.

    ACTIVE Phase and Step records remain intact as the Initiative's saved
    resume position.
    """

    if initiative is None or not initiative.pk:
        raise PlanningLifecycleError(
            "A persisted Initiative is required."
        )

    with transaction.atomic():
        locked = (
            Initiative.objects
            .select_for_update()
            .get(pk=initiative.pk)
        )

        if locked.status != ExecutionStatus.ACTIVE:
            raise PlanningLifecycleError(
                "Only an ACTIVE Initiative can be paused."
            )

        locked.status = ExecutionStatus.PAUSED
        locked.save(
            update_fields=[
                "status",
            ]
        )

    return locked


def activate_phase(phase: Phase) -> Phase:
    """
    Make one Phase the ACTIVE resume Phase within its Initiative.

    Any other ACTIVE Phase in the same Initiative is PAUSED.

    Step statuses are preserved so a paused Phase retains its internal
    resume Step.
    """

    if phase is None or not phase.pk:
        raise PlanningLifecycleError(
            "A persisted Phase is required."
        )

    if phase.status == ExecutionStatus.COMPLETED:
        raise PlanningLifecycleError(
            "A completed Phase cannot be activated."
        )

    if phase.status == ExecutionStatus.CANCELLED:
        raise PlanningLifecycleError(
            "A cancelled Phase cannot be activated."
        )

    with transaction.atomic():
        locked = (
            Phase.objects
            .select_for_update()
            .select_related("initiative")
            .get(pk=phase.pk)
        )

        conflicts = (
            Phase.objects
            .select_for_update()
            .filter(
                initiative=locked.initiative,
                status=ExecutionStatus.ACTIVE,
            )
            .exclude(pk=locked.pk)
        )

        conflicts.update(
            status=ExecutionStatus.PAUSED,
        )

        if locked.status != ExecutionStatus.ACTIVE:
            locked.status = ExecutionStatus.ACTIVE
            locked.save(
                update_fields=[
                    "status",
                ]
            )

    return locked


def pause_phase(phase: Phase) -> Phase:
    """
    Pause one Phase without changing its child Step lifecycle state.
    """

    if phase is None or not phase.pk:
        raise PlanningLifecycleError(
            "A persisted Phase is required."
        )

    with transaction.atomic():
        locked = (
            Phase.objects
            .select_for_update()
            .get(pk=phase.pk)
        )

        if locked.status != ExecutionStatus.ACTIVE:
            raise PlanningLifecycleError(
                "Only an ACTIVE Phase can be paused."
            )

        locked.status = ExecutionStatus.PAUSED
        locked.save(
            update_fields=[
                "status",
            ]
        )

    return locked


def activate_step(step: Step) -> Step:
    """
    Make one Step the ACTIVE resume Step within its Phase.

    Any other ACTIVE Step in the same Phase is PAUSED.

    Activation changes Planning lifecycle state only. It does not create
    a TimeEntry or imply that timed work has begun.
    """

    if step is None or not step.pk:
        raise PlanningLifecycleError(
            "A persisted Step is required."
        )

    if step.status == ExecutionStatus.COMPLETED:
        raise PlanningLifecycleError(
            "A completed Step cannot be activated."
        )

    if step.status == ExecutionStatus.CANCELLED:
        raise PlanningLifecycleError(
            "A cancelled Step cannot be activated."
        )

    with transaction.atomic():
        locked = (
            Step.objects
            .select_for_update()
            .select_related("phase")
            .get(pk=step.pk)
        )

        conflicts = (
            Step.objects
            .select_for_update()
            .filter(
                phase=locked.phase,
                status=ExecutionStatus.ACTIVE,
            )
            .exclude(pk=locked.pk)
        )

        conflicts.update(
            status=ExecutionStatus.PAUSED,
        )

        if locked.status != ExecutionStatus.ACTIVE:
            locked.status = ExecutionStatus.ACTIVE
            locked.save(
                update_fields=[
                    "status",
                ]
            )

    return locked


def pause_step(step: Step) -> Step:
    """Pause one ACTIVE Step."""

    if step is None or not step.pk:
        raise PlanningLifecycleError(
            "A persisted Step is required."
        )

    with transaction.atomic():
        locked = (
            Step.objects
            .select_for_update()
            .get(pk=step.pk)
        )

        if locked.status != ExecutionStatus.ACTIVE:
            raise PlanningLifecycleError(
                "Only an ACTIVE Step can be paused."
            )

        locked.status = ExecutionStatus.PAUSED
        locked.save(
            update_fields=[
                "status",
            ]
        )

    return locked

# ======================================================================
# FILE: aurora/subsystems/planning/services/lifecycle.py
# END: PLANNING_LIFECYCLE_SERVICE
# ======================================================================