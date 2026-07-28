# ======================================================================
# FILE: aurora/subsystems/planning/api/steps.py (PATCH 2 OF 5)
# START: STEP_PERSISTENCE
# ======================================================================
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Max
from django.http import JsonResponse

from aurora.models import ExecutionStatus, Phase, Step
from aurora.subsystems.planning.api.serializers import serialize_step


def resolve_step_save_context(payload):
    """Resolves and validates the Step, parent Phase, title, and status."""
    step_id = payload.get("step_id")
    step = None

    if step_id not in (None, ""):
        try:
            step = (
                Step.objects
                .select_related("phase")
                .get(pk=step_id)
            )
        except (Step.DoesNotExist, TypeError, ValueError):
            return None, JsonResponse(
                {
                    "status": "error",
                    "message": "The selected Step does not exist.",
                    "field_errors": {
                        "step_id": "Select a valid Step.",
                    },
                },
                status=404,
            )

    phase_id = payload.get(
        "phase_id",
        step.phase_id if step else None,
    )

    if phase_id in (None, ""):
        return None, JsonResponse(
            {
                "status": "error",
                "message": "Phase is required.",
                "field_errors": {
                    "phase_id": "Select a Phase.",
                },
            },
            status=400,
        )

    try:
        phase = Phase.objects.get(pk=phase_id)
    except (Phase.DoesNotExist, TypeError, ValueError):
        return None, JsonResponse(
            {
                "status": "error",
                "message": "The selected Phase does not exist.",
                "field_errors": {
                    "phase_id": "Select a valid Phase.",
                },
            },
            status=404,
        )

    title = str(payload.get("title", "")).strip()

    if not title:
        return None, JsonResponse(
            {
                "status": "error",
                "message": "Step title is required.",
                "field_errors": {
                    "title": "Enter a Step title.",
                },
            },
            status=400,
        )

    status = str(
        payload.get(
            "status",
            step.status if step else ExecutionStatus.PLANNED,
        )
    ).strip().upper()

    valid_statuses = {
        choice.value
        for choice in ExecutionStatus
    }

    if status not in valid_statuses:
        return None, JsonResponse(
            {
                "status": "error",
                "message": "Step status is invalid.",
                "field_errors": {
                    "status": "Select a valid Step status.",
                },
            },
            status=400,
        )

    assigned_to_id = payload.get(
        "assigned_to_id",
        step.assigned_to_id if step else None,
    )

    if assigned_to_id in (None, ""):
        return None, JsonResponse(
            {
                "status": "error",
                "message": "Step assignee is required.",
                "field_errors": {
                    "assigned_to_id": "Select a user.",
                },
            },
            status=400,
        )

    User = get_user_model()

    try:
        assigned_to = User.objects.get(pk=assigned_to_id)
    except (User.DoesNotExist, TypeError, ValueError):
        return None, JsonResponse(
            {
                "status": "error",
                "message": "The selected Step assignee does not exist.",
                "field_errors": {
                    "assigned_to_id": "Select a valid user.",
                },
            },
            status=404,
        )

    return {
        "step": step,
        "phase": phase,
        "title": title,
        "status": status,
        "assigned_to": assigned_to,
    }, None


def resolve_step_save_details(payload, step):
    """Validates and normalizes optional Step planning details."""
    estimated_minutes_value = payload.get(
        "estimated_minutes",
        step.estimated_minutes if step else None,
    )

    if estimated_minutes_value in (None, ""):
        estimated_minutes = None
    else:
        try:
            estimated_minutes = int(estimated_minutes_value)
        except (TypeError, ValueError):
            return None, JsonResponse(
                {
                    "status": "error",
                    "message": "Step estimate is invalid.",
                    "field_errors": {
                        "estimated_minutes": (
                            "Enter an estimate using whole minutes."
                        ),
                    },
                },
                status=400,
            )

        if estimated_minutes < 0:
            return None, JsonResponse(
                {
                    "status": "error",
                    "message": "Step estimate is invalid.",
                    "field_errors": {
                        "estimated_minutes": (
                            "Estimated minutes cannot be negative."
                        ),
                    },
                },
                status=400,
            )

    confidence_value = payload.get(
        "estimate_confidence",
        step.estimate_confidence if step else "",
    )

    estimate_confidence = str(
        confidence_value or ""
    ).strip().upper()

    if not estimate_confidence:
        estimate_confidence = None
    elif estimate_confidence not in {
        "LOW",
        "MEDIUM",
        "HIGH",
    }:
        return None, JsonResponse(
            {
                "status": "error",
                "message": "Step estimate confidence is invalid.",
                "field_errors": {
                    "estimate_confidence": (
                        "Select Low, Medium, or High confidence."
                    ),
                },
            },
            status=400,
        )

    description = str(
        payload.get(
            "description",
            step.description if step else "",
        )
    ).strip()

    validation_description = str(
        payload.get(
            "validation_description",
            step.validation_description if step else "",
        )
    ).strip()

    return {
        "description": description,
        "estimated_minutes": estimated_minutes,
        "estimate_confidence": estimate_confidence,
        "validation_description": validation_description,
    }, None


def save_step(request, payload):
    """Validates and persists a new or existing Step."""
    context, error_response = resolve_step_save_context(payload)

    if error_response:
        return error_response

    step = context["step"]
    phase = context["phase"]

    details, error_response = resolve_step_save_details(
        payload,
        step,
    )

    if error_response:
        return error_response

    with transaction.atomic():
        if step is None:
            highest_position = (
                Step.objects
                .filter(phase=phase)
                .aggregate(highest=Max("position"))
                .get("highest")
            )

            step = Step.objects.create(
                phase=phase,
                title=context["title"],
                description=details["description"],
                status=context["status"],
                position=(
                    highest_position + 1
                    if highest_position is not None
                    else 0
                ),
                estimated_minutes=details["estimated_minutes"],
                estimate_confidence=details["estimate_confidence"],
                validation_description=(
                    details["validation_description"]
                ),
                created_by=request.user,
                assigned_to=context["assigned_to"],
            )

            response_status = 201
            message = "Step created."
        else:
            if step.phase_id != phase.pk:
                highest_position = (
                    Step.objects
                    .filter(phase=phase)
                    .aggregate(highest=Max("position"))
                    .get("highest")
                )

                step.phase = phase
                step.position = (
                    highest_position + 1
                    if highest_position is not None
                    else 0
                )

            step.title = context["title"]
            step.description = details["description"]
            step.status = context["status"]
            step.estimated_minutes = details["estimated_minutes"]
            step.estimate_confidence = details["estimate_confidence"]
            step.validation_description = (
                details["validation_description"]
            )
            step.assigned_to = context["assigned_to"]

            step.save()

            response_status = 200
            message = "Step updated."

    return JsonResponse(
        {
            "status": "success",
            "message": message,
            "step": serialize_step(step),
            "phase_id": phase.pk,
            "initiative_id": phase.initiative_id,
        },
        status=response_status,
    )


def delete_step(payload):
    """Deletes an existing Step and returns its hierarchy context."""
    step_id = payload.get("step_id")

    if step_id in (None, ""):
        return JsonResponse(
            {
                "status": "error",
                "message": "Step is required.",
                "field_errors": {
                    "step_id": "Select a Step.",
                },
            },
            status=400,
        )

    try:
        step = (
            Step.objects
            .select_related("phase")
            .get(pk=step_id)
        )
    except (Step.DoesNotExist, TypeError, ValueError):
        return JsonResponse(
            {
                "status": "error",
                "message": "The selected Step does not exist.",
                "field_errors": {
                    "step_id": "Select a valid Step.",
                },
            },
            status=404,
        )

    deleted_step_id = step.pk
    phase_id = step.phase_id
    initiative_id = step.phase.initiative_id

    with transaction.atomic():
        step.delete()

    return JsonResponse(
        {
            "status": "success",
            "message": "Step deleted.",
            "step_id": deleted_step_id,
            "phase_id": phase_id,
            "initiative_id": initiative_id,
        }
    )


def create_step(request, payload):
    """Compatibility wrapper until endpoint dispatch uses save operations."""
    return save_step(request, payload)
# ======================================================================
# END: STEP_PERSISTENCE (PATCH 2 OF 5)
# ======================================================================