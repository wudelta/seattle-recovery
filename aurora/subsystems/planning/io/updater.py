# ======================================================================
# FILE: aurora/subsystems/planning/io/updater.py
# START: PLANNING_DOCUMENT_UPDATER
# ======================================================================
from dataclasses import dataclass
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Max

from aurora.models import (
    Initiative,
    Phase,
    Project,
    Step,
    StepDocument,
    StepFile,
    StepValidation,
)
from aurora.subsystems.planning.io.exceptions import PlanningImportError
from aurora.subsystems.planning.io.schema import validate_planning_update


User = get_user_model()


@dataclass(frozen=True)
class PlanningUpdateResult:
    """Summary of a validated planning-document update."""

    project_slug: str
    projects: int
    initiatives: int
    phases: int
    steps: int
    applied: bool


def update_planning_document(
    document: Any,
    *,
    user: User,
    apply: bool = False,
) -> PlanningUpdateResult:
    """Validate and optionally apply a planning dictionary update."""

    if user is None or not user.pk:
        raise PlanningImportError(
            "A persisted user is required to update a planning document."
        )

    normalized = validate_planning_update(document)
    project_slug = normalized["target"]["project_slug"]
    counts = _count_records(normalized)

    result = PlanningUpdateResult(
        project_slug=project_slug,
        projects=counts["projects"],
        initiatives=counts["initiatives"],
        phases=counts["phases"],
        steps=counts["steps"],
        applied=apply,
    )

    if not apply:
        project = _resolve_project_for_validation(
            project_slug,
            normalized,
        )
        _validate_database_targets(project, normalized)
        return result

    try:
        with transaction.atomic():
            project = _resolve_project_for_apply(
                project_slug,
                normalized,
                user,
            )
            context = _validate_database_targets(
                project,
                normalized,
            )
            _apply_update(
                project=project,
                normalized=normalized,
                context=context,
                user=user,
            )
    except Exception as exc:
        if isinstance(exc, PlanningImportError):
            raise

        raise PlanningImportError(
            f'Planning update for project "{project_slug}" failed.'
        ) from exc

    return result


def _resolve_project_for_validation(
    project_slug: str,
    normalized: dict[str, Any],
) -> Project:
    project = Project.objects.filter(slug=project_slug).first()
    project_additions = normalized["add_projects"]

    if project is not None:
        if project_additions:
            raise PlanningImportError(
                f'Project "{project_slug}" already exists and cannot be added again.'
            )

        return project

    if not project_additions:
        raise PlanningImportError(
            f'Project "{project_slug}" does not exist.'
        )

    return _build_unsaved_project(project_additions[0])


def _resolve_project_for_apply(
    project_slug: str,
    normalized: dict[str, Any],
    user: User,
) -> Project:
    project = (
        Project.objects
        .select_for_update()
        .filter(slug=project_slug)
        .first()
    )
    project_additions = normalized["add_projects"]

    if project is not None:
        if project_additions:
            raise PlanningImportError(
                f'Project "{project_slug}" already exists and cannot be added again.'
            )

        return project

    if not project_additions:
        raise PlanningImportError(
            f'Project "{project_slug}" does not exist.'
        )

    project = _build_unsaved_project(
        project_additions[0],
        user=user,
    )
    project.position = _next_position(Project.objects.all())
    project.full_clean()
    project.save()

    return project


def _build_unsaved_project(
    data: dict[str, Any],
    *,
    user: User | None = None,
) -> Project:
    return Project(
        title=data["title"],
        slug=data["slug"],
        description=data["description"],
        status=data["status"],
        active=data["active"],
        position=0,
        created_by=user,
        assigned_to=user,
    )


def _validate_database_targets(
    project: Project,
    normalized: dict[str, Any],
) -> dict[str, Any]:
    initiatives = {
        initiative.title: initiative
        for initiative in Initiative.objects.filter(project=project)
    } if project.pk else {}
    planned_initiative_titles = set(initiatives)

    phases: dict[tuple[str, str], Phase] = {}
    planned_phase_titles: dict[str, set[str]] = {}
    planned_step_titles: dict[tuple[str, str], set[str]] = {}

    for initiative_title, initiative in initiatives.items():
        initiative_phases = Phase.objects.filter(
            initiative=initiative
        )

        planned_phase_titles[initiative_title] = set()

        for phase in initiative_phases:
            phase_key = (initiative_title, phase.title)
            phases[phase_key] = phase
            planned_phase_titles[initiative_title].add(phase.title)
            planned_step_titles[phase_key] = set(
                Step.objects.filter(phase=phase).values_list(
                    "title",
                    flat=True,
                )
            )

    for initiative_data in normalized["add_initiatives"]:
        initiative_title = initiative_data["title"]

        if initiative_title in planned_initiative_titles:
            raise PlanningImportError(
                f'Initiative "{initiative_title}" already exists '
                f'in project "{project.slug}".'
            )

        planned_initiative_titles.add(initiative_title)

    for addition in normalized["add_phases"]:
        initiative_title = addition["initiative_title"]

        if initiative_title not in initiatives:
            raise PlanningImportError(
                f'Initiative "{initiative_title}" does not exist '
                f'in project "{project.slug}".'
            )

        for phase_data in addition["phases"]:
            phase_title = phase_data["title"]

            if phase_title in planned_phase_titles[initiative_title]:
                raise PlanningImportError(
                    f'Phase "{phase_title}" already exists in '
                    f'Initiative "{initiative_title}".'
                )

            planned_phase_titles[initiative_title].add(phase_title)

    for addition in normalized["add_steps"]:
        initiative_title = addition["initiative_title"]
        phase_title = addition["phase_title"]
        phase_key = (initiative_title, phase_title)

        if initiative_title not in initiatives:
            raise PlanningImportError(
                f'Initiative "{initiative_title}" does not exist '
                f'in project "{project.slug}".'
            )

        if phase_key not in phases:
            raise PlanningImportError(
                f'Phase "{phase_title}" does not exist in '
                f'Initiative "{initiative_title}".'
            )

        for step_data in addition["steps"]:
            step_title = step_data["title"]

            if step_title in planned_step_titles[phase_key]:
                raise PlanningImportError(
                    f'Step "{step_title}" already exists in '
                    f'Phase "{phase_title}".'
                )

            planned_step_titles[phase_key].add(step_title)

    return {
        "initiatives": initiatives,
        "phases": phases,
    }


def _apply_update(
    *,
    project: Project,
    normalized: dict[str, Any],
    context: dict[str, Any],
    user: User,
) -> None:
    initiatives = context["initiatives"]
    phases = context["phases"]

    next_initiative_position = _next_position(
        Initiative.objects.filter(project=project)
    )

    for initiative_data in normalized["add_initiatives"]:
        initiative = _create_initiative(
            initiative_data,
            project,
            user,
            next_initiative_position,
        )
        next_initiative_position += 1

        next_phase_position = 1

        for phase_data in initiative_data["phases"]:
            phase = _create_phase(
                phase_data,
                initiative,
                user,
                next_phase_position,
            )
            next_phase_position += 1

            next_step_position = 1

            for step_data in phase_data["steps"]:
                _create_step(
                    step_data,
                    phase,
                    user,
                    next_step_position,
                )
                next_step_position += 1

    for addition in normalized["add_phases"]:
        initiative = initiatives[addition["initiative_title"]]
        next_phase_position = _next_position(
            Phase.objects.filter(initiative=initiative)
        )

        for phase_data in addition["phases"]:
            phase = _create_phase(
                phase_data,
                initiative,
                user,
                next_phase_position,
            )
            next_phase_position += 1

            next_step_position = 1

            for step_data in phase_data["steps"]:
                _create_step(
                    step_data,
                    phase,
                    user,
                    next_step_position,
                )
                next_step_position += 1

    for addition in normalized["add_steps"]:
        phase_key = (
            addition["initiative_title"],
            addition["phase_title"],
        )
        phase = phases[phase_key]
        next_step_position = _next_position(
            Step.objects.filter(phase=phase)
        )

        for step_data in addition["steps"]:
            _create_step(
                step_data,
                phase,
                user,
                next_step_position,
            )
            next_step_position += 1


def _create_initiative(
    data: dict[str, Any],
    project: Project,
    user: User,
    position: int,
) -> Initiative:
    initiative = Initiative(
        project=project,
        title=data["title"],
        description=data["description"],
        status=data["status"],
        position=position,
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
    position: int,
) -> Phase:
    phase = Phase(
        initiative=initiative,
        title=data["title"],
        description=data["description"],
        status=data["status"],
        position=position,
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
    position: int,
) -> Step:
    step = Step(
        phase=phase,
        title=data["title"],
        description=data["description"],
        status=data["status"],
        position=position,
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

    _create_step_document(step, data["document"])
    _create_step_validation(step, data["validation"])
    _create_step_files(
        step,
        data["planned_files"],
        StepFile.Role.PLANNED,
        user,
    )
    _create_step_files(
        step,
        data["actual_files"],
        StepFile.Role.ACTUAL,
        user,
    )

    return step


def _create_step_document(
    step: Step,
    data: dict[str, str],
) -> None:
    if not any(data.values()):
        return

    document = StepDocument(
        step=step,
        **data,
    )
    document.full_clean()
    document.save()


def _create_step_validation(
    step: Step,
    data: dict[str, str],
) -> None:
    if not any(data.values()):
        return

    validation = StepValidation(
        step=step,
        description=data["description"],
        notes=data["notes"],
    )
    validation.full_clean()
    validation.save()


def _create_step_files(
    step: Step,
    files: list[dict[str, str]],
    role: str,
    user: User,
) -> None:
    for file_data in files:
        step_file = StepFile(
            step=step,
            file_path=file_data["file_path"],
            role=role,
            reason=file_data["reason"],
            recorded_by=user,
        )
        step_file.full_clean()
        step_file.save()


def _next_position(queryset: Any) -> int:
    highest_position = queryset.aggregate(
        highest=Max("position")
    )["highest"]

    return (highest_position or 0) + 1


def _count_records(
    normalized: dict[str, Any],
) -> dict[str, int]:
    projects = normalized["add_projects"]
    initiatives = normalized["add_initiatives"]

    initiative_phases = [
        phase
        for initiative in initiatives
        for phase in initiative["phases"]
    ]
    appended_phases = [
        phase
        for addition in normalized["add_phases"]
        for phase in addition["phases"]
    ]
    phases = initiative_phases + appended_phases

    nested_steps = [
        step
        for phase in phases
        for step in phase["steps"]
    ]
    appended_steps = [
        step
        for addition in normalized["add_steps"]
        for step in addition["steps"]
    ]

    return {
        "projects": len(projects),
        "initiatives": len(initiatives),
        "phases": len(phases),
        "steps": len(nested_steps) + len(appended_steps),
    }
# ======================================================================
# END: PLANNING_DOCUMENT_UPDATER
# ======================================================================
