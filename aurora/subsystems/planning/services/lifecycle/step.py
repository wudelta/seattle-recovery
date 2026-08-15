# ======================================================================
# FILE: aurora/subsystems/planning/services/lifecycle/step.py
# START: PLANNING_STEP_LIFECYCLE
# ======================================================================

from django.db import transaction
from django.utils import timezone

from aurora.models import ExecutionStatus, Step, TimeEntry

from aurora.subsystems.planning.services.lifecycle.exceptions import (
    PlanningLifecycleError,
)


def activate_step(step: Step) -> Step:
    """
    Make one Step the ACTIVE resume Step within its Phase.

    Activation changes lifecycle state only. It does not start timing.
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

        (
            Step.objects
            .select_for_update()
            .filter(
                phase=locked.phase,
                status=ExecutionStatus.ACTIVE,
            )
            .exclude(pk=locked.pk)
            .update(
                status=ExecutionStatus.PAUSED,
            )
        )

        if locked.status != ExecutionStatus.ACTIVE:
            locked.status = ExecutionStatus.ACTIVE
            locked.save(
                update_fields=["status"]
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
            update_fields=["status"]
        )

    return locked


def complete_step(step: Step, user) -> Step:
    """
    Complete one Step and persist historical completion attribution.

    Any open TimeEntry for this user and Step is closed before completion.
    """

    if step is None or not step.pk:
        raise PlanningLifecycleError(
            "A persisted Step is required."
        )

    if not user or not getattr(user, "is_authenticated", False):
        raise PlanningLifecycleError(
            "An authenticated user is required to complete a Step."
        )

    with transaction.atomic():
        locked = (
            Step.objects
            .select_for_update()
            .get(pk=step.pk)
        )

        if locked.status == ExecutionStatus.COMPLETED:
            raise PlanningLifecycleError(
                "This Step is already completed."
            )

        if locked.status == ExecutionStatus.CANCELLED:
            raise PlanningLifecycleError(
                "A cancelled Step cannot be completed."
            )

        now = timezone.now()

        (
            TimeEntry.objects
            .select_for_update()
            .filter(
                user=user,
                step=locked,
                ended_at__isnull=True,
            )
            .update(
                ended_at=now,
            )
        )

        locked.status = ExecutionStatus.COMPLETED
        locked.completed_by = user
        locked.completed_at = now
        locked.save(
            update_fields=[
                "status",
                "completed_by",
                "completed_at",
            ]
        )

    return locked

# ======================================================================
# END: PLANNING_STEP_LIFECYCLE
# ======================================================================
