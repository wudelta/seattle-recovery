# ======================================================================
# FILE: aurora/subsystems/engineering_session/api/endpoint.py
# START: ENGINEERING_SESSION_API_ENDPOINT
# ======================================================================

import json
from dataclasses import asdict

from django.http import JsonResponse

from aurora.models import DeltaNotesEntry, Initiative, Phase
from aurora.subsystems.engineering_session.services import (
    EngineeringSessionError,
    EngineeringSessionPlanningError,
    apply_delta_note_planning,
    end_session,
    get_active_session,
    get_next_unprocessed_delta_note,
    get_session_workflow_status,
    propose_delta_note_planning,
    resolve_delta_note,
    start_session,
)
from aurora.subsystems.planning.io.exceptions import (
    PlanningImportError,
    PlanningSchemaError,
)
from aurora.subsystems.planning.services import (
    PlanningGenerationError,
    PlanningLifecycleError,
    PlanningTimeTrackingError,
    approve_initiative_completion,
    approve_phase_completion,
    complete_step_and_evaluate_parents,
    end_step_work,
    get_executable_step,
    reject_initiative_completion,
    reject_phase_completion,
    request_initiative_completion,
    start_step_work,
)


def _serialize_session(session):
    """Return stable API data for one EngineeringSession."""

    if session is None:
        return None

    return {
        "id": session.id,
        "started_at": session.started_at.isoformat(),
        "ended_at": (
            session.ended_at.isoformat()
            if session.ended_at
            else None
        ),
    }


def _serialize_time_entry(time_entry):
    """Return stable API data for one Planning TimeEntry."""

    if time_entry is None:
        return None

    return {
        "id": time_entry.id,
        "step_id": time_entry.step_id,
        "step": time_entry.step.title,
        "started_at": time_entry.started_at.isoformat(),
        "ended_at": (
            time_entry.ended_at.isoformat()
            if time_entry.ended_at
            else None
        ),
    }


def _serialize_delta_note(note):
    """Return stable API data for one Delta Note."""

    if note is None:
        return None

    return {
        "id": note.pk,
        "text": note.text,
        "created_at": note.created_at.isoformat(),
        "updated_at": note.updated_at.isoformat(),
    }


def _serialize_planning_proposal(proposal):
    """Return stable API data for one validated Planning proposal."""

    return {
        "note_id": proposal.note_id,
        "note_text": proposal.note_text,
        "project_slug": proposal.project_slug,
        "document": proposal.document,
        "validation": asdict(
            proposal.validation
        ),
    }


def _serialize_planning_application(application):
    """Return stable API data for an applied Delta Note Planning proposal."""

    return {
        "note_id": application.note_id,
        "project_slug": application.project_slug,
        "validation": asdict(
            application.validation
        ),
        "application": asdict(
            application.application
        ),
        "note_resolved": application.note_resolved,
    }


def _parse_planning_document(value):
    """Parse one browser-submitted Planning dictionary."""

    if not isinstance(value, str) or not value.strip():
        raise EngineeringSessionPlanningError(
            "Planning proposal document is required."
        )

    try:
        document = json.loads(
            value
        )
    except json.JSONDecodeError as error:
        raise EngineeringSessionPlanningError(
            "Planning proposal document is not valid JSON."
        ) from error

    if not isinstance(document, dict):
        raise EngineeringSessionPlanningError(
            "Planning proposal document must be an object."
        )

    return document


def _require_active_session(user):
    """Require an active Engineering Session for workflow mutations."""

    session = get_active_session(user)

    if session is None:
        raise EngineeringSessionError(
            "An active engineering session is required."
        )

    return session


def engineering_session_endpoint(request):
    """Read or change the authenticated user's Engineering Session."""

    if request.method == "GET":
        session = get_active_session(request.user)
        workflow = get_session_workflow_status(request.user)

        return JsonResponse(
            {
                "status": "success",
                "active": session is not None,
                "session": _serialize_session(session),
                "workflow": workflow,
            }
        )

    if request.method != "POST":
        return JsonResponse(
            {
                "status": "error",
                "message": "Method not allowed.",
            },
            status=405,
        )

    action = request.POST.get("action")

    try:
        if action == "start":
            session = start_session(request.user)

            return JsonResponse(
                {
                    "status": "success",
                    "active": True,
                    "session": _serialize_session(session),
                }
            )

        if action == "end":
            session = end_session(request.user)

            return JsonResponse(
                {
                    "status": "success",
                    "active": False,
                    "session": _serialize_session(session),
                }
            )

        if action == "start_step_work":
            _require_active_session(request.user)

            time_entry = start_step_work(request.user)

            return JsonResponse(
                {
                    "status": "success",
                    "action": "start_step_work",
                    "time_entry": _serialize_time_entry(time_entry),
                    "workflow": get_session_workflow_status(
                        request.user
                    ),
                }
            )

        if action == "end_step_work":
            _require_active_session(request.user)

            time_entry = end_step_work(request.user)

            return JsonResponse(
                {
                    "status": "success",
                    "action": "end_step_work",
                    "time_entry": _serialize_time_entry(time_entry),
                    "workflow": get_session_workflow_status(
                        request.user
                    ),
                }
            )

        if action == "complete_step":
            _require_active_session(request.user)

            step = get_executable_step(
                request.user
            )

            lifecycle = complete_step_and_evaluate_parents(
                step,
                request.user,
                auto_phase=False,
                auto_initiative=False,
            )

            return JsonResponse(
                {
                    "status": "success",
                    "action": "complete_step",
                    "lifecycle": lifecycle,
                    "workflow": get_session_workflow_status(
                        request.user
                    ),
                }
            )

        if action == "next_delta_note":
            _require_active_session(request.user)

            note = get_next_unprocessed_delta_note(
                request.user
            )

            return JsonResponse(
                {
                    "status": "success",
                    "action": "next_delta_note",
                    "note": _serialize_delta_note(note),
                    "workflow": get_session_workflow_status(
                        request.user
                    ),
                }
            )

        if action == "resolve_delta_note":
            _require_active_session(request.user)

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
                    "action": "resolve_delta_note",
                    "note_id": note_id,
                    "workflow": get_session_workflow_status(
                        request.user
                    ),
                }
            )

        if action == "propose_delta_note_planning":
            _require_active_session(request.user)

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
                    "action": "propose_delta_note_planning",
                    "proposal": _serialize_planning_proposal(
                        proposal
                    ),
                    "workflow": get_session_workflow_status(
                        request.user
                    ),
                }
            )

        if action == "apply_delta_note_planning":
            _require_active_session(request.user)

            note = DeltaNotesEntry.objects.get(
                pk=request.POST.get("note_id"),
                user=request.user,
                processed=False,
            )

            document = _parse_planning_document(
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
                    "action": "apply_delta_note_planning",
                    "result": _serialize_planning_application(
                        application
                    ),
                    "workflow": get_session_workflow_status(
                        request.user
                    ),
                }
            )

        if action == "approve_phase_completion":
            _require_active_session(request.user)

            phase = (
                Phase.objects
                .select_related("initiative")
                .get(
                    pk=request.POST.get("phase_id")
                )
            )

            decision = approve_phase_completion(
                phase
            )

            initiative_completion = (
                request_initiative_completion(
                    phase.initiative,
                    auto=False,
                )
            )

            return JsonResponse(
                {
                    "status": "success",
                    "action": action,
                    "decision": decision,
                    "initiative_completion": (
                        initiative_completion
                    ),
                    "workflow": get_session_workflow_status(
                        request.user
                    ),
                }
            )

        if action == "reject_phase_completion":
            _require_active_session(request.user)

            phase = Phase.objects.get(
                pk=request.POST.get("phase_id")
            )

            decision = reject_phase_completion(
                phase,
                reason=request.POST.get(
                    "reason",
                    "",
                ),
            )

            return JsonResponse(
                {
                    "status": "success",
                    "action": action,
                    "decision": decision,
                    "workflow": get_session_workflow_status(
                        request.user
                    ),
                }
            )

        if action == "approve_initiative_completion":
            _require_active_session(request.user)

            initiative = Initiative.objects.get(
                pk=request.POST.get("initiative_id")
            )

            decision = approve_initiative_completion(
                initiative
            )

            return JsonResponse(
                {
                    "status": "success",
                    "action": action,
                    "decision": decision,
                    "workflow": get_session_workflow_status(
                        request.user
                    ),
                }
            )

        if action == "reject_initiative_completion":
            _require_active_session(request.user)

            initiative = Initiative.objects.get(
                pk=request.POST.get("initiative_id")
            )

            decision = reject_initiative_completion(
                initiative,
                reason=request.POST.get(
                    "reason",
                    "",
                ),
            )

            return JsonResponse(
                {
                    "status": "success",
                    "action": action,
                    "decision": decision,
                    "workflow": get_session_workflow_status(
                        request.user
                    ),
                }
            )

    except (
        EngineeringSessionError,
        EngineeringSessionPlanningError,
        PlanningGenerationError,
        PlanningImportError,
        PlanningLifecycleError,
        PlanningSchemaError,
        PlanningTimeTrackingError,
    ) as error:
        return JsonResponse(
            {
                "status": "error",
                "message": str(error),
            },
            status=400,
        )

    except (
        DeltaNotesEntry.DoesNotExist,
        Phase.DoesNotExist,
        Initiative.DoesNotExist,
        ValueError,
        TypeError,
    ):
        return JsonResponse(
            {
                "status": "error",
                "message": "Invalid workflow target.",
            },
            status=400,
        )

    return JsonResponse(
        {
            "status": "error",
            "message": f"Unknown action: {action}",
        },
        status=400,
    )

# ======================================================================
# END: ENGINEERING_SESSION_API_ENDPOINT
# ======================================================================