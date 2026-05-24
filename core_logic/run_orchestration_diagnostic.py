import time
from console_visualizer import AuroraTerminalConsole
from minion_runner import MinionAutomationEngine

def execute_integrated_diagnostic_pipeline():
    """
    Binds Phase 1 Dashboard Visuals to Phase 2 Minion Subprocess Executions.
    Displays dynamic terminal updates as code verification sweeps run.
    """
    console = AuroraTerminalConsole()
    minion = MinionAutomationEngine()

    # 1. Establish Initialization Metrics Dashboard State
    metrics = {
        "user_id": "delta",
        "session_duration": "0m 02s",
        "postgres_status": "ONLINE (MOCK_TEST_DB)",
        "neo4j_nodes": 5,
        "prompt_tokens": 12500,     # Simulating typical high-density context limits
        "completion_tokens": 1100,
        "token_limit": 14400
    }

    task_state = {
        "target": "aurora.tests.test_session_close_api",
        "phase": "LAUNCHING SYSTEM TEST SUBPROCESS SUB-MATRIX",
        "status": "📡 DETACHING TERMINAL WORKER SCRIPT..."
    }

    # Render starting setup layout
    console.render_dashboard(metrics, task_state)
    time.sleep(1.0)

    # 2. Update Console Display for Active Subprocess Step
    task_state["phase"] = "STAGE 3: Running background django.test.TestCase validations"
    task_state["status"] = "⏳ RUNNING REVERSE PATH LOOKUPS (TEST_RUNNER PIPELINE)..."
    console.render_dashboard(metrics, task_state)

    # 3. Fire the Live Subprocess Execution Core
    success, summary, trace_log = minion.run_automated_test_suite("aurora.tests.test_session_close_api")

    # 4. Parse Results and Render Final Systems State Display
    metrics["session_duration"] = "0m 05s"
    metrics["neo4j_nodes"] = 6  # Simulating system log increment
    
    if success:
        task_state["status"] = f"✅ SUCCESS: {summary}"
    else:
        task_state["status"] = f"❌ CRASH FAULT TRACE CAUGHT: {summary}"

    console.render_dashboard(metrics, task_state)

    # Output detailed trace output logging blocks directly underneath the scannable dashboard
    print("📝 --- DETAILED ENGINE SUBPROCESS OUTPUT TRACE ---")
    # Display the final 15 lines of the trace output log matrix to save terminal vertical space
    trace_lines = [line for line in trace_log.split("\n") if line.strip()]
    for line in trace_lines[-15:]:
        print(f"   {line}")
    print("="*65 + "\n")

if __name__ == "__main__":
    execute_integrated_diagnostic_pipeline()
