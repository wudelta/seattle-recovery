# ======================================================================
# FILE: aurora/minions/data_engine.py (PATCH 1 OF 1)
# START: DATA_ENGINE_COORDINATOR_LOGIC
# ======================================================================
import os
import asyncio
from django.conf import settings
from aurora.minions.engine import MinionRunner
from aurora.minions.automation_utilities import WorkspaceAutomationRunner
from aurora.api.dev_streamer_api import async_send_to_console

class DataEngineCoordinator:
    """Assembles lightweight, injection-free async database api views natively inside forged skeletons."""

    def __init__(self, user):
        self.user = user
        self.runner = MinionRunner()
        self.automation = WorkspaceAutomationRunner(user=user)

    async def assemble_async_data_endpoint(self, target_app: str, endpoint_name: str, query_instructions: str) -> bool:
        """
        Triggers the 8B minion_data_endpoint agent to generate raw, high-performance
        async view queries, and writes them cleanly inside the forged API skeleton.
        """
        clean_app = target_app.strip().lower()
        clean_name = endpoint_name.strip().lower().replace(" ", "_")
        func_name = f"{clean_name}_endpoint"
        
        await async_send_to_console(f"⚡ [DATA_ENGINE] Instructing minion_data_endpoint to synthesize logic for: {func_name}...")
        
        # 1. Initialize empty target canvas file using Step 2 automation tool hooks
        # This triggers ApiSkeletonBuilder.forge_api via automation wrapper mapping
        success = await self.automation.execute_api_command(clean_name)
        if not success:
            await async_send_to_console(f"❌ [DATA_ENGINE] Automation view skeleton generation block failed for resource: {clean_name}")
            return False

        target_filepath = os.path.join(self.automation.base_dir, clean_app, "api", f"{clean_name}_api.py")
        if not os.path.exists(target_filepath):
            await async_send_to_console(f"❌ [DATA_ENGINE] Forged script file structure unmapped on disk: {target_filepath}")
            return False

        # Formulate strict prompts matching the structural signature of the newly unmasked api_skeleton anchors
        generation_prompt = (
            f"Write the inside logic for a high-performance Django view function named 'def {func_name}(request):'.\n"
            f"Requirements:\n{query_instructions}\n\n"
            f"CRITICAL FORMATTING BOUNDARY:\n"
            f"Return ONLY raw python code rows that fill the interior execution track of the view. "
            f"Do NOT include the 'def {func_name}(request):' line itself, do NOT add decorators, and do NOT wrap in markdown backticks."
        )

        generated_inner_code = ""
        async for chunk in self.runner.run_minion_task_stream("minion_wu", generation_prompt):
            generated_inner_code += chunk

        def inject_query_logic():
            with open(target_filepath, "r") as f:
                content = f.read()

            # Align explicitly with the permanent text anchors generated inside api_skeleton.py
            start_anchor = "# START: API_ENDPOINT_LOGIC"
            end_anchor = "# END: API_ENDPOINT_LOGIC"

            if start_anchor in content and end_anchor in content:
                header = content.split(start_anchor)[0] + start_anchor + "\n"
                tail = "\n" + end_anchor + content.split(end_anchor)[1]
                
                # Format complete executable block containing the AI logic matrix
                indented_code = "\n".join([f"    {line}" if line.strip() else "" for line in generated_inner_code.strip().split("\n")])
                updated_content = (
                    f"{header}"
                    f"def {func_name}(request):\n"
                    f"    \"\"\"Automated JSON payload endpoint forged by Aurora and optimized by Fleet Minions.\"\"\"\n"
                    f"{indented_code}"
                    f"{tail}"
                )
                
                with open(target_filepath, "w") as f:
                    f.write(updated_content)
                return True
            return False

        from asgiref.sync import sync_to_async
        updated = await sync_to_async(inject_query_logic, thread_sensitive=False)()
        
        if updated:
            await async_send_to_console(f"✅ [DATA_ENGINE] Asynchronous query logic surgically injected into: {target_filepath}")
            return True
        else:
            await async_send_to_console(f"❌ [DATA_ENGINE] Anchor matching alignment error during merge: {target_filepath}")
            return False
# ======================================================================
# END: DATA_ENGINE_COORDINATOR_LOGIC (PATCH 1 OF 1)
# ======================================================================
