# ======================================================================
# FILE: aurora/subsystems/planning/api/phases.py 
# START: PHASE_PERSISTENCE
# ======================================================================
from django.db import transaction
from django.db.models import Max
from django.http import JsonResponse

from aurora.models import ExecutionStatus, Initiative, Phase
from aurora.subsystems.planning.api.serializers import serialize_phase


def save_phase(payload):
    """Validates and persists a new or existing Phase."""
    phase_id = payload.get("phase_id")
    phase = None

    if phase_id not in (None, ""):
        try:
            phase = (
                Phase.objects
                .select_related("initiative")
                .get(pk=phase_id)
            )
        except (Phase.DoesNotExist, TypeError, ValueError):
            return JsonResponse(
                {
                    "status": "error",
                    "message": "The selected Phase does not exist.",
                    "field_errors": {
                        "phase_id": "Select a valid Phase.",
                    },
                },
                status=404,
            )

    initiative_id = payload.get(
        "initiative_id",
        phase.initiative_id if phase else None,
    )

    if initiative_id in (None, ""):
        return JsonResponse(
            {
                "status": "error",
                "message": "Initiative is required.",
                "field_errors": {
                    "initiative_id": "Select an Initiative.",
                },
            },
            status=400,
        )

    try:
        initiative = Initiative.objects.get(pk=initiative_id)
    except (Initiative.DoesNotExist, TypeError, ValueError):
        return JsonResponse(
            {
                "status": "error",
                "message": "The selected Initiative does not exist.",
                "field_errors": {
                    "initiative_id": "Select a valid Initiative.",
                },
            },
            status=404,
        )

    title = str(payload.get("title", "")).strip()

    if not title:
        return JsonResponse(
            {
                "status": "error",
                "message": "Phase title is required.",
                "field_errors": {
                    "title": "Enter a Phase title.",
                },
            },
            status=400,
        )

    status = str(
        payload.get(
            "status",
            phase.status if phase else ExecutionStatus.PLANNED,
        )
    ).strip().upper()

    valid_statuses = {
        choice.value
        for choice in ExecutionStatus
    }

    if status not in valid_statuses:
        return JsonResponse(
            {
                "status": "error",
                "message": "Phase status is invalid.",
                "field_errors": {
                    "status": "Select a valid Phase status.",
                },
            },
            status=400,
        )

    description = str(
        payload.get(
            "description",
            phase.description if phase else "",
        )
    ).strip()

    with transaction.atomic():
        if phase is None:
            highest_position = (
                Phase.objects
                .filter(initiative=initiative)
                .aggregate(highest=Max("position"))
                .get("highest")
            )

            phase = Phase.objects.create(
                initiative=initiative,
                title=title,
                description=description,
                status=status,
                position=(
                    highest_position + 1
                    if highest_position is not None
                    else 0
                ),
            )

            response_status = 201
            message = "Phase created."
        else:
            if phase.initiative_id != initiative.pk:
                highest_position = (
                    Phase.objects
                    .filter(initiative=initiative)
                    .aggregate(highest=Max("position"))
                    .get("highest")
                )

                phase.initiative = initiative
                phase.position = (
                    highest_position + 1
                    if highest_position is not None
                    else 0
                )

            phase.title = title
            phase.description = description
            phase.status = status

            phase.save(
                update_fields=[
                    "initiative",
                    "title",
                    "description",
                    "status",
                    "position",
                    "updated_at",
                ]
            )

            response_status = 200
            message = "Phase updated."

    return JsonResponse(
        {
            "status": "success",
            "message": message,
            "phase": serialize_phase(phase),
            "initiative_id": initiative.pk,
        },
        status=response_status,
    )


def create_phase(payload):
    """Compatibility wrapper until endpoint dispatch uses save operations."""
    return save_phase(payload)
# ======================================================================
# END: PHASE_PERSISTENCE 
# ======================================================================