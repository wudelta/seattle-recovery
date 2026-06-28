# ======================================================================
# FILE: aurora/minions/automation_utilities.py (PATCH 1 OF 1)
# START: WORKSPACE_AUTOMATION_UTILITIES
# ======================================================================
import os
import asyncio
import traceback
from django.conf import settings
from asgiref.sync import sync_to_async
from aurora.models import ComponentRegistry
from aurora.api.dev_streamer_api import async_send_to_console

class WorkspaceAutomationRunner:
    """Handles shell script simulation and safe file creation tasks for page and api resources."""

    def __init__(self, user, dry_run: bool = True):
        self.user = user
        self.base_dir = getattr(settings, "BASE_DIR", os.getcwd())
        # SAFETY PROTECTION: Default to True to guarantee explicit approval is required to write to disk
        self.dry_run = dry_run 

    async def execute_page_command(self, page_name: str) -> bool:
        """
        Executes the /page command macro: provisions a blank view structure file on disk, 
        registers existence in the ComponentRegistry, and appends base routing maps.
        """
        try:
            clean_name = page_name.strip().lower().replace(" ", "_")
            template_dir = os.path.join(self.base_dir, "aurora", "templates", "aurora", "pages")
            target_filepath = os.path.join(template_dir, f"{clean_name}.html")

            if self.dry_run:
                await async_send_to_console(f"🛡️ [DRY-RUN SIMULATION] Would create template directory: '{template_dir}'")
                await async_send_to_console(f"🛡️ [DRY-RUN SIMULATION] Would write page view asset layout file: '{target_filepath}'")
                return True

            await async_send_to_console(f"🛠️ [AUTOMATION] Provisioning target file templates for layout view matrix: '{clean_name}'...")
            os.makedirs(template_dir, exist_ok=True)
            if not os.path.exists(target_filepath):
                with open(target_filepath, "w") as f:
                    f.write(f"<!-- Aurora Generated Page Layout Panel: {clean_name} -->\n")
                    f.write("<div class='container p-4 text-light'>\n")
                    f.write(f" <h3>Workspace Module Interface Deck: {clean_name}</h3>\n")
                    f.write("</div>\n")

            def update_registry():
                comp, created = ComponentRegistry.objects.update_or_create(
                    file_path=os.path.relpath(target_filepath, self.base_dir),
                    defaults={
                        "name": f"page_{clean_name}",
                        "persona": "UI_LAYOUT",
                        "status": "ACTIVE",
                        "visibility": "PRIVATE",
                        "created_by": self.user
                    }
                )
                return created

            is_new = await sync_to_async(update_registry, thread_sensitive=False)()
            status_text = "Registered structural layout" if is_new else "Synchronized active structural mapping"
            await async_send_to_console(f"✅ [REGISTRY MULTI-MATRIX]: {status_text} for 'page_{clean_name}'.")
            return True
        except Exception as err:
            await async_send_to_console(f"💥 [AUTOMATION SCHEDULER FAULT]: Failed /page sequence execution: {str(err)}")
            return False

    async def execute_api_command(self, api_name: str) -> bool:
        """
        Executes the /api command macro: generates an empty asynchronous Django backend view file, 
        configures registry paths, and hooks tracking channels.
        """
        try:
            clean_name = api_name.strip().lower().replace(" ", "_")
            api_dir = os.path.join(self.base_dir, "aurora", "api")
            target_filepath = os.path.join(api_dir, f"{clean_name}_api.py")

            if self.dry_run:
                await async_send_to_console(f"🛡️ [DRY-RUN SIMULATION] Would create engine module directory: '{api_dir}'")
                await async_send_to_console(f"🛡️ [DRY-RUN SIMULATION] Would write async API script module file: '{target_filepath}'")
                return True

            await async_send_to_console(f"⚙️ [AUTOMATION] Assembling async data engine pipeline structural nodes: '{clean_name}'...")
            os.makedirs(api_dir, exist_ok=True)
            if not os.path.exists(target_filepath):
                with open(target_filepath, "w") as f:
                    f.write(f"# Aurora Generated Asynchronous API Endpoints module: {clean_name}\n")
                    f.write("from django.http import JsonResponse\n\n")
                    f.write(f"async def {clean_name}_endpoint(request):\n")
                    f.write(" \"\"\"Asynchronous backend transaction execution router framework.\"\"\"\n")
                    f.write(" return JsonResponse({\"status\": \"active\", \"engine\": \"aurora_core\"})\n")

            def update_registry():
                comp, created = ComponentRegistry.objects.update_or_create(
                    file_path=os.path.relpath(target_filepath, self.base_dir),
                    defaults={
                        "name": f"api_{clean_name}",
                        "persona": "COMPILER_MODULE",
                        "status": "ACTIVE",
                        "visibility": "PRIVATE",
                        "created_by": self.user
                    }
                )
                return created

            is_new = await sync_to_async(update_registry, thread_sensitive=False)()
            status_text = "Registered structural data hook" if is_new else "Synchronized active data mapping"
            await async_send_to_console(f"✅ [REGISTRY MULTI-MATRIX]: {status_text} for 'api_{clean_name}'.")
            return True
        except Exception as err:
            await async_send_to_console(f"💥 [AUTOMATION SCHEDULER FAULT]: Failed /api sequence execution: {str(err)}")
            return False
# ======================================================================
# END: WORKSPACE_AUTOMATION_UTILITIES (PATCH 1 OF 1)
# ======================================================================
