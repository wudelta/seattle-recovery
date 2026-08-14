# ======================================================================
# FILE: aurora/subsystems/planning/services/reconciliation.py
# START: PLANNING_RECONCILIATION_SNAPSHOT_SERVICE
# ======================================================================

from typing import Any

from aurora.models import Project, UserPosition


def _serialize_user(user) -> dict[str, Any] | None:
    """Return stable user identity for reconciliation evidence."""

    if user is None:
        return None

    return {
        "id": str(user.pk),
        "username": user.username,
    }


def _serialize_time_entries(step) -> list[dict[str, Any]]:
    """Return historical work intervals recorded against one Step."""

    return [
        {
            "id": entry.pk,
            "user": _serialize_user(entry.user),
            "started_at": entry.started_at.isoformat(),
            "ended_at": (
                entry.ended_at.isoformat()
                if entry.ended_at
                else None
            ),
        }
        for entry in step.time_entries.all().order_by(
            "started_at",
            "pk",
        )
    ]


def _serialize_step(step) -> dict[str, Any]:
    """Return reconciliation evidence for one persisted Step."""

    return {
        "id": step.pk,
        "title": step.title,
        "description": step.description,
        "status": step.status,
        "position": step.position,
        "assigned_to": _serialize_user(step.assigned_to),
        "created_by": _serialize_user(step.created_by),
        "estimated_minutes": step.estimated_minutes,
        "estimate_confidence": step.estimate_confidence,
        "risk_level": step.risk_level,
        "risk_description": step.risk_description,
        "validation_description": step.validation_description,
        "validated_by": _serialize_user(step.validated_by),
        "validation_notes": step.validation_notes,
        "created_at": step.created_at.isoformat(),
        "updated_at": step.updated_at.isoformat(),
        "completed_at": (
            step.completed_at.isoformat()
            if step.completed_at
            else None
        ),
        "time_entries": _serialize_time_entries(step),
    }


def _serialize_phase(phase) -> dict[str, Any]:
    """Return reconciliation evidence for one persisted Phase."""

    return {
        "id": phase.pk,
        "title": phase.title,
        "description": phase.description,
        "status": phase.status,
        "position": phase.position,
        "assigned_to": _serialize_user(phase.assigned_to),
        "created_by": _serialize_user(phase.created_by),
        "created_at": phase.created_at.isoformat(),
        "updated_at": phase.updated_at.isoformat(),
        "completed_at": (
            phase.completed_at.isoformat()
            if phase.completed_at
            else None
        ),
        "steps": [
            _serialize_step(step)
            for step in phase.steps.all().order_by(
                "position",
                "pk",
            )
        ],
    }


def _serialize_initiative(initiative) -> dict[str, Any]:
    """Return reconciliation evidence for one persisted Initiative."""

    return {
        "id": initiative.pk,
        "title": initiative.title,
        "description": initiative.description,
        "status": initiative.status,
        "position": initiative.position,
        "assigned_to": _serialize_user(initiative.assigned_to),
        "created_by": _serialize_user(initiative.created_by),
        "created_at": initiative.created_at.isoformat(),
        "updated_at": initiative.updated_at.isoformat(),
        "completed_at": (
            initiative.completed_at.isoformat()
            if initiative.completed_at
            else None
        ),
        "phases": [
            _serialize_phase(phase)
            for phase in initiative.phases.all().order_by(
                "position",
                "pk",
            )
        ],
    }


def _serialize_project(project) -> dict[str, Any]:
    """Return reconciliation evidence for one persisted Project."""

    return {
        "id": project.pk,
        "title": project.title,
        "slug": project.slug,
        "description": project.description,
        "status": project.status,
        "position": project.position,
        "active": project.active,
        "assigned_to": _serialize_user(project.assigned_to),
        "created_by": _serialize_user(project.created_by),
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
        "completed_at": (
            project.completed_at.isoformat()
            if project.completed_at
            else None
        ),
        "initiatives": [
            _serialize_initiative(initiative)
            for initiative in project.initiatives.all().order_by(
                "position",
                "pk",
            )
        ],
    }


def _serialize_user_positions() -> list[dict[str, Any]]:
    """
    Return current UI navigation positions.

    UserPosition is diagnostic evidence only. It represents where a user
    is currently positioned in Planning and must not be treated as proof
    of executable work.
    """

    positions = (
        UserPosition.objects
        .select_related(
            "user",
            "project",
            "initiative",
            "phase",
            "step",
        )
        .order_by("user__username")
    )

    return [
        {
            "user": _serialize_user(position.user),
            "project_id": position.project_id,
            "initiative_id": position.initiative_id,
            "phase_id": position.phase_id,
            "step_id": position.step_id,
            "updated_at": position.updated_at.isoformat(),
        }
        for position in positions
    ]


def build_planning_reconciliation_snapshot() -> dict[str, Any]:
    """
    Return authoritative persisted Planning evidence for reconciliation.

    This snapshot is diagnostic. It is not an import document and must not
    be treated as the canonical Planning interchange schema.
    """

    projects = (
        Project.objects
        .select_related(
            "assigned_to",
            "created_by",
        )
        .prefetch_related(
            "initiatives__assigned_to",
            "initiatives__created_by",
            "initiatives__phases__assigned_to",
            "initiatives__phases__created_by",
            "initiatives__phases__steps__assigned_to",
            "initiatives__phases__steps__created_by",
            "initiatives__phases__steps__validated_by",
            "initiatives__phases__steps__time_entries__user",
        )
        .order_by(
            "position",
            "pk",
        )
    )

    return {
        "snapshot_type": "planning_reconciliation",
        "projects": [
            _serialize_project(project)
            for project in projects
        ],
        "user_positions": _serialize_user_positions(),
    }

# ======================================================================
# FILE: aurora/subsystems/planning/services/reconciliation.py
# END: PLANNING_RECONCILIATION_SNAPSHOT_SERVICE
# ======================================================================