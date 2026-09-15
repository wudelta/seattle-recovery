# ======================================================================
# FILE: aurora/subsystems/decision_engine/services/reconciliation.py
# START: DECISION_ENGINE_RECONCILIATION_SERVICE
# ======================================================================

from collections.abc import Mapping, Sequence

from django.db import transaction

from aurora.access import can_reconcile_decision_engine
from aurora.subsystems.decision_engine.models import (
    DecisionEngineDisposition,
    DecisionEngineIntakeDisposition,
    DecisionEngineSourceType,
)
from aurora.subsystems.decision_engine.services.work import (
    create_decision_engine_work,
)
from aurora.subsystems.delta_notes.models import DeltaNotesEntry
from aurora.subsystems.engineering_discovery.models import (
    EngineeringFinding,
    EngineeringFindingResolutionState,
)


class DecisionEngineReconciliationError(ValueError):
    """Raised when selected organizational intake cannot be committed safely."""


def _required_text(value, *, field_name: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise DecisionEngineReconciliationError(f"{field_name} is required.")
    return normalized


def _normalize_sources(sources) -> list[dict[str, object]]:
    if (
        not isinstance(sources, Sequence)
        or isinstance(sources, (str, bytes))
        or not sources
    ):
        raise DecisionEngineReconciliationError(
            "At least one selected intake source is required."
        )

    normalized = []
    seen = set()

    for source in sources:
        if not isinstance(source, Mapping):
            raise DecisionEngineReconciliationError(
                "Each selected intake source must be an object."
            )

        source_type = str(source.get("source_type", "")).strip()
        raw_source_id = source.get("source_id")

        if source_type not in DecisionEngineSourceType.values:
            raise DecisionEngineReconciliationError(
                f"Unsupported Decision Engine source type: {source_type or 'missing'}."
            )

        try:
            source_id = int(raw_source_id)
        except (TypeError, ValueError) as exc:
            raise DecisionEngineReconciliationError(
                "Each selected intake source requires a valid source_id."
            ) from exc

        if source_id <= 0:
            raise DecisionEngineReconciliationError(
                "Each selected intake source requires a positive source_id."
            )

        if source.get("scope_confirmed") is not True:
            raise DecisionEngineReconciliationError(
                "Every selected intake item must be explicitly confirmed as "
                "belonging entirely to this one body of work. Mixed or ambiguous "
                "scope requires human mitigation before commit."
            )

        key = (source_type, source_id)
        if key in seen:
            raise DecisionEngineReconciliationError(
                f"Duplicate selected intake source: {source_type}:{source_id}."
            )

        seen.add(key)
        normalized.append({"source_type": source_type, "source_id": source_id})

    return normalized


def _existing_disposition(*, source_type: str, source_id: int):
    existing = (
        DecisionEngineIntakeDisposition.objects
        .select_for_update()
        .filter(source_type=source_type, source_id=source_id)
        .first()
    )
    if existing is not None:
        raise DecisionEngineReconciliationError(
            f"{source_type}:{source_id} already has Decision Engine disposition "
            f"{existing.disposition}."
        )


def _lock_source(user, *, source_type: str, source_id: int):
    if source_type == DecisionEngineSourceType.DELTA_NOTE:
        try:
            note = (
                DeltaNotesEntry.objects
                .select_for_update()
                .select_related("user")
                .get(pk=source_id, user=user, processed=False)
            )
        except DeltaNotesEntry.DoesNotExist as exc:
            raise DecisionEngineReconciliationError(
                f"Delta Note {source_id} is no longer authorized actionable intake."
            ) from exc

        _existing_disposition(source_type=source_type, source_id=source_id)
        return {
            "source_type": source_type,
            "source_id": source_id,
            "delta_note": note,
            "engineering_finding": None,
        }

    try:
        finding = (
            EngineeringFinding.objects
            .select_for_update()
            .get(
                pk=source_id,
                resolution_state=EngineeringFindingResolutionState.UNRESOLVED,
            )
        )
    except EngineeringFinding.DoesNotExist as exc:
        raise DecisionEngineReconciliationError(
            f"Engineering Finding {source_id} is no longer actionable intake."
        ) from exc

    _existing_disposition(source_type=source_type, source_id=source_id)
    return {
        "source_type": source_type,
        "source_id": source_id,
        "delta_note": None,
        "engineering_finding": finding,
    }


def commit_selected_intake_to_work(
    user,
    *,
    title,
    description,
    reason,
    sources,
) -> dict[str, object]:
    """Commit one explicitly authorized selected intake set to durable work."""

    if not can_reconcile_decision_engine(user):
        raise DecisionEngineReconciliationError(
            "Initiative-owner Decision Engine reconciliation authority is required."
        )

    normalized_title = _required_text(title, field_name="title")
    normalized_description = _required_text(description, field_name="description")
    normalized_reason = _required_text(reason, field_name="reason")
    normalized_sources = _normalize_sources(sources)

    with transaction.atomic():
        locked_sources = [
            _lock_source(
                user,
                source_type=source["source_type"],
                source_id=source["source_id"],
            )
            for source in normalized_sources
        ]

        work = create_decision_engine_work(
            user,
            title=normalized_title,
            description=normalized_description,
        )

        committed_sources = []
        for source in locked_sources:
            note = source["delta_note"]
            finding = source["engineering_finding"]

            disposition = DecisionEngineIntakeDisposition.objects.create(
                source_type=source["source_type"],
                source_id=source["source_id"],
                delta_note=note,
                engineering_finding=finding,
                disposition=DecisionEngineDisposition.WORK_COMMITTED,
                resolving_work=work,
                authorized_by=user,
                reason=normalized_reason,
            )

            if note is not None:
                note.processed = True
                note.save(update_fields=["processed", "updated_at"])

            committed_sources.append(
                {
                    "source_type": source["source_type"],
                    "source_id": source["source_id"],
                    "disposition_id": disposition.pk,
                }
            )

    return {
        "work": {
            "id": work.pk,
            "title": work.title,
            "description": work.description,
            "created_by": work.created_by.username,
            "created_at": work.created_at.isoformat(),
        },
        "committed_sources": committed_sources,
    }


# ======================================================================
# END: DECISION_ENGINE_RECONCILIATION_SERVICE
# ======================================================================
