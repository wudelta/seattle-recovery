# ======================================================================
# FILE: aurora/subsystems/engineering_discovery/services/remediation.py
# START: ENGINEERING_FINDING_REMEDIATION_ROUTING
# ======================================================================

from typing import Any

from django.db import transaction

from aurora.subsystems.engineering_discovery.models import (
    EngineeringFinding,
    EngineeringFindingBlockingClassification,
    EngineeringFindingResolutionState,
)
from aurora.subsystems.planning.services.remediation import (
    PlanningRemediationError,
    PlanningRemediationResult,
    start_remedial_phase,
)


class EngineeringFindingRemediationError(RuntimeError):
    """Raised when one BLOCKING finding cannot be routed into remedial work."""


def route_blocking_finding(
    user,
    *,
    finding: EngineeringFinding,
    remedial_phase: dict[str, Any],
) -> PlanningRemediationResult:
    """
    Route one unresolved BLOCKING finding into Planning-owned remedial work.

    Engineering Discovery validates finding semantics and provenance.
    Planning owns creation and lifecycle activation of the remedial hierarchy.
    """

    if not user or not getattr(user, "is_authenticated", False):
        raise EngineeringFindingRemediationError(
            "An authenticated user is required to route a BLOCKING finding."
        )

    if finding is None or not getattr(finding, "pk", None):
        raise EngineeringFindingRemediationError(
            "A persisted Engineering Finding is required."
        )

    try:
        with transaction.atomic():
            current = (
                EngineeringFinding.objects
                .select_for_update()
                .select_related(
                    "originating_step",
                )
                .get(pk=finding.pk)
            )

            if current.discovered_by_id != user.pk:
                raise EngineeringFindingRemediationError(
                    "The finding was not submitted by this user."
                )

            if (
                current.blocking_classification
                != EngineeringFindingBlockingClassification.BLOCKING
            ):
                raise EngineeringFindingRemediationError(
                    "Only a BLOCKING finding may interrupt current Planning work."
                )

            if (
                current.resolution_state
                != EngineeringFindingResolutionState.UNRESOLVED
            ):
                raise EngineeringFindingRemediationError(
                    "Resolved findings do not require remedial Planning work."
                )

            if current.remedial_phase_id is not None:
                raise EngineeringFindingRemediationError(
                    "This finding already has a remedial Planning Phase."
                )

            result = start_remedial_phase(
                user,
                blocked_step=current.originating_step,
                remedial_phase=remedial_phase,
            )

            current.remedial_phase_id = result.remedial_phase_id
            current.save(
                update_fields=[
                    "remedial_phase",
                    "updated_at",
                ]
            )

            return result

    except EngineeringFindingRemediationError:
        raise
    except PlanningRemediationError as exc:
        raise EngineeringFindingRemediationError(
            str(exc)
        ) from exc


# ======================================================================
# END: ENGINEERING_FINDING_REMEDIATION_ROUTING
# ======================================================================
