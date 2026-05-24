import os
import subprocess
import sys
import logging

logger = logging.getLogger("aurora.minion_runner")
logger.setLevel(logging.DEBUG)

class MinionAutomationEngine:
    """
    Mechanical Layer Worker Engine for Project Aurora.
    Executes terminal tests, parses output traces, and isolates runtime crashes.
    """
    def __init__(self):
        self.test_command = ["python", "manage.py", "test"]

    def run_automated_test_suite(self, target_app=None):
        """
        Executes the Django test framework within an isolated terminal subprocess.
        Captures and parses stdout/stderr to find failure points [STAGE 3].
        """
        command = list(self.test_command)
        if target_app:
            command.append(target_app)
            print(f"\n⚙️ [MINION WORKER] Targeting specific app matrix tests: {target_app}")
        else:
            print("\n⚙️ [MINION WORKER] Triggering full system test suite verification pass...")

        try:
            # Force target environment profile flag for safety guardrails
            env_matrix = os.environ.copy()
            env_matrix["DJANGO_TEST_ENVIRONMENT"] = "true"

            # Execute terminal test pipeline cleanly
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                env=env_matrix,
                check=False  # Do not crash the parent thread if tests fail
            )

            stdout_data = result.stdout
            stderr_data = result.stderr
            combined_trace = stdout_data + "\n" + stderr_data

            # Analyze output metrics
            if result.returncode == 0:
                print("✅ [MINION WORKER] Test suite executed with zero compilation or runtime errors.")
                return True, "ALL TESTS PASSED CLEANLY", combined_trace
            else:
                print("❌ [MINION WORKER CRASH] Structural anomaly intercepted inside the testing sequence.")
                # Extract the final lines of the traceback block to pinpoint the error
                error_lines = [line for line in combined_trace.split('\n') if line.strip()]
                summary_error = error_lines[-1] if error_lines else "Unknown Subprocess Exception"
                return False, f"TEST FAILURE: {summary_error}", combined_trace

        except Exception as system_err:
            print(f"❌ [MINION CRITICAL] Subprocess engine thread broke: {str(system_err)}")
            return False, f"System Execution Error: {str(system_err)}", ""

    def apply_regex_patch(self, file_path, search_string, replace_string):
        """
        Performs explicit string-replacement operations directly on disk [STAGE 1].
        Requires strict sanity checks to safeguard files against zero-byte truncation.
        """
        print(f"🔍 [MINION WORKER] Targeting file modification matrix: {file_path}")
        if not os.path.exists(file_path):
            print(f"❌ [MINION CRITICAL] Targeted file path string missing: {file_path}")
            return False

        try:
            # Step 1: Read incoming file state safely
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            if search_string not in original_content:
                print("⚠️ [MINION WORKER] Target pattern missing from source code. Skipping patch.")
                return False

            # Step 2: Calculate target modification changes
            modified_content = original_content.replace(search_string, replace_string)

            # Step 3: Enforce strict safety sanity check steps before writing to disk
            if len(modified_content) == 0 and len(original_content) > 0:
                print("❌ [MINION CRITICAL] Sanity Check Failed: Prevented a silent truncation crash.")
                return False

            # Step 4: Commit modifications to the disk partition
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
                
            print(f"✅ [MINION WORKER] File update finalized. Written {len(modified_content)} characters safely.")
            return True

        except Exception as write_err:
            print(f"❌ [MINION CRITICAL] Safe storage write execution failed: {str(write_err)}")
            return False

if __name__ == "__main__":
    # Test script initialization loop to inspect display behavior locally
    runner = MinionAutomationEngine()
    success, summary, full_trace = runner.run_automated_test_suite("aurora.tests.test_session_close_api")
    print(f"\n📊 Extraction Result Code: {success}")
    print(f"📝 Summary Metric Line   : {summary}")
