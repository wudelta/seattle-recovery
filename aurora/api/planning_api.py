# ======================================================================
# FILE: aurora/api/planning_api.py (PATCH 1 OF 9)
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


def serialize_initiative_option(initiative):
    """Serializes one Initiative for the workspace selector."""
    return {
        "id": initiative.pk,
        "project_id": initiative.project_id,
        "title": initiative.title,
        "status": initiative.status,
        "status_label": initiative.get_status_display(),
        "position": initiative.position,
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
# END: PLANNING_SERIALIZATION (PATCH 1 OF 9)
# ======================================================================

# ======================================================================
# FILE: aurora/api/planning_api.py (PATCH 2 OF 9)
# START: PLANNING_HIERARCHY_QUERY
# ======================================================================
def build_planning_payload(
    project_slug=None,
    initiative_id=None,
):
    """Builds the focused planning workspace for one active Project."""
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
            "initiative_options": [],
            "active_initiative": None,
            "summary": {
                "initiative_count": 0,
                "phase_count": 0,
                "step_count": 0,
            },
        }

    initiative_options = list(
        Initiative.objects
        .filter(project=active_project)
        .select_related("project")
        .order_by("position", "created_at")
    )

    active_initiative = None

    if initiative_id not in (None, ""):
        requested_initiative_id = str(initiative_id)

        active_initiative = next(
            (
                initiative
                for initiative in initiative_options
                if str(initiative.pk) == requested_initiative_id
            ),
            None,
        )

    if active_initiative is None and initiative_options:
        active_initiative = initiative_options[0]

    active_initiative_payload = None

    if active_initiative is not None:
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

        active_initiative = (
            Initiative.objects
            .select_related("project", "created_by")
            .prefetch_related(
                Prefetch(
                    "phases",
                    queryset=phase_queryset,
                )
            )
            .get(pk=active_initiative.pk)
        )

        active_initiative_payload = serialize_initiative(
            active_initiative
        )

    phase_count = (
        active_initiative_payload["phase_count"]
        if active_initiative_payload
        else 0
    )

    step_count = sum(
        phase["step_count"]
        for phase in (
            active_initiative_payload["phases"]
            if active_initiative_payload
            else []
        )
    )

    return {
        "status": "success",
        "projects": project_payload,
        "active_project": serialize_project(active_project),
        "initiative_options": [
            serialize_initiative_option(initiative)
            for initiative in initiative_options
        ],
        "active_initiative": active_initiative_payload,
        "summary": {
            "initiative_count": len(initiative_options),
            "phase_count": phase_count,
            "step_count": step_count,
        },
    }
# ======================================================================
# END: PLANNING_HIERARCHY_QUERY (PATCH 2 OF 9)
# ======================================================================

# ======================================================================
# FILE: aurora/api/planning_api.py (PATCH 3 OF 9)
# START: PLANNING_API_ENDPOINT
# ======================================================================
@login_required
@require_http_methods(["GET", "POST"])
def planning_api(request):
    """Reads or creates Decision Engine planning records."""
    if request.method == "GET":
        project_slug = request.GET.get("project")
        initiative_id = request.GET.get("initiative")

        return JsonResponse(
            build_planning_payload(
                project_slug=project_slug,
                initiative_id=initiative_id,
            )
        )

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "status": "error",
                "message": "Request body must contain valid JSON.",
            },
            status=400,
        )

    operation = payload.get("operation")

    if operation == "create_initiative":
        return create_initiative(request, payload)

    if operation == "create_phase":
        return create_phase(payload)

    if operation == "create_step":
        return create_step(payload)

    return JsonResponse(
        {
            "status": "error",
            "message": (
                "operation must be create_initiative, "
                "create_phase, or create_step."
            ),
        },
        status=400,
    )
# ======================================================================
# END: PLANNING_API_ENDPOINT (PATCH 3 OF 9)
# ======================================================================

# ======================================================================
# FILE: aurora/api/planning_api.py (PATCH 4 OF 9)
# START: INITIATIVE_CREATION_API
# ======================================================================
def save_initiative(request, payload):
    """Creates or updates one Initiative beneath a Project."""
    initiative_id = payload.get("initiative_id")
    initiative = None

    if initiative_id not in (None, ""):
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

    title = str(payload.get("title", "")).strip()

    if not title:
        return JsonResponse(
            {
                "status": "error",
                "message": "Initiative title is required.",
                "field_errors": {
                    "title": "Enter an Initiative title.",
                },
            },
            status=400,
        )

    status = str(
        payload.get("status", ExecutionStatus.PLANNED)
    ).strip().upper()

    valid_statuses = {
        choice.value
        for choice in ExecutionStatus
    }

    if status not in valid_statuses:
        return JsonResponse(
            {
                "status": "error",
                "message": "Initiative status is invalid.",
                "field_errors": {
                    "status": "Select a valid Initiative status.",
                },
            },
            status=400,
        )

    description = str(
        payload.get("description", "")
    ).strip()

    created = initiative is None
    project_changed = (
        initiative is not None
        and initiative.project_id != project.pk
    )

    with transaction.atomic():
        if created:
            initiative = Initiative(
                created_by=request.user,
            )

        if created or project_changed:
            highest_position = (
                Initiative.objects
                .filter(project=project)
                .aggregate(highest=Max("position"))
                .get("highest")
            )

            initiative.position = (
                highest_position + 1
                if highest_position is not None
                else 0
            )

        initiative.project = project
        initiative.title = title
        initiative.description = description
        initiative.status = status
        initiative.save()

    return JsonResponse(
        {
            "status": "success",
            "message": (
                "Initiative created."
                if created
                else "Initiative updated."
            ),
            "initiative": serialize_initiative(initiative),
        },
        status=201 if created else 200,
    )


def create_initiative(request, payload):
    """Compatibility wrapper for Initiative creation."""
    return save_initiative(request, payload)
# ======================================================================
# END: INITIATIVE_CREATION_API (PATCH 4 OF 9)
# ======================================================================

# ======================================================================
# FILE: aurora/api/planning_api.py (PATCH 5 OF 9)
# START: PHASE_CREATION_API
# ======================================================================
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
# END: PHASE_CREATION_API (PATCH 5 OF 9)
# ======================================================================

# ======================================================================
# FILE: aurora/api/planning_api.py (PATCH 6 OF 9)
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

    return {
        "step": step,
        "phase": phase,
        "title": title,
        "status": status,
    }, None
# ======================================================================
# END: STEP_SAVE_CONTEXT (PATCH 6 OF 9)
# ======================================================================

# ======================================================================
# FILE: aurora/api/planning_api.py (PATCH 7 OF 9)
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
# END: STEP_SAVE_DETAILS (PATCH 7 OF 9)
# ======================================================================

# ======================================================================
# FILE: aurora/api/planning_api.py (PATCH 8 OF 9)
# START: STEP_CREATION_API
# ======================================================================
def save_step(payload):
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


def create_step(payload):
    """Compatibility wrapper until endpoint dispatch uses save operations."""
    return save_step(payload)
# ======================================================================
# END: STEP_CREATION_API (PATCH 8 OF 9)
# ======================================================================

# ======================================================================
# FILE: aurora/api/planning_api.py (PATCH 9 OF 9)
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

        initiative_id = str(
            request.GET.get("initiative", "")
        ).strip()

        return JsonResponse(
            build_planning_payload(
                project_slug=project_slug or None,
                initiative_id=initiative_id or None,
            )
        )

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "status": "error",
                "message": "Request body must contain valid JSON.",
            },
            status=400,
        )

    operation = str(
        payload.get("operation", "create_initiative")
    ).strip().lower()

    if operation in {
        "create_initiative",
        "save_initiative",
    }:
        return save_initiative(request, payload)

    if operation in {
        "create_phase",
        "save_phase",
    }:
        return save_phase(payload)

    if operation in {
        "create_step",
        "save_step",
    }:
        return save_step(payload)

    return JsonResponse(
        {
            "status": "error",
            "message": "The requested planning operation is not supported.",
        },
        status=400,
    )
# ======================================================================
# END: PLANNING_ENDPOINT_ROUTER (PATCH 9 OF 9)
# ======================================================================