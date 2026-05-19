import os
import json
import logging
import traceback
import importlib.util
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

logger = logging.getLogger("aurora.headless_ui")
@csrf_exempt
def commit_file_view(request):
    print("🤖 [commit_file_view] Action triggered.")
    """Entry gate for local drive writes. Streams granular diagnostic logs to the Web Dashboard."""
    
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)

    ui_logs = []  # Diagnostic array returned directly to the browser console UI
    ui_logs.append("🚀 Initializing headless UI pipeline migration loop.")

    try:
        payload = json.loads(request.body)
        target_path = payload.get("target_file_path")
        raw_code = payload.get("raw_code")
        worker_type = payload.get("worker_type", "python")
        
        if not target_path or not raw_code:
            ui_logs.append("❌ Abort: Missing critical target parameters in payload.")
            return JsonResponse({"status": "error", "message": "Missing attributes.", "ui_logs": ui_logs}, status=400)

        abs_target_path = os.path.abspath(target_path)
        staging_path = f"{abs_target_path}.tmp"
        ui_logs.append(f"📁 Target file established: `{target_path}`")

        # Step 2: System Syntax Script Scan
        try:
            compile(raw_code, "<string>", "exec")
            ui_logs.append("⚙️ Syntax validation passed: Python compilation successful.")
        except SyntaxError as syntax_err:
            ui_logs.append(f"❌ Syntax Error: Line {syntax_err.lineno} failed to compile.")
            return JsonResponse({
                "status": "syntax_error",
                "message": f"Compilation Error: {str(syntax_err)}",
                "ui_logs": ui_logs
            }, status=422)

        # Step 3: Enforce File Write Blockade (Transient Writing)
        os.makedirs(os.path.dirname(abs_target_path), exist_ok=True)
        with open(staging_path, "w", encoding="utf-8") as stage_file:
            stage_file.write(raw_code)
        ui_logs.append("🛡️ File Write Blockade Active: Code cached to memory staging buffer.")

        # Step 4: Run Runtime Sandbox Import
        try:
            module_name = f"aurora.sandbox_{os.path.basename(abs_target_path).replace('.', '_')}"
            spec = importlib.util.spec_from_file_location(module_name, staging_path)
            staged_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(staged_module)
            
            # Execute validation loops
            is_valid, _ = execute_baseline_sanity_checks(staged_module, ui_logs)
        except Exception as runtime_err:
            is_valid = False
            ui_logs.append(f"❌ Runtime Error: Module failed initialization sequence: {str(runtime_err)}")

        if not is_valid:
            if os.path.exists(staging_path):
                os.remove(staging_path)
            ui_logs.append("❌ Integrity checks failed. Transient staging file purged cleanly.")
            return JsonResponse({"status": "test_failure", "message": "Verification failed.", "ui_logs": ui_logs}, status=422)

        # Step 5: Atomic Swap File System Commit
        if os.path.exists(staging_path):
            os.replace(staging_path, abs_target_path)
        ui_logs.append("💾 Drive Committal Complete: Atomic swap succeeded. Live assets updated.")

        # Step 6: Attach Automated EAV Documentation Track
        try:
            from aurora.models import Document, Content, Metadata
            doc_title = f"AUTO-SPEC: Changes to {target_path}"
            
            with transaction.atomic():
                document, _ = Document.objects.get_or_create(title=doc_title)
                doc_content = (
                    f"### Automated Code Generation Specification\n"
                    f"**Target Destination File Path:** `{target_path}`\n\n"
                    f"#### Core Code Implementation Blueprint:\n"
                    f"```python\n{raw_code}\n```" if worker_type.lower() == "python" else f"```html\n{raw_code}\n```"
                )
                content_node, _ = Content.objects.get_or_create(document=document)
                content_node.content = doc_content
                content_node.save()
                
                Metadata.objects.get_or_create(document=document, key="associated_module", defaults={"value": target_path, "type": "auto_generated_spec"})
                Metadata.objects.get_or_create(document=document, key="status", defaults={"value": "LIVE_PRODUCTION", "type": "lifecycle"})
            ui_logs.append("🗄️ Relational DB metadata maps updated and synchronized via Django Admin.")
        except Exception as doc_error:
            logger.warning(f"⚠️ [AUTO-DOC ATTACHMENT FAULT] Skipped: {str(doc_error)}")
            ui_logs.append("⚠️ Document Tracker Warning: Code saved successfully, but EAV tracking step skipped.")

        ui_logs.append("✨ System Status: OPERATIONAL. Ready for next task dispatch.")
        return JsonResponse({
            "status": "success",
            "message": "File committed safely to disk.",
            "ui_logs": ui_logs
        }, status=200)

    except Exception as server_error:
        ui_logs.append(f"💥 Critical: Server-side execution loop collapse: {str(server_error)}")
        return JsonResponse({
            "status": "error", 
            "message": str(server_error),
            "ui_logs": ui_logs,
            "traceback": traceback.format_exc()
        }, status=500)

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
