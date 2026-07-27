# ======================================================================
# FILE: aurora/subsystems/planning/api/projects.py
# START: PROJECT_PERSISTENCE
# ======================================================================
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max
from django.http import JsonResponse
from django.utils.text import slugify

from aurora.models import ExecutionStatus, Project


User = get_user_model()


def _user_display_name(user):
    """Returns a stable human-readable label for one user."""
    return user.get_full_name().strip() or user.username


def _serialize_project(project):
    """Serializes one Project for planning API responses."""
    return {
        "id": project.pk,
        "title": project.title,
        "slug": project.slug,
        "description": project.description,
        "color": project.color,
        "icon": project.icon,
        "status": project.status,
        "position": project.position,
        "active": project.active,
        "created_by_id": str(project.created_by_id),
        "created_by_name": _user_display_name(
            project.created_by
        ),
        "assigned_to_id": str(project.assigned_to_id),
        "assigned_to_name": _user_display_name(
            project.assigned_to
        ),
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


def _resolve_assigned_user(payload, project):
    """Resolves an assignee UUID or preserves the existing assignee."""
    assigned_to_id = str(
        payload.get("assigned_to_id") or ""
    ).strip()

    if not assigned_to_id:
        if project is not None:
            return project.assigned_to, None

        return None, JsonResponse(
            {
                "status": "error",
                "message": "Project assignment is required.",
                "field_errors": {
                    "assigned_to_id": (
                        "Select a user to assign this Project."
                    ),
                },
            },
            status=400,
        )

    try:
        assigned_to = User.objects.get(
            pk=assigned_to_id,
        )
    except (User.DoesNotExist, ValidationError, ValueError):
        return None, JsonResponse(
            {
                "status": "error",
                "message": "The selected assignee does not exist.",
                "field_errors": {
                    "assigned_to_id": (
                        "Select a valid user. The assigned_to_id "
                        "value must be the user's UUID."
                    ),
                },
            },
            status=400,
        )

    return assigned_to, None


def _parse_project_status(payload, project):
    """Returns a valid lifecycle status or a field error response."""
    default_status = (
        project.status
        if project is not None
        else ExecutionStatus.PLANNED
    )

    status_value = str(
        payload.get("status") or default_status
    ).strip().upper()

    if status_value not in ExecutionStatus.values:
        return None, JsonResponse(
            {
                "status": "error",
                "message": "Project status is invalid.",
                "field_errors": {
                    "status": "Select a valid Project status.",
                },
            },
            status=400,
        )

    return status_value, None


def _active_project_conflict(project):
    """Returns whether another Project already has ACTIVE status."""
    active_projects = Project.objects.filter(
        status=ExecutionStatus.ACTIVE,
    )

    if project is not None:
        active_projects = active_projects.exclude(
            pk=project.pk,
        )

    return active_projects.exists()


def save_project(request, payload):
    """Creates or updates one Project."""
    project_slug = str(
        payload.get("project_slug") or ""
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
                    "message": (
                        "The selected Project does not exist."
                    ),
                    "field_errors": {
                        "project_slug": (
                            "Select a valid Project."
                        ),
                    },
                },
                status=404,
            )

    title = str(
        payload.get("title") or ""
    ).strip()

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
        payload.get("description") or ""
    ).strip()

    color = str(
        payload.get("color") or ""
    ).strip()

    icon = str(
        payload.get("icon") or ""
    ).strip()

    status_value, status_error = _parse_project_status(
        payload,
        project,
    )

    if status_error is not None:
        return status_error

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
                    "active": (
                        "Select a valid active state."
                    ),
                },
            },
            status=400,
        )

    assigned_to, assignment_error = _resolve_assigned_user(
        payload,
        project,
    )

    if assignment_error is not None:
        return assignment_error

    if (
        status_value == ExecutionStatus.ACTIVE
        and _active_project_conflict(project)
    ):
        return JsonResponse(
            {
                "status": "error",
                "message": "Another Project is already active.",
                "field_errors": {
                    "status": (
                        "Pause or complete the active Project "
                        "before activating this one."
                    ),
                },
            },
            status=409,
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
                created_by=request.user,
            )

        project.title = title
        project.description = description
        project.color = color
        project.icon = icon
        project.status = status_value
        project.active = active
        project.assigned_to = assigned_to
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
        payload.get("project_slug") or ""
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
                "message": (
                    "The selected Project does not exist."
                ),
                "field_errors": {
                    "project_slug": (
                        "Select a valid Project."
                    ),
                },
            },
            status=404,
        )

    initiative_count = project.initiatives.count()

    if initiative_count:
        phase_count = (
            project.initiatives
            .filter(phases__isnull=False)
            .values("phases__pk")
            .distinct()
            .count()
        )

        step_count = (
            project.initiatives
            .filter(phases__steps__isnull=False)
            .values("phases__steps__pk")
            .distinct()
            .count()
        )

        return JsonResponse(
            {
                "status": "error",
                "message": (
                    "This Project cannot be deleted because it "
                    "contains planning work."
                ),
                "initiative_count": initiative_count,
                "phase_count": phase_count,
                "step_count": step_count,
                "can_delete": False,
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