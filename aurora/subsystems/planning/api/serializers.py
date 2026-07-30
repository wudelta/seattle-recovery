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


def serialize_step_file(step_file):
    """Serializes one planned or actual repository file."""
    return {
        "id": step_file.pk,
        "file_path": step_file.file_path,
        "role": step_file.role,
        "role_label": step_file.get_role_display(),
        "reason": step_file.reason,
        "recorded_by_id": (
            str(step_file.recorded_by_id)
            if step_file.recorded_by_id
            else None
        ),
        "created_at": step_file.created_at.isoformat(),
        "updated_at": step_file.updated_at.isoformat(),
    }


def serialize_step(step):
    """Serializes one implementation step for the planning workspace."""
    created_by = serialize_user(step.created_by)
    assigned_to = serialize_user(step.assigned_to)

    document = getattr(
        step,
        "document",
        None,
    )

    validation = getattr(
        step,
        "validation",
        None,
    )

    step_files = list(step.files.all())

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

        # Legacy validation contract retained during staged migration.
        "validation_description": step.validation_description,
        "validated_by": serialize_user(step.validated_by),
        "validation_notes": step.validation_notes,

        "document": (
            {
                "id": document.pk,
                "technical_design": document.technical_design,
                "dependencies": document.dependencies,
                "assumptions": document.assumptions,
                "implementation_notes": (
                    document.implementation_notes
                ),
                "discussion": document.discussion,
                "created_at": document.created_at.isoformat(),
                "updated_at": document.updated_at.isoformat(),
            }
            if document
            else None
        ),
        "validation": (
            {
                "id": validation.pk,
                "description": validation.description,
                "notes": validation.notes,
                "validated_by": serialize_user(
                    validation.validated_by
                ),
                "validated_by_id": (
                    str(validation.validated_by_id)
                    if validation.validated_by_id
                    else None
                ),
                "validated_at": (
                    validation.validated_at.isoformat()
                    if validation.validated_at
                    else None
                ),
                "created_at": validation.created_at.isoformat(),
                "updated_at": validation.updated_at.isoformat(),
            }
            if validation
            else None
        ),
        "planned_files": [
            serialize_step_file(step_file)
            for step_file in step_files
            if step_file.role == "PLANNED"
        ],
        "actual_files": [
            serialize_step_file(step_file)
            for step_file in step_files
            if step_file.role == "ACTUAL"
        ],
        "created_by": created_by,
        "created_by_name": (
            created_by["display_name"]
            if created_by
            else ""
        ),
        "assigned_to": assigned_to,
        "assigned_to_id": (
            str(step.assigned_to_id)
            if step.assigned_to_id
            else None
        ),
        "assigned_to_name": (
            assigned_to["display_name"]
            if assigned_to
            else ""
        ),
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
    created_by = serialize_user(phase.created_by)
    assigned_to = serialize_user(phase.assigned_to)

    return {
        "id": phase.pk,
        "title": phase.title,
        "description": phase.description,
        "status": phase.status,
        "status_label": phase.get_status_display(),
        "position": phase.position,
        "step_count": len(steps),
        "created_by": created_by,
        "created_by_name": (
            created_by["display_name"]
            if created_by
            else ""
        ),
        "assigned_to": assigned_to,
        "assigned_to_id": (
            str(phase.assigned_to_id)
            if phase.assigned_to_id
            else None
        ),
        "assigned_to_name": (
            assigned_to["display_name"]
            if assigned_to
            else ""
        ),
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
    created_by = serialize_user(initiative.created_by)
    assigned_to = serialize_user(initiative.assigned_to)

    return {
        "id": initiative.pk,
        "project_id": initiative.project_id,
        "project_slug": initiative.project.slug,
        "title": initiative.title,
        "description": initiative.description,
        "status": initiative.status,
        "status_label": initiative.get_status_display(),
        "position": initiative.position,
        "created_by": created_by,
        "created_by_name": (
            created_by["display_name"]
            if created_by
            else ""
        ),
        "assigned_to": assigned_to,
        "assigned_to_id": (
            str(initiative.assigned_to_id)
            if initiative.assigned_to_id
            else None
        ),
        "assigned_to_name": (
            assigned_to["display_name"]
            if assigned_to
            else ""
        ),
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