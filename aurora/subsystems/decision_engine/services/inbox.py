# ======================================================================
# FILE: aurora/subsystems/decision_engine/services/inbox.py
# START: DECISION_ENGINE_RAW_INBOX
# ======================================================================

from aurora.subsystems.delta_notes.services import (
    get_unprocessed_notes_for_organization,
)
from aurora.subsystems.engineering_discovery.services import (
    get_unresolved_findings_for_organization,
)


def get_raw_decision_engine_inbox(user) -> dict[str, object]:
    """Aggregate raw organizational evidence without mutating source records."""

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
    items.sort(
        key=lambda item: (
            str(item["created_at"]),
            str(item["source_type"]),
            str(item["source_id"]),
        ),
        reverse=True,
    )

    return {
        "counts": {
            "total": len(items),
            "delta_notes": len(notes),
            "engineering_findings": len(findings),
        },
        "items": items,
    }


# ======================================================================
# END: DECISION_ENGINE_RAW_INBOX
# ======================================================================
