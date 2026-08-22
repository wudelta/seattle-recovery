# ======================================================================
# FILE: aurora/subsystems/wu_chat/api/chat.py
# START: WU_CHAT_REQUEST_ENDPOINT
# ======================================================================

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from aurora.subsystems.wu_chat.services.orchestration import (
    process_wu_logic_synchronous,
)
from aurora.subsystems.wu_chat.services.traffic_safety import (
    enforce_context_token_budget,
)


@login_required
def wu_chat_endpoint(request):
    """
    Process Wu requests and return chat, review, and execution telemetry.
    """
    from aurora.models import ChatLedgerEntry

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        delta_notes = data.get("delta_notes", "").strip()
        session_id = data.get(
            "session_id",
            "default_cockpit_thread",
        )

        if not delta_notes:
            return JsonResponse(
                {"error": "Empty delta notes provided"},
                status=400,
            )

        try:
            sanitized_notes = enforce_context_token_budget(
                delta_notes
            )
        except ValueError as rate_err:
            return JsonResponse(
                {
                    "error": (
                        "🛡️ [GATEWAY SHIELD]: "
                        f"{str(rate_err)}"
                    )
                },
                status=429,
            )

        ChatLedgerEntry.objects.create(
            user=request.user,
            session_id=session_id,
            role="user",
            text=sanitized_notes,
        )

        result = process_wu_logic_synchronous(
            sanitized_notes,
            request.user,
            session_id=session_id,
        )

        if result["status"] == "ERROR":
            return JsonResponse(
                {
                    "error": result["message"],
                    "traceback": result["trace"],
                },
                status=500,
            )

        model_reply = result.get(
            "wu_response",
            "",
        ).strip()

        if model_reply:
            ChatLedgerEntry.objects.create(
                user=request.user,
                session_id=session_id,
                role="model",
                text=model_reply,
            )

        return JsonResponse(
            {
                "status": "wu_is_processing",
                "direct_text_output": result["wu_response"],
                "patch": result.get("patch"),
                "patch_error": result.get("patch_error"),
                "telemetry": result.get("telemetry", {}),
                "fuel_gauge": result.get(
                    "fuel_gauge",
                    {},
                ),
            }
        )

    except Exception as err:
        return JsonResponse(
            {"error": str(err)},
            status=400,
        )

# ======================================================================
# END: WU_CHAT_REQUEST_ENDPOINT
# ======================================================================
