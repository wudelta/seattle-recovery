# ======================================================================
# FILE: aurora/subsystems/planning/api/payload.py
# START: PLANNING_HIERARCHY_PAYLOAD
# ======================================================================
from django.db.models import Count, Prefetch

from aurora.models import Initiative, Phase, Project, Step
from aurora.subsystems.planning.api.serializers import (
    serialize_initiative,
    serialize_initiative_option,
    serialize_project,
)


def build_planning_payload(
    project_slug=None,
    initiative_id=None,
):
    """Builds the focused planning workspace for one active Project."""
    projects = list(
        Project.objects
        .filter(active=True)
        .annotate(
            initiative_count=Count(
                "initiatives",
                distinct=True,
            ),
            project_phase_count=Count(
                "initiatives__phases",
                distinct=True,
            ),
            project_step_count=Count(
                "initiatives__phases__steps",
                distinct=True,
            ),
        )
        .order_by("position", "title")
    )

    active_project = None

    if project_slug:
        active_project = next(
            (
                project
                for project in projects
                if project.slug == project_slug
            ),
            None,
        )

    if active_project is None and projects:
        active_project = projects[0]

    project_payload = [
        serialize_project(project)
        for project in projects
    ]

    if active_project is None:
        return {
            "status": "success",
            "projects": project_payload,
            "active_project": None,
            "initiative_options": [],
            "active_initiative": None,
            "summary": {
                "initiative_count": 0,
                "phase_count": 0,
                "step_count": 0,
            },
        }

    active_project_payload = serialize_project(
        active_project
    )

    active_project_payload.update(
        {
            "initiative_count": (
                active_project.initiative_count
            ),
            "phase_count": (
                active_project.project_phase_count
            ),
            "step_count": (
                active_project.project_step_count
            ),
            "can_delete": (
                active_project.initiative_count == 0
            ),
        }
    )

    initiative_options = list(
        Initiative.objects
        .filter(project=active_project)
        .select_related("project")
        .order_by("position", "created_at")
    )

    active_initiative = None

    if initiative_id not in (None, ""):
        requested_initiative_id = str(initiative_id)

        active_initiative = next(
            (
                initiative
                for initiative in initiative_options
                if str(initiative.pk) == requested_initiative_id
            ),
            None,
        )

    if active_initiative is None and initiative_options:
        active_initiative = initiative_options[0]

    active_initiative_payload = None

    if active_initiative is not None:
        step_queryset = (
            Step.objects
            .select_related("validated_by")
            .order_by("position", "created_at")
        )

        phase_queryset = (
            Phase.objects
            .order_by("position", "created_at")
            .prefetch_related(
                Prefetch(
                    "steps",
                    queryset=step_queryset,
                )
            )
        )

        active_initiative = (
            Initiative.objects
            .select_related("project", "created_by")
            .prefetch_related(
                Prefetch(
                    "phases",
                    queryset=phase_queryset,
                )
            )
            .get(pk=active_initiative.pk)
        )

        active_initiative_payload = serialize_initiative(
            active_initiative
        )

    phase_count = (
        active_initiative_payload["phase_count"]
        if active_initiative_payload
        else 0
    )

    step_count = sum(
        phase["step_count"]
        for phase in (
            active_initiative_payload["phases"]
            if active_initiative_payload
            else []
        )
    )

    return {
        "status": "success",
        "projects": project_payload,
        "active_project": active_project_payload,
        "initiative_options": [
            serialize_initiative_option(initiative)
            for initiative in initiative_options
        ],
        "active_initiative": active_initiative_payload,
        "summary": {
            "initiative_count": len(initiative_options),
            "phase_count": phase_count,
            "step_count": step_count,
        },
    }
# ======================================================================
# END: PLANNING_HIERARCHY_PAYLOAD
# ======================================================================