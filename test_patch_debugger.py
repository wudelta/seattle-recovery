import traceback
import sys
import os

# Ensure Django environment path is loaded for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core_logic.settings")

import django
django.setup()

from aurora.minion_array.router import dispatch_to_minion

def broken_function():
    """This function is mathematically broken and will crash."""
    numerator = 100
    denominator = 0  # Intentionally breaking this logic
    result = numerator / denominator
    return result

if __name__ == "__main__":
    print("🚀 Triggering simulated code crash matrix...")
    
    try:
        broken_function()
    except ZeroDivisionError as err:
        print("💥 Crash intercepted! Capturing terminal tracebacks...")
        
        # 1. Capture the raw string of the error traceback
        tb_lines = traceback.format_exception(type(err), err, err.__traceback__)
        raw_traceback = "".join(tb_lines)
        
        # 2. Read the file context of this script to give the minion code context
        with open(__file__, "r", encoding="utf-8") as f:
            script_source_code = f.read()
            
        print("📡 Dispatching traceback parameters directly to patch_debugger minion...")
        
        # 3. Fire the micro-worker through your dynamic dynamic router
        corrected_code_patch = dispatch_to_minion(
            worker_type="patch_debugger",
            task_details=raw_traceback,
            fallback_context=script_source_code
        )
        
        print("\n🤖 === MINION PATCH REPAIR RECEIVED ===")
        print(corrected_code_patch)
        print("========================================\n")
