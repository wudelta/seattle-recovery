import os
import json
import shutil
import logging
import re
from groq import Groq  

# Ensure local .env file loads explicitly into environment memory matrices
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.getcwd(), '.env'))
except ImportError:
    pass

from core_logic.minion_runner import MinionAutomationEngine  

logger = logging.getLogger("aurora.minion_patcher")

class SafeMinionPatcher:
    """
    Self-Correcting Execution Patcher for Project Aurora.
    Guarantees zero-byte file protection and automated loop self-healing.
    """
    def __init__(self):
        self.runner = MinionAutomationEngine()
        self.max_attempts = 3

    def commit_safe_patch(self, target_file_path, updated_code_payload, test_app_namespace=None):
        """
        Executes a sandboxed atomic code replacement pass with automated self-healing.
        Guarantees that broken code or crashes will never truncate files on disk.
        """
        print(f"\n🛡️ [SAFE PATCHER] Initiating transaction verification for: {os.path.basename(target_file_path)}")
        
        if not os.path.exists(target_file_path):
            print(f"❌ [STAGE 2 CRASH] Targeted file string path does not exist: {target_file_path}")
            return False

        # --- GUARDRAIL 1: PRE-FLIGHT LENGTH INTERCEPT ---
        if not updated_code_payload or len(updated_code_payload.strip()) == 0:
            print("❌ [STAGE 2 BLOCK] Prevented a silent truncation crash. Input payload is empty. Target file untouched.")
            return False

        with open(target_file_path, 'r', encoding='utf-8') as f:
            original_code = f.read()

        # Alert if the payload drops more than 50% of the file's size unexpectedly
        if len(updated_code_payload) < (len(original_code) * 0.5):
            print("⚠️ [STAGE 2 WARNING] Payload size anomaly detected (significantly smaller than original file).")
            confirm = input("Confirm this reduction is intentional? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ [STAGE 2 BLOCK] File modification aborted by human operator.")
                return False

        # --- GUARDRAIL 2: SANDBOXED STAGING (.TMP WRITE) ---
        tmp_file_path = target_file_path + ".tmp"
        backup_file_path = target_file_path + ".bak"
        
        try:
            # Write out to a temporary sandbox path file first
            with open(tmp_file_path, 'w', encoding='utf-8') as f:
                f.write(updated_code_payload)
            print("✅ [STAGE 2] Sandboxed temporary staging file written to disk matrix.")

            # Create a rapid restore backup image of your current good code file
            shutil.copy2(target_file_path, backup_file_path)

            # Atomic Swap into production track for terminal testing run execution passes
            shutil.move(tmp_file_path, target_file_path)

            # --- GUARDRAIL 3: AUTOMATED TESTING & SELF-CORRECTION LOOP ---
            attempt = 1
            while attempt <= self.max_attempts:
                print(f"🔍 [STAGE 3] Running verification pass (Attempt {attempt}/{self.max_attempts})...")
                
                # Execute your terminal test framework framework cleanly
                success, error_summary, full_trace = self.runner.run_automated_test_suite(test_app_namespace)
                
                if success:
                    print(f"✅ [STAGE 3 SUCCESS] Integration test passed. Removing backup file matrices.")
                    if os.path.exists(backup_file_path):
                        os.remove(backup_file_path)
                    return True
                else:
                    print(f"❌ [STAGE 3 FAIL] Test failed on attempt {attempt}: {error_summary}")
                    
                    if attempt < self.max_attempts:
                        print("🔄 [STAGE 3] Dispatching error trace back to Minion model for self-correction...")
                        # FIXED: Activating live 8B API loop to self-heal code errors on the fly
                        updated_code_payload = self.invoke_8b_self_healing_routine(target_file_path, full_trace)
                        
                        if updated_code_payload:
                            with open(target_file_path, 'w', encoding='utf-8') as f:
                                f.write(updated_code_payload)
                            attempt += 1
                            continue
                    
                    # Final attempt reached with failures. Execute absolute safety rollback sequence.
                    print("💥 [CRITICAL FAILURE] Self-correction limits exceeded. Triggering rollback...")
                    shutil.move(backup_file_path, target_file_path)
                    print("⏪ [ROLLBACK COMPLETE] Original code file has been restored to its previous intact state.")
                    return False

        except Exception as err:
            print(f"❌ [SYSTEM EXCEPTION] Error caught mid-transaction: {str(err)}")
            # Fail-Safe: Absolute restore recovery tracking pass
            if os.path.exists(backup_file_path):
                shutil.move(backup_file_path, target_file_path)
                print("⏪ Fail-safe recovery activated. Original file restored safely.")
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
            return False

    def invoke_8b_self_healing_routine(self, file_path, stack_trace):
        """
        Triggers an immediate single-turn Groq call passing the faulty code + error trace log.
        Returns a cleaned python string block containing the proposed fix.
        """
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            print("❌ [HEALING FAIL] Missing GROQ_API_KEY environment variable. Cannot auto-heal.")
            return None

        # Read what the current broken file looks like on disk
        with open(file_path, 'r', encoding='utf-8') as f:
            faulty_code = f.read()

        system_instruction = (
            "You are a precise, headless code debugging utility. Your task is to fix a python file that "
            "is causing a Django unit test failure. Read the provided faulty code and the exact terminal "
            "trace error log. Output the complete, fixed script. You must never generate conversational "
            "chatter, introductory remarks, markdown text descriptions, or Human-centric filler notes. "
            "Only return raw, executable Python code."
        )

        user_content = (
            f"=== TARGET FILE: {os.path.basename(file_path)} ===\n"
            f"{faulty_code}\n\n"
            f"=== TERMINAL STDOUT/STDERR TRACEBACK ===\n"
            f"{stack_trace}\n"
        )

        try:
            client = Groq(api_key=api_key)
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_content}
                ],
                model="llama3-8b-8192",  # Using the rapid 8B track
                temperature=0.0,         # Absolute lowest temp for deterministic code compilation
                max_tokens=2500
            )
            
            raw_output = chat_completion.choices.message.content.strip()
            
            # Defensive clean block parsing: strip out markdown code wrappers if the model injected them
            if raw_output.startswith("```python"):
                raw_output = raw_output.split("```python", 1)[1].rsplit("```", 1)[0].strip()
            elif raw_output.startswith("```"):
                raw_output = raw_output.split("```", 1)[1].rsplit("```", 1)[0].strip()
                
            return raw_output

        except Exception as model_err:
            print(f"❌ [HEALING FAULT] Groq API interaction failed during self-correction: {str(model_err)}")
            return None
