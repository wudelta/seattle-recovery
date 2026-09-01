# ======================================================================
# FILE: aurora/subsystems/engineering_discovery/services/planning.py
# START: ENGINEERING_FINDING_PLANNING_INTEGRATION
# ======================================================================

from pprint import pformat

from aurora.subsystems.engineering_discovery.models import (
    EngineeringFinding,
    EngineeringFindingResolutionState,
)
from aurora.subsystems.planning.services.generation import (
    PlanningGenerationResult,
    generate_planning_update,
)


class EngineeringFindingPlanningError(ValueError):
    """Raised when selected findings cannot support Planning generation."""


def generate_planning_update_from_findings(
    user,
    *,
    finding_ids: list[int],
    engineering_intent: str,
    project_slug: str,
) -> PlanningGenerationResult:
    """
    Generate one dry-run Planning proposal from human-selected finding evidence.

    Finding selection is explicit. Engineering Discovery supplies persisted
    evidence; the caller supplies the human engineering intent. Planning remains
    responsible for proposal generation, lifecycle preflight, schema validation,
    and the non-applied Planning result.

    Originating Planning hierarchy is provenance only. Deferred cleanup work
    must not silently target an Initiative from which a selected finding
    originated.
    """

    if not user or not getattr(user, "is_authenticated", False):
        raise EngineeringFindingPlanningError(
            "An authenticated user is required."
        )

    intent = engineering_intent.strip()
    slug = project_slug.strip()

    if not intent:
        raise EngineeringFindingPlanningError(
            "Human engineering intent is required."
        )

    if not slug:
        raise EngineeringFindingPlanningError(
            "Target Project slug is required."
        )

    selected_ids = list(dict.fromkeys(finding_ids))

    if not selected_ids:
        raise EngineeringFindingPlanningError(
            "At least one human-selected Engineering Finding is required."
        )

    findings = list(
        EngineeringFinding.objects
        .filter(pk__in=selected_ids)
        .select_related(
            "originating_step__phase__initiative__project",
            "discovered_by",
        )
    )

    found_ids = {finding.pk for finding in findings}
    missing_ids = [
        finding_id
        for finding_id in selected_ids
        if finding_id not in found_ids
    ]
    if missing_ids:
        raise EngineeringFindingPlanningError(
            "Selected Engineering Finding(s) do not exist: "
            + ", ".join(str(finding_id) for finding_id in missing_ids)
        )

    for finding in findings:
        project = finding.originating_step.phase.initiative.project

        if project.slug != slug:
            raise EngineeringFindingPlanningError(
                f"Engineering Finding {finding.pk} belongs to Project "
                f'"{project.slug}", not "{slug}".'
            )

        if finding.resolution_state != EngineeringFindingResolutionState.UNRESOLVED:
            raise EngineeringFindingPlanningError(
                f"Engineering Finding {finding.pk} is already resolved."
            )

    findings_by_id = {
        finding.pk: finding
        for finding in findings
    }

    ordered_findings = [
        findings_by_id[finding_id]
        for finding_id in selected_ids
    ]
    evidence = [
        _serialize_selected_finding(finding)
        for finding in ordered_findings
    ]
    originating_initiative_titles = {
        finding.originating_step.phase.initiative.title
        for finding in ordered_findings
    }

    result = generate_planning_update(
        engineering_intent=intent,
        project_slug=slug,
        user=user,
        supporting_evidence=(
            "Human-selected unresolved Engineering Findings:\n"
            + pformat(
                evidence,
                sort_dicts=False,
                width=100,
            )
            + "\n\n"
            "BOUNDARY CONSTRAINT:\n"
            "The originating Planning hierarchy recorded above is provenance "
            "only. It identifies where each problem was encountered; it is not "
            "authorization to append cleanup work to that Initiative or Phase. "
            "Deferred cleanup work must not target any originating Initiative "
            "represented by the selected findings. The human engineering intent "
            "remains the objective-selection authority."
        ),
    )

    _validate_cleanup_destination_separation(
        result.document,
        originating_initiative_titles=originating_initiative_titles,
    )

    return result


def _validate_cleanup_destination_separation(
    document: dict[str, object],
    *,
    originating_initiative_titles: set[str],
) -> None:
    """
    Reject generated cleanup work that reuses finding provenance as ownership.

    New Initiatives are permitted. Additions to existing Initiatives are
    rejected when their target title matches an Initiative from which any
    selected finding originated.
    """

    targeted_existing_initiatives: set[str] = set()

    for phase_group in document.get("add_phases", []):
        if not isinstance(phase_group, dict):
            continue

        initiative_title = phase_group.get("initiative_title")
        if isinstance(initiative_title, str):
            targeted_existing_initiatives.add(initiative_title)

    for step_group in document.get("add_steps", []):
        if not isinstance(step_group, dict):
            continue

        initiative_title = step_group.get("initiative_title")
        if isinstance(initiative_title, str):
            targeted_existing_initiatives.add(initiative_title)

    invalid_targets = sorted(
        targeted_existing_initiatives
        & originating_initiative_titles
    )

    if invalid_targets:
        raise EngineeringFindingPlanningError(
            "Generated cleanup Planning proposal targets originating "
            "Initiative provenance instead of separate future work: "
            + ", ".join(invalid_targets)
        )


def _serialize_selected_finding(
    finding: EngineeringFinding,
) -> dict[str, object]:
    """Return bounded persisted evidence for one selected finding."""

    step = finding.originating_step
    phase = step.phase
    initiative = phase.initiative

    return {
        "finding_id": finding.pk,
        "category": finding.category,
        "blocking_classification": finding.blocking_classification,
        "resolution_state": finding.resolution_state,
        "observed_condition": finding.observed_condition,
        "evidence": finding.evidence,
        "steps_to_reproduce": finding.steps_to_reproduce,
        "originating_planning": {
            "initiative_id": initiative.pk,
            "initiative_title": initiative.title,
            "phase_id": phase.pk,
            "phase_title": phase.title,
            "step_id": step.pk,
            "step_title": step.title,
        },
    }


# ======================================================================
# END: ENGINEERING_FINDING_PLANNING_INTEGRATION
# ======================================================================
