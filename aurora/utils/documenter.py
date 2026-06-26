# ======================================================================
# FILE: aurora/utils/documenter.py (PATCH 1 OF 1)
# START: BATCH_PAUSE_THROTTLED_DOCUMENTER_CRAWLER
# ======================================================================
import os
import sys
import asyncio
from django.conf import settings
from aurora.models import ComponentRegistry
from aurora.minions.engine import MinionRunner
from aurora.api.dev_streamer_api import async_send_to_console

class WorkspaceDocumenter:
    """
    Crawls active registered application modules from disk, passes code to the
    Groq fleet AI writer minion, and streams live telemetry to the browser console.
    """
    def __init__(self, runner=None):
        self.runner = runner or MinionRunner()

    async def log_async(self, message: str):
        """Streams tracing lines over real-time WebSockets and fallbacks cleanly to stdout."""
        print(message)
        try:
            await async_send_to_console(message)
        except Exception:
            pass

    def read_source_code(self, absolute_path: str) -> str:
        """Safely pulls code text files from disk straight into memory buffers."""
        if not os.path.exists(absolute_path):
            return ""
        try:
            with open(absolute_path, "r", encoding="utf-8") as file_stream:
                return file_stream.read()
        except Exception as err:
            print(f"⚠️ [FILE READ EXCEPTION] Path {absolute_path}: {str(err)}")
            return ""

    async def execute_documentation_sweep_async(self) -> dict:
        """
        FIXED: Uses Django's native async queryset evaluation loop (.all()) 
        to stream rows across Daphne thread layers safely without losing context.
        """
        report = {
            "processed_files": [],
            "skipped_files": [],
            "failures": []
        }
        
        # FIXED: Evaluate the queryset count using native async ORM methods (.acount)
        active_queryset = ComponentRegistry.objects.filter(status="ACTIVE")
        total_count = await active_queryset.acount()
        
        await self.log_async(f"🔎 [SWEEP START] Found {total_count} active components to evaluate.")
        
        processed_in_current_batch = 0
        current_index = 0
        
        # FIXED: Use 'async for' to streams rows asynchronously from PostgreSQL natively
        async for component in active_queryset:
            current_index += 1
            path = component.file_path
            await self.log_async(f"⚡ [{current_index}/{total_count}] Evaluating component '{component.name}' at path: {path}")
            
            audiences = component.description_audiences or {}
            if audiences.get("developer_docs") and audiences.get("stakeholder_docs") and component.description:
                await self.log_async(f"⏩ [SKIP] Complete documentation already exists for: {path}")
                report["skipped_files"].append(path)
                continue
                
            code_content = self.read_source_code(path)
            if not code_content:
                await self.log_async(f"❌ [FAILURE] Target file missing or empty on disk: {path}")
                report["failures"].append(path)
                continue
                
            try:
                await self.log_async(f"🤖 [AI RUN] Requesting developer_docs generation...")
                dev_prompt = f"Analyze this source code module and generate a detailed developer-oriented engineering architecture overview:\n\n{code_content}"
                dev_docs = self.runner.run_minion_task("minion_AI_writer", dev_prompt)
                
                await self.log_async(f"🤖 [AI RUN] Requesting stakeholder_docs generation...")
                stakeholder_prompt = f"Analyze this source code module and translate its utility into a clean business value overview for non-technical stakeholders:\n\n{code_content}"
                stakeholder_docs = self.runner.run_minion_task("minion_AI_writer", stakeholder_prompt)
                
                if "Error:" in dev_docs or "Error:" in stakeholder_docs:
                    await self.log_async(f"❌ [API FAULT] Engine execution returned an internal error state.")
                    report["failures"].append(path)
                    continue
                    
                await self.log_async(f"💾 [DB WRITE] Saving plain-text overview and rich documentation dictionaries...")
                component.description = f"Automated engineering profile for module {component.name} handling runtime codebase assets."
                
                # FIXED: Use native async save (.asave) to commit row columns safely
                component.description_audiences["developer_docs"] = dev_docs
                component.description_audiences["stakeholder_docs"] = stakeholder_docs
                await component.asave()
                
                await self.log_async(f"✅ [SUCCESS] Fields successfully committed for: {path}")
                report["processed_files"].append(path)
                
                processed_in_current_batch += 1
                if processed_in_current_batch >= 10 and current_index < total_count:
                    await self.log_async(f"\n⏳ [BATCH LIMIT REACHED] Processed {processed_in_current_batch} records in this slot.")
                    await self.log_async("⏸️ Pausing execution loop for 60 seconds to completely refresh your token rate limits...\n")
                    await asyncio.sleep(60)
                    processed_in_current_batch = 0
                    
            except Exception as loop_err:
                await self.log_async(f"💥 [CRASH] Fatal mutation failure on component loop: {str(loop_err)}")
                report["failures"].append(path)
                
        return report

    def clear_component_documentation(self, component) -> bool:
        """Utility maintenance helper to reset the JSON documentation fields for a targeted component row."""
        try:
            print(f"🧹 [DB clean] Wiping documentation fields for: {component.file_path}")
            component.description = ""
            component.description_audiences = {}
            component.save()
            return True
        except Exception as err:
            print(f"❌ [DB clean FAULT] Failed to clear component state: {str(err)}")
            return False
# ======================================================================
# END: BATCH_PAUSE_THROTTLED_DOCUMENTER_CRAWLER (PATCH 1 OF 1)
# ======================================================================
