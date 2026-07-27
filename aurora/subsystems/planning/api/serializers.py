# ======================================================================
# FILE: aurora/subsystems/planning/api/serializers.py
# START: PLANNING_SERIALIZERS
# ======================================================================
from aurora.models import Initiative


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
    created_by = serialize_user(project.created_by)
    assigned_to = serialize_user(project.assigned_to)

    return {
        "id": project.pk,
        "title": project.title,
        "slug": project.slug,
        "description": project.description,
        "color": project.color,
        "icon": project.icon,
        "status": project.status,
        "status_label": project.get_status_display(),
        "position": project.position,
        "active": project.active,
        "created_by": created_by,
        "created_by_name": (
            created_by["display_name"]
            if created_by
            else ""
        ),
        "assigned_to": assigned_to,
        "assigned_to_id": (
            str(project.assigned_to_id)
            if project.assigned_to_id
            else None
        ),
        "assigned_to_name": (
            assigned_to["display_name"]
            if assigned_to
            else ""
        ),
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


def serialize_initiative(initiative: Initiative):
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
# END: PLANNING_SERIALIZERS
# ======================================================================