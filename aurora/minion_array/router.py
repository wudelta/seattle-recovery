# aurora/minion_array/router.py
import os
import importlib
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout

console = Console()

def render_terminal_monitor(worker_type, target_path, status_msg, logs=""):
    """Generates a scannable, dense visual overlay inside your current active shell."""
    monitor_layout = Layout()
    monitor_layout.split(
        Layout(name="header", size=3),
        Layout(name="body", size=7),
        Layout(name="footer", size=3)
    )
    
    monitor_layout["header"].update(Panel(
        f"📡 [bold cyan]AURORA ARRAY STREAM LIVE FEED[/bold cyan] | Active Worker Module: [yellow]generate_{worker_type.upper()}[/yellow]",
        style="blue"
    ))
    monitor_layout["body"].update(Panel(
        f"[bold white]Target Destination File :[/bold white] {target_path}\n"
        f"[bold white]Current Processing Layer :[/bold white] [green]{status_msg}[/green]\n\n"
        f"[bold white]System Execution Trace Logs:[/bold white]\n[dim white]{logs}[/dim white]",
        style="white"
    ))
    monitor_layout["footer"].update(Panel(
        "[bold yellow]Automation Engine Status: Intercepting Background Micro-Worker Output Processes...[/bold yellow]",
        style="yellow"
    ))
    return monitor_layout

def dispatch_to_minion(worker_type, task_details, fallback_context=""):
    """Dynamically mounts micro-workers and coordinates live console tracing and human guardrails."""
    
    # Clean away redundant prefixes if passed as 'generate_python' or 'generate_html'
    worker_type = worker_type.lower().replace("generate_", "")
    
    print(f"📡 Dynamic routing task allocation mapping: minion_array.{worker_type}")

    target_file_path = "unspecified_artifact_file"
    clean_task_details = task_details
    
    # 1. Clear array parsing out the targeted file path string safely
    if "| FILE:" in task_details:
        parts = task_details.split("| FILE:")
        # Read the second index string (everything after | FILE:)
        after_file_tag = parts[1].strip()
        
        # Split at the very first newline to cleanly separate file path from code block
        path_line_split = after_file_tag.split("\n", 1)
        
        # Clear out rogue square brackets from the string container
        target_file_path = path_line_split[0].replace("]", "").replace("[", "").strip()
        
        # The remainder of the split array holds the actual code body text payload
        if len(path_line_split) > 1:
            clean_task_details = path_line_split[1].strip()
        else:
            clean_task_details = ""

    # 2. Boot up the live monitoring terminal window panel view
    with Live(render_terminal_monitor(worker_type, target_file_path, "Spawning worker process..."), console=console, refresh_per_second=4) as live:
        
        # 3. Dynamically mount the micro-worker module via importlib
        live.update(render_terminal_monitor(worker_type, target_file_path, "Mounting module into importlib array..."))
        try:
            module_name = f"aurora.minion_array.generate_{worker_type}"
            worker_module = importlib.import_module(module_name)
            
            live.update(render_terminal_monitor(worker_type, target_file_path, "Executing minion code generation logic..."))
            raw_code = worker_module.run(clean_task_details, fallback_context).strip()
            
            while raw_code.startswith("```"):
                lines = raw_code.splitlines()
                if lines[-1].startswith("```"):
                    raw_code = "\n".join(lines[1:-1]).strip()
                else:
                    raw_code = "\n".join(lines[1:]).strip()
        except Exception as err:
            live.stop()
            console.print(f"\n❌ [ROUTER CRITICAL ERROR] Failed to mount or run worker: {str(err)}", style="bold red")
            return f"<!-- Router Fault: Breakdown in worker load context: {str(err)} -->"

        # 4. Enforce automated syntax integrity checks via subprocess tests
        live.update(render_terminal_monitor(worker_type, target_file_path, "Running background validation suite (manage.py check)..."))
        check_run = subprocess.run(["python", "manage.py", "check"], capture_output=True, text=True)
        
        if check_run.returncode != 0:
            live.update(render_terminal_monitor(worker_type, target_file_path, "❌ SYNTAX FAULT ENCOUNTERED", logs=check_run.stderr))
            live.stop()
            console.print("\n[bold red]Structural check failed. Re-routing output straight to patch_debugger.py...[/bold red]")
            return f"<!-- Router Fault: Django check failed: {check_run.stderr} -->"
        
        # 5. Intercept layout design files for user validation approval guardrails
        if worker_type.lower() in ["html", "css"]:
            live.update(render_terminal_monitor(worker_type, target_file_path, "⚠️ AWAITING DELTA'S OPERATIONAL SIGN-OFF..."))
            live.stop()  # Release control back to keyboard standard input streams
            
            print("\n" + "=" * 80)
            console.print(f"⚠️  [APPROVAL MANDATE REQUIREMENT] Minion 'generate_{worker_type}' is altering presentation layouts.", style="bold yellow")
            console.print(f"Target Destination Path: {target_file_path}\n", style="dim white")
            
            approval = input("Review changes? Commit and write this code layout to your physical disk? (y/n): ")
            print("=" * 80 + "\n")
            
            if approval.lower() != 'y':
                console.print("[CANCELED] Modification block rejected by system operator Delta. Process aborted.", style="bold red")
                return "<!-- Router Notification: Change block rejected by operator Delta -->"

    # 6. Complete file drop write sequence to physical disk with Automated Documentation Hook
    try:
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
        with open(target_file_path, "w", encoding="utf-8") as f:
            f.write(raw_code)
        console.print(f"✔ [SUCCESS] File written successfully to -> {target_file_path}\n", style="bold green")
        
        # === AUTOMATED DOCUMENTATION GENERATOR LOOP ===
        try:
            # Dynamically pull the model entities from your active application context
            from aurora.models import Document, Content, Metadata
            
            # Formulate an automated technical specification title matching the file path
            doc_title = f"AUTO-SPEC: Changes to {target_file_path}"
            document, doc_created = Document.objects.get_or_create(title=doc_title)
            
            # Map out the exact code transformation delta body text directly into the Content table
            doc_content = (
                f"### Automated Code Generation Specification\n"
                f"**Generated By Micro-Minion:** generate_{worker_type.lower()}\n"
                f"**Target Destination File Path:** `{target_file_path}`\n\n"
                f"#### Core Code Implementation Blueprint:\n"
                f"```python\n{raw_code}\n```"
                if worker_type.lower() == "python" else
                f"```html\n{raw_code}\n```"
            )
            
            content_node, content_created = Content.objects.get_or_create(
                document=document,
                defaults={'content': doc_content}
            )
            if not content_created:
                content_node.content = doc_content
                content_node.save()
                
            # Log the Module Path Association tags right into your Metadata tables
            metadata_tags = [
                {"key": "associated_module", "value": target_file_path, "type": "auto_generated_spec"},
                {"key": "project_scope", "value": "aurora", "type": "ecosystem_partition"},
                {"key": "criticality", "value": "MEDIUM", "type": "system_audit"},
                {"key": "status", "value": "LIVE_PRODUCTION", "type": "lifecycle"}
            ]
            
            for tag in metadata_tags:
                meta_node, meta_created = Metadata.objects.get_or_create(
                    document=document,
                    key=tag["key"],
                    defaults={"value": tag["value"], "type": tag["type"], "status": "ACTIVE"}
                )
                if not meta_created:
                    meta_node.value = tag["value"]
                    meta_node.type = tag["type"]
                    meta_node.save()
                    
            console.print("✔ [AUTO-DOC] PostgreSQL relational tracking tables updated successfully.", style="dim green")
        except Exception as doc_err:
            console.print(f"⚠️ [AUTO-DOC WARNING] Relational logging skipped: {str(doc_err)}", style="dim yellow")
        # ===============================================

        return f"💾 **System Action:** Code generated and written directly to local file path: `{target_file_path}`"
    except Exception as fs_err:
        console.print(f"❌ [DISK SYSTEM ERROR] Failed writing to file path: {str(fs_err)}", style="bold red")
        return f"<!-- Router Fault: File system write crash: {str(fs_err)} -->"
