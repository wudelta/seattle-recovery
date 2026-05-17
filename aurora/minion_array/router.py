# FILE: aurora/router.py
"""
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T20:22:45.554642+00:00
 PROJECT ECOSYSTEM: AURORA
 FILE PATH: aurora/minion_array/router.py
 TECHNICAL MATRIX: Python Module. Exported Logic Components: dispatch_to_minion, render_terminal_monitor

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[router.py] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[AURORA]
 ```
"""
# aurora/minion_array/router.py
import os
import importlib
import subprocess

def dispatch_to_minion(worker_type, task_details, fallback_context="", headless=False):
    """
    Dynamically mounts micro-workers.
    headless=True: Bypasses terminal UI, executes in-memory, returns a dict structure.
    headless=False: Interactive terminal loop mode with Rich TUI.
    """
    # Clean away redundant prefixes if passed as 'generate_python' or 'generate_html'
    worker_type = worker_type.lower().replace("generate_", "")
    
    target_file_path = "unspecified_artifact_file"
    clean_task_details = task_details
    
    # 1. Parse out targeted file path safely
    if "| FILE:" in task_details:
        parts = task_details.split("| FILE:")
        after_file_tag = parts[1].strip()
        path_line_split = after_file_tag.split("\n", 1)
        target_file_path = path_line_split[0].replace("]", "").replace("[", "").strip()
        
        if len(path_line_split) > 1:
            clean_task_details = path_line_split[1].strip()
        else:
            clean_task_details = ""

    # 2. Dynamic module mounting via importlib
    try:
        module_name = f"aurora.minion_array.generate_{worker_type}"
        worker_module = importlib.import_module(module_name)
        raw_code = worker_module.run(clean_task_details, fallback_context).strip()
        
        while raw_code.startswith("```"):
            lines = raw_code.splitlines()
            if lines[-1].startswith("```"):
                raw_code = "\n".join(lines[1:-1]).strip()
            else:
                raw_code = "\n".join(lines[1:]).strip()
    except Exception as err:
        if headless:
            return {"status": "error", "message": f"Module load exception: {str(err)}"}
        return f"<!-- Router Fault: Breakdown in worker load context: {str(err)} -->"

    # 3. Headless Routing Pipeline Short-Circuit (Zero-Disk-Risk Web Safe Boundary)
    if headless:
        # Enforce isolated framework sanity checks before showing code to human
        check_run = subprocess.run(["python", "manage.py", "check"], capture_output=True, text=True)
        return {
            "status": "pending_approval",
            "worker_type": worker_type,
            "target_file_path": target_file_path,
            "raw_code": raw_code,
            "validation_logs": check_run.stderr if check_run.returncode != 0 else "System check passed cleanly."
        }

    # =====================================================================
    # TERMINAL BACKWARD-COMPATIBILITY MODE (Runs strictly inside test harnesses)
    # =====================================================================
    from rich.console import Console
    from rich.panel import Panel
    from rich.live import Live
    from rich.layout import Layout
    
    console = Console()
    
    def render_terminal_monitor(msg, logs=""):
        l = Layout()
        l.split(Layout(name="h", size=3), Layout(name="b", size=7), Layout(name="f", size=3))
        l["h"].update(Panel(f"📡 [cyan]AURORA TERMINAL MONITOR[/cyan] | Worker: {worker_type.upper()}"))
        l["b"].update(Panel(f"File: {target_file_path}\nAction: {msg}\n\n[dim]{logs}[/dim]"))
        l["f"].update(Panel("[yellow]Terminal Harness Context Active[/yellow]"))
        return l

    with Live(render_terminal_monitor("Running validation check..."), console=console, refresh_per_second=4) as live:
        check_run = subprocess.run(["python", "manage.py", "check"], capture_output=True, text=True)
        if check_run.returncode != 0:
            live.stop()
            return f"<!-- Router Fault: Django check failed: {check_run.stderr} -->"
        
        if worker_type.lower() in ["html", "css"]:
            live.stop()
            print("\n" + "=" * 80)
            approval = input(f"⚠️ Altering design assets for '{target_file_path}'. Commit to disk? (y/n): ")
            if approval.lower() != 'y':
                return "<!-- Router Notification: Canceled by user -->"

    try:
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
        with open(target_file_path, "w", encoding="utf-8") as f:
            f.write(raw_code)
            
        # Optional: Relational Auto-Doc Trigger Block
        try:
            from aurora.models import Document, Content, Metadata
            doc_title = f"AUTO-SPEC: Changes to {target_file_path}"
            document, _ = Document.objects.get_or_create(title=doc_title)
            c_node, _ = Content.objects.get_or_create(document=document, defaults={'content': f"```\n{raw_code}\n```"})
            Metadata.objects.get_or_create(document=document, key="associated_module", defaults={"value": target_file_path, "type": "auto_generated_spec"})
        except:
            pass

        return f"💾 **System Action:** Code generated and written directly to local file path: `{target_file_path}`"
    except Exception as fs_err:
        return f"<!-- Router Fault: File system write crash: {str(fs_err)} -->"