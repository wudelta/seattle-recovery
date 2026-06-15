# ======================================================================
# FILE: aurora/utils/documenter.py (PATCH 1 OF 2)
# START: WORKSPACE_CRAWLER_INITIALIZATION_AND_DISK_READER
# ======================================================================
import os
import sys
from aurora.models import ComponentRegistry
from aurora.minions.engine import MinionRunner

class WorkspaceDocumenter:
    """
    Crawls active registered project components, extracts raw source contents, 
    and leverages the data-driven MinionRunner engine to generate multi-audience documentation.
    """

    def __init__(self, workspace_root: str = "."):
        self.workspace_root = os.path.abspath(workspace_root)
        self.runner = MinionRunner()

    def read_source_code(self, relative_path: str) -> str:
        """Safely extracts raw source text from the physical filesystem disk track."""
        full_path = os.path.join(self.workspace_root, relative_path)
        if not os.path.exists(full_path):
            sys.stderr.write(f"[DOCUMENTER WARNING] File target missing from disk: {relative_path}\n")
            return ""
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as read_err:
            sys.stderr.write(f"[DOCUMENTER ERROR] Critical file read failure on {relative_path}: {str(read_err)}\n")
            return ""
# ======================================================================
# END: WORKSPACE_CRAWLER_INITIALIZATION_AND_DISK_READER (PATCH 1 OF 2)
# ======================================================================

# ======================================================================
# FILE: aurora/utils/documenter.py (PATCH 2 OF 2)
# START: CRAWLER_INFERENCE_LOOP_AND_RELATIONAL_WRITER
# ======================================================================
    def execute_documentation_sweep(self) -> dict:
        """
        Discovers all active registered components, filters out fully 
        documented tracks, and processes targets via the AI writer minion.
        """
        unprocessed_components = ComponentRegistry.objects.filter(status="ACTIVE")
        report = {"processed_files": [], "skipped_files": [], "failures": []}

        for component in unprocessed_components:
            # Optimization: Skip files that already possess complete dual-track descriptions
            has_dev = component.description_audiences.get("developer_docs") if isinstance(component.description_audiences, dict) else None
            has_stake = component.description_audiences.get("stakeholder_docs") if isinstance(component.description_audiences, dict) else None
            
            if has_dev and has_stake:
                report["skipped_files"].append(component.file_path)
                continue

            raw_code = self.read_source_code(component.file_path)
            if not raw_code:
                report["failures"].append(f"{component.file_path} (Empty/Missing)")
                continue

            # 1. Compile Detailed Technical Developer Prompt
            dev_prompt = (
                f"Analyze this source code module text:\n\n{raw_code}\n\n"
                f"Write a highly detailed technical description for software developers. "
                f"Focus on syntax logic, import dependencies, and operational responsibilities."
            )
            dev_docs = self.runner.run_minion_task("minion_AI_writer", dev_prompt)

            # 2. Compile High-Level Non-Technical Stakeholder Prompt
            stakeholder_prompt = (
                f"Analyze this source code module text:\n\n{raw_code}\n\n"
                f"Write a simple, high-level functional overview for non-technical business stakeholders. "
                f"Describe what this file achieves in plain English without discussing raw syntax or variables."
            )
            stakeholder_docs = self.runner.run_minion_task("minion_AI_writer", stakeholder_prompt)

            # 3. Securely commit blocks directly to the relational fields
            if dev_docs and "Error:" not in dev_docs:
                component.update_audience_docs("developer_docs", dev_docs)
            if stakeholder_docs and "Error:" not in stakeholder_docs:
                component.update_audience_docs("stakeholder_docs", stakeholder_docs)

            report["processed_files"].append(component.file_path)

        return report

# Standalone execution hook wrapper layer
if __name__ == "__main__":
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_logic.settings')
    django.setup()
    
    print("🤖 [DOCUMENTER] Initializing automated workspace documentation sweep...")
    documenter = WorkspaceDocumenter()
    sweep_report = documenter.execute_documentation_sweep()
    print(f"📊 [SWEEP COMPLETE] Processed: {len(sweep_report['processed_files'])} | Skipped: {len(sweep_report['skipped_files'])} | Faults: {len(sweep_report['failures'])}")
# ======================================================================
# END: CRAWLER_INFERENCE_LOOP_AND_RELATIONAL_WRITER (PATCH 2 OF 2)
# ======================================================================
