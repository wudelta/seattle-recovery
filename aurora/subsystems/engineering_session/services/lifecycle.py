# ======================================================================
# FILE: aurora/subsystems/engineering_session/services/lifecycle.py
# START: ENGINEERING_SESSION_LIFECYCLE_SERVICE
# ======================================================================

from django.db import transaction
from django.utils import timezone

from aurora.models import EngineeringSession


class EngineeringSessionError(RuntimeError):
    """Raised when an engineering-session lifecycle transition is invalid."""


def start_session(user) -> EngineeringSession:
    """
    Start one engineering session for an authenticated user.

    A user may have at most one open EngineeringSession at a time.
    """

    if not user or not getattr(user, "is_authenticated", False):
        raise EngineeringSessionError(
            "An authenticated user is required to start an engineering session."
        )

    existing = (
        EngineeringSession.objects
        .filter(
            user=user,
            ended_at__isnull=True,
        )
        .order_by("-started_at")
        .first()
    )

    if existing is not None:
        return existing

    with transaction.atomic():
        return EngineeringSession.objects.create(
            user=user,
            started_at=timezone.now(),
        )


def end_session(user) -> EngineeringSession:
    """
    End the user's active engineering session.

    Raises when no open session exists.
    """

    if not user or not getattr(user, "is_authenticated", False):
        raise EngineeringSessionError(
            "An authenticated user is required to end an engineering session."
        )

    with transaction.atomic():
        session = (
            EngineeringSession.objects
            .select_for_update()
            .filter(
                user=user,
                ended_at__isnull=True,
            )
            .order_by("-started_at")
            .first()
        )

        if session is None:
            raise EngineeringSessionError(
                "No active engineering session exists."
            )

        session.ended_at = timezone.now()
        session.save(
            update_fields=[
                "ended_at",
            ]
        )

    return session


def get_active_session(user) -> EngineeringSession | None:
    """Return the user's current open engineering session, if one exists."""

    if not user or not getattr(user, "is_authenticated", False):
        return None

    return (
        EngineeringSession.objects
        .filter(
            user=user,
            ended_at__isnull=True,
        )
        .order_by("-started_at")
        .first()
    )

# ======================================================================
# FILE: aurora/subsystems/engineering_session/services/lifecycle.py
# END: ENGINEERING_SESSION_LIFECYCLE_SERVICE
# ======================================================================