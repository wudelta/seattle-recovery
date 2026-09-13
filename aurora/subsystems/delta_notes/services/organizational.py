# ======================================================================
# FILE: aurora/subsystems/delta_notes/services/organizational.py
# START: DELTA_NOTES_ORGANIZATIONAL_READER
# ======================================================================

from aurora.access import can_access_aurora
from aurora.subsystems.delta_notes.models import DeltaNotesEntry


class DeltaNotesOrganizationReadError(ValueError):
    """Raised when organization-wide Delta Notes cannot be read safely."""


def get_unprocessed_notes_for_organization(user) -> list[dict[str, object]]:
    """Return all current unprocessed Delta Notes across Aurora."""

    if not can_access_aurora(user):
        raise DeltaNotesOrganizationReadError(
            "Aurora developer access is required to read organizational Delta Notes."
        )

    notes = (
        DeltaNotesEntry.objects
        .filter(processed=False)
        .select_related("user")
        .order_by("-created_at", "pk")
    )

    return [
        {
            "note_id": note.pk,
            "text": note.text,
            "author": note.user.username,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat(),
        }
        for note in notes
    ]


# ======================================================================
# END: DELTA_NOTES_ORGANIZATIONAL_READER
# ======================================================================
