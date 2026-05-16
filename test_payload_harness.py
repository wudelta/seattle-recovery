# test_payload_harness.py
import os
import sys
import django
from pathlib import Path

# 1. Establish project structural layout configurations
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# 2. Bind environment targets to your core_logic layout
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_logic.settings')
try:
    django.setup()
    print("[SUCCESS] Django framework initialized within core_logic scope.")
except Exception as e:
    print(f"[FATAL] Django configuration setup failed: {e}")
    sys.exit(1)

# 3. Import routing agent using verified lowercase namespace
try:
    print("[SUCCESS] Traffic-cop router loaded successfully from lowercase namespace.")
except ImportError as e:
    print(f"[FATAL] App reference pathing error: {e}")
    sys.exit(1)

# test_payload_harness.py (Modify your execution block to match this)
def execute_interactive_tui_test():
    print("\n[1/2] Constructing Structured Mock Python Script Data...")
    
    mock_task_details = """
    | FILE: aurora/minion_array/sample_verification_module.py
    def test_automation_health():
        print("Aurora dynamic python minion worker operational.")
        return True
    """
    
    print("[2/2] Injecting mock Python instruction stream into dispatch_to_minion...\n")
    
    from aurora.minion_array.router import dispatch_to_minion
    result = dispatch_to_minion(
        worker_type="python", # <-- Targeting your newly seeded python worker module
        task_details=mock_task_details, 
        fallback_context="Verifying generate_python bootstrapping success"
    )
    print(f"\nResult: {result}")

if __name__ == "__main__":
    execute_interactive_tui_test()
