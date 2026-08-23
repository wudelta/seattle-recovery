# ======================================================================
# FILE: aurora/subsystems/planning/services/generation_preflight.py
# START: PLANNING_GENERATION_PREFLIGHT
# ======================================================================

from dataclasses import dataclass

from aurora.models import ExecutionStatus, Initiative


class PlanningGenerationPreflightError(RuntimeError):
    """Raised when lifecycle state is unsafe for Planning generation."""


@dataclass(frozen=True)
class PlanningGenerationPreflight:
    """Authoritative lifecycle context established before AI generation."""

    project_slug: str
    active_initiative_id: int | None
    active_initiative_title: str | None

    @property
    def has_active_initiative(self) -> bool:
        return self.active_initiative_id is not None

    def as_evidence(self) -> dict:
        """Return compact lifecycle evidence for the Planning Generator."""

        return {
            "project_slug": self.project_slug,
            "has_active_initiative": self.has_active_initiative,
            "active_initiative_id": self.active_initiative_id,
            "active_initiative_title": self.active_initiative_title,
        }


def preflight_planning_generation(
    *,
    project_slug: str,
    user,
) -> PlanningGenerationPreflight:
    """
    Establish Initiative lifecycle state before AI generation.

    One ACTIVE Initiative is valid existing context. Multiple ACTIVE
    Initiatives for the same user and Project are ambiguous and must be
    resolved through Planning lifecycle authority before generation.
    """

    slug = project_slug.strip()

    if not slug:
        raise PlanningGenerationPreflightError(
            "Target Project slug is required."
        )

    if user is None or not user.pk:
        raise PlanningGenerationPreflightError(
            "A persisted user is required."
        )

    active_initiatives = list(
        Initiative.objects
        .filter(
            project__slug=slug,
            assigned_to=user,
            status=ExecutionStatus.ACTIVE,
        )
        .order_by(
            "position",
            "pk",
        )[:2]
    )

    if len(active_initiatives) > 1:
        titles = ", ".join(
            initiative.title
            for initiative in active_initiatives
        )

        raise PlanningGenerationPreflightError(
            "Planning generation cannot continue because multiple ACTIVE "
            "Initiatives are assigned to this user in the target Project: "
            f"{titles}."
        )

    if not active_initiatives:
        return PlanningGenerationPreflight(
            project_slug=slug,
            active_initiative_id=None,
            active_initiative_title=None,
        )

    active = active_initiatives[0]

    return PlanningGenerationPreflight(
        project_slug=slug,
        active_initiative_id=active.pk,
        active_initiative_title=active.title,
    )


# ======================================================================
# END: PLANNING_GENERATION_PREFLIGHT
# ======================================================================