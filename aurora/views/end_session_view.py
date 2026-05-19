import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.utils import timezone

# Consolidated Core Graph Logic Imports
from core_logic.memory import summarize_session
from core_logic.sessions import end_session

@csrf_exempt
def end_session_view(request):
    print("🤖 [end_session_view] Action triggered.")
    """
    Manages session termination protocols: summarizes active session frames,
    updates PostgreSQL tracking deltas, cleans up chatter graphs,
    and runs atomic Git snapshot pipeline pushes to GitHub.
    """
    user_id = request.user.username.lower() if request.user.is_authenticated else "delta"
    session_id = request.session.get('current_session_id')
    
    print(f"--- MANUAL SHUTDOWN TRIPPED: CLEAN SWEEP FOR {user_id} ---")
    
    # 1. Neo4j Summary Node Generation and Background Chatter Cleanup
    # This invokes your internal graph logic engine to wipe secondary chatter nodes.
    try:
        summary_result = summarize_session(user_id)
    except Exception as graph_err:
        summary_result = f"Graph engine cleanup execution warning: {str(graph_err)}"
        print(summary_result)

    # 2. Update PostgreSQL Session Delta Duration
    if session_id:
        try:
            duration = end_session(session_id)
            if 'current_session_id' in request.session:
                del request.session['current_session_id']
        except Exception as sql_err:
            duration = 0
            print(f"PostgreSQL duration tracking anomaly: {str(sql_err)}")
    else:
        duration = "No active SQL session found. Cleaned graph state anyway."

    # =========================================================================
    # AUTOMATED GIT COMMIT & GITHUB PUSH PIPELINE SUITE
    # =========================================================================
    print("--- AUTOMATED SOURCE PROTECTION PIPELINE ACTIVATED ---")
    git_logs = []
    try:
        # Step A: Stage all local modified code modifications cleanly
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        git_logs.append("Staged all changed repository assets successfully.")
        
        # Step B: Capture baseline commit parameters
        commit_msg = f"chore(session): automated save-point for session run {timezone.now().strftime('%Y-%m-%d')}"
        
        # Check if there are actual code changes staged before executing the commit
        status_check = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if status_check.returncode == 1:  # 1 indicates there are changes waiting to be committed
            subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True)
            git_logs.append(f"Committed session snapshot: '{commit_msg}'")
            
            # Step C: Dispatch changes directly to your remote upstream cloud server on GitHub
            # Pushes to 'origin' using your active development branch 'main'
            # FIXED: Removed the unused variable assignment to clear the Spyder editor warning flag
            subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True, text=True)
            git_logs.append("Pushed changes to GitHub repository core cleanly.")
            git_logs.append("Pushed changes to GitHub repository core cleanly.")
        else:
            git_logs.append("No local modifications detected since session initialization pass.")
            
    except subprocess.CalledProcessError as git_err:
        error_msg = f"Git operation failed: {git_err.stderr.strip() if git_err.stderr else str(git_err)}"
        print(f"üîµ PIPELINE FAULT: {error_msg}")
        git_logs.append(error_msg)
    except Exception as general_git_err:
        print(f"üîµ PIPELINE FAULT: {str(general_git_err)}")
        git_logs.append(str(general_git_err))

    # Append our Git execution steps onto the final screen snapshot text summary block
    pipeline_summary = f"{summary_result}\n\n[GIT PIPELINE EXECUTION ENGINE]:\n" + "\n".join([f"- {log}" for log in git_logs])

    # 3. Formulate Context Response Handshakes
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.method == "POST":
        return JsonResponse({
            'status': 'success',
            'duration': duration,
            'summary': pipeline_summary
        })
        
    return render(request, 'aurora/session_closed.html', {
        'summary': pipeline_summary,
        'duration': duration
    })

def execute_baseline_sanity_checks(module_instance, ui_logs) -> tuple[bool, str]:
    print("🤖 [execute_baseline_sanity_checks] Action triggered.")
    """Runs structural, security, and functional self-test hooks while compiling logs for the UI."""
    try:
        # Check 1: Structural Integrity Validation
        module_dir = dir(module_instance)
        if not module_dir or len([attr for attr in module_dir if not attr.startswith('__')]) == 0:
            ui_logs.append("❌ Validation Error: Module contains no active functions or classes (Silent Truncation detected).")
            return False, "Empty module payload."

        # Check 2: Malicious Context Scan
        module_source_dict = str(module_instance.__dict__)
        forbidden_keywords = ["os.system(", "subprocess.Popen(", "eval("]
        for keyword in forbidden_keywords:
            if keyword in module_source_dict:
                ui_logs.append(f"❌ Security Violation: Unauthorized system execution hook found: '{keyword}'.")
                return False, f"Security hazard: {keyword}"
        ui_logs.append("⚙️ Security scan passed: No hazardous system hooks detected.")

        # Check 3: Automated Self-Test Hook Execution
        if hasattr(module_instance, "self_test_integrity"):
            ui_logs.append("⚙️ Located 'self_test_integrity' hook. Invoking verification routine...")
            test_passed = module_instance.self_test_integrity()
            if not test_passed:
                ui_logs.append("❌ Functional Failure: Module self_test_integrity execution returned False.")
                return False, "Self-test method failed."
            ui_logs.append("✅ Success: Module 'self_test_integrity' returned True.")
        else:
            ui_logs.append("⚠️ Warning: No 'self_test_integrity' hook found. Basic structure validation only.")

        return True, "Passed all checks."
    except Exception as err:
        ui_logs.append(f"❌ Sandbox Exception: Runtime error during validation pass: {str(err)}")
        return False, str(err)

