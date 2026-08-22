# ======================================================================
# FILE: aurora/subsystems/engineering_session/api/completion_actions.py
# START: ENGINEERING_SESSION_COMPLETION_REVIEW_ACTIONS
# ======================================================================

from django.http import JsonResponse

from aurora.models import Initiative, Phase
from aurora.subsystems.engineering_session.api.common import (
    require_active_session,
)
from aurora.subsystems.engineering_session.services import (
    get_session_workflow_status,
)
from aurora.subsystems.planning.services import (
    approve_initiative_completion,
    approve_phase_completion,
    reject_initiative_completion,
    reject_phase_completion,
    request_initiative_completion,
)


COMPLETION_ACTIONS = {
    "approve_phase_completion",
    "reject_phase_completion",
    "approve_initiative_completion",
    "reject_initiative_completion",
}


def handle_completion_action(request, action):
    """Handle Phase and Initiative completion review decisions."""

    require_active_session(
        request.user
    )

    if action == "approve_phase_completion":
        phase = (
            Phase.objects
            .select_related("initiative")
            .get(
                pk=request.POST.get("phase_id")
            )
        )

        decision = approve_phase_completion(
            phase
        )

        initiative_completion = request_initiative_completion(
            phase.initiative,
            auto=False,
        )

        return JsonResponse(
            {
                "status": "success",
                "action": action,
                "decision": decision,
                "initiative_completion": initiative_completion,
                "workflow": get_session_workflow_status(
                    request.user
                ),
            }
        )

    if action == "reject_phase_completion":
        phase = Phase.objects.get(
            pk=request.POST.get("phase_id")
        )

        decision = reject_phase_completion(
            phase,
            reason=request.POST.get(
                "reason",
                "",
            ),
        )

        return JsonResponse(
            {
                "status": "success",
                "action": action,
                "decision": decision,
                "workflow": get_session_workflow_status(
                    request.user
                ),
            }
        )

    if action == "approve_initiative_completion":
        initiative = Initiative.objects.get(
            pk=request.POST.get("initiative_id")
        )

        decision = approve_initiative_completion(
            initiative
        )

        return JsonResponse(
            {
                "status": "success",
                "action": action,
                "decision": decision,
                "workflow": get_session_workflow_status(
                    request.user
                ),
            }
        )

    initiative = Initiative.objects.get(
        pk=request.POST.get("initiative_id")
    )

    decision = reject_initiative_completion(
        initiative,
        reason=request.POST.get(
            "reason",
            "",
        ),
    )

    return JsonResponse(
        {
            "status": "success",
            "action": action,
            "decision": decision,
            "workflow": get_session_workflow_status(
                request.user
            ),
        }
    )


# ======================================================================
# END: ENGINEERING_SESSION_COMPLETION_REVIEW_ACTIONS
# ======================================================================
