# ======================================================================
# FILE: aurora/subsystems/hansel/services/trails.py
# START: HANSEL_TRAIL_SERVICE
# ======================================================================

from collections.abc import Iterable

from django.db import transaction
from django.utils import timezone

from aurora.models import (
    HanselTrail,
    HanselTrailAuthority,
    HanselTrailOutcome,
)
from aurora.subsystems.planning.services import (
    get_executable_step,
)


class HanselTrailError(RuntimeError):
    """Raised when a Hansel trail transition is invalid."""


TERMINAL_OUTCOMES = frozenset(
    {
        HanselTrailOutcome.SUFFICIENT,
        HanselTrailOutcome.INCOMPLETE,
        HanselTrailOutcome.BROKEN,
        HanselTrailOutcome.REDISCOVERED,
    }
)


def start_hansel_trail(
    user,
) -> HanselTrail:
    """
    Start repository-authority discovery for the executable Planning Step.

    An already-open trail for the same Step is returned idempotently.
    An open trail for another Step is treated as stale workflow state and
    must be resolved explicitly before another trail begins.
    """

    if not user or not getattr(user, "is_authenticated", False):
        raise HanselTrailError(
            "An authenticated user is required to start a Hansel trail."
        )

    step = get_executable_step(
        user
    )

    with transaction.atomic():
        open_trail = (
            HanselTrail.objects
            .select_for_update()
            .filter(
                user=user,
                outcome=HanselTrailOutcome.IN_PROGRESS,
                ended_at__isnull=True,
            )
            .select_related(
                "step",
            )
            .order_by(
                "-started_at",
                "-pk",
            )
            .first()
        )

        if open_trail is not None:
            if open_trail.step_id == step.pk:
                return open_trail

            raise HanselTrailError(
                "An IN_PROGRESS Hansel trail already exists for another "
                f"Planning Step: {open_trail.step.title}."
            )

        return HanselTrail.objects.create(
            user=user,
            step=step,
        )


def complete_hansel_trail(
    *,
    trail_id: int,
    user,
    outcome: str,
    authority_paths: Iterable[str] = (),
    notes: str = "",
) -> HanselTrail:
    """
    Close one Hansel trail with its observed discovery outcome.

    Trail completion records repository authorities actually reached. It does
    not mutate Planning lifecycle state or Planning TimeEntry state.
    """

    if not user or not getattr(user, "is_authenticated", False):
        raise HanselTrailError(
            "An authenticated user is required to complete a Hansel trail."
        )

    normalized_outcome = str(
        outcome
    ).strip().upper()

    if normalized_outcome not in TERMINAL_OUTCOMES:
        raise HanselTrailError(
            "Hansel trail outcome must be one of: "
            "SUFFICIENT, INCOMPLETE, BROKEN, REDISCOVERED."
        )

    normalized_paths = _normalize_authority_paths(
        authority_paths
    )

    if (
        normalized_outcome == HanselTrailOutcome.SUFFICIENT
        and not normalized_paths
    ):
        raise HanselTrailError(
            "A SUFFICIENT Hansel trail must record at least one "
            "repository authority."
        )

    normalized_notes = str(
        notes
    ).strip()

    with transaction.atomic():
        trail = (
            HanselTrail.objects
            .select_for_update()
            .select_related(
                "step",
            )
            .get(
                pk=trail_id,
            )
        )

        if trail.user_id != user.pk:
            raise HanselTrailError(
                "This Hansel trail does not belong to the authenticated user."
            )

        if (
            trail.outcome != HanselTrailOutcome.IN_PROGRESS
            or trail.ended_at is not None
        ):
            raise HanselTrailError(
                "This Hansel trail is already closed."
            )

        for authority_path in normalized_paths:
            HanselTrailAuthority.objects.get_or_create(
                trail=trail,
                authority_path=authority_path,
            )

        trail.outcome = normalized_outcome
        trail.notes = normalized_notes
        trail.ended_at = timezone.now()
        trail.save(
            update_fields=[
                "outcome",
                "notes",
                "ended_at",
            ]
        )

    return trail


def _normalize_authority_paths(
    values: Iterable[str],
) -> tuple[str, ...]:
    """Return unique nonblank authority paths while preserving order."""

    normalized: list[str] = []
    seen: set[str] = set()

    for value in values:
        path = str(
            value
        ).strip()

        if not path or path in seen:
            continue

        seen.add(
            path
        )
        normalized.append(
            path
        )

    return tuple(
        normalized
    )


# ======================================================================
# END: HANSEL_TRAIL_SERVICE
# ======================================================================