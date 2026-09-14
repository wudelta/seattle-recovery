# ======================================================================
# FILE: aurora/subsystems/decision_engine/services/work.py
# START: DECISION_ENGINE_WORK_PERSISTENCE_SERVICE
# ======================================================================

from django.db import transaction

from aurora.subsystems.decision_engine.models import DecisionEngineWork


class DecisionEngineWorkPersistenceError(ValueError):
    """Raised when durable Decision Engine work cannot be persisted or read."""


def _normalize_required_text(value, *, field_name: str) -> str:
    normalized = str(value or "").strip()

    if not normalized:
        raise DecisionEngineWorkPersistenceError(
            f"{field_name} is required."
        )

    return normalized


def create_decision_engine_work(
    user,
    *,
    title,
    description,
) -> DecisionEngineWork:
    """
    Persist one durable organization-level body of work.

    This is the low-level Decision Engine persistence boundary. It does not
    select intake, mutate source records, approve Planning work, or create
    Planning hierarchy.
    """

    if not user or not getattr(user, "is_authenticated", False):
        raise DecisionEngineWorkPersistenceError(
            "An authenticated user is required to create Decision Engine work."
        )

    normalized_title = _normalize_required_text(
        title,
        field_name="title",
    )
    normalized_description = _normalize_required_text(
        description,
        field_name="description",
    )

    with transaction.atomic():
        return DecisionEngineWork.objects.create(
            title=normalized_title,
            description=normalized_description,
            created_by=user,
        )


def get_decision_engine_work(work_id) -> DecisionEngineWork:
    """Return one persisted DecisionEngineWork by primary key."""

    try:
        return DecisionEngineWork.objects.select_related(
            "created_by"
        ).get(pk=work_id)
    except (DecisionEngineWork.DoesNotExist, TypeError, ValueError) as exc:
        raise DecisionEngineWorkPersistenceError(
            "Decision Engine work could not be resolved."
        ) from exc


# ======================================================================
# END: DECISION_ENGINE_WORK_PERSISTENCE_SERVICE
# ======================================================================
