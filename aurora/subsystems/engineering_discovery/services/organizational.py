# ======================================================================
# FILE: aurora/subsystems/engineering_discovery/services/organizational.py
# START: ENGINEERING_FINDING_ORGANIZATIONAL_READER
# ======================================================================

from aurora.access import can_access_aurora
from aurora.subsystems.engineering_discovery.models import (
    EngineeringFinding,
    EngineeringFindingResolutionState,
)


class EngineeringFindingOrganizationReadError(ValueError):
    """Raised when organization-wide Engineering Findings cannot be read safely."""


def get_unresolved_findings_for_organization(user) -> list[dict[str, object]]:
    """Return every unresolved Engineering Finding across Aurora."""

    if not can_access_aurora(user):
        raise EngineeringFindingOrganizationReadError(
            "Aurora developer access is required to read organizational Engineering Findings."
        )

    findings = (
        EngineeringFinding.objects
        .filter(resolution_state=EngineeringFindingResolutionState.UNRESOLVED)
        .select_related(
            "originating_step__phase__initiative__project",
            "discovered_by",
            "remedial_phase",
        )
        .order_by("-created_at", "pk")
    )

    result = []

    for finding in findings:
        step = finding.originating_step

        if step is None:
            project = initiative = phase = originating_step = None
        else:
            phase_record = step.phase
            initiative_record = phase_record.initiative
            project_record = initiative_record.project
            project = {
                "id": project_record.pk,
                "slug": project_record.slug,
                "title": project_record.title,
            }
            initiative = {
                "id": initiative_record.pk,
                "title": initiative_record.title,
            }
            phase = {
                "id": phase_record.pk,
                "title": phase_record.title,
            }
            originating_step = {
                "id": step.pk,
                "title": step.title,
            }

        result.append({
            "finding_id": finding.pk,
            "category": finding.category,
            "blocking_classification": finding.blocking_classification,
            "resolution_state": finding.resolution_state,
            "observed_condition": finding.observed_condition,
            "evidence": finding.evidence,
            "steps_to_reproduce": finding.steps_to_reproduce,
            "discovered_by": finding.discovered_by.username,
            "created_at": finding.created_at.isoformat(),
            "project": project,
            "initiative": initiative,
            "phase": phase,
            "originating_step": originating_step,
            "remedial_phase": (
                {
                    "id": finding.remedial_phase_id,
                    "title": finding.remedial_phase.title,
                }
                if finding.remedial_phase_id is not None
                else None
            ),
        })

    return result


# ======================================================================
# END: ENGINEERING_FINDING_ORGANIZATIONAL_READER
# ======================================================================
