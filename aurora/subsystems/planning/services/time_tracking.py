# ======================================================================
# FILE: aurora/subsystems/planning/services/time_tracking.py
# START: PLANNING_STEP_TIME_TRACKING_SERVICE
# ======================================================================

from django.db import transaction
from django.utils import timezone

from aurora.models import TimeEntry, UserPosition


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


def start_step_work(user) -> TimeEntry:
    """
    Start time tracking for the user's currently selected Planning Step.

    A Step must already be selected through Planning.UserPosition.
    The service never infers or automatically selects work.
    """

    if not user or not getattr(user, "is_authenticated", False):
        raise PlanningTimeTrackingError(
            "An authenticated user is required to start Step work."
        )

    existing = get_active_time_entry(user)

    if existing is not None:
        return existing

    position = (
        UserPosition.objects
        .select_related("step")
        .filter(user=user)
        .first()
    )

    if position is None or position.step is None:
        raise PlanningTimeTrackingError(
            "No Planning Step is currently selected."
        )

    with transaction.atomic():
        return TimeEntry.objects.create(
            user=user,
            step=position.step,
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
# FILE: aurora/subsystems/planning/services/time_tracking.py
# END: PLANNING_STEP_TIME_TRACKING_SERVICE
# ======================================================================