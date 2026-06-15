# ======================================================================
# FILE: aurora/utils/documenter.py (PATCH 1 OF 1)
# START: BATCH_PAUSE_THROTTLED_DOCUMENTER_CRAWLER
# ======================================================================
import os
import sys
import time
from django.conf import settings
from aurora.models import ComponentRegistry
from aurora.minions.engine import MinionRunner

class WorkspaceDocumenter:
    """
    Crawls active registered application modules from disk, passes code to 
    the Groq fleet AI writer minion, and synchronizes the generated output.
    """
    def __init__(self, runner=None):
        self.runner = runner or MinionRunner()
        # Default fallback stream pointer to stdout if not overridden by the command bridge
        self.emit_log = lambda text: sys.stdout.write(text)

    def log(self, message: str):
        """Helper tool to cleanly format and broadcast tracking feeds."""
        self.emit_log(f"{message}\n")

    def get_active_components(self):
        """Fetches active workspace components tracked inside the PostgreSQL ledger."""
        return ComponentRegistry.objects.filter(status="ACTIVE")

    def read_source_code(self, absolute_path: str) -> str:
        """Safely pulls code text files from disk straight into memory buffers."""
        if not os.path.exists(absolute_path):
            return ""
        try:
            with open(absolute_path, "r", encoding="utf-8") as file_stream:
                return file_stream.read()
        except Exception as err:
            self.log(f"⚠️ [FILE READ EXCEPTION] Path {absolute_path}: {str(err)}")
            return ""

    def execute_documentation_sweep(self) -> dict:
        """
        Orchestrates the workspace crawl loop. Processes records in chunks of 10,
        pausing for 60 seconds between batches to respect Groq Cloud TPM caps.
        """
        report = {
            "processed_files": [],
            "skipped_files": [],
            "failures": []
        }
        
        active_components = self.get_active_components()
        total_count = active_components.count()
        self.log(f"🔎 [SWEEP START] Found {total_count} active components to evaluate.")

        processed_in_current_batch = 0
        current_index = 0

        for component in active_components:
            current_index += 1
            path = component.file_path
            self.log(f"⚡ [{current_index}/{total_count}] Evaluating component '{component.name}' at path: {path}")

            # 1. Optimization Check: Skip if both doc fields are already filled
            audiences = component.description_audiences or {}
            if audiences.get("developer_docs") and audiences.get("stakeholder_docs") and component.description:
                self.log(f"⏩ [SKIP] Complete documentation already exists for: {path}")
                report["skipped_files"].append(path)
                continue

            # 2. File Check: Read source module from disk path
            code_content = self.read_source_code(path)
            if not code_content:
                self.log(f"❌ [FAILURE] Target file missing or empty on disk: {path}")
                report["failures"].append(path)
                continue

            try:
                # 3. Audience Prompt Step 1: Technical Developer Context
                self.log(f"🤖 [AI RUN] Requesting developer_docs generation...")
                dev_prompt = f"Analyze this source code module and generate a detailed developer-oriented engineering architecture overview:\n\n{code_content}"
                dev_docs = self.runner.run_minion_task("minion_AI_writer", dev_prompt)
                
                # 4. Audience Prompt Step 2: Non-Technical Stakeholder Context
                self.log(f"🤖 [AI RUN] Requesting stakeholder_docs generation...")
                stakeholder_prompt = f"Analyze this source code module and translate its utility into a clean business value overview for non-technical stakeholders:\n\n{code_content}"
                stakeholder_docs = self.runner.run_minion_task("minion_AI_writer", stakeholder_prompt)

                # Validate execution error payloads from the underlying engine
                if "Error:" in dev_docs or "Error:" in stakeholder_docs:
                    self.log(f"❌ [API FAULT] Engine execution returned an internal error state.")
                    report["failures"].append(path)
                    continue

                # 5. Database Save State: Route text strings to respective model targets
                self.log(f"💾 [DB WRITE] Saving plain-text overview and rich documentation dictionaries...")
                component.description = f"Automated engineering profile for module {component.name} handling runtime codebase assets."
                component.update_audience_docs("developer_docs", dev_docs)
                component.update_audience_docs("stakeholder_docs", stakeholder_docs)
                
                self.log(f"✅ [SUCCESS] Fields successfully committed for: {path}")
                report["processed_files"].append(path)
                
                # 6. Batch Throttling Engine
                processed_in_current_batch += 1
                
                # If we processed 10 active files, and there are still more records remaining, pause
                if processed_in_current_batch >= 10 and current_index < total_count:
                    self.log(f"\n⏳ [BATCH LIMIT REACHED] Processed {processed_in_current_batch} records in this slot.")
                    self.log("⏸️ Pausing execution loop for 60 seconds to completely refresh your token rate limits...\n")
                    time.sleep(60)
                    processed_in_current_batch = 0 # Reset batch counter

            except Exception as loop_err:
                self.log(f"💥 [CRASH] Fatal mutation failure on component loop: {str(loop_err)}")
                report["failures"].append(path)

        return report

    def clear_component_documentation(self, component) -> bool:
        """
        Utility maintenance helper to reset the JSON documentation fields 
        for a targeted component row when forced updates are required.
        """
        try:
            self.log(f"🧹 [DB clean] Wiping documentation fields for: {component.file_path}")
            component.description = ""
            component.description_audiences = {}
            component.save()
            return True
        except Exception as err:
            self.log(f"❌ [DB clean FAULT] Failed to clear component state: {str(err)}")
            return False
# ======================================================================
# END: BATCH_PAUSE_THROTTLED_DOCUMENTER_CRAWLER
# ======================================================================
