# ======================================================================
# FILE: aurora/api/wu_chat_api.py (PATCH 1 OF 1)
# START: API_ENDPOINT_LOGIC
# ======================================================================
import json
import asyncio
import traceback
import re
import sys
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

def process_wu_logic_synchronous(user_delta_notes, user):
    """Executes the full Groq query and macro execution sequence reading strictly from database directives."""
    try:
        runner = MinionRunner()
        
        # FIX: Completely removed the hardcoded instructions string payload overwrite loop.
        # Dynamically pull the active master prompt configuration straight out of the PostgreSQL ledger.
        try:
            wu_config = DeltaDirectives.objects.get(directive_name="minion_wu", is_active=True)
        except DeltaDirectives.DoesNotExist:
            # Safe initial fallback seed ONLY if the registry is completely empty
            baseline_instructions = (
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
            wu_config = DeltaDirectives.objects.create(
                directive_name="minion_wu",
                instructions=baseline_instructions,
                constraints={"model": "llama-3.3-70b-versatile", "temperature": 0.4, "max_tokens": 1000},
                is_active=True,
                created_by=user
            )

        from asgiref.sync import async_to_sync
        complete_response_text = ""
        
        # Drive the streaming token channel directly using the database record instance
        stream_generator = runner.run_minion_task_stream("minion_wu", user_delta_notes)
        
        async def consume_stream():
            nonlocal complete_response_text
            token_buffer = ""
            
            async for token in stream_generator:
                complete_response_text += token
                token_buffer += token
                
                sys.stdout.write(token)
                sys.stdout.flush()
                
                if len(token_buffer) >= 20 or ' ' in token or '\n' in token:
                    try:
                        await async_send_to_console(token_buffer)
                    except Exception:
                        pass
                    token_buffer = ""
            
            if token_buffer:
                try:
                    await async_send_to_console(token_buffer)
                except Exception:
                    pass

        async_to_sync(consume_stream)()
        sys.stdout.write("\n[GROQ RESPONSE FINALIZED]\n")
        sys.stdout.flush()

        command_blocks = re.findall(r"\[COMMAND:\s*(.*?)\]", complete_response_text)
        
        if command_blocks:
            auto_runner = WorkspaceAutomationRunner(user=user)
            coupler = FleetPipelineCoupler(user=user)
            data_coordinator = DataEngineCoordinator(user=user)
            graph_binder = WorkspaceGraphBinder(user=user)

            for command_string in command_blocks:
                parts = command_string.strip().split()
                if not parts:
                    continue
                
                macro = parts[0].lower().strip()
                if macro == "/page" and len(parts) >= 2:
                    page_target = parts[1]
                    async_to_sync(auto_runner.execute_page_command)(page_target)
                    async_to_sync(coupler.run_ui_assembly_pipeline)(
                        target_app="aurora", 
                        page_name=page_target, 
                        layout_instructions=f"Build layout canvas: {user_delta_notes}"
                    )
                
                elif macro == "/api" and len(parts) >= 2:
                    api_target = parts[1]
                    async_to_sync(data_coordinator.assemble_async_data_endpoint)(
                        target_app="aurora",
                        endpoint_name=api_target,
                        query_instructions=f"Synthesize async backend query following: {user_delta_notes}"
                    )

                elif macro == "/bind" and len(parts) >= 4:
                    async_to_sync(graph_binder.execute_workspace_binding)(
                        app_name=parts[1],
                        function_name=parts[2],
                        api_name=parts[3]
                    )

        try:
            async_to_sync(async_send_to_console)("\n🏁 [STREAM_COMPLETE]\n")
        except Exception:
            pass

        return {"status": "SUCCESS", "wu_response": complete_response_text, "commands_found": len(command_blocks)}
    except Exception as err:
        error_trace = traceback.format_exc()
        sys.stderr.write(f"\n💥 [CRITICAL RUNTIME ERROR]:\n{error_trace}\n")
        sys.stderr.flush()
        return {"status": "ERROR", "message": str(err), "trace": error_trace}

@login_required
def wu_chat_endpoint(request):
    """Processes requests synchronously during diagnostic test runs to force error output directly back to the UI."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            delta_notes = data.get("delta_notes", "").strip()
            if not delta_notes:
                return JsonResponse({"error": "Empty delta notes provided"}, status=400)
                
            result = process_wu_logic_synchronous(delta_notes, request.user)
            if result["status"] == "ERROR":
                return JsonResponse({"error": result["message"], "traceback": result["trace"]}, status=500)
                
            return JsonResponse({"status": "wu_is_processing", "direct_text_output": result["wu_response"]})
        except Exception as err:
            return JsonResponse({"error": str(err)}, status=400)
            
    return JsonResponse({"error": "POST required"}, status=405)
# ======================================================================
# END: API_ENDPOINT_LOGIC (PATCH 1 OF 1)
# ======================================================================
