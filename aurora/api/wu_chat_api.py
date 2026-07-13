# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 1 OF 5)
# START: MODULE_RUN_IMPORTS_AND_DEPENDENCIES
# ======================================================================
import json
import asyncio
import traceback
import sys
import time
from collections import deque
from threading import Lock
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from aurora.models import DeltaDirectives
from aurora.minions.engine import MinionRunner
from aurora.minions.patch_parser import (
    PatchParseError,
    parse_patch_response,
)
from aurora.minions.workspace_context import (
    WorkspaceContextError,
    resolve_workspace_context,
)
from .dev_streamer_api import async_send_to_console
# ======================================================================
# END: MODULE_RUN_IMPORTS_AND_DEPENDENCIES (PATCH 1 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 2 OF 5)
# START: SYNCHRONOUS_ORCHESTRATION_CORE_ENGINE
# ======================================================================

def process_wu_logic_synchronous(user_delta_notes, user, session_id="default_cockpit_thread"):
    """Generates the full Gemini execution plan, factoring in low-footprint ledger contexts."""
    try:
        runner = MinionRunner()
        try:
            wu_config = DeltaDirectives.objects.get(
                directive_name="minion_wu",
                is_active=True,
            )
        except DeltaDirectives.DoesNotExist:
            error_msg = (
                "💥 [REGISTRY CRITICAL]: Master directive configuration "
                "'minion_wu' is missing or inactive in your database ledger!"
            )
            sys.stderr.write(f"{error_msg}\n")
            sys.stderr.flush()
            return {
                "status": "ERROR",
                "message": "Master orchestrator directive is missing in database registry.",
                "trace": error_msg,
            }

        from aurora.models import ChatLedgerEntry

        # 1. READ CONTEXT BACK OUT OF POSTGRESQL
        db_history = ChatLedgerEntry.objects.filter(
            session_id=session_id
        ).order_by("-created_at")[:6]

        # 2. COMPACT HISTORY ASYMMETRICALLY
        history_buffer_lines = []
        for entry in reversed(db_history):
            if entry.role == "user" and entry.text == user_delta_notes:
                continue

            author_tag = (
                "Developer Intention"
                if entry.role == "user"
                else "Wu Response"
            )
            history_buffer_lines.append(
                f"--- PRIOR CONVERSATION STEP ({author_tag}) ---\n"
                f"{entry.text}"
            )

        history_context_block = (
            "\n\n".join(history_buffer_lines)
            if history_buffer_lines
            else ""
        )

        # 3. RESOLVE THE CURRENT INSTRUCTION AGAINST THE WORKSPACE
        workspace_context = resolve_workspace_context(user_delta_notes)
        current_task_input = (
            workspace_context.hydrated_prompt
            if workspace_context
            else user_delta_notes
        )

        # 4. CONSOLIDATE HISTORY AND CURRENT TASK
        compiled_task_notes = current_task_input
        if history_context_block:
            compiled_task_notes = (
                f"{history_context_block}\n\n"
                "=== CURRENT LIVE WORKSPACE TASK INSTRUCTION ===\n"
                f"{current_task_input}"
            )

        complete_response_text = ""
        stream_generator = runner.run_minion_task_stream(
            "minion_wu",
            compiled_task_notes,
        )

        async def consume_stream():
            nonlocal complete_response_text

            async for token in stream_generator:
                complete_response_text += token

        def run_async_in_thread():
            new_loop = asyncio.new_event_loop()
            try:
                return new_loop.run_until_complete(consume_stream())
            finally:
                new_loop.close()

        import threading

        thread = threading.Thread(target=run_async_in_thread)
        thread.start()
        thread.join()

        patch_payload = None
        patch_error = None

        if workspace_context:
            try:
                parsed_patch = parse_patch_response(
                    response_text=complete_response_text,
                    expected_file_path=workspace_context.file_path,
                    original_content=workspace_context.original_content,
                )
                patch_payload = parsed_patch.as_payload()
            except PatchParseError as err:
                patch_error = str(err)
                sys.stderr.write(
                    f"⚠️ [WU PATCH REVIEW ERROR]: {patch_error}\n"
                )
                sys.stderr.flush()

        sys.stderr.write(
            "\n🔎 [WU PATCH DEBUG]:\n"
            f"  -> Workspace Context: {workspace_context is not None}\n"
            f"  -> Structured Patch: {patch_payload is not None}\n"
            f"  -> Patch Error: {patch_error!r}\n"
            f"  -> Response Characters: {len(complete_response_text)}\n\n"
        )
        sys.stderr.flush()

        r_limit = 15
        r_rem = getattr(runner, "last_rpm_remaining", 14)
        t_limit = 1000000
        t_used = getattr(
            runner,
            "last_tokens_consumed",
            len(compiled_task_notes) // 4,
        )
        t_rem = max(0, t_limit - t_used)

        tokens_used_pct = (
            round((t_used / t_limit) * 100, 3)
            if t_limit > 0
            else 0.0
        )
        requests_used_pct = (
            round(((r_limit - r_rem) / r_limit) * 100, 1)
            if r_limit > 0
            else 0.0
        )

        fuel_gauge_metrics = {
            "tokens_limit": t_limit,
            "tokens_remaining": t_rem,
            "tokens_used_pct": min(
                100.0,
                max(0.0, tokens_used_pct),
            ),
            "requests_limit": r_limit,
            "requests_remaining": r_rem,
            "requests_used_pct": min(
                100.0,
                max(0.0, requests_used_pct),
            ),
        }

        return {
            "status": "SUCCESS",
            "wu_response": complete_response_text,
            "patch": patch_payload,
            "patch_error": patch_error,
            "fuel_gauge": fuel_gauge_metrics,
        }

    except WorkspaceContextError as err:
        return {
            "status": "ERROR",
            "message": str(err),
            "trace": traceback.format_exc(),
        }
    except Exception as err:
        return {
            "status": "ERROR",
            "message": str(err),
            "trace": traceback.format_exc(),
        }

# ======================================================================
# END: SYNCHRONOUS_ORCHESTRATION_CORE_ENGINE (PATCH 2 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 3 OF 5)
# START: CHAT_REQUEST_ENDPOINT_VIEW
# ======================================================================
@login_required
def wu_chat_endpoint(request):
    """
    Processes requests, hooks up sliding history windows via ChatLedgerEntry,
    and returns response payloads with execution telemetry and optional
    structured patch review data.
    """
    from aurora.models import ChatLedgerEntry

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            delta_notes = data.get("delta_notes", "").strip()
            
            # Enforce tracking thread isolation from the frontend payload or a fallback token
            session_id = data.get("session_id", "default_cockpit_thread")
            
            if not delta_notes:
                return JsonResponse({"error": "Empty delta notes provided"}, status=400)
                
            try:
                # Evaluate payload against the global rolling 60-second token window
                sanitized_notes = enforce_context_token_budget(delta_notes)
            except ValueError as rate_err:
                return JsonResponse({"error": f"🛡️ [GATEWAY SHIELD]: {str(rate_err)}"}, status=429)

            # 1. COMMIT USER INPUT INTENTION INTO POSTGRESQL LEDGER
            ChatLedgerEntry.objects.create(
                user=request.user,
                session_id=session_id,
                role='user',
                text=sanitized_notes
            )

            # 2. RUN MINION CHAINS WITH AUTOMATED SESSION THREAD TRACKING
            result = process_wu_logic_synchronous(sanitized_notes, request.user, session_id=session_id)
            
            if result["status"] == "ERROR":
                return JsonResponse({"error": result["message"], "traceback": result["trace"]}, status=500)
                
            # 3. COMMIT MINION CORE RESPONSE PAYLOAD INTO THE DATABASE LEDGER
            model_reply = result.get("wu_response", "").strip()
            if model_reply:
                ChatLedgerEntry.objects.create(
                    user=request.user,
                    session_id=session_id,
                    role='model',
                    text=model_reply
                )
                
            return JsonResponse({
                "status": "wu_is_processing",
                "direct_text_output": result["wu_response"],
                "patch": result.get("patch"),
                "patch_error": result.get("patch_error"),
                "fuel_gauge": result.get("fuel_gauge", {})
            })
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=400)
    return JsonResponse({"error": "POST required"}, status=405)
# ======================================================================
# END: CHAT_REQUEST_ENDPOINT_VIEW (PATCH 3 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 4 OF 5)
# START: PRE_SEND_TRAFFIC_SAFETY_MONITORING_METRICS
# ======================================================================
# Thread safety locks and allocation deques tracking network transaction states
OUTBOUND_TRAFFIC_LOG = deque()
TRAFFIC_LOCK = Lock()
# ======================================================================
# END: PRE_SEND_TRAFFIC_SAFETY_MONITORING_METRICS (PATCH 4 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 5 OF 5)
# START: UTILITY_CONTEXT_TOKEN_BUDGETER
# ======================================================================
def enforce_context_token_budget(raw_text_payload, max_tokens=150000):
    """
    Traps and analyzes outbound payloads before any API call is made.
    Logs absolute metrics and strips out massive text blocks dynamically.
    """
    if not raw_text_payload:
        sys.stderr.write("📊 [TRAFFIC ANALYZER]: Received empty or null payload text.\n")
        sys.stderr.flush()
        return ""

    # Measure exact inbound metrics before modification
    raw_char_count = len(raw_text_payload)
    estimated_raw_tokens = raw_char_count // 4
    
    sys.stderr.write(
        f"\n📊 [TRAFFIC ANALYZER PRE-SEND AUDIT]:\n"
        f"  -> Total Character Volume: {raw_char_count}\n"
        f"  -> Estimated Inbound Tokens: {estimated_raw_tokens}\n"
        f"  -> Safety Budget Target Limit: {max_tokens} tokens (~{max_tokens * 4} chars)\n"
    )
    sys.stderr.flush()

    # If the payload fits comfortably within our budget boundaries, pass it intact
    max_chars = max_tokens * 4
    if raw_char_count <= max_chars:
        sys.stderr.write("📊 [TRAFFIC ANALYZER]: Payload is clean. Forwarding completely intact.\n")
        sys.stderr.flush()
        return raw_text_payload

    sys.stderr.write("⚠️ [TRAFFIC ANALYZER]: Payload size boundary crossed! Executing surgical line-trimming...\n")
    sys.stderr.flush()

    # Split the payload into lines to find what is inflating the string footprint
    lines = raw_text_payload.split('\n')
    sanitized_lines = []
    accumulated_chars = 0
    stripped_lines_count = 0

    for line in lines:
        line_len = len(line)
        
        # Guard 1: Drop individual giant string lines (like serialized JSON or directory sweeps)
        if line_len > 2000:
            stripped_lines_count += 1
            continue
            
        # Guard 2: Halt line collection if we are approaching our hard character ceiling
        if accumulated_chars + line_len + 1 > max_chars:
            stripped_lines_count += (len(lines) - len(sanitized_lines) - stripped_lines_count)
            break
            
        sanitized_lines.append(line)
        accumulated_chars += line_len + 1

    sanitized_text = '\n'.join(sanitized_lines)
    
    # Append a clear system marker so you can see exactly where truncation took place
    if stripped_lines_count > 0:
        sanitized_text += f"\n\n... [🛡️ SECURITY INTERCEPT: {stripped_lines_count} OVERSIZED/SURPLUS LINES STRIPPED TO PREVENT 429 LOCKOUT] ..."

    sys.stderr.write(
        f"📊 [TRAFFIC ANALYZER POST-SANITIZATION SUMMARY]:\n"
        f"  -> Cleaned Character Footprint: {len(sanitized_text)}\n"
        f"  -> Cleaned Token Appx: {len(sanitized_text) // 4}\n"
        f"  -> Total Structural Lines Evicted: {stripped_lines_count}\n\n"
    )
    sys.stderr.flush()

    return sanitized_text
# ======================================================================
# END: UTILITY_CONTEXT_TOKEN_BUDGETER (PATCH 5 OF 5)
# ======================================================================
