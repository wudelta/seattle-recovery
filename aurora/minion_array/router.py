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
        # Split the second segment at the first newline to separate path from code
        path_line_split = parts[1].split("\n", 1)
        
        # Isolate the clean file path and remove stray brackets
        target_file_path = path_line_split[0].replace("]", "").strip()
        
        # The remaining text block is passed to the micro-minion
        if len(path_line_split) > 1:
            clean_task_details = path_line_split[1].strip()
        else:
            clean_task_details = ""

    try:
        # 2. Dynamically mount the micro-worker module
        # Open aurora/minion_array/router.py and modify line 24 to:
        module_name = f"aurora.minion_array.generate_{worker_type}"
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
