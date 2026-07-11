# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 1 OF 6)
# START: MODULE_RUN_IMPORTS_AND_DEPENDENCIES
# ======================================================================
import json
import asyncio
import traceback
import re
import sys
import os
import time
from collections import deque
from threading import Lock
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from asgiref.sync import sync_to_async, async_to_sync
from aurora.models import DeltaDirectives, WorkspaceTransaction, TrackedCommand
from aurora.minions.engine import MinionRunner
from .dev_streamer_api import async_send_to_console
# ======================================================================
# END: MODULE_RUN_IMPORTS_AND_DEPENDENCIES (PATCH 1 OF 6)
# ======================================================================

# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 2 OF 6)
# START: SYNCHRONOUS_ORCHESTRATION_CORE_ENGINE
# ======================================================================

def process_wu_logic_synchronous(user_delta_notes, user, session_id="default_cockpit_thread"):
    """Generates the full Gemini execution plan, factoring in low-footprint ledger contexts."""
    try:
        runner = MinionRunner()
        try:
            wu_config = DeltaDirectives.objects.get(directive_name="minion_wu", is_active=True)
        except DeltaDirectives.DoesNotExist:
            error_msg = "💥 [REGISTRY CRITICAL]: Master directive configuration 'minion_wu' is missing or inactive in your database ledger!"
            sys.stderr.write(f"{error_msg}\n")
            sys.stderr.flush()
            return {"status": "ERROR", "message": "Master orchestrator directive is missing in database registry.", "trace": error_msg}

        from aurora.models import ChatLedgerEntry

        # 1. READ CONTEXT BACK OUT OF POSTGRESQL (Strict Limit to Last 6 Blocks to Prevent Bloat)
        db_history = ChatLedgerEntry.objects.filter(
            session_id=session_id
        ).order_by('-created_at')[:6]

        # 2. COMPACT HISTORY ASYMMETRICALLY: Format into a lightweight instruction context block
        history_buffer_lines = []
        for entry in reversed(db_history):
            # Skip appending the active prompt if it was already saved to avoid doubling text inputs
            if entry.role == 'user' and entry.text == user_delta_notes:
                continue
            author_tag = "Developer Intention" if entry.role == 'user' else "Wu Response"
            history_buffer_lines.append(f"--- PRIOR CONVERSATION STEP ({author_tag}) ---\n{entry.text}")

        # Unify history block text or remain fallback-clean if it is a fresh session thread
        history_context_block = "\n\n".join(history_buffer_lines) if history_buffer_lines else ""

        # 3. CONSOLIDATE PAYLOAD: Graft compact history right ahead of your raw user notes
        compiled_task_notes = user_delta_notes
        if history_context_block:
            compiled_task_notes = f"{history_context_block}\n\n=== CURRENT LIVE WORKSPACE TASK INSTRUCTION ===\n{user_delta_notes}"

        complete_response_text = ""
        stream_generator = runner.run_minion_task_stream("minion_wu", compiled_task_notes)

        # Thread-safe async worker strategy to read tokens without latching onto or blocking Daphne's main event loop
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

        # Map to Gemini's high-capacity free tier limits (15 Requests Per Minute, 1M Context).
        r_limit = 15
        r_rem = getattr(runner, "last_rpm_remaining", 14)
        t_limit = 1000000
        t_used = getattr(runner, "last_tokens_consumed", len(compiled_task_notes) // 4)
        t_rem = max(0, t_limit - t_used)
        tokens_used_pct = round((t_used / t_limit) * 100, 3) if t_limit > 0 else 0.0
        requests_used_pct = round(((r_limit - r_rem) / r_limit) * 100, 1) if r_limit > 0 else 0.0

        fuel_gauge_metrics = {
            "tokens_limit": t_limit,
            "tokens_remaining": t_rem,
            "tokens_used_pct": min(100.0, max(0.0, tokens_used_pct)),
            "requests_limit": r_limit,
            "requests_remaining": r_rem,
            "requests_used_pct": min(100.0, max(0.0, requests_used_pct))
        }

        # Casing-flexible regex processing block handling varied layout margins
        command_blocks = re.findall(r"\[[Cc][Oo][Mm][Mm][Aa][Nn][Dd]:\s*(.*?)\]", complete_response_text)

        transaction = None

        if command_blocks:
            transaction = WorkspaceTransaction.objects.create(
                user=user,
                prompt_context=user_delta_notes,
                status='PENDING'
            )

            for index, command_string in enumerate(command_blocks):
                parts = command_string.strip().split()
                if not parts:
                    continue

                macro = parts[0].lower().strip()
                predicted_files = []
                clean_arg = parts[1].strip().lower().replace(" ", "_") if len(parts) >= 2 else ""

                if not clean_arg:
                    continue

                if macro == "/page":
                    predicted_files.append(f"aurora/templates/aurora/pages/{clean_arg}.html")
                elif macro == "/api":
                    predicted_files.append(f"aurora/api/{clean_arg}_api.py")

                TrackedCommand.objects.create(
                    transaction=transaction,
                    macro=macro,
                    arguments=parts[1:],
                    affected_files=predicted_files,
                    execution_order=index
                )

        return {
            "status": "SUCCESS",
            "wu_response": complete_response_text,
            "transaction_id": str(transaction.id) if transaction else None,
            "fuel_gauge": fuel_gauge_metrics
        }

    except Exception as err:
        return {"status": "ERROR", "message": str(err), "trace": traceback.format_exc()}

# ======================================================================
# END: SYNCHRONOUS_ORCHESTRATION_CORE_ENGINE (PATCH 2 OF 6)
# ======================================================================

# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 3 OF 6)
# START: CHAT_REQUEST_ENDPOINT_VIEW
# ======================================================================
@login_required
def wu_chat_endpoint(request):
    """
    Processes requests, hooks up sliding history windows via ChatLedgerEntry,
    and returns response payloads along with transaction metadata.
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
                "transaction_id": result["transaction_id"],
                "fuel_gauge": result.get("fuel_gauge", {})
            })
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=400)
    return JsonResponse({"error": "POST required"}, status=405)
# ======================================================================
# END: CHAT_REQUEST_ENDPOINT_VIEW (PATCH 3 OF 6)
# ======================================================================

# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 4 OF 6)
# START: PRE_SEND_TRAFFIC_SAFETY_MONITORING_METRICS
# ======================================================================
# Thread safety locks and allocation deques tracking network transaction states
OUTBOUND_TRAFFIC_LOG = deque()
TRAFFIC_LOCK = Lock()
# ======================================================================
# END: PRE_SEND_TRAFFIC_SAFETY_MONITORING_METRICS (PATCH 4 OF 6)
# ======================================================================

# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 5 OF 6)
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
# END: UTILITY_CONTEXT_TOKEN_BUDGETER (PATCH 5 OF 6)
# ======================================================================

# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 6 OF 6)
# START: TRANSACTION_ACTION_CONTROLLER_VIEW
# ======================================================================
@login_required
def process_transaction_action(request, tx_id):
    """Approve or surgically Rollback (/destroy) workspace changes by transaction tracking ID."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    def _execute_sync_action_logic():
        try:
            tx = WorkspaceTransaction.objects.prefetch_related('commands').get(id=tx_id, user=request.user)
            action = json.loads(request.body).get("action", "").upper()
            base_dir = os.path.abspath(getattr(settings, "BASE_DIR", os.getcwd()))

            if action == "APPROVE":
                from aurora.minions.automation_utilities import WorkspaceAutomationRunner
                runner = WorkspaceAutomationRunner(user=request.user, dry_run=False)
                for cmd in tx.commands.all():
                    if cmd.macro == "/page" and cmd.arguments:
                        async_to_sync(runner.execute_page_command)(cmd.arguments[0])
                    elif cmd.macro == "/api" and cmd.arguments:
                        async_to_sync(runner.execute_api_command)(cmd.arguments[0])
                tx.status = 'EXECUTED'
                tx.save()
                return {"status": "SUCCESS", "message": "Transaction executed and files written."}

            elif action == "DESTROY":
                for cmd in tx.commands.all():
                    for file_path in cmd.affected_files:
                        if not file_path or not isinstance(file_path, str):
                            continue
                        # Strict path evaluation guarding to prevent directory traversal
                        full_path = os.path.abspath(os.path.join(base_dir, file_path))
                        if not full_path.startswith(base_dir) or full_path == base_dir:
                            sys.stderr.write(f"⚠️ [SECURITY ALERT]: Blocked destructive outside directory sweep path: {file_path}\n")
                            continue
                        if os.path.exists(full_path) and os.path.isfile(full_path):
                            os.remove(full_path)
                tx.status = 'ROLLED_BACK'
                tx.save()
                return {"status": "SUCCESS", "message": "Transaction files destroyed and configuration rolled back."}

            return {"error": "Invalid action context", "status_code": 400}
        except WorkspaceTransaction.DoesNotExist:
            return {"error": "Transaction context lookup failure.", "status_code": 404}
        except Exception as err:
            return {"error": str(err), "status_code": 500}

    try:
        loop = asyncio.get_running_loop()
        is_async_context = True
    except RuntimeError:
        is_async_context = False

    if is_async_context:
        async def run_in_thread():
            return await sync_to_async(_execute_sync_action_logic, thread_sensitive=False)()
        result = async_to_sync(run_in_thread)()
    else:
        result = _execute_sync_action_logic()

    if "error" in result:
        return JsonResponse({"error": result["error"]}, status=result.get("status_code", 400))
    return JsonResponse(result)
# ======================================================================
# END: TRANSACTION_ACTION_CONTROLLER_VIEW (PATCH 6 OF 6)
# ======================================================================
