# ======================================================================
# FILE: aurora/subsystems/planning/io/exporter.py
# START: PLANNING_DOCUMENT_EXPORTER
# ======================================================================
from typing import Any

from aurora.models import Project
from aurora.subsystems.planning.io.exceptions import PlanningExportError
from aurora.subsystems.planning.io.schema import SCHEMA_VERSION


def export_planning_document(project: Project) -> dict[str, Any]:
    """Serialize one persisted Project hierarchy into the planning schema."""

    if project is None or not project.pk:
        raise PlanningExportError(
            "A persisted Project is required for planning export."
        )

    initiatives = project.initiatives.order_by("position", "pk")

    return {
        "schema_version": SCHEMA_VERSION,
        "project": {
            "title": project.title,
            "slug": project.slug,
            "description": project.description,
            "status": project.status,
            "position": project.position,
            "active": project.active,
            "initiatives": [
                _export_initiative(initiative)
                for initiative in initiatives
            ],
        },
    }


def _export_initiative(initiative) -> dict[str, Any]:
    phases = initiative.phases.order_by("position", "pk")

    return {
        "title": initiative.title,
        "description": initiative.description,
        "status": initiative.status,
        "position": initiative.position,
        "phases": [
            _export_phase(phase)
            for phase in phases
        ],
    }


def _export_phase(phase) -> dict[str, Any]:
    steps = phase.steps.order_by("position", "pk")

    return {
        "title": phase.title,
        "description": phase.description,
        "status": phase.status,
        "position": phase.position,
        "steps": [
            _export_step(step)
            for step in steps
        ],
    }


def _export_step(step) -> dict[str, Any]:
    document = {
        "title": step.title,
        "description": step.description,
        "status": step.status,
        "position": step.position,
        "estimated_minutes": step.estimated_minutes,
        "estimate_confidence": step.estimate_confidence,
        "risk_level": step.risk_level,
        "risk_description": step.risk_description,
        "validation_description": step.validation_description,
    }

    return {
        key: value
        for key, value in document.items()
        if value not in (None, "")
    }
# ======================================================================
# END: PLANNING_DOCUMENT_EXPORTER
# ======================================================================