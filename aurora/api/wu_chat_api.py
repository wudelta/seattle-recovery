# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 1 OF 1)
# START: API_ENDPOINT_LOGIC
# ======================================================================
import json
import asyncio
import traceback
import re
import sys
import os
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings  # FIX: Added missing settings import for absolute file path resolution
from asgiref.sync import sync_to_async, async_to_sync
from aurora.models import DeltaDirectives, WorkspaceTransaction, TrackedCommand
from aurora.minions.engine import MinionRunner
from .dev_streamer_api import async_send_to_console

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
            try:
                async_to_sync(async_send_to_console)(json.dumps({
                    "event": "wu_chat_token", 
                    "text": error_msg
                }))
            except Exception:
                pass
            return {"status": "ERROR", "message": "Master orchestrator directive is missing in database registry.", "trace": error_msg}

        complete_response_text = ""
        stream_generator = runner.run_minion_task_stream("minion_wu", user_delta_notes)

        async def consume_stream():
            nonlocal complete_response_text
            async for token in stream_generator:
                complete_response_text += token
                sys.stdout.write(token)
                sys.stdout.flush()
                try:
                    await async_send_to_console(json.dumps({"event": "wu_chat_token", "text": token}))
                except Exception:
                    pass

        async_to_sync(consume_stream)()

        transaction = WorkspaceTransaction.objects.create(
            user=user,
            prompt_context=user_delta_notes,
            status='PENDING'
        )

        command_blocks = re.findall(r"\[COMMAND:\s*(.*?)\]", complete_response_text)
        for index, command_string in enumerate(command_blocks):
            parts = command_string.strip().split()
            if not parts:
                continue
            
            macro = parts.lower().strip()
            predicted_files = []
            clean_arg = parts.strip().lower().replace(" ", "_") if len(parts) >= 2 else ""
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

        try:
            async_to_sync(async_send_to_console)(json.dumps({"event": "wu_chat_complete"}))
        except Exception:
            pass

        return {"status": "SUCCESS", "wu_response": complete_response_text, "transaction_id": str(transaction.id)}
    except Exception as err:
        return {"status": "ERROR", "message": str(err), "trace": traceback.format_exc()}

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

@login_required
def process_transaction_action(request, tx_id):
    """Approve or surgically Rollback (/destroy) workspace changes by transaction tracking ID."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
        
    def _execute_sync_action_logic():
        try:
            tx = WorkspaceTransaction.objects.prefetch_related('commands').get(id=tx_id, user=request.user)
            action = json.loads(request.body).get("action", "").upper()

            if action == "APPROVE":
                from aurora.minions.automation_utilities import WorkspaceAutomationRunner
                runner = WorkspaceAutomationRunner(user=request.user, dry_run=False)
                for cmd in tx.commands.all():
                    if cmd.macro == "/page" and cmd.arguments:
                        async_to_sync(runner.execute_page_command)(cmd.arguments)
                    elif cmd.macro == "/api" and cmd.arguments:
                        async_to_sync(runner.execute_api_command)(cmd.arguments)
                tx.status = 'EXECUTED'
                tx.save()
                return {"status": "SUCCESS", "message": "Transaction executed and files written."}

            elif action == "DESTROY":
                for cmd in tx.commands.all():
                    for file_path in cmd.affected_files:
                        full_path = os.path.join(getattr(settings, "BASE_DIR", os.getcwd()), file_path)
                        if os.path.exists(full_path):
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
# END: API_ENDPOINT_LOGIC (PATCH 1 OF 1)
# ======================================================================
