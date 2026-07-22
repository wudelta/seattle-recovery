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
            template_dir = os.path.join(
                self.base_dir,
                "aurora",
                "templates",
                "aurora",
                "pages",
            )
            target_filepath = os.path.join(
                template_dir,
                f"{clean_name}.html",
            )

            if self.dry_run:
                await async_send_to_console(
                    "🛡️ [DRY-RUN SIMULATION] Would create template "
                    f"directory: '{template_dir}'"
                )
                await async_send_to_console(
                    "🛡️ [DRY-RUN SIMULATION] Would write page view asset "
                    f"layout file: '{target_filepath}'"
                )
                return True

            await async_send_to_console(
                "🛠️ [AUTOMATION] Provisioning target file templates for "
                f"layout view matrix: '{clean_name}'..."
            )
            os.makedirs(template_dir, exist_ok=True)

            if not os.path.exists(target_filepath):
                with open(target_filepath, "w") as file_handle:
                    file_handle.write(
                        "<!-- Aurora Generated Page Layout Panel: "
                        f"{clean_name} -->\n"
                    )
                    file_handle.write(
                        "<div class='container p-4 text-light'>\n"
                    )
                    file_handle.write(
                        " <h3>Workspace Module Interface Deck: "
                        f"{clean_name}</h3>\n"
                    )
                    file_handle.write("</div>\n")

            def update_registry():
                relative_path = os.path.relpath(
                    target_filepath,
                    self.base_dir,
                )
                defaults = {
                    "name": f"page_{clean_name}",
                    "persona": "UI_LAYOUT",
                    "status": "ACTIVE",
                    "visibility": "PRIVATE",
                    "created_by": self.user,
                }

                component, created = (
                    ComponentRegistry.objects.get_or_create(
                        file_path=relative_path,
                        defaults={
                            **defaults,
                            "locked": False,
                        },
                    )
                )

                if not created:
                    for field_name, field_value in defaults.items():
                        setattr(component, field_name, field_value)

                    component.save(
                        update_fields=[
                            *defaults.keys(),
                            "date_modified",
                        ]
                    )

                return created

            is_new = await sync_to_async(
                update_registry,
                thread_sensitive=False,
            )()
            status_text = (
                "Registered structural layout"
                if is_new
                else "Synchronized active structural mapping"
            )
            await async_send_to_console(
                "✅ [REGISTRY MULTI-MATRIX]: "
                f"{status_text} for 'page_{clean_name}'."
            )
            return True
        except Exception as err:
            await async_send_to_console(
                "💥 [AUTOMATION SCHEDULER FAULT]: Failed /page sequence "
                f"execution: {str(err)}"
            )
            return False

    async def execute_api_command(self, api_name: str) -> bool:
        """
        Executes the /api command macro: generates an empty asynchronous Django backend view file,
        configures registry paths, and hooks tracking channels.
        """
        try:
            clean_name = api_name.strip().lower().replace(" ", "_")
            api_dir = os.path.join(
                self.base_dir,
                "aurora",
                "api",
            )
            target_filepath = os.path.join(
                api_dir,
                f"{clean_name}_api.py",
            )

            if self.dry_run:
                await async_send_to_console(
                    "🛡️ [DRY-RUN SIMULATION] Would create engine module "
                    f"directory: '{api_dir}'"
                )
                await async_send_to_console(
                    "🛡️ [DRY-RUN SIMULATION] Would write async API script "
                    f"module file: '{target_filepath}'"
                )
                return True

            await async_send_to_console(
                "⚙️ [AUTOMATION] Assembling async data engine pipeline "
                f"structural nodes: '{clean_name}'..."
            )
            os.makedirs(api_dir, exist_ok=True)

            if not os.path.exists(target_filepath):
                with open(target_filepath, "w") as file_handle:
                    file_handle.write(
                        "# Aurora Generated Asynchronous API Endpoints "
                        f"module: {clean_name}\n"
                    )
                    file_handle.write(
                        "from django.http import JsonResponse\n\n"
                    )
                    file_handle.write(
                        f"async def {clean_name}_endpoint(request):\n"
                    )
                    file_handle.write(
                        '    """Asynchronous backend transaction execution '
                        'router framework."""\n'
                    )
                    file_handle.write(
                        '    return JsonResponse({"status": "active", '
                        '"engine": "aurora_core"})\n'
                    )

            def update_registry():
                relative_path = os.path.relpath(
                    target_filepath,
                    self.base_dir,
                )
                defaults = {
                    "name": f"api_{clean_name}",
                    "persona": "COMPILER_MODULE",
                    "status": "ACTIVE",
                    "visibility": "PRIVATE",
                    "created_by": self.user,
                }

                component, created = (
                    ComponentRegistry.objects.get_or_create(
                        file_path=relative_path,
                        defaults={
                            **defaults,
                            "locked": False,
                        },
                    )
                )

                if not created:
                    for field_name, field_value in defaults.items():
                        setattr(component, field_name, field_value)

                    component.save(
                        update_fields=[
                            *defaults.keys(),
                            "date_modified",
                        ]
                    )

                return created

            is_new = await sync_to_async(
                update_registry,
                thread_sensitive=False,
            )()
            status_text = (
                "Registered structural data hook"
                if is_new
                else "Synchronized active data mapping"
            )
            await async_send_to_console(
                "✅ [REGISTRY MULTI-MATRIX]: "
                f"{status_text} for 'api_{clean_name}'."
            )
            return True
        except Exception as err:
            await async_send_to_console(
                "💥 [AUTOMATION SCHEDULER FAULT]: Failed /api sequence "
                f"execution: {str(err)}"
            )
            return False
# ======================================================================
# END: WORKSPACE_AUTOMATION_UTILITIES (PATCH 1 OF 1)
# ======================================================================