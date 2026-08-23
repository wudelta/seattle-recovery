# ======================================================================
# FILE: aurora/subsystems/hansel/services/reconciliation.py
# START: HANSEL_TRAIL_RECONCILIATION
# ======================================================================

from dataclasses import dataclass

from aurora.models import (
    HanselTrail,
    HanselTrailOutcome,
)


@dataclass(frozen=True)
class HanselReconciliationCandidate:
    """One repository authority observed during a Hansel trail."""

    authority_path: str


@dataclass(frozen=True)
class HanselTrailReconciliation:
    """Deterministic reconciliation evidence for one completed trail."""

    trail_id: int
    step_id: int
    step_title: str
    outcome: str
    reconciliation_required: bool
    reason: str
    candidates: tuple[HanselReconciliationCandidate, ...]


def build_hansel_trail_reconciliation(
    trail: HanselTrail,
) -> HanselTrailReconciliation:
    """
    Classify one completed Hansel trail for catalogue reconciliation.

    This function surfaces evidence only. It never edits a Hansel contract
    because runtime trail evidence cannot establish that an observed authority
    is a durable route suitable for future workers.
    """

    if (
        trail.outcome == HanselTrailOutcome.IN_PROGRESS
        or trail.ended_at is None
    ):
        raise ValueError(
            "Hansel reconciliation requires a completed trail."
        )

    candidates = tuple(
        HanselReconciliationCandidate(
            authority_path=authority_path,
        )
        for authority_path in trail.authorities.values_list(
            "authority_path",
            flat=True,
        )
    )

    required, reason = _classify_reconciliation(
        trail.outcome
    )

    return HanselTrailReconciliation(
        trail_id=trail.pk,
        step_id=trail.step_id,
        step_title=trail.step.title,
        outcome=trail.outcome,
        reconciliation_required=required,
        reason=reason,
        candidates=candidates,
    )


def _classify_reconciliation(
    outcome: str,
) -> tuple[bool, str]:
    """Return deterministic reconciliation classification and rationale."""

    if outcome == HanselTrailOutcome.SUFFICIENT:
        return (
            False,
            (
                "Hansel reached sufficient authority without an observed "
                "routing failure."
            ),
        )

    if outcome == HanselTrailOutcome.BROKEN:
        return (
            True,
            (
                "A Hansel breadcrumb failed and the affected catalogue "
                "requires reconciliation."
            ),
        )

    if outcome == HanselTrailOutcome.REDISCOVERED:
        return (
            True,
            (
                "Repository authority required rediscovery outside the "
                "existing Hansel route."
            ),
        )

    if outcome == HanselTrailOutcome.INCOMPLETE:
        return (
            True,
            (
                "Hansel did not reach sufficient authority; the trail "
                "requires review before the catalogue can be considered "
                "complete for this task."
            ),
        )

    raise ValueError(
        f"Unsupported Hansel trail outcome: {outcome}."
    )


# ======================================================================
# END: HANSEL_TRAIL_RECONCILIATION
# ======================================================================