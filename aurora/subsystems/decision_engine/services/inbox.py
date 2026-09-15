# ======================================================================
# FILE: aurora/subsystems/decision_engine/services/inbox.py
# START: DECISION_ENGINE_RAW_INBOX
# ======================================================================

from aurora.subsystems.decision_engine.models import (
    DecisionEngineDisposition,
    DecisionEngineIntakeDisposition,
)
from aurora.subsystems.delta_notes.services import (
    get_unprocessed_notes_for_organization,
)
from aurora.subsystems.engineering_discovery.services import (
    get_unresolved_findings_for_organization,
)


TERMINAL_DISPOSITIONS = {
    DecisionEngineDisposition.WORK_COMMITTED,
    DecisionEngineDisposition.REJECTED,
    DecisionEngineDisposition.WITHDRAWN,
}


def _terminal_source_keys(items) -> set[tuple[str, int]]:
    if not items:
        return set()

    source_types = {str(item["source_type"]) for item in items}
    source_ids = {int(item["source_id"]) for item in items}

    return set(
        DecisionEngineIntakeDisposition.objects
        .filter(
            source_type__in=source_types,
            source_id__in=source_ids,
            disposition__in=TERMINAL_DISPOSITIONS,
        )
        .values_list("source_type", "source_id")
    )


def get_raw_decision_engine_inbox(user) -> dict[str, object]:
    """Aggregate authorized actionable organizational evidence without mutation."""

    notes = get_unprocessed_notes_for_organization(user)
    findings = get_unresolved_findings_for_organization(user)

    items = [
        {
            "source_type": "DELTA_NOTE",
            "source_id": note["note_id"],
            "created_at": note["created_at"],
            "source_record": note,
        }
        for note in notes
    ]
    items.extend(
        {
            "source_type": "ENGINEERING_FINDING",
            "source_id": finding["finding_id"],
            "created_at": finding["created_at"],
            "source_record": finding,
        }
        for finding in findings
    )

    terminal_keys = _terminal_source_keys(items)
    items = [
        item
        for item in items
        if (str(item["source_type"]), int(item["source_id"])) not in terminal_keys
    ]

    items.sort(
        key=lambda item: (
            str(item["created_at"]),
            str(item["source_type"]),
            str(item["source_id"]),
        ),
        reverse=True,
    )

    delta_count = sum(item["source_type"] == "DELTA_NOTE" for item in items)
    finding_count = sum(
        item["source_type"] == "ENGINEERING_FINDING" for item in items
    )

    return {
        "counts": {
            "total": len(items),
            "delta_notes": delta_count,
            "engineering_findings": finding_count,
        },
        "items": items,
    }


# ======================================================================
# END: DECISION_ENGINE_RAW_INBOX
# ======================================================================
