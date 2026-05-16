# test_mem0_hybrid.py
import os
import sys
import django

sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_logic.settings')
django.setup()

# Target the consolidated memory controller module
from core_logic.memory import IsolatedMemoryEngine

def execute_hybrid_test_sweep():
    print("📡 Launching Consolidated Mem0 Gemini Connectivity Audit...")
    try:
        engine = IsolatedMemoryEngine()
        
        print("\n[1/2] Injecting structural milestone to vector space...")
        test_fact = "The router entry point function signature is explicitly named dispatch_to_minion"
        result = engine.store_development_fact(user_id="delta", text=test_fact, project_scope="aurora")
        print(f"✔ Transaction Response logged: {result}")
        
        print("\n[2/2] Running semantic proximity query check...")
        retrieved_context = engine.search_relevant_context(user_id="delta", query="What is the router function named?")
        print(f"✔ Retrieved Data Node Matrix:\n{retrieved_context}")
    except Exception as e:
        print(f"\n❌ SWEEP CONFIGURATION CRASH: {str(e)}")

if __name__ == "__main__":
    execute_hybrid_test_sweep()
