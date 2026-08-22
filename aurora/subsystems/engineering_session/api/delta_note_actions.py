# ======================================================================
# FILE: aurora/subsystems/engineering_session/api/delta_note_actions.py
# START: ENGINEERING_SESSION_DELTA_NOTE_ACTIONS
# ======================================================================

from django.http import JsonResponse

from aurora.models import DeltaNotesEntry
from aurora.subsystems.engineering_session.api.common import (
    parse_planning_document,
    require_active_session,
)
from aurora.subsystems.engineering_session.api.serializers import (
    serialize_delta_note,
    serialize_grouped_planning_application,
    serialize_planning_application,
    serialize_planning_proposal,
)
from aurora.subsystems.engineering_session.services import (
    EngineeringSessionPlanningError,
    apply_delta_note_planning,
    apply_delta_notes_to_new_initiative,
    get_next_unprocessed_delta_note,
    get_session_workflow_status,
    propose_delta_note_planning,
    resolve_delta_note,
)


DELTA_NOTE_ACTIONS = {
    "next_delta_note",
    "resolve_delta_note",
    "propose_delta_note_planning",
    "apply_delta_note_planning",
    "apply_delta_notes_planning",
}


def _load_grouped_delta_notes(request):
    """Return the requested unique unresolved Delta Notes in submitted order."""

    raw_note_ids = request.POST.getlist(
        "note_ids"
    )

    if not raw_note_ids:
        raise EngineeringSessionPlanningError(
            "At least one source Delta Note is required."
        )

    try:
        note_ids = [
            int(note_id)
            for note_id in raw_note_ids
        ]
    except (TypeError, ValueError) as error:
        raise EngineeringSessionPlanningError(
            "Delta Note IDs must be integers."
        ) from error

    if len(note_ids) != len(set(note_ids)):
        raise EngineeringSessionPlanningError(
            "Source Delta Notes must be unique."
        )

    notes_by_id = {
        note.pk: note
        for note in (
            DeltaNotesEntry.objects
            .filter(
                pk__in=note_ids,
                user=request.user,
                processed=False,
            )
        )
    }

    if len(notes_by_id) != len(note_ids):
        raise EngineeringSessionPlanningError(
            "One or more source Delta Notes are unavailable."
        )

    return [
        notes_by_id[note_id]
        for note_id in note_ids
    ]


def handle_delta_note_action(request, action):
    """Handle Delta Note disposition and Planning handoff actions."""

    require_active_session(
        request.user
    )

    if action == "next_delta_note":
        note = get_next_unprocessed_delta_note(
            request.user
        )

        return JsonResponse(
            {
                "status": "success",
                "action": action,
                "note": serialize_delta_note(
                    note
                ),
                "workflow": get_session_workflow_status(
                    request.user
                ),
            }
        )

    if action == "resolve_delta_note":
        note = DeltaNotesEntry.objects.get(
            pk=request.POST.get("note_id"),
            user=request.user,
            processed=False,
        )

        note_id = note.pk

        resolve_delta_note(
            note
        )

        return JsonResponse(
            {
                "status": "success",
                "action": action,
                "note_id": note_id,
                "workflow": get_session_workflow_status(
                    request.user
                ),
            }
        )

    if action == "propose_delta_note_planning":
        note = DeltaNotesEntry.objects.get(
            pk=request.POST.get("note_id"),
            user=request.user,
            processed=False,
        )

        proposal = propose_delta_note_planning(
            note=note,
            project_slug=request.POST.get(
                "project_slug",
                "",
            ),
            user=request.user,
        )

        return JsonResponse(
            {
                "status": "success",
                "action": action,
                "proposal": serialize_planning_proposal(
                    proposal
                ),
                "workflow": get_session_workflow_status(
                    request.user
                ),
            }
        )

    if action == "apply_delta_note_planning":
        note = DeltaNotesEntry.objects.get(
            pk=request.POST.get("note_id"),
            user=request.user,
            processed=False,
        )

        document = parse_planning_document(
            request.POST.get(
                "planning_document",
                "",
            )
        )

        application = apply_delta_note_planning(
            note=note,
            document=document,
            user=request.user,
        )

        return JsonResponse(
            {
                "status": "success",
                "action": action,
                "result": serialize_planning_application(
                    application
                ),
                "workflow": get_session_workflow_status(
                    request.user
                ),
            }
        )

    notes = _load_grouped_delta_notes(
        request
    )

    document = parse_planning_document(
        request.POST.get(
            "planning_document",
            "",
        )
    )

    application = apply_delta_notes_to_new_initiative(
        notes=notes,
        document=document,
        user=request.user,
    )

    return JsonResponse(
        {
            "status": "success",
            "action": "apply_delta_notes_planning",
            "result": serialize_grouped_planning_application(
                application
            ),
            "workflow": get_session_workflow_status(
                request.user
            ),
        }
    )


# ======================================================================
# END: ENGINEERING_SESSION_DELTA_NOTE_ACTIONS
# ======================================================================
