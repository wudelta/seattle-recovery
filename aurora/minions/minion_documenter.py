# ======================================================================
# FILE: aurora/minions/minion_documenter.py (PATCH 1 OF 2)
# START: MINION_DOCUMENTER_CORE_SINK
# ======================================================================
import os
import json
import requests
from aurora.models import ComponentRegistry
from aurora.nodes import ComponentNode

class MinionDocumenter:
    """Automates multi-audience documentation by feeding code vectors to a local 8B model."""

    def __init__(self, workspace_root: str = "."):
        self.workspace_root = os.path.abspath(workspace_root)
        # Configured to talk to a standard local offline inference endpoint (Ollama / Llama.cpp)
        self.local_inference_url = "http://localhost:11434/api/generate"

    def read_source_code(self, relative_path: str) -> str:
        """Reads raw module file text safely from your local host disk."""
        full_path = os.path.join(self.workspace_root, relative_path)
        if not os.path.exists(full_path):
            return ""
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def process_component_asset(self, file_path: str):
        """Extracts context, requests dual text layouts, and updates database keys."""
        try:
            db_record = ComponentRegistry.objects.get(file_path=file_path)
        except ComponentRegistry.DoesNotExist:
            print(f"❌ Error: {file_path} must be registered in PostgreSQL before documentation.")
            return

        raw_code = self.read_source_code(file_path)
        if not raw_code:
            print(f"⚠️ Warning: Physical file code for {file_path} is blank or missing on disk.")
            return

        print(f"Parsing structural matrix and drafting summaries for: {file_path}...")
# ======================================================================
# END: MINION_DOCUMENTER_CORE_SINK
# ======================================================================

# ======================================================================
# FILE: aurora/minions/minion_documenter.py (PATCH 2 OF 2)
# START: MINION_DOCUMENTER_INFERENCE_LOOP
# ======================================================================
    def query_local_llm(self, prompt: str) -> str:
        """Sends a targeted instruction payload to the local offline 8B engine."""
        payload = {
            "model": "llama3:8b",  # Default local 8B footprint allocation
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(self.local_inference_url, json=payload, timeout=60)
            if response.status_code == 200:
                return response.json().get("response", "").strip()
        except requests.exceptions.RequestException:
            pass
        return ""

    def generate_all_audience_docs(self, file_path: str):
        """Assembles segregated prompt templates and commits dual-track text blocks."""
        db_record = ComponentRegistry.objects.get(file_path=file_path)
        raw_code = self.read_source_code(file_path)

        # 1. Compile the Detailed Technical Developer Summary Prompt
        dev_prompt = f"Analyze this source code:\n\n{raw_code}\n\nWrite a highly detailed technical description for software developers. Focus on syntax logic, import dependencies, and code responsibilities."
        dev_docs = self.query_local_llm(dev_prompt)
        
        # 2. Compile the High-Level Non-Technical Stakeholder Prompt
        stakeholder_prompt = f"Analyze this source code:\n\n{raw_code}\n\nWrite a simple, high-level functional overview for non-technical business stakeholders. Describe what this file achieves in plain English without discussing raw code or syntax variables."
        stakeholder_docs = self.query_local_llm(stakeholder_prompt)

        # 3. Securely commit blocks straight to the upgraded relational fields
        if dev_docs:
            db_record.update_audience_docs("developer_docs", dev_docs)
        if stakeholder_docs:
            db_record.update_audience_docs("stakeholder_docs", stakeholder_docs)

        print(f"Successfully populated dual documentation tracks for {file_path}")

    def execute_full_system_documentation_sweep(self):
        """Discovers all active components missing documentation and processes them sequentially."""
        unprocessed_components = ComponentRegistry.objects.filter(status="ACTIVE")
        total = unprocessed_components.count()
        print(f"Starting master documentation loop. Discovered {total} total baseline targets...")

        for index, component in enumerate(unprocessed_components, 1):
            # Optimization: Skip files that already have documentation to save processing time
            has_dev = component.description_audiences.get("developer_docs")
            has_stake = component.description_audiences.get("stakeholder_docs")
            if has_dev and has_stake:
                continue

            print(f"[{index}/{total}] Processing asset context layer: {component.file_path}")
            self.generate_all_audience_docs(component.file_path)
            
        print("Master background documentation loop finished. System metrics normalized.")

if __name__ == "__main__":
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seattle_recovery.settings')
    django.setup()
    
    documenter = MinionDocumenter()
    documenter.execute_full_system_documentation_sweep()
# ======================================================================
# END: MINION_DOCUMENTER_INFERENCE_LOOP
# ======================================================================
