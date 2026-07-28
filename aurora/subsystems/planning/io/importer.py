# ======================================================================
# FILE: aurora/subsystems/planning/io/importer.py
# START: PLANNING_DOCUMENT_IMPORTER
# ======================================================================
from dataclasses import dataclass
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction

from aurora.models import Initiative, Phase, Project, Step
from aurora.subsystems.planning.io.exceptions import PlanningImportError
from aurora.subsystems.planning.io.schema import validate_planning_document


User = get_user_model()


@dataclass(frozen=True)
class PlanningImportResult:
    """Summary of a validated planning-document import."""

    project_slug: str
    projects: int
    initiatives: int
    phases: int
    steps: int
    applied: bool


def import_planning_document(
    document: Any,
    *,
    user: User,
    apply: bool = False,
) -> PlanningImportResult:
    """Validate and optionally import one complete planning hierarchy."""

    if user is None or not user.pk:
        raise PlanningImportError(
            "A persisted user is required to import a planning document."
        )

    normalized = validate_planning_document(document)
    project_data = normalized["project"]
    counts = _count_records(project_data)

    if Project.objects.filter(slug=project_data["slug"]).exists():
        raise PlanningImportError(
            f'A project with slug "{project_data["slug"]}" already exists.'
        )

    result = PlanningImportResult(
        project_slug=project_data["slug"],
        projects=1,
        initiatives=counts["initiatives"],
        phases=counts["phases"],
        steps=counts["steps"],
        applied=apply,
    )

    if not apply:
        return result

    try:
        with transaction.atomic():
            project = _create_project(project_data, user)

            for initiative_data in project_data["initiatives"]:
                initiative = _create_initiative(
                    initiative_data,
                    project,
                    user,
                )

                for phase_data in initiative_data["phases"]:
                    phase = _create_phase(
                        phase_data,
                        initiative,
                        user,
                    )

                    for step_data in phase_data["steps"]:
                        _create_step(
                            step_data,
                            phase,
                            user,
                        )
    except Exception as exc:
        if isinstance(exc, PlanningImportError):
            raise

        raise PlanningImportError(
            f'Planning import for project "{project_data["slug"]}" failed.'
        ) from exc

    return result


def _create_project(
    data: dict[str, Any],
    user: User,
) -> Project:
    project = Project(
        title=data["title"],
        slug=data["slug"],
        description=data["description"],
        status=data["status"],
        position=data["position"],
        active=data["active"],
        created_by=user,
        assigned_to=user,
    )
    project.full_clean()
    project.save()

    return project


def _create_initiative(
    data: dict[str, Any],
    project: Project,
    user: User,
) -> Initiative:
    initiative = Initiative(
        project=project,
        title=data["title"],
        description=data["description"],
        status=data["status"],
        position=data["position"],
        created_by=user,
        assigned_to=user,
    )
    initiative.full_clean()
    initiative.save()

    return initiative


def _create_phase(
    data: dict[str, Any],
    initiative: Initiative,
    user: User,
) -> Phase:
    phase = Phase(
        initiative=initiative,
        title=data["title"],
        description=data["description"],
        status=data["status"],
        position=data["position"],
        created_by=user,
        assigned_to=user,
    )
    phase.full_clean()
    phase.save()

    return phase


def _create_step(
    data: dict[str, Any],
    phase: Phase,
    user: User,
) -> Step:
    step = Step(
        phase=phase,
        title=data["title"],
        description=data["description"],
        status=data["status"],
        position=data["position"],
        estimated_minutes=data["estimated_minutes"],
        estimate_confidence=data["estimate_confidence"],
        risk_level=data["risk_level"],
        risk_description=data["risk_description"],
        validation_description=data["validation_description"],
        created_by=user,
        assigned_to=user,
    )
    step.full_clean()
    step.save()

    return step


def _count_records(project_data: dict[str, Any]) -> dict[str, int]:
    initiatives = project_data["initiatives"]
    phases = [
        phase
        for initiative in initiatives
        for phase in initiative["phases"]
    ]
    steps = [
        step
        for phase in phases
        for step in phase["steps"]
    ]

    return {
        "initiatives": len(initiatives),
        "phases": len(phases),
        "steps": len(steps),
    }
# ======================================================================
# END: PLANNING_DOCUMENT_IMPORTER
# ======================================================================