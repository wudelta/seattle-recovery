# ======================================================================
# FILE: aurora/subsystems/engineering_discovery/services/findings.py
# START: ENGINEERING_FINDING_SUBMISSION_SERVICE
# ======================================================================

from django.db import transaction
from django.utils import timezone

from aurora.subsystems.engineering_discovery.models import (
    EngineeringFinding,
    EngineeringFindingBlockingClassification,
    EngineeringFindingCategory,
    EngineeringFindingResolutionState,
)
from aurora.subsystems.planning.services.time_tracking import (
    PlanningTimeTrackingError,
    get_executable_step,
)


class EngineeringFindingSubmissionError(ValueError):
    """Raised when one bounded Engineering Finding cannot be submitted."""


class EngineeringFindingResolutionError(ValueError):
    """Raised when one Engineering Finding cannot be resolved."""


def _normalize_required_text(value, *, field_name: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise EngineeringFindingSubmissionError(
            f"{field_name} is required."
        )
    return normalized


def _normalize_resolution_evidence(value) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise EngineeringFindingResolutionError(
            "resolution_evidence is required."
        )
    return normalized


def _normalize_optional_text(value) -> str:
    return str(value or "").strip()


def _validate_choice(value, *, choices, field_name: str) -> str:
    normalized = str(value or "").strip().upper()
    allowed = {choice for choice, _label in choices}

    if normalized not in allowed:
        raise EngineeringFindingSubmissionError(
            f"Unsupported {field_name}: {value!r}."
        )

    return normalized


def submit_finding(
    user,
    *,
    category,
    blocking_classification,
    observed_condition,
    evidence="",
    steps_to_reproduce="",
) -> EngineeringFinding:
    """
    Persist one finding against the user's lifecycle-authoritative ACTIVE Step.

    Provenance is resolved from Planning. The caller cannot supply Project,
    Initiative, Phase, or Step identifiers.

    At least one of evidence or steps_to_reproduce must be present. Reproduction
    steps may themselves constitute sufficient verification evidence.
    """

    if not user or not getattr(user, "is_authenticated", False):
        raise EngineeringFindingSubmissionError(
            "An authenticated user is required to submit an Engineering Finding."
        )

    normalized_category = _validate_choice(
        category,
        choices=EngineeringFindingCategory.choices,
        field_name="category",
    )
    normalized_blocking = _validate_choice(
        blocking_classification,
        choices=EngineeringFindingBlockingClassification.choices,
        field_name="blocking classification",
    )
    normalized_condition = _normalize_required_text(
        observed_condition,
        field_name="observed_condition",
    )
    normalized_evidence = _normalize_optional_text(evidence)
    normalized_reproduction = _normalize_optional_text(steps_to_reproduce)

    if not normalized_evidence and not normalized_reproduction:
        raise EngineeringFindingSubmissionError(
            "A finding requires evidence, steps_to_reproduce, or both."
        )

    try:
        originating_step = get_executable_step(user)
    except PlanningTimeTrackingError as exc:
        raise EngineeringFindingSubmissionError(
            "Lifecycle-authoritative Planning provenance could not be resolved."
        ) from exc

    with transaction.atomic():
        return EngineeringFinding.objects.create(
            originating_step=originating_step,
            discovered_by=user,
            category=normalized_category,
            blocking_classification=normalized_blocking,
            resolution_state=EngineeringFindingResolutionState.UNRESOLVED,
            observed_condition=normalized_condition,
            evidence=normalized_evidence,
            steps_to_reproduce=normalized_reproduction,
        )


def resolve_finding(
    user,
    *,
    finding: EngineeringFinding,
    resolution_evidence,
) -> EngineeringFinding:
    """
    Resolve one persisted Engineering Finding with deterministic evidence.

    Resolution preserves the finding's original Planning provenance and
    discovery evidence. It changes only the durable resolution lifecycle
    fields owned by Engineering Discovery.
    """

    if not user or not getattr(user, "is_authenticated", False):
        raise EngineeringFindingResolutionError(
            "An authenticated user is required to resolve an Engineering Finding."
        )

    if finding is None or not getattr(finding, "pk", None):
        raise EngineeringFindingResolutionError(
            "A persisted Engineering Finding is required."
        )

    normalized_evidence = _normalize_resolution_evidence(
        resolution_evidence
    )

    with transaction.atomic():
        try:
            current = (
                EngineeringFinding.objects
                .select_for_update()
                .get(pk=finding.pk)
            )
        except EngineeringFinding.DoesNotExist as exc:
            raise EngineeringFindingResolutionError(
                "The Engineering Finding no longer exists."
            ) from exc

        if current.discovered_by_id != user.pk:
            raise EngineeringFindingResolutionError(
                "The finding was not submitted by this user."
            )

        if (
            current.resolution_state
            != EngineeringFindingResolutionState.UNRESOLVED
        ):
            raise EngineeringFindingResolutionError(
                "The Engineering Finding is already resolved."
            )

        current.resolution_state = EngineeringFindingResolutionState.RESOLVED
        current.resolution_evidence = normalized_evidence
        current.resolved_at = timezone.now()
        current.save(
            update_fields=[
                "resolution_state",
                "resolution_evidence",
                "resolved_at",
                "updated_at",
            ]
        )

        return current


# ======================================================================
# END: ENGINEERING_FINDING_SUBMISSION_SERVICE
# ======================================================================
