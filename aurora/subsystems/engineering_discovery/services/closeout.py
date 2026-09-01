# ======================================================================
# FILE: aurora/subsystems/engineering_discovery/services/closeout.py
# START: ENGINEERING_FINDING_CLOSEOUT_VIEW
# ======================================================================

from aurora.subsystems.engineering_discovery.models import (
    EngineeringFinding,
    EngineeringFindingResolutionState,
)
from aurora.subsystems.planning.models import Initiative


class EngineeringFindingCloseoutError(ValueError):
    """Raised when a bounded Engineering Finding closeout view cannot be resolved."""


def get_unresolved_findings_for_initiative(
    user,
    *,
    initiative: Initiative,
) -> list[dict[str, object]]:
    """
    Return unresolved Engineering Findings originating from one Initiative.

    The Initiative is the closeout scope. Finding provenance remains anchored to
    each originating Step and is derived through the persisted Planning
    hierarchy. This operation is read-only and does not perform reconciliation
    or choose future engineering work.
    """

    if not user or not getattr(user, "is_authenticated", False):
        raise EngineeringFindingCloseoutError(
            "An authenticated user is required to read Engineering Findings."
        )

    if initiative is None or not getattr(initiative, "pk", None):
        raise EngineeringFindingCloseoutError(
            "A persisted Planning Initiative is required."
        )

    current_initiative = (
        Initiative.objects
        .select_related("project", "assigned_to")
        .filter(pk=initiative.pk)
        .first()
    )
    if current_initiative is None:
        raise EngineeringFindingCloseoutError(
            "The requested Planning Initiative does not exist."
        )

    if current_initiative.assigned_to_id != user.pk:
        raise EngineeringFindingCloseoutError(
            "The requested Planning Initiative is not assigned to this user."
        )

    findings = (
        EngineeringFinding.objects
        .filter(
            originating_step__phase__initiative=current_initiative,
            resolution_state=EngineeringFindingResolutionState.UNRESOLVED,
        )
        .select_related(
            "originating_step__phase__initiative__project",
            "discovered_by",
            "remedial_phase",
        )
        .order_by(
            "originating_step__phase__position",
            "originating_step__position",
            "created_at",
            "pk",
        )
    )

    return [
        {
            "finding_id": finding.pk,
            "category": finding.category,
            "blocking_classification": finding.blocking_classification,
            "resolution_state": finding.resolution_state,
            "observed_condition": finding.observed_condition,
            "evidence": finding.evidence,
            "steps_to_reproduce": finding.steps_to_reproduce,
            "discovered_by": finding.discovered_by.username,
            "created_at": finding.created_at.isoformat(),
            "project": {
                "id": current_initiative.project_id,
                "slug": current_initiative.project.slug,
                "title": current_initiative.project.title,
            },
            "initiative": {
                "id": current_initiative.pk,
                "title": current_initiative.title,
            },
            "phase": {
                "id": finding.originating_step.phase_id,
                "title": finding.originating_step.phase.title,
            },
            "originating_step": {
                "id": finding.originating_step_id,
                "title": finding.originating_step.title,
            },
            "remedial_phase": (
                {
                    "id": finding.remedial_phase_id,
                    "title": finding.remedial_phase.title,
                }
                if finding.remedial_phase_id is not None
                else None
            ),
        }
        for finding in findings
    ]


# ======================================================================
# END: ENGINEERING_FINDING_CLOSEOUT_VIEW
# ======================================================================
