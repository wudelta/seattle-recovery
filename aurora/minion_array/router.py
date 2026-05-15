import importlib
import os
from django.conf import settings

def dispatch_to_minion(worker_type, task_details, fallback_context=""):
    """
    Dynamically loads micro-minions and handles direct file-system writing.
    Expected task format from Wu: "create a button component | FILE: path/to/file.html"
    """
    print(f"📡 Dynamic routing task allocation mapping: minion_array.{worker_type}")
    
    # 1. Parse out the targeted file path if injected by Wu's brain
    target_file_path = ""
    clean_task_details = task_details
    
    if "| FILE:" in task_details:
        parts = task_details.split("| FILE:")
        clean_task_details = parts[0].strip()
        # Clean away stray brackets or spaces from the end
        target_file_path = parts[1].replace("]", "").strip()

    try:
        # 2. Dynamically mount the micro-worker module
        module_name = f"aurora.minion_array.{worker_type}"
        worker_module = importlib.import_module(module_name)
        raw_code = worker_module.run(clean_task_details, fallback_context).strip()
        
        # 3. Multi-pass string fence filtering
        while raw_code.startswith("```"):
            lines = raw_code.splitlines()
            if lines and lines[0].strip().startswith("```"):
                lines.pop(0)
            if lines and lines[-1].strip().startswith("```"):
                lines.pop()
            raw_code = "\n".join(lines).strip()
            
        if raw_code.endswith("```"):
            raw_code = raw_code[:-3].strip()
            
        # 4. DIRECT FILE WRITING INJECTION SAFETY INTERCEPT
        if target_file_path:
            # Anchor the file write to your physical Ubuntu laptop workspace root directory
            absolute_path = os.path.join(settings.BASE_DIR, target_file_path)
            
            # Ensure nested layout directories (like templates/) exist before writing
            os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
            
            with open(absolute_path, "w", encoding="utf-8") as f:
                f.write(raw_code)
                
            return f"💾 **System Action:** Code generated and written directly to local file path: `{target_file_path}`"
            
        return raw_code
        
    except ModuleNotFoundError:
        return f"<!-- Router Fault: The micro-worker task tracker '{worker_type}' does not exist inside minion_array. -->"
    except Exception as e:
        return f"<!-- Router Exception Tracker: Breakdown in {worker_type} loop execution context: {str(e)} -->"
