# ======================================================================
# FILE: aurora/api/planning_api.py (PATCH 1 OF 7)
# START: PLANNING_SERIALIZATION
# ======================================================================
import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Max, Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from aurora.models import (
    ExecutionStatus,
    Initiative,
    Phase,
    Project,
    Step,
)


def serialize_user(user):
    """Returns a compact identity payload for planning ownership fields."""
    if user is None:
        return None

    full_name = user.get_full_name().strip()

    return {
        "id": str(user.pk),
        "username": user.get_username(),
        "display_name": full_name or user.get_username(),
    }


def serialize_project(project):
    """Serializes one selectable Decision Engine project."""
    return {
        "id": project.pk,
        "title": project.title,
        "slug": project.slug,
        "description": project.description,
        "color": project.color,
        "icon": project.icon,
        "position": project.position,
        "active": project.active,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
    }


def serialize_step(step):
    """Serializes one implementation step for the planning workspace."""
    return {
        "id": step.pk,
        "title": step.title,
        "description": step.description,
        "status": step.status,
        "status_label": step.get_status_display(),
        "position": step.position,
        "estimated_minutes": step.estimated_minutes,
        "estimate_confidence": step.estimate_confidence,
        "estimate_confidence_label": (
            step.get_estimate_confidence_display()
            if step.estimate_confidence
            else None
        ),
        "risk_level": step.risk_level,
        "risk_level_label": step.get_risk_level_display(),
        "risk_description": step.risk_description,
        "validation_description": step.validation_description,
        "validated_by": serialize_user(step.validated_by),
        "validation_notes": step.validation_notes,
        "created_at": step.created_at.isoformat(),
        "updated_at": step.updated_at.isoformat(),
        "completed_at": (
            step.completed_at.isoformat()
            if step.completed_at
            else None
        ),
    }


def serialize_phase(phase):
    """Serializes one ordered phase and its implementation steps."""
    steps = list(phase.steps.all())

    return {
        "id": phase.pk,
        "title": phase.title,
        "description": phase.description,
        "status": phase.status,
        "status_label": phase.get_status_display(),
        "position": phase.position,
        "step_count": len(steps),
        "steps": [
            serialize_step(step)
            for step in steps
        ],
        "created_at": phase.created_at.isoformat(),
        "updated_at": phase.updated_at.isoformat(),
        "completed_at": (
            phase.completed_at.isoformat()
            if phase.completed_at
            else None
        ),
    }


def serialize_initiative(initiative):
    """Serializes one initiative and its complete planning hierarchy."""
    phases = list(initiative.phases.all())

    return {
        "id": initiative.pk,
        "project_id": initiative.project_id,
        "project_slug": initiative.project.slug,
        "title": initiative.title,
        "description": initiative.description,
        "status": initiative.status,
        "status_label": initiative.get_status_display(),
        "position": initiative.position,
        "created_by": serialize_user(initiative.created_by),
        "phase_count": len(phases),
        "phases": [
            serialize_phase(phase)
            for phase in phases
        ],
        "created_at": initiative.created_at.isoformat(),
        "updated_at": initiative.updated_at.isoformat(),
        "completed_at": (
            initiative.completed_at.isoformat()
            if initiative.completed_at
            else None
        ),
    }
# ======================================================================
# END: PLANNING_SERIALIZATION (PATCH 1 OF 7)
# ======================================================================

# ======================================================================
# FILE: aurora/api/planning_api.py (PATCH 2 OF 7)
# START: PLANNING_HIERARCHY_QUERY
# ======================================================================
def build_planning_payload(project_slug=None):
    """Builds the persisted planning hierarchy for one active Project."""
    projects = list(
        Project.objects
        .filter(active=True)
        .order_by("position", "title")
    )

    active_project = None

    if project_slug:
        active_project = next(
            (
                project
                for project in projects
                if project.slug == project_slug
            ),
            None,
        )

    if active_project is None and projects:
        active_project = projects[0]

    project_payload = [
        serialize_project(project)
        for project in projects
    ]

    if active_project is None:
        return {
            "status": "success",
            "projects": project_payload,
            "active_project": None,
            "summary": {
                "initiative_count": 0,
                "phase_count": 0,
                "step_count": 0,
            },
            "initiatives": [],
        }

    step_queryset = (
        Step.objects
        .select_related("validated_by")
        .order_by("position", "created_at")
    )

    phase_queryset = (
        Phase.objects
        .order_by("position", "created_at")
        .prefetch_related(
            Prefetch(
                "steps",
                queryset=step_queryset,
            )
        )
    )

    initiatives = (
        Initiative.objects
        .filter(project=active_project)
        .select_related("project", "created_by")
        .order_by("position", "created_at")
        .prefetch_related(
            Prefetch(
                "phases",
                queryset=phase_queryset,
            )
        )
    )

    initiative_payload = [
        serialize_initiative(initiative)
        for initiative in initiatives
    ]

    phase_count = sum(
        initiative["phase_count"]
        for initiative in initiative_payload
    )

    step_count = sum(
        phase["step_count"]
        for initiative in initiative_payload
        for phase in initiative["phases"]
    )

    return {
        "status": "success",
        "projects": project_payload,
        "active_project": serialize_project(active_project),
        "summary": {
            "initiative_count": len(initiative_payload),
            "phase_count": phase_count,
            "step_count": step_count,
        },
        "initiatives": initiative_payload,
    }
# ======================================================================
# END: PLANNING_HIERARCHY_QUERY (PATCH 2 OF 7)
# ======================================================================

# ======================================================================
# FILE: aurora/api/planning_api.py (PATCH 3 OF 7)
# START: PLANNING_REQUEST_VALIDATION
# ======================================================================
def parse_json_request(request):
    """Returns a decoded JSON object or a structured validation error."""
    try:
        payload = json.loads(request.body or b"{}")
    except (TypeError, ValueError, json.JSONDecodeError):
        return None, JsonResponse(
            {
                "status": "error",
                "message": "The request body must contain valid JSON.",
            },
            status=400,
        )

    if not isinstance(payload, dict):
        return None, JsonResponse(
            {
                "status": "error",
                "message": "The request body must be a JSON object.",
            },
            status=400,
        )

    return payload, None


def valid_execution_statuses():
    """Returns the persisted lifecycle values accepted by planning records."""
    return {
        choice.value
        for choice in ExecutionStatus
    }


def validate_title(payload, record_label):
    """Validates a required planning-record title."""
    title = str(payload.get("title", "")).strip()

    if not title:
        return None, JsonResponse(
            {
                "status": "error",
                "message": f"{record_label} title is required.",
                "field_errors": {
                    "title": f"Enter a {record_label} title.",
                },
            },
            status=400,
        )

    if len(title) > 255:
        return None, JsonResponse(
            {
                "status": "error",
                "message": (
                    f"{record_label} title must not exceed 255 characters."
                ),
                "field_errors": {
                    "title": "Use 255 characters or fewer.",
                },
            },
            status=400,
        )

    return title, None


def validate_status(payload, record_label):
    """Validates an optional execution status."""
    status = str(
        payload.get("status", ExecutionStatus.PLANNED)
    ).strip().upper()

    if status not in valid_execution_statuses():
        return None, JsonResponse(
            {
                "status": "error",
                "message": f"{record_label} status is invalid.",
                "field_errors": {
                    "status": f"Select a valid {record_label} status.",
                },
            },
            status=400,
        )

    return status, None
# ======================================================================
# END: PLANNING_REQUEST_VALIDATION (PATCH 3 OF 7)
# ======================================================================

# ======================================================================
# FILE: aurora/api/planning_api.py (PATCH 4 OF 7)
# START: INITIATIVE_CREATION_API
# ======================================================================
def create_initiative(request, payload):
    """Validates and persists one new Initiative beneath a Project."""
    project_slug = str(
        payload.get("project_slug", "")
    ).strip()

    if not project_slug:
        return JsonResponse(
            {
                "status": "error",
                "message": "Project is required.",
                "field_errors": {
                    "project_slug": "Select a Project.",
                },
            },
            status=400,
        )

    try:
        project = Project.objects.get(
            slug=project_slug,
            active=True,
        )
    except Project.DoesNotExist:
        return JsonResponse(
            {
                "status": "error",
                "message": "The selected Project does not exist.",
                "field_errors": {
                    "project_slug": "Select a valid active Project.",
                },
            },
            status=404,
        )

    title, error_response = validate_title(
        payload,
        "Initiative",
    )

    if error_response is not None:
        return error_response

    status, error_response = validate_status(
        payload,
        "Initiative",
    )

    if error_response is not None:
        return error_response

    description = str(payload.get("description", "")).strip()

    with transaction.atomic():
        highest_position = (
            Initiative.objects
            .filter(project=project)
            .aggregate(highest=Max("position"))
            .get("highest")
        )

        initiative = Initiative.objects.create(
            project=project,
            title=title,
            description=description,
            status=status,
            position=(
                highest_position + 1
                if highest_position is not None
                else 0
            ),
            created_by=request.user,
        )

    return JsonResponse(
        {
            "status": "success",
            "message": "Initiative created.",
            "initiative": serialize_initiative(initiative),
        },
        status=201,
    )
# ======================================================================
# END: INITIATIVE_CREATION_API (PATCH 4 OF 7)
# ======================================================================

# ======================================================================
# FILE: aurora/api/planning_api.py (PATCH 5 OF 7)
# START: PHASE_CREATION_API
# ======================================================================
def create_phase(payload):
    """Validates and persists one Phase beneath an Initiative."""
    initiative_id = payload.get("initiative_id")

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

    title, error_response = validate_title(
        payload,
        "Phase",
    )

    if error_response is not None:
        return error_response

    status, error_response = validate_status(
        payload,
        "Phase",
    )

    if error_response is not None:
        return error_response

    description = str(payload.get("description", "")).strip()

    with transaction.atomic():
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

    return JsonResponse(
        {
            "status": "success",
            "message": "Phase created.",
            "phase": serialize_phase(phase),
            "initiative_id": initiative.pk,
        },
        status=201,
    )
# ======================================================================
# END: PHASE_CREATION_API (PATCH 5 OF 6)
# ======================================================================

# ======================================================================
# FILE: aurora/api/planning_api.py (PATCH 6 OF 7)
# START: STEP_CREATION_API
# ======================================================================
def create_step(payload):
    """Validates and persists one Step beneath a Phase."""
    phase_id = payload.get("phase_id")

    if phase_id in (None, ""):
        return JsonResponse(
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

    title, error_response = validate_title(
        payload,
        "Step",
    )

    if error_response is not None:
        return error_response

    status, error_response = validate_status(
        payload,
        "Step",
    )

    if error_response is not None:
        return error_response

    estimated_minutes_value = payload.get("estimated_minutes")

    if estimated_minutes_value in (None, ""):
        estimated_minutes = None
    else:
        try:
            estimated_minutes = int(estimated_minutes_value)
        except (TypeError, ValueError):
            return JsonResponse(
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
            return JsonResponse(
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

    estimate_confidence = str(
        payload.get("estimate_confidence", "")
    ).strip().upper()

    if not estimate_confidence:
        estimate_confidence = None
    elif estimate_confidence not in {
        "LOW",
        "MEDIUM",
        "HIGH",
    }:
        return JsonResponse(
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
        payload.get("description", "")
    ).strip()

    validation_description = str(
        payload.get("validation_description", "")
    ).strip()

    with transaction.atomic():
        highest_position = (
            Step.objects
            .filter(phase=phase)
            .aggregate(highest=Max("position"))
            .get("highest")
        )

        step = Step.objects.create(
            phase=phase,
            title=title,
            description=description,
            status=status,
            position=(
                highest_position + 1
                if highest_position is not None
                else 0
            ),
            estimated_minutes=estimated_minutes,
            estimate_confidence=estimate_confidence,
            validation_description=validation_description,
        )

    return JsonResponse(
        {
            "status": "success",
            "message": "Step created.",
            "step": serialize_step(step),
            "phase_id": phase.pk,
            "initiative_id": phase.initiative_id,
        },
        status=201,
    )
# ======================================================================
# END: STEP_CREATION_API (PATCH 6 OF 7)
# ======================================================================

# ======================================================================
# FILE: aurora/api/planning_api.py (PATCH 7 OF 7)
# START: PLANNING_ENDPOINT_ROUTER
# ======================================================================
@login_required
@require_http_methods(["GET", "POST"])
def planning_endpoint(request):
    """Reads the hierarchy or performs a supported planning operation."""
    if request.method == "GET":
        project_slug = str(
            request.GET.get("project", "")
        ).strip()

        return JsonResponse(
            build_planning_payload(
                project_slug=project_slug or None,
            )
        )

    payload, error_response = parse_json_request(request)

    if error_response is not None:
        return error_response

    operation = str(
        payload.get("operation", "create_initiative")
    ).strip().lower()

    if operation == "create_initiative":
        return create_initiative(request, payload)

    if operation == "create_phase":
        return create_phase(payload)

    if operation == "create_step":
        return create_step(payload)

    return JsonResponse(
        {
            "status": "error",
            "message": "The requested planning operation is not supported.",
        },
        status=400,
    )
# ======================================================================
# END: PLANNING_ENDPOINT_ROUTER (PATCH 7 OF 7)
# ======================================================================