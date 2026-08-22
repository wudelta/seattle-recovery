# ======================================================================
# FILE: aurora/subsystems/engineering_session/services/planning.py
# START: ENGINEERING_SESSION_PLANNING_HANDOFF
# ======================================================================

from dataclasses import dataclass
from typing import Any, Iterable

from django.db import transaction

from aurora.models import (
    DeltaNotesEntry,
    Initiative,
    InitiativeSourceDeltaNote,
    Project,
)
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
    """Result of applying an approved single-note Planning proposal."""

    note_id: int
    project_slug: str
    validation: PlanningUpdateResult
    application: PlanningUpdateResult
    note_resolved: bool


@dataclass(frozen=True)
class DeltaNotesInitiativeApplication:
    """Result of one grouped Delta Note to Initiative handoff."""

    note_ids: tuple[int, ...]
    project_slug: str
    initiative_id: int
    initiative_title: str
    validation: PlanningUpdateResult
    application: PlanningUpdateResult
    provenance_links_created: int
    notes_resolved: bool


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
    Revalidate and apply one approved single-note Planning proposal.

    This compatibility workflow preserves the existing one-note behavior.

    The Delta Note is resolved only after the Planning mutation succeeds.
    """

    _validate_delta_note_handoff(
        note=note,
        user=user,
    )

    _require_planning_document(
        document
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


def apply_delta_notes_to_new_initiative(
    *,
    notes: Iterable[DeltaNotesEntry],
    document: dict[str, Any],
    user,
) -> DeltaNotesInitiativeApplication:
    """
    Apply one new-Initiative Planning handoff from one or more Delta Notes.

    The operation is atomic:

    1. validate every source Delta Note;
    2. dry-validate the Planning dictionary;
    3. apply the Planning mutation;
    4. resolve the newly created Initiative;
    5. persist Initiative-to-Delta-Note provenance;
    6. resolve every source Delta Note.

    Any failure rolls back Planning mutation, provenance, and note resolution.

    This grouped workflow intentionally requires exactly one newly added
    Initiative. It does not infer provenance for add_phases or add_steps.
    """

    source_notes = list(
        notes
    )

    _validate_delta_note_group(
        notes=source_notes,
        user=user,
    )

    _require_planning_document(
        document
    )

    initiative_title = _require_single_new_initiative_title(
        document
    )

    project_slug = _require_document_project_slug(
        document
    )

    validation = update_planning_document(
        document,
        user=user,
        apply=False,
    )

    note_ids = tuple(
        note.pk
        for note in source_notes
    )

    with transaction.atomic():
        locked_notes = list(
            DeltaNotesEntry.objects
            .select_for_update()
            .filter(
                pk__in=note_ids,
            )
            .order_by("pk")
        )

        if {
            note.pk
            for note in locked_notes
        } != set(note_ids):
            raise EngineeringSessionPlanningError(
                "One or more source Delta Notes no longer exist."
            )

        for note in locked_notes:
            _validate_delta_note_handoff(
                note=note,
                user=user,
            )

        application = update_planning_document(
            document,
            user=user,
            apply=True,
        )

        initiative = _resolve_created_initiative(
            project_slug=project_slug,
            initiative_title=initiative_title,
        )

        links_created = 0

        for note in locked_notes:
            _, created = (
                InitiativeSourceDeltaNote.objects
                .get_or_create(
                    initiative=initiative,
                    delta_note=note,
                )
            )

            if created:
                links_created += 1

        for note in locked_notes:
            resolve_delta_note(
                note
            )

        unresolved_count = (
            DeltaNotesEntry.objects
            .filter(
                pk__in=note_ids,
                processed=False,
            )
            .count()
        )

        if unresolved_count:
            raise EngineeringSessionPlanningError(
                "Planning succeeded, but one or more source "
                "Delta Notes were not resolved."
            )

    return DeltaNotesInitiativeApplication(
        note_ids=note_ids,
        project_slug=application.project_slug,
        initiative_id=initiative.pk,
        initiative_title=initiative.title,
        validation=validation,
        application=application,
        provenance_links_created=links_created,
        notes_resolved=True,
    )


def _validate_delta_note_group(
    *,
    notes: list[DeltaNotesEntry],
    user,
) -> None:
    """Validate one non-empty unique group of source Delta Notes."""

    if not notes:
        raise EngineeringSessionPlanningError(
            "At least one source Delta Note is required."
        )

    note_ids = [
        note.pk
        for note in notes
    ]

    if len(note_ids) != len(set(note_ids)):
        raise EngineeringSessionPlanningError(
            "Source Delta Notes must be unique."
        )

    for note in notes:
        _validate_delta_note_handoff(
            note=note,
            user=user,
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


def _require_planning_document(
    document: dict[str, Any],
) -> None:
    """Require one Planning dictionary."""

    if not isinstance(document, dict):
        raise EngineeringSessionPlanningError(
            "A Planning dictionary is required."
        )


def _require_single_new_initiative_title(
    document: dict[str, Any],
) -> str:
    """Return the title of the one Initiative created by grouped handoff."""

    initiatives = document.get(
        "add_initiatives",
        []
    )

    if not isinstance(initiatives, list):
        raise EngineeringSessionPlanningError(
            "add_initiatives must be a list."
        )

    if len(initiatives) != 1:
        raise EngineeringSessionPlanningError(
            "Grouped Delta Note provenance currently requires "
            "exactly one new Initiative."
        )

    initiative = initiatives[0]

    if not isinstance(initiative, dict):
        raise EngineeringSessionPlanningError(
            "The new Initiative definition must be a dictionary."
        )

    title = str(
        initiative.get(
            "title",
            "",
        )
    ).strip()

    if not title:
        raise EngineeringSessionPlanningError(
            "The new Initiative requires a title."
        )

    return title


def _require_document_project_slug(
    document: dict[str, Any],
) -> str:
    """Return the target Project slug from one Planning dictionary."""

    target = document.get(
        "target",
        {}
    )

    if not isinstance(target, dict):
        raise EngineeringSessionPlanningError(
            "Planning target must be a dictionary."
        )

    return _require_project_slug(
        str(
            target.get(
                "project_slug",
                "",
            )
        )
    )


def _resolve_created_initiative(
    *,
    project_slug: str,
    initiative_title: str,
) -> Initiative:
    """Resolve the Initiative created by the grouped Planning mutation."""

    try:
        project = Project.objects.get(
            slug=project_slug,
        )
    except Project.DoesNotExist as error:
        raise EngineeringSessionPlanningError(
            f'Planning Project "{project_slug}" does not exist '
            "after application."
        ) from error

    try:
        return Initiative.objects.get(
            project=project,
            title=initiative_title,
        )
    except Initiative.DoesNotExist as error:
        raise EngineeringSessionPlanningError(
            "Planning application did not create the expected "
            f'Initiative "{initiative_title}".'
        ) from error
    except Initiative.MultipleObjectsReturned as error:
        raise EngineeringSessionPlanningError(
            "Planning provenance is ambiguous because multiple "
            f'Initiatives named "{initiative_title}" exist in '
            f'Project "{project_slug}".'
        ) from error


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