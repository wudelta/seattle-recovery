# ======================================================================
# FILE: aurora/api/blueprint.py (PATCH 1 OF 1)
# START: MASTER_BLUEPRINT_ROUTING_DISPATCHER
# ======================================================================
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from aurora.utils.page_skeleton import PageSkeletonBuilder
from aurora.api.handlers.page import PageCommandHandler
from aurora.api.handlers.api import ApiCommandHandler
from aurora.api.handlers.destroy import DestroyCommandHandler

# Structural Command Pattern Mapping Matrix
COMMAND_MAP = {
    "/page": PageCommandHandler(),
    "/api": ApiCommandHandler(),
    "/destroy": DestroyCommandHandler(),
}

@csrf_exempt
def execute_blueprint_api(request):
    """
    Centralized automation routing gateway. Parses incoming blueprint directives 
    and hands them off to dedicated sub-command execution handlers.
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        raw_cmd = request.POST.get("blueprint", "").strip()
        if not raw_cmd:
            try:
                data = json.loads(request.body.decode('utf-8'))
                raw_cmd = data.get("blueprint", "").strip()
            except Exception:
                pass

        if not raw_cmd:
            return JsonResponse({
                "status": "success",
                "minion_log": "System standing ready...",
                "generated_code": "",
                "validation": {"valid": True, "errors": [], "warnings": []}
            })

        PageSkeletonBuilder.emit_log(f"[COMMAND] Intercepted automation route directive: '{raw_cmd}'\n")

        # Command Tokenization Pass
        parts = raw_cmd.split()
        trigger = parts[0].lower() if parts else ""

        # Check if the instruction looks like a slash command
        if trigger.startswith("/"):
            if trigger in COMMAND_MAP:
                # Delegate directly to the clean modular command object handler
                return COMMAND_MAP[trigger].execute(request, parts, raw_cmd)
            else:
                # FIX: Explicitly intercept unknown slash commands to fulfill validation constraints
                error_log = "Unknown automation instruction syntax path entered."
                PageSkeletonBuilder.emit_log(f"[FAIL] {error_log}\n")
                return JsonResponse({
                    "status": "success",
                    "minion_log": "Unknown automation instruction",
                    "generated_code": "",
                    "telemetry_stream": PageSkeletonBuilder.flush_telemetry(),
                    "validation": {"valid": False, "errors": [error_log], "warnings": []}
                })

        # TIER 2: AI INTELLECTUAL ORCHESTRATION GATEWAY (Plain English Fallback Mode)
        PageSkeletonBuilder.emit_log("[INFO] Routing command string to conversational pipeline processing layer...\n")
        return JsonResponse({
            "status": "success",
            "minion_log": "Wu engine is ready. Cloud gateway waiting for plain English commands.",
            "generated_code": "# Wu Active\n",
            "telemetry_stream": PageSkeletonBuilder.flush_telemetry(),
            "validation": {"valid": True, "errors": [], "warnings": []}
        })

    except Exception as e:
        error_msg = f"Forge process view fault: {str(e)}"
        PageSkeletonBuilder.emit_log(f"[FAIL] Core architectural router exception intercepted: {error_msg}\n")
        return JsonResponse({
            "status": "success",
            "minion_log": error_msg,
            "generated_code": "",
            "telemetry_stream": PageSkeletonBuilder.flush_telemetry(),
            "validation": {"valid": False, "errors": [str(e)], "warnings": []}
        })
# ======================================================================
# END: MASTER_BLUEPRINT_ROUTING_DISPATCHER (PATCH 1 OF 1)
# ======================================================================
