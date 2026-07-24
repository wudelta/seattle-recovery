# ======================================================================
# FILE: aurora/subsystems/planning/api/initiatives.py 
# START: INITIATIVE_PERSISTENCE
# ======================================================================
from django.db import transaction
from django.db.models import Max
from django.http import JsonResponse

from aurora.models import ExecutionStatus, Initiative, Project
from aurora.subsystems.planning.api.serializers import (
    serialize_initiative,
)


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
# END: INITIATIVE_PERSISTENCE 
# ======================================================================