# ======================================================================
# FILE: aurora/subsystems/planning/services/time_tracking.py
# START: PLANNING_STEP_TIME_TRACKING_SERVICE
# ======================================================================

from django.db import transaction
from django.utils import timezone

from aurora.models import (
    ExecutionStatus,
    Initiative,
    Phase,
    Step,
    TimeEntry,
)
from aurora.subsystems.planning.services.lifecycle import (
    PlanningLifecycleError,
    activate_initiative,
    activate_phase,
    activate_step,
)


class PlanningTimeTrackingError(RuntimeError):
    """Raised when a Planning step-time transition is invalid."""


def get_active_time_entry(user) -> TimeEntry | None:
    """Return the user's current open Planning TimeEntry, if one exists."""

    if not user or not getattr(user, "is_authenticated", False):
        return None

    return (
        TimeEntry.objects
        .filter(
            user=user,
            ended_at__isnull=True,
        )
        .select_related(
            "step",
            "step__phase",
            "step__phase__initiative",
            "step__phase__initiative__project",
        )
        .order_by("-started_at")
        .first()
    )


def get_executable_step(user) -> Step:
    """
    Resolve the user's one executable Planning Step.

    Executable work requires one ACTIVE Initiative assigned to the user,
    one ACTIVE Phase within that Initiative assigned to the user, and one
    ACTIVE Step within that Phase.

    UserPosition is intentionally not consulted.
    """

    if not user or not getattr(user, "is_authenticated", False):
        raise PlanningTimeTrackingError(
            "An authenticated user is required to resolve executable work."
        )

    initiatives = list(
        Initiative.objects
        .filter(
            assigned_to=user,
            status=ExecutionStatus.ACTIVE,
        )
        .order_by("position", "pk")
    )

    if not initiatives:
        raise PlanningTimeTrackingError(
            "No ACTIVE Initiative is assigned to this user."
        )

    if len(initiatives) > 1:
        raise PlanningTimeTrackingError(
            "Multiple ACTIVE Initiatives are assigned to this user."
        )

    initiative = initiatives[0]

    phases = list(
        Phase.objects
        .filter(
            initiative=initiative,
            assigned_to=user,
            status=ExecutionStatus.ACTIVE,
        )
        .order_by("position", "pk")
    )

    if not phases:
        raise PlanningTimeTrackingError(
            "The ACTIVE Initiative has no ACTIVE Phase assigned to this user."
        )

    if len(phases) > 1:
        raise PlanningTimeTrackingError(
            "The ACTIVE Initiative has multiple ACTIVE Phases assigned "
            "to this user."
        )

    phase = phases[0]

    steps = list(
        Step.objects
        .filter(
            phase=phase,
            status=ExecutionStatus.ACTIVE,
        )
        .order_by("position", "pk")
    )

    if not steps:
        raise PlanningTimeTrackingError(
            "The ACTIVE Phase has no ACTIVE Step."
        )

    if len(steps) > 1:
        raise PlanningTimeTrackingError(
            "The ACTIVE Phase has multiple ACTIVE Steps."
        )

    return steps[0]


def start_step_work(user) -> TimeEntry:
    """
    Resume timing for the user's already executable Planning Step.

    This compatibility operation does not choose or activate work. New work
    should begin through start_planning_work() with an explicit Step.
    """

    if not user or not getattr(user, "is_authenticated", False):
        raise PlanningTimeTrackingError(
            "An authenticated user is required to start Step work."
        )

    existing = get_active_time_entry(
        user
    )

    if existing is not None:
        return existing

    step = get_executable_step(
        user
    )

    with transaction.atomic():
        return TimeEntry.objects.create(
            user=user,
            step=step,
            started_at=timezone.now(),
        )


def end_step_work(user) -> TimeEntry:
    """Close the user's current open Planning TimeEntry."""

    if not user or not getattr(user, "is_authenticated", False):
        raise PlanningTimeTrackingError(
            "An authenticated user is required to end Step work."
        )

    with transaction.atomic():
        time_entry = (
            TimeEntry.objects
            .select_for_update()
            .filter(
                user=user,
                ended_at__isnull=True,
            )
            .select_related("step")
            .order_by("-started_at")
            .first()
        )

        if time_entry is None:
            raise PlanningTimeTrackingError(
                "No active Planning Step work interval exists."
            )

        time_entry.ended_at = timezone.now()
        time_entry.save(
            update_fields=[
                "ended_at",
            ]
        )

    return time_entry


# ======================================================================
# END: PLANNING_STEP_TIME_TRACKING_SERVICE
# ======================================================================