# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 1 OF 1)
# START: API_ENDPOINT_LOGIC
# ======================================================================
import json
import asyncio
import traceback
import re
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from asgiref.sync import sync_to_async
from aurora.models import DeltaDirectives
from aurora.minions.engine import MinionRunner
from aurora.minions.automation_utilities import WorkspaceAutomationRunner
from aurora.minions.pipeline_coupler import FleetPipelineCoupler
from aurora.minions.data_engine import DataEngineCoordinator
from aurora.minions.graph_binder import WorkspaceGraphBinder
from .dev_streamer_api import async_send_to_console

async def interact_with_wu_async(user_delta_notes: str, user):
    """
    Seeds Wu rules and streams tokens via Daphne without blocking.
    Wu analyzes the human intention, streams his plan, and triggers
    the automation sub-fleet using macro parsing strategies.
    """
    try:
        runner = MinionRunner()
        wu_instructions = (
            "You are Wu, the 70B Orchestrator Fleet Commander. You speak to the developer in natural human language.\n"
            "Your job is to read 'delta_notes' and explain exactly how you will solve it by assigning sub-tasks.\n\n"
            "YOUR FLEET DIRECTORY & COMMAND SHELL MAPS:\n"
            "- `/page [name]`: Triggers a new blank view structure file layout context.\n"
            "- `/api [name]`: Generates an empty asynchronous Django backend API view schema.\n"
            "- `/bind [app] [func] [api]`: Compiles relational dependencies across your directory structure into Neo4j.\n\n"
            "CRITICAL RESPONSE FORMAT:\n"
            "Outline your multi-step routing plan step-by-step. At the very end of your response, "
            "you must append the exact command shell scripts you want the automation runner to execute. "
            "Put each execution string on its own new line using brackets, like: [COMMAND: /page profile_view]"
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

        await sync_to_async(sync_wu_record)()
        await async_send_to_console("⚡ [ORCHESTRATOR] Routing execution strings to Fleet Commander Wu...")
        await async_send_to_console("\n🔮 [WU ORCHESTRATION PLAN]: ")

        # 1. Stream Wu's high-level human orchestration breakdown plan live to the dashboard
        complete_response_text = ""
        async for token in runner.run_minion_task_stream("minion_wu", user_delta_notes):
            complete_response_text += token
            await async_send_to_console(token)
            
        await async_send_to_console("\n")

        # 2. Extract and parse programmatic execution scripts from Wu's response stream
        command_blocks = re.findall(r"\[COMMAND:\s*(.*?)\]", complete_response_text)
        
        if command_blocks:
            await async_send_to_console("⚙️ [ORCHESTRATOR] Commencing execution track for sub-minion command macros...")
            
            # Instantiating our verified step automation runners
            auto_runner = WorkspaceAutomationRunner(user=user)
            coupler = FleetPipelineCoupler(user=user)
            data_coordinator = DataEngineCoordinator(user=user)
            graph_binder = WorkspaceGraphBinder(user=user)

            for command_string in command_blocks:
                parts = command_string.strip().split()
                if not parts:
                    continue
                
                macro = parts[0].lower().strip()
                
                # Dynamic Branch A: Physical Layout Page Canvas Creation
                if macro == "/page" and len(parts) >= 2:
                    page_target = parts[1]
                    await auto_runner.execute_page_command(page_target)
                    # Pipeline Hand-off: Feed layout instructions directly down to 8B UI specialization minions
                    await coupler.run_ui_assembly_pipeline(
                        target_app="aurora", 
                        page_name=page_target, 
                        layout_instructions=f"Build layout canvas following user delta goals: {user_delta_notes}"
                    )
                
                # Dynamic Branch B: Backend Asynchronous API Query Hook Generation
                elif macro == "/api" and len(parts) >= 2:
                    api_target = parts[1]
                    await data_coordinator.assemble_async_data_endpoint(
                        target_app="aurora",
                        endpoint_name=api_target,
                        query_instructions=f"Synthesize async backend handler query inside anchors following: {user_delta_notes}"
                    )

                # Dynamic Branch C: Neo4j Relational Dependency Graph Matrix Compilation
                elif macro == "/bind" and len(parts) >= 4:
                    await graph_binder.execute_workspace_binding(
                        app_name=parts[1],
                        function_name=parts[2],
                        api_name=parts[3]
                    )
        else:
            await async_send_to_console("ℹ️ [ORCHESTRATOR] Conversational execution resolved. No command scripts intercepted.")

    except Exception as e:
        await async_send_to_console(f"\n💥 [ORCHESTRATOR ERROR]:\n{traceback.format_exc()}")

@login_required
def wu_chat_endpoint(request):
    """Fires off background processing tasks within the active loop context safely across all thread states."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            delta_notes = data.get("delta_notes", "").strip()
            
            if not delta_notes:
                return JsonResponse({"error": "Empty delta notes provided"}, status=400)
                
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None

            if loop and loop.is_running():
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
