# ======================================================================
# FILE: aurora/subsystems/planning/api/initiatives.py
# START: INITIATIVE_PERSISTENCE_IMPORTS
# ======================================================================

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Max
from django.http import JsonResponse

from aurora.models import ExecutionStatus, Initiative, Project
from aurora.subsystems.planning.api.serializers import (
    serialize_initiative,
)
from aurora.subsystems.planning.services.lifecycle import (
    establish_initiative_work,
)
from aurora.subsystems.planning.services.lifecycle.exceptions import (
    PlanningLifecycleError,
)


User = get_user_model()

# ======================================================================
# END: INITIATIVE_PERSISTENCE_IMPORTS
# ======================================================================

# ======================================================================
# FILE: aurora/subsystems/planning/api/initiatives.py
# START: INITIATIVE_PERSISTENCE
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

    assigned_to_id = payload.get("assigned_to_id")

    if assigned_to_id in (None, ""):
        return JsonResponse(
            {
                "status": "error",
                "message": "Initiative assignee is required.",
                "field_errors": {
                    "assigned_to_id": (
                        "Select a user to assign this Initiative."
                    ),
                },
            },
            status=400,
        )

    try:
        assigned_to = User.objects.get(
            pk=assigned_to_id,
            is_active=True,
        )
    except (User.DoesNotExist, TypeError, ValueError):
        return JsonResponse(
            {
                "status": "error",
                "message": "The selected assignee is invalid.",
                "field_errors": {
                    "assigned_to_id": (
                        "Select a valid active user."
                    ),
                },
            },
            status=400,
        )

    created = initiative is None

    status = str(
        payload.get(
            "status",
            (
                ExecutionStatus.PLANNED
                if created
                else initiative.status
            ),
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
                "message": "Initiative status is invalid.",
                "field_errors": {
                    "status": "Select a valid Initiative status.",
                },
            },
            status=400,
        )

    if status == ExecutionStatus.COMPLETED:
        return JsonResponse(
            {
                "status": "error",
                "message": (
                    "Initiative completion must use Planning lifecycle "
                    "authority."
                ),
                "field_errors": {
                    "status": (
                        "Complete the Initiative through its lifecycle "
                        "workflow."
                    ),
                },
            },
            status=409,
        )

    description = str(
        payload.get("description", "")
    ).strip()

    project_changed = (
        initiative is not None
        and initiative.project_id != project.pk
    )

    try:
        with transaction.atomic():
            if created:
                initiative = Initiative(
                    created_by=request.user,
                    status=ExecutionStatus.PLANNED,
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
            initiative.assigned_to = assigned_to

            if status != ExecutionStatus.ACTIVE:
                initiative.status = status

            initiative.save()

            if status == ExecutionStatus.ACTIVE:
                establish_initiative_work(
                    initiative,
                    assigned_to,
                )

                initiative.refresh_from_db()

    except PlanningLifecycleError as exc:
        return JsonResponse(
            {
                "status": "error",
                "message": str(exc),
                "field_errors": {
                    "status": str(exc),
                },
            },
            status=409,
        )

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


def delete_initiative(payload):
    """Deletes an Initiative and its dependent Phases and Steps."""
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
        initiative = (
            Initiative.objects
            .select_related("project")
            .get(pk=initiative_id)
        )
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

    deleted_initiative_id = initiative.pk
    project_slug = initiative.project.slug

    with transaction.atomic():
        initiative.delete()

    return JsonResponse(
        {
            "status": "success",
            "message": "Initiative deleted.",
            "initiative_id": deleted_initiative_id,
            "project_slug": project_slug,
        }
    )


def create_initiative(request, payload):
    """Compatibility wrapper for Initiative creation."""
    return save_initiative(request, payload)
# ======================================================================
# END: INITIATIVE_PERSISTENCE
# ======================================================================