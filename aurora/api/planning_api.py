# ======================================================================
# FILE: aurora/api/planning_api.py (PATCH 1 OF 1)
# START: PLANNING_API
# ======================================================================
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from aurora.models import Initiative, Phase, Step


def serialize_user(user):
    """Returns a compact identity payload for planning ownership fields."""
    if user is None:
        return None

    full_name = user.get_full_name().strip()

    return {
        "id": str(user.pk),
        "username": user.get_username(),
        "display_name": full_name or user.get_username(),
    }


def serialize_step(step):
    """Serializes one implementation step for the planning workspace."""
    return {
        "id": step.pk,
        "title": step.title,
        "description": step.description,
        "status": step.status,
        "status_label": step.get_status_display(),
        "position": step.position,
        "estimated_minutes": step.estimated_minutes,
        "estimate_confidence": step.estimate_confidence,
        "estimate_confidence_label": (
            step.get_estimate_confidence_display()
            if step.estimate_confidence
            else None
        ),
        "validation_description": step.validation_description,
        "validated_by": serialize_user(step.validated_by),
        "validation_notes": step.validation_notes,
        "created_at": step.created_at.isoformat(),
        "updated_at": step.updated_at.isoformat(),
        "completed_at": (
            step.completed_at.isoformat()
            if step.completed_at
            else None
        ),
    }


def serialize_phase(phase):
    """Serializes one ordered phase and its implementation steps."""
    steps = list(phase.steps.all())

    return {
        "id": phase.pk,
        "title": phase.title,
        "description": phase.description,
        "status": phase.status,
        "status_label": phase.get_status_display(),
        "position": phase.position,
        "step_count": len(steps),
        "steps": [
            serialize_step(step)
            for step in steps
        ],
        "created_at": phase.created_at.isoformat(),
        "updated_at": phase.updated_at.isoformat(),
        "completed_at": (
            phase.completed_at.isoformat()
            if phase.completed_at
            else None
        ),
    }


def serialize_initiative(initiative):
    """Serializes one initiative and its complete planning hierarchy."""
    phases = list(initiative.phases.all())

    return {
        "id": initiative.pk,
        "title": initiative.title,
        "description": initiative.description,
        "status": initiative.status,
        "status_label": initiative.get_status_display(),
        "position": initiative.position,
        "created_by": serialize_user(initiative.created_by),
        "phase_count": len(phases),
        "phases": [
            serialize_phase(phase)
            for phase in phases
        ],
        "created_at": initiative.created_at.isoformat(),
        "updated_at": initiative.updated_at.isoformat(),
        "completed_at": (
            initiative.completed_at.isoformat()
            if initiative.completed_at
            else None
        ),
    }


@login_required
@require_GET
def planning_endpoint(request):
    """Returns the persisted Initiative → Phase → Step hierarchy."""
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

    initiatives = (
        Initiative.objects
        .select_related("created_by")
        .order_by("position", "created_at")
        .prefetch_related(
            Prefetch(
                "phases",
                queryset=phase_queryset,
            )
        )
    )

    initiative_payload = [
        serialize_initiative(initiative)
        for initiative in initiatives
    ]

    phase_count = sum(
        initiative["phase_count"]
        for initiative in initiative_payload
    )

    step_count = sum(
        phase["step_count"]
        for initiative in initiative_payload
        for phase in initiative["phases"]
    )

    return JsonResponse({
        "status": "success",
        "summary": {
            "initiative_count": len(initiative_payload),
            "phase_count": phase_count,
            "step_count": step_count,
        },
        "initiatives": initiative_payload,
    })
# ======================================================================
# END: PLANNING_API (PATCH 1 OF 1)
# ======================================================================