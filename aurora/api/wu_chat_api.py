# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 1 OF 1)
# START: API_ENDPOINT_LOGIC
# ======================================================================
import json
import asyncio
import traceback
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from aurora.models import DeltaDirectives
from aurora.minions.engine import MinionRunner
from .dev_streamer_api import async_send_to_console

async def interact_with_wu_async(user_delta_notes: str, user):
    """
    Seeds Wu with his operational architecture rules dynamically and asks him 
    to outline his execution strategy plan in natural human-like language.
    """
    try:
        runner = MinionRunner()
        
        wu_instructions = (
            "You are Wu, the 70B Orchestrator Fleet Commander. You are the only minion allowed to "
            "speak to the developer in natural human language. Your job is to read 'delta_notes' and "
            "explain exactly how you will solve it by assigning sub-tasks to your specialized fleet.\n\n"
            "YOUR FLEET DIRECTORY & CAPABILITIES:\n"
            "- `/page [name]`: Command to generate a new view file and bind its structural routing context.\n"
            "- `minion_UI_layout`: Handles writing raw, clean structural HTML (No CSS, no JavaScript).\n"
            "- `minion_UI_style`: Receives the HTML blueprint and writes pure, modular CSS formatting.\n"
            "- `minion_UI_logic`: Appends clean interactive frontend JavaScript logic parameters.\n"
            "- `minion_data_endpoint`: Uses the `/api` command to construct backend endpoints and write DB queries.\n"
            "- `/bind`: Command invoked at the end to compile relational dependencies across the workspace graph.\n\n"
            "CRITICAL CONSTRAINTS:\n"
            "Do NOT write actual code files yourself. Speak like a lead engineering commander. "
            "Outline your multi-step routing plan step-by-step, stating which commands or minions you will invoke."
        )

        def sync_wu_record():
            wu_row, _ = DeltaDirectives.objects.update_or_create(
                directive_name="minion_wu",
                defaults={
                    "instructions": wu_instructions,
                    "constraints": {"model": "llama-3.3-70b-versatile", "temperature": 0.4, "max_tokens": 1000},
                    "is_active": True,
                    "created_by": user
                }
            )
            return wu_row

        from asgiref.sync import sync_to_async
        await sync_to_async(sync_wu_record)()

        await async_send_to_console("⚡ [ORCHESTRATOR] Initializing connection to Fleet Commander Wu...")
        
        # Invoke Wu using his target system instructions
        wu_response = runner.run_minion_task("minion_wu", user_delta_notes)
        
        # Stream Wu's human plan directly to the chat dashboard box in real-time
        await async_send_to_console(f"\n🔮 [WU ORCHESTRATION PLAN]:\n{wu_response}\n")

    except Exception as e:
        await async_send_to_console(f"💥 [ORCHESTRATOR ERROR]:\n{traceback.format_exc()}")

@login_required
def wu_chat_endpoint(request):
    """FIXED: Replaced dummy payload with active asynchronous orchestration trigger loop."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            delta_notes = data.get("delta_notes", "")
            
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(interact_with_wu_async(delta_notes, request.user))
            else:
                from asgiref.sync import async_to_sync
                async_to_sync(interact_with_wu_async)(delta_notes, request.user)
                
            return JsonResponse({"status": "wu_is_processing"})
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=400)
    return JsonResponse({"error": "POST required"}, status=405)
# ======================================================================
# END: API_ENDPOINT_LOGIC (PATCH 1 OF 1)
# ======================================================================
