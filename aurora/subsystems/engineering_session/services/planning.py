# ======================================================================
# FILE: aurora/subsystems/engineering_session/services/planning.py
# START: ENGINEERING_SESSION_PLANNING_HANDOFF
# ======================================================================

from dataclasses import dataclass
from typing import Any

from aurora.models import DeltaNotesEntry
from aurora.subsystems.engineering_session.services.delta_notes import (
    resolve_delta_note,
)
from aurora.subsystems.planning.io.updater import (
    PlanningUpdateResult,
    update_planning_document,
)
from aurora.subsystems.planning.services import (
    PlanningGenerationResult,
    generate_planning_update,
)


class EngineeringSessionPlanningError(RuntimeError):
    """Raised when a session-level Planning handoff is invalid."""


@dataclass(frozen=True)
class DeltaNotePlanningProposal:
    """One validated Planning proposal derived from a Delta Note."""

    note_id: int
    note_text: str
    project_slug: str
    document: dict[str, Any]
    validation: PlanningUpdateResult


@dataclass(frozen=True)
class DeltaNotePlanningApplication:
    """Result of applying an approved Delta Note Planning proposal."""

    note_id: int
    project_slug: str
    validation: PlanningUpdateResult
    application: PlanningUpdateResult
    note_resolved: bool


def propose_delta_note_planning(
    *,
    note: DeltaNotesEntry,
    project_slug: str,
    user,
) -> DeltaNotePlanningProposal:
    """
    Generate a validated Planning proposal from one unresolved Delta Note.

    This service never applies Planning mutations and never resolves the
    Delta Note.
    """

    _validate_delta_note_handoff(
        note=note,
        user=user,
    )

    slug = _require_project_slug(
        project_slug
    )

    result: PlanningGenerationResult = generate_planning_update(
        engineering_intent=note.text,
        project_slug=slug,
        user=user,
    )

    return DeltaNotePlanningProposal(
        note_id=note.pk,
        note_text=note.text,
        project_slug=slug,
        document=result.document,
        validation=result.validation,
    )


def apply_delta_note_planning(
    *,
    note: DeltaNotesEntry,
    document: dict[str, Any],
    user,
) -> DeltaNotePlanningApplication:
    """
    Revalidate and apply one approved Planning proposal.

    The Delta Note is resolved only after the Planning mutation succeeds.
    """

    _validate_delta_note_handoff(
        note=note,
        user=user,
    )

    if not isinstance(document, dict):
        raise EngineeringSessionPlanningError(
            "A Planning dictionary is required."
        )

    validation = update_planning_document(
        document,
        user=user,
        apply=False,
    )

    application = update_planning_document(
        document,
        user=user,
        apply=True,
    )

    resolve_delta_note(note)

    note.refresh_from_db()

    return DeltaNotePlanningApplication(
        note_id=note.pk,
        project_slug=application.project_slug,
        validation=validation,
        application=application,
        note_resolved=note.processed,
    )


def _validate_delta_note_handoff(
    *,
    note: DeltaNotesEntry,
    user,
) -> None:
    """Validate ownership and unresolved state for one Delta Note."""

    if note is None or not note.pk:
        raise EngineeringSessionPlanningError(
            "A persisted Delta Note is required."
        )

    if user is None or not user.pk:
        raise EngineeringSessionPlanningError(
            "A persisted user is required."
        )

    if note.user_id != user.pk:
        raise EngineeringSessionPlanningError(
            "The Delta Note does not belong to this user."
        )

    if note.processed:
        raise EngineeringSessionPlanningError(
            "A processed Delta Note cannot be sent to Planning."
        )


def _require_project_slug(
    project_slug: str,
) -> str:
    """Return one non-empty target Project slug."""

    slug = project_slug.strip()

    if not slug:
        raise EngineeringSessionPlanningError(
            "Target Project slug is required."
        )

    return slug


# ======================================================================
# END: ENGINEERING_SESSION_PLANNING_HANDOFF
# ======================================================================