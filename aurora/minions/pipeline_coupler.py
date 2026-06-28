# ======================================================================
# FILE: aurora/minions/pipeline_coupler.py (PATCH 1 OF 1)
# START: FLEET_PIPELINE_COUPLER_ENGINE
# ======================================================================
import os
import asyncio
from django.conf import settings
from asgiref.sync import sync_to_async
from aurora.models import ComponentRegistry
from aurora.minions.engine import MinionRunner
from aurora.api.dev_streamer_api import async_send_to_console

class FleetPipelineCoupler:
    """Orchestrates sequential task hand-offs across specialized 8B minions with safety gating."""

    def __init__(self, user, dry_run: bool = True):
        self.user = user
        self.runner = MinionRunner()
        self.base_dir = getattr(settings, "BASE_DIR", os.getcwd())
        # SAFETY PROTECTION: Inherit verification mode from the top-level orchestration gateway
        self.dry_run = dry_run

    async def run_ui_assembly_pipeline(self, target_app: str, page_name: str, layout_instructions: str):
        """
        Runs the 8B worker fleet in series. Pass-through variables capture the output from 
        upstream builders to constrain downstream presentation logic safely.
        """
        clean_page = page_name.strip().lower().replace(" ", "_")
        clean_app = target_app.strip().lower()
        template_rel_path = f"{clean_app}/templates/{clean_app}/{clean_page}.html"
        template_abs_path = os.path.join(self.base_dir, clean_app, "templates", clean_app, f"{clean_page}.html")

        # In a dry-run scenario, the base template file might not exist yet, which is safe.
        if not self.dry_run and not os.path.exists(template_abs_path):
            await async_send_to_console(f"❌ [PIPELINE FAULT] Base template container artifact missing from disk path: {template_abs_path}")
            return False

        # --- Phase 1: minion_UI_layout (HTML Building) ---
        await async_send_to_console("🏗️ [PIPELINE] Initializing Phase 1: Structural HTML Blueprint generation...")
        html_blueprint = ""
        # FIX: Delegated to the specific database worker profile instead of feeding into Wu recursively
        async for chunk in self.runner.run_minion_task_stream("minion_ui_layout", layout_instructions):
            html_blueprint += chunk

        # --- Phase 2: minion_UI_style (CSS Presentation) ---
        await async_send_to_console("🎨 [PIPELINE] Initializing Phase 2: Presentation CSS Class mapping...")
        css_constraints = f"HTML Skeleton Input Context:\n{html_blueprint}\n\nAesthetic Instructions:\n{layout_instructions}"
        css_payload = ""
        # FIX: Delegated to the specific database worker profile instead of feeding into Wu recursively
        async for chunk in self.runner.run_minion_task_stream("minion_ui_style", css_constraints):
            css_payload += chunk

        # --- Phase 3: minion_UI_logic (JavaScript Interactivity) ---
        await async_send_to_console("⚡ [PIPELINE] Initializing Phase 3: Frontend Script behavior synthesis...")
        js_constraints = f"HTML Blueprint:\n{html_blueprint}\n\nCSS Style classes:\n{css_payload}\n\nBehavior Prompts:\n{layout_instructions}"
        js_payload = ""
        # FIX: Delegated to the specific database worker profile instead of feeding into Wu recursively
        async for chunk in self.runner.run_minion_task_stream("minion_ui_logic", js_constraints):
            js_payload += chunk

        # --- Phase 4: Surgical File Merging and Assembly ---
        if self.dry_run:
            await async_send_to_console(f"🛡️ [DRY-RUN SIMULATION] Would merge code assets into target file template: '{template_abs_path}'")
            await async_send_to_console("🎉 [DRY-RUN SIMULATION] Assembly pipeline simulation completed successfully.")
            return True

        await async_send_to_console(f"💾 [PIPELINE] Injecting component artifacts to workspace target: {template_rel_path}")
        def merge_file_assets():
            with open(template_abs_path, "r") as f:
                content = f.read()

            injected_layout = (
                f"\n<!-- START: FORGED_UI_CONSOLE_CONTAINER -->\n"
                f"<style>\n{css_payload}\n</style>\n"
                f"<div class='container p-3 text-light'>\n{html_blueprint}\n</div>\n"
                f"<script>\n{js_payload}\n</script>\n"
                f"<!-- END: FORGED_UI_CONSOLE_CONTAINER -->\n"
            )

            if "<!-- START: FORGED_UI_CONSOLE_CONTAINER -->" in content:
                parts = content.split("<!-- START: FORGED_UI_CONSOLE_CONTAINER -->")
                tail = parts[1].split("<!-- END: FORGED_UI_CONSOLE_CONTAINER -->", 1)
                updated_content = parts[0] + injected_layout + tail[1]
            else:
                updated_content = content.replace("{% block content %}", f"{{% block content %}}{injected_layout}")

            with open(template_abs_path, "w") as f:
                f.write(updated_content)

        await sync_to_async(merge_file_assets, thread_sensitive=False)()
        await async_send_to_console("🎉 [PIPELINE SUCCESS] Component interface compilation sweep completed successfully.")
        return True
# ======================================================================
# END: FLEET_PIPELINE_COUPLER_ENGINE (PATCH 1 OF 1)
# ======================================================================
