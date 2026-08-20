# ======================================================================
# FILE: aurora/subsystems/engineering_session/services/delta_notes.py
# START: ENGINEERING_SESSION_DELTA_NOTES_SERVICE
# ======================================================================

from aurora.models import DeltaNotesEntry


def get_next_unprocessed_delta_note(user):
    """Return the user's oldest unprocessed Delta Note."""

    return (
        DeltaNotesEntry.objects
        .filter(
            user=user,
            processed=False,
        )
        .order_by(
            "created_at",
            "pk",
        )
        .first()
    )


def resolve_delta_note(note: DeltaNotesEntry) -> None:
    """
    Mark one Delta Note resolved after its disposition has succeeded.

    Planning or other owning subsystems must complete their mutation before
    this function is called.
    """

    if note is None or not note.pk:
        return

    note.processed = True
    note.save(
        update_fields=[
            "processed",
        ]
    )

# ======================================================================
# END: ENGINEERING_SESSION_DELTA_NOTES_SERVICE
# ======================================================================