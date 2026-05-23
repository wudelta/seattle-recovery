import os
import json
import logging
import threading
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

# Consolidated Core Graph Logic Imports
from core_logic.memory import summarize_session
from core_logic.sessions import end_session

# Setup structured file and terminal logger
logger = logging.getLogger("aurora.sessions.close")
logger.setLevel(logging.DEBUG)


def asynchronous_git_pipeline(commit_msg, logger_instance):
    """
    Runs the automated Git staging, committing, and pushing operations
    on an isolated background thread to prevent Django server freezes.
    """
    print("\n🧵 [BACKGROUND THREAD] Asynchronous Git pipeline worker activated.")
    import subprocess
    
    try:
        # Step A: Stage all local modified modifications cleanly
        print("📁 [GIT WORKER] Staging changed repository assets via 'git add -A'...")
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
        
        # Step B: Check for actual changes waiting to be committed
        status_check = subprocess.run(["git", "diff", "--cached", "--quiet"])
        
        if status_check.returncode == 1:
            print(f"📝 [GIT WORKER] Code changes detected. Running commit: '{commit_msg}'")
            subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True)
            
            # Step C: Dispatch snapshot directly to GitHub
            print("📡 [GIT WORKER] Initializing upstream push to origin main (Network I/O bound)...")
            push_process = subprocess.run(["git", "push", "origin", "main"], check=True, capture_output=True, text=True)
            
            print("✅ [GIT WORKER] Upstream sync finalized successfully.")
            logger_instance.info("Background Git push to GitHub repository main completed cleanly.")
        else:
            print("ℹ️ [GIT WORKER] No local code modifications detected. Git push loop bypassed.")
            logger_instance.info("Git pipeline finalized: Zero new repository snapshot changes to sync.")
            
    except subprocess.CalledProcessError as git_err:
        err_output = git_err.stderr.strip() if git_err.stderr else str(git_err)
        print(f"❌ [GIT WORKER FAILURE] Subprocess error caught: {err_output}")
        logger_instance.error(f"Background Git pipeline operation fault: {err_output}")
    except Exception as general_err:
        print(f"❌ [GIT WORKER FAILURE] General background error: {str(general_err)}")
        logger_instance.critical(f"Unhandled systemic error inside Git worker thread: {str(general_err)}")
    print("🧵 [BACKGROUND THREAD] Worker thread terminated smoothly.\n")


@csrf_exempt
@login_required
@require_POST  # Pure decoupled API endpoints must restrict usage strictly to secure data transfers
def end_session_view(request):
    shutdown_time = timezone.now()
    print(f"\n🚀 [STOP SESSION] Termination sequence triggered at {shutdown_time.isoformat()}")
    logger.info("Evening shutdown sequence initiated.")
    
    user_id = request.user.username.lower()
    
    # Try to extract the session token from headless JSON or standard request metrics
    session_id = None
    try:
        if request.body:
            json_payload = json.loads(request.body)
            session_id = json_payload.get('session_id')
    except (json.JSONDecodeError, TypeError):
        pass
        
    if not session_id:
        session_id = request.session.get('current_session_id')

    print(f"--- MANUAL SHUTDOWN TRIPPED: CLEAN SWEEP FOR {user_id.upper()} ---")

    # --- 1. NEO4J SUMMARY GENERATION & BACKGROUND CLEANUP ---
    print("🔍 [STAGE 1] Triggering Neo4j Graph database summary node compilation...")
    try:
        summary_result = summarize_session(user_id)
        print("✅ [STAGE 1] Graph summary node compiled and raw chatter swept cleanly.")
    except Exception as graph_err:
        summary_result = f"Graph engine cleanup execution warning: {str(graph_err)}"
        print(f"⚠️ [STAGE 1 WARNING] Neo4j graph interaction bypassed: {str(graph_err)}")
        logger.warning(f"Database graph engine tracking variance: {str(graph_err)}")

    # --- 2. UPDATE POSTGRESQL SESSION DURATION ---
    print("🔍 [STAGE 2] Calculating PostgreSQL session tracking durations...")
    duration = 0
    if session_id:
        try:
            duration = end_session(session_id)
            if 'current_session_id' in request.session:
                del request.session['current_session_id']
            print(f"⏱️ [STAGE 2] PostgreSQL duration closed. Active running time: {duration} seconds.")
        except Exception as sql_err:
            print(f"❌ [STAGE 2 CRASH] PostgreSQL tracking breakdown: {str(sql_err)}")
            logger.error(f"SQL duration processing anomaly: {str(sql_err)}")
    else:
        duration = "No active SQL session found. Cleaned graph state anyway."
        print("ℹ️ [STAGE 2 INFO] Missing active SQL token. Skipping duration calculations.")

    # --- 3. DISPATCH OFF-THREAD BACKGROUND SOURCE PROTECTION PIPELINE ---
    print("🔍 [STAGE 3] Spawning safe background thread for Git automation pipeline...")
    commit_msg = f"chore(session): automated save-point for session run {shutdown_time.strftime('%Y-%m-%d')}"
    
    # Create and fire the safe off-thread background process worker loop
    git_thread = threading.Thread(
        target=asynchronous_git_pipeline,
        args=(commit_msg, logger),
        daemon=True # Daemon status ensures the thread won't keep Django alive if the server stops
    )
    git_thread.start()
    print("✅ [STAGE 3] Background thread detached. Moving cleanly to transaction finalization.")

    # --- 4. FORMULATE PURE DATA JSON CONTRACT PACKAGES ---
    print("🏁 [FINALIZE] Headless shutdown transaction compiled. Dispatching data payload down pipeline.\n")
    return JsonResponse({
        'status': 'success',
        'session_status': 'closed',
        'duration': duration,
        'summary': summary_result,
        'git_pipeline_status': 'Asynchronous operations detached and running safely in background.'
    })


def execute_baseline_sanity_checks(module_instance, ui_logs) -> tuple[bool, str]:
    print("🤖 [execute_baseline_sanity_checks] Action triggered.")
    """Runs structural, security, and functional self-test hooks while compiling logs for the UI."""
    try:
        module_dir = dir(module_instance)
        if not module_dir or len([attr for attr in module_dir if not attr.startswith('__')]) == 0:
            ui_logs.append("❌ Validation Error: Module contains no active functions or classes.")
            return False, "Empty module payload."

        module_source_dict = str(module_instance.__dict__)
        forbidden_keywords = ["os.system(", "subprocess.Popen(", "eval("]
        for keyword in forbidden_keywords:
            if keyword in module_source_dict:
                ui_logs.append(f"❌ Security Violation: Unauthorized system execution hook found: '{keyword}'.")
                return False, f"Security hazard: {keyword}"
        ui_logs.append("⚙️ Security scan passed: No hazardous system hooks detected.")

        if hasattr(module_instance, "self_test_integrity"):
            ui_logs.append("⚙️ Located 'self_test_integrity' hook. Invoking verification routine...")
            test_passed = module_instance.self_test_integrity()
            if not test_passed:
                ui_logs.append("❌ Functional Failure: Module self_test_integrity returned False.")
                return False, "Self-test method failed."
            ui_logs.append("✅ Success: Module 'self_test_integrity' returned True.")
        else:
            ui_logs.append("⚠️ Warning: No 'self_test_integrity' hook found. Basic structure validation only.")
        return True, "Passed all checks."
    except Exception as err:
        ui_logs.append(f"❌ Sandbox Exception: Runtime error during validation pass: {str(err)}")
        return False, str(err)
