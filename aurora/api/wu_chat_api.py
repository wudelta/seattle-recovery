# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 1 OF 4)
# START: MODULE_RUN_IMPORTS_AND_DEPENDENCIES
# ======================================================================
import json
import asyncio
import traceback
import re
import sys
import os
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from asgiref.sync import sync_to_async, async_to_sync
from aurora.models import DeltaDirectives, WorkspaceTransaction, TrackedCommand
from aurora.minions.engine import MinionRunner
from .dev_streamer_api import async_send_to_console
# ======================================================================
# END: MODULE_RUN_IMPORTS_AND_DEPENDENCIES (PATCH 1 OF 4)
# ======================================================================

# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 2 OF 4)
# START: SYNCHRONOUS_ORCHESTRATION_CORE_ENGINE
# ======================================================================
def process_wu_logic_synchronous(user_delta_notes, user):
    """Generates the full Groq execution plan and records pending tracking blocks."""
    try:
        runner = MinionRunner()
        try:
            wu_config = DeltaDirectives.objects.get(directive_name="minion_wu", is_active=True)
        except DeltaDirectives.DoesNotExist:
            error_msg = "💥 [REGISTRY CRITICAL]: Master directive configuration 'minion_wu' is missing or inactive in your database ledger!"
            sys.stderr.write(f"{error_msg}\n")
            sys.stderr.flush()
            return {"status": "ERROR", "message": "Master orchestrator directive is missing in database registry.", "trace": error_msg}

        complete_response_text = ""
        stream_generator = runner.run_minion_task_stream("minion_wu", user_delta_notes)

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

        transaction = WorkspaceTransaction.objects.create(
            user=user,
            prompt_context=user_delta_notes,
            status='PENDING'
        )

        # Casing-flexible regex processing block handling varied layout margins
        command_blocks = re.findall(r"\[[Cc][Oo][Mm][Mm][Aa][Nn][Dd]:\s*(.*?)\]", complete_response_text)
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

        return {"status": "SUCCESS", "wu_response": complete_response_text, "transaction_id": str(transaction.id)}
    except Exception as err:
        return {"status": "ERROR", "message": str(err), "trace": traceback.format_exc()}
# ======================================================================
# END: SYNCHRONOUS_ORCHESTRATION_CORE_ENGINE (PATCH 2 OF 4)
# ======================================================================

# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 3 OF 4)
# START: CHAT_REQUEST_ENDPOINT_VIEW
# ======================================================================
@login_required
def wu_chat_endpoint(request):
    """Processes requests, returning text alongside a unique transaction review token ID."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            delta_notes = data.get("delta_notes", "").strip()
            if not delta_notes:
                return JsonResponse({"error": "Empty delta notes provided"}, status=400)
            result = process_wu_logic_synchronous(delta_notes, request.user)
            if result["status"] == "ERROR":
                return JsonResponse({"error": result["message"], "traceback": result["trace"]}, status=500)
            return JsonResponse({"status": "wu_is_processing", "direct_text_output": result["wu_response"], "transaction_id": result["transaction_id"]})
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=400)
    return JsonResponse({"error": "POST required"}, status=405)
# ======================================================================
# END: CHAT_REQUEST_ENDPOINT_VIEW (PATCH 3 OF 4)
# ======================================================================

# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 4 OF 4)
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
                        
                        # Strict path evaluation guarding to prevent directory traversal out of project workspace
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
# END: TRANSACTION_ACTION_CONTROLLER_VIEW (PATCH 4 OF 4)
# ======================================================================
