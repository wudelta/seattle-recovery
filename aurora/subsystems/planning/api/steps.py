# ======================================================================
# FILE: aurora/subsystems/planning/api/steps.py
# START: STEP_IMPORTS
# ======================================================================
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Max
from django.http import JsonResponse

from aurora.models import (
    ExecutionStatus,
    Phase,
    Step,
    StepDocument,
    StepFile,
    StepValidation,
)
from aurora.subsystems.planning.api.serializers import serialize_step
# ======================================================================
# END: STEP_IMPORTS
# ======================================================================


# ======================================================================
# FILE: aurora/subsystems/planning/api/steps.py
# START: STEP_SAVE_CONTEXT
# ======================================================================
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
# ======================================================================
# END: STEP_SAVE_CONTEXT
# ======================================================================


# ======================================================================
# FILE: aurora/subsystems/planning/api/steps.py
# START: STEP_SAVE_DETAILS
# ======================================================================
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
# ======================================================================
# END: STEP_SAVE_DETAILS
# ======================================================================


# ======================================================================
# FILE: aurora/subsystems/planning/api/steps.py
# START: STEP_CORE_PERSISTENCE
# ======================================================================
def save_step_core(
    *,
    request,
    step,
    phase,
    context,
    details,
):
    """Creates or updates the core Step record."""
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

        return step, 201, "Step created."

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

    return step, 200, "Step updated."
# ======================================================================
# END: STEP_CORE_PERSISTENCE
# ======================================================================


# ======================================================================
# FILE: aurora/subsystems/planning/api/steps.py
# START: STEP_DOCUMENT_PERSISTENCE
# ======================================================================
def save_step_document(*, step, payload):
    """Creates or updates supporting technical documentation for a Step."""
    document_payload = payload.get("document")

    if document_payload is None:
        document_payload = {
            field_name: payload[field_name]
            for field_name in (
                "technical_design",
                "dependencies",
                "assumptions",
                "implementation_notes",
                "discussion",
            )
            if field_name in payload
        }

    if not isinstance(document_payload, dict):
        return

    supported_fields = (
        "technical_design",
        "dependencies",
        "assumptions",
        "implementation_notes",
        "discussion",
    )

    provided_fields = {
        field_name: str(
            document_payload.get(field_name, "")
        ).strip()
        for field_name in supported_fields
        if field_name in document_payload
    }

    if not provided_fields:
        return

    document, _created = StepDocument.objects.update_or_create(
        step=step,
        defaults=provided_fields,
    )

    step.document = document
# ======================================================================
# END: STEP_DOCUMENT_PERSISTENCE
# ======================================================================


# ======================================================================
# FILE: aurora/subsystems/planning/api/steps.py
# START: STEP_VALIDATION_PERSISTENCE
# ======================================================================
def save_step_validation(*, step, payload):
    """Creates or updates validation metadata for a Step."""
    validation_payload = payload.get("validation")

    if validation_payload is None:
        validation_payload = {
            field_name: payload[field_name]
            for field_name in (
                "validation_description",
                "validation_notes",
                "validated_by",
                "validated_at",
            )
            if field_name in payload
        }

    if not isinstance(validation_payload, dict):
        return

    defaults = {}

    if (
        "validation_description" in validation_payload
        or "description" in validation_payload
    ):
        defaults["description"] = str(
            validation_payload.get(
                "description",
                validation_payload.get(
                    "validation_description",
                    "",
                ),
            )
        ).strip()

    if (
        "validation_notes" in validation_payload
        or "notes" in validation_payload
    ):
        defaults["notes"] = str(
            validation_payload.get(
                "notes",
                validation_payload.get(
                    "validation_notes",
                    "",
                ),
            )
        ).strip()

    if "validated_at" in validation_payload:
        defaults["validated_at"] = (
            validation_payload.get("validated_at")
            or None
        )

    if "validated_by" in validation_payload:
        validated_by = validation_payload.get("validated_by")

        if validated_by in (None, ""):
            defaults["validated_by"] = None
        else:
            try:
                defaults["validated_by"] = (
                    get_user_model()
                    .objects
                    .get(pk=validated_by)
                )
            except get_user_model().DoesNotExist:
                defaults["validated_by"] = None

    if not defaults:
        return

    validation, _created = (
        StepValidation.objects.update_or_create(
            step=step,
            defaults=defaults,
        )
    )

    step.validation = validation
# ======================================================================
# END: STEP_VALIDATION_PERSISTENCE
# ======================================================================


# ======================================================================
# FILE: aurora/subsystems/planning/api/steps.py
# START: STEP_FILE_PERSISTENCE
# ======================================================================
def save_step_files(*, request, step, payload):
    """Synchronizes submitted planned and actual files for a Step."""
    files_supplied = any(
        key in payload
        for key in (
            "files",
            "planned_files",
            "actual_files",
        )
    )

    if not files_supplied:
        return

    file_payloads = []

    legacy_files = payload.get("files")

    if isinstance(legacy_files, list):
        file_payloads.extend(legacy_files)

    for role, payload_key in (
        (StepFile.Role.PLANNED, "planned_files"),
        (StepFile.Role.ACTUAL, "actual_files"),
    ):
        role_payloads = payload.get(payload_key)

        if not isinstance(role_payloads, list):
            continue

        for file_payload in role_payloads:
            if not isinstance(file_payload, dict):
                continue

            normalized_payload = dict(file_payload)
            normalized_payload["role"] = role
            file_payloads.append(normalized_payload)

    submitted_keys = set()

    for file_payload in file_payloads:
        if not isinstance(file_payload, dict):
            continue

        file_path = str(
            file_payload.get("file_path", "")
        ).strip()

        role = str(
            file_payload.get("role", "")
        ).strip().upper()

        if not file_path:
            continue

        if role not in StepFile.Role.values:
            continue

        reason = str(
            file_payload.get("reason", "")
        ).strip()

        StepFile.objects.update_or_create(
            step=step,
            file_path=file_path,
            role=role,
            defaults={
                "reason": reason,
                "recorded_by": request.user,
            },
        )

        submitted_keys.add((file_path, role))

    existing_files = StepFile.objects.filter(step=step)

    for step_file in existing_files:
        key = (step_file.file_path, step_file.role)

        if key not in submitted_keys:
            step_file.delete()
# ======================================================================
# END: STEP_FILE_PERSISTENCE
# ======================================================================


# ======================================================================
# FILE: aurora/subsystems/planning/api/steps.py
# START: STEP_SAVE_ORCHESTRATION
# ======================================================================
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
        step, response_status, message = save_step_core(
            request=request,
            step=step,
            phase=phase,
            context=context,
            details=details,
        )

        save_step_document(
            step=step,
            payload=payload,
        )

        save_step_validation(
            step=step,
            payload=payload,
        )

        save_step_files(
            request=request,
            step=step,
            payload=payload,
        )

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
# ======================================================================
# END: STEP_SAVE_ORCHESTRATION
# ======================================================================


# ======================================================================
# FILE: aurora/subsystems/planning/api/steps.py
# START: STEP_DELETE
# ======================================================================
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
# ======================================================================
# END: STEP_DELETE
# ======================================================================


# ======================================================================
# FILE: aurora/subsystems/planning/api/steps.py
# START: STEP_COMPATIBILITY
# ======================================================================
def create_step(request, payload):
    """Compatibility wrapper until endpoint dispatch uses save operations."""
    return save_step(request, payload)
# ======================================================================
# END: STEP_COMPATIBILITY
# ======================================================================