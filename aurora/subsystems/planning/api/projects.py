# ======================================================================
# FILE: aurora/subsystems/planning/api/projects.py
# START: PROJECT_PERSISTENCE
# ======================================================================
from django.db import transaction
from django.db.models import Max
from django.http import JsonResponse
from django.utils.text import slugify

from aurora.models import Project


def _serialize_project(project):
    """Serializes one Project for planning API responses."""
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


def _generate_unique_slug(title):
    """Generates a stable unique Project slug from its title."""
    base_slug = slugify(title) or "project"
    candidate = base_slug
    suffix = 2

    while Project.objects.filter(slug=candidate).exists():
        candidate = f"{base_slug}-{suffix}"
        suffix += 1

    return candidate


def _parse_active(value):
    """Normalizes common JSON and form representations of a boolean."""
    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()

    if normalized in {"true", "1", "yes", "on"}:
        return True

    if normalized in {"false", "0", "no", "off", ""}:
        return False

    return None


def save_project(request, payload):
    """Creates or updates one Project."""
    del request

    project_slug = str(
        payload.get("project_slug", "")
    ).strip()

    project = None

    if project_slug:
        try:
            project = Project.objects.get(
                slug=project_slug,
            )
        except Project.DoesNotExist:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "The selected Project does not exist.",
                    "field_errors": {
                        "project_slug": "Select a valid Project.",
                    },
                },
                status=404,
            )

    title = str(payload.get("title", "")).strip()

    if not title:
        return JsonResponse(
            {
                "status": "error",
                "message": "Project title is required.",
                "field_errors": {
                    "title": "Enter a Project title.",
                },
            },
            status=400,
        )

    description = str(
        payload.get("description", "")
    ).strip()

    color = str(
        payload.get("color", "")
    ).strip()

    icon = str(
        payload.get("icon", "")
    ).strip()

    active = _parse_active(
        payload.get(
            "active",
            project.active if project is not None else True,
        )
    )

    if active is None:
        return JsonResponse(
            {
                "status": "error",
                "message": "Project active state is invalid.",
                "field_errors": {
                    "active": "Select a valid active state.",
                },
            },
            status=400,
        )

    created = project is None

    with transaction.atomic():
        if created:
            highest_position = (
                Project.objects
                .aggregate(highest=Max("position"))
                .get("highest")
            )

            project = Project(
                slug=_generate_unique_slug(title),
                position=(
                    highest_position + 1
                    if highest_position is not None
                    else 0
                ),
            )

        project.title = title
        project.description = description
        project.color = color
        project.icon = icon
        project.active = active
        project.save()

    return JsonResponse(
        {
            "status": "success",
            "message": (
                "Project created."
                if created
                else "Project updated."
            ),
            "project": _serialize_project(project),
        },
        status=201 if created else 200,
    )


def delete_project(payload):
    """Deletes an empty Project."""
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
        )
    except Project.DoesNotExist:
        return JsonResponse(
            {
                "status": "error",
                "message": "The selected Project does not exist.",
                "field_errors": {
                    "project_slug": "Select a valid Project.",
                },
            },
            status=404,
        )

    initiative_count = project.initiatives.count()

    if initiative_count:
        return JsonResponse(
            {
                "status": "error",
                "message": (
                    "Delete all Initiatives before deleting this Project."
                ),
                "initiative_count": initiative_count,
            },
            status=409,
        )

    deleted_project_slug = project.slug

    with transaction.atomic():
        project.delete()

    return JsonResponse(
        {
            "status": "success",
            "message": "Project deleted.",
            "project_slug": deleted_project_slug,
        }
    )


def create_project(request, payload):
    """Compatibility wrapper for Project creation."""
    return save_project(request, payload)
# ======================================================================
# END: PROJECT_PERSISTENCE
# ======================================================================