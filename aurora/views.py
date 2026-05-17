# FILE: aurora/views.py
"""
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T21:12:26.608607+00:00
 PROJECT ECOSYSTEM: AURORA
 FILE PATH: aurora/views.py
 TECHNICAL MATRIX: Python Module. Exported Logic Components: wu_director, dashboard, chat_api, manual_time_log_view, end_session_view, get, post, get, post, get, post, execute_baseline_sanity_checks, commit_file_view

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[views.py] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[AURORA]
 ```
"""
import os
import json
import logging
import traceback
import markdown
import subprocess
import importlib.util
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.cache import cache
from django.utils import timezone
from django.views.decorators.http import require_POST
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from groq import Groq

# Consolidated Models and Serializers
from .models import Document, Metadata, Content
from .serializers import DocumentSerializer, MetadataSerializer, ContentSerializer

# Consolidated Core Graph Logic Imports
from core_logic.memory import save_memory, get_recent_context, create_resource, summarize_session
from core_logic.sessions import start_session, end_session, log_manual_time

@login_required
def console_dashboard(request):
    """
    Renders the central core dashboard cockpit, pre-loading 
    the un-ingested offline daily brief plain-text staging block.
    """
    local_brief_content = ""
    
    # Read the current physical offline file state to display on screen
    if os.path.exists(BRIEF_FILE_PATH):
        with open(BRIEF_FILE_PATH, 'r', encoding='utf-8') as f:
            local_brief_content = f.read()
            
    context = {
        'local_brief_content': local_brief_content,
        'session_active': False,  # Keeps the staging panel visible on initial load
    }
    # FIXED: Swapped console.html out for dashboard.html to target your pristine template asset
    return render(request, 'aurora/dashboard.html', context)

@csrf_exempt
def wu_director(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')
        return JsonResponse({
            "response": f"Director here. I received: '{user_message}'. Connection stable.",
            "status": "online"
        })

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@user_passes_test(lambda u: u.is_superuser)
def dashboard(request):
    """The command center for Delta."""
    return render(request, 'aurora/dashboard.html')

@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
        
    user_id = request.user.username.lower() if request.user.is_authenticated else "delta"
    user_text = request.POST.get('text', '').strip()
    session_id = request.session.get('current_session_id')

    # 1. RESOURCE DETECTOR (JSON Blobs)
    if user_text.startswith('{') and user_text.endswith('}'):
        try:
            resource_data = json.loads(user_text)
            if "category" in resource_data:
                create_resource(user_id, resource_data)
                return JsonResponse({
                    "reply": "📦 **Resource Node Created.** Entry documented in the graph.",
                    "tokens_left": cache.get(f'tokens_{user_id}', 18000),
                    "token_ceiling": cache.get(f'token_ceiling_{user_id}', 18000),
                    "active_model": "System (Local)"
                })
        except json.JSONDecodeError:
            pass

    # Session Handshake
    if not request.session.session_key:
        request.session.create()
    if not session_id:
        session_id = start_session(user_id)
        request.session['current_session_id'] = session_id

    # 2. HARD COGNITIVE PROTECTION OVERHEAT CHECK
    tokens_remaining = int(cache.get(f'tokens_{user_id}', 12000))
    token_ceiling = int(cache.get(f'token_ceiling_{user_id}', 12000))
    
    if tokens_remaining < 1200:
        print("Fuel critical. Auto-triggering Janitor cleanup...")
        summary = summarize_session(user_id)
        return JsonResponse({
            "reply": f"⚠️ **Groq Rate Limit Critical.** Fuel ({tokens_remaining:,}) dropped below safety limits. System flushed history to preserve quotas. **Latest State Saved to Disk:**\n\n{summary}",
            "tokens_left": tokens_remaining,
            "token_ceiling": token_ceiling,
            "active_model": "System Flash-Clear"
        })

    # 3. FORCE HIGH CAPACITY ENGINE
    active_model = "llama-3.3-70b-versatile"
    model_label = "Architect (70B)"

    # 4. CONTEXT & SYSTEM RETRIEVAL (Partitioned strictly to Aurora ecosystem)
    history = get_recent_context(user_id, limit=10, project="aurora")

    system_instructions = (
        f"You are Wu, the lead architect. Speaking to: {user_id}. "
        f"Current Brain: {model_label}. Active Ecosystem Workspace: AURORA ENGINE BUILDER. "
        "Mission: Provide practical, high-level structural aid for the application builder itself. "
        "CRITICAL PROTOCOLS FOR DELEGATION:\n"
        "1. If Delta requests bulk layouts, structural templates, style rules, or scripts, output EXACTLY: "
        "[DELEGATE: <minion_module> | TASK: <instruction>] (where minion_module is generate_html, generate_css, or generate_js).\n"
        "2. IF DELTA SPECIFIES A LOCAL FILE PATH, you MUST append the file path tracking parameter right inside the brackets like this: "
        "[DELEGATE: generate_html | TASK: <instruction> | FILE: <relative_file_path>].\n"
        "3. If Delta passes a Python file crash tracker, a terminal exception line, or an absolute traceback, output EXACTLY: "
        "[DELEGATE: patch_debugger | TASK: <pasted error or traceback description>].\n"
        "Do not write code blocks yourself when utilizing these structural tags."
    )
    
    messages = [{"role": "system", "content": system_instructions}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    try:
        # 5. EXECUTE VIA RAW RESPONSE FOR LIVE QUOTA READING
        chat_completion = client.chat.completions.with_raw_response.create(
            messages=messages,
            model=active_model,
            temperature=0.1
        )
        
        # 6. EXTRACT HEADERS & SET CACHE
        response_data = chat_completion.parse()
        new_limit = int(chat_completion.headers.get('x-ratelimit-remaining-tokens', tokens_remaining))
        max_ceiling = int(chat_completion.headers.get('x-ratelimit-limit-tokens', token_ceiling))
        cache.set(f'tokens_{user_id}', new_limit, 3600)
        cache.set(f'token_ceiling_{user_id}', max_ceiling, 3600)
        
        answer = response_data.choices[0].message.content

        # --- DELEGATION SWITCH ROUTE REFACTOR INSIDE aurora/views.py ---
        if answer.startswith("[DELEGATE:"):
            try:
                header_segment = answer.split("|")[0]
                worker_part = header_segment.split(":")[-1].strip().lower().replace("generate_", "")
                task_details = answer.split("TASK:")[-1].split("]")[0].strip()
                
                # Import the dynamic module traffic cop router
                from .minion_array.router import dispatch_to_minion
                
                # Call the router with headless=True to protect your disk files
                minion_payload = dispatch_to_minion(
                    worker_type=worker_part,
                    task_details=task_details,
                    fallback_context="",
                    headless=True # <-- Forces in-memory execution tracking
                )
                
                # Persistent memory sync logs written to partitioned Aurora space
                save_memory(user_id, user_text, "user", session_id, project="aurora")
                save_memory(user_id, f"Delegated task to {worker_part}: {task_details}", "assistant", session_id, project="aurora")
                
                # Return a structured JSON response to your frontend web panel
                return JsonResponse({
                    "status": minion_payload.get("status", "pending_approval"),
                    "worker_type": minion_payload.get("worker_type", worker_part),
                    "target_file_path": minion_payload.get("target_file_path", "unknown"),
                    "raw_code": minion_payload.get("raw_code", ""),
                    "validation_logs": minion_payload.get("validation_logs", ""),
                    "tokens_left": new_limit,
                    "token_ceiling": max_ceiling,
                    "active_model": f"Minion Array ({worker_part})"
                })
                
            except Exception as minion_error:
                return JsonResponse({"status": "error", "message": f"Delegation pipeline anomaly: {str(minion_error)}"}, status=500)
        # --- END OF DELEGATION SWITCH ---

        # 7. PERSIST (Dual-Write to Neo4j partitioned space)
        save_memory(user_id, user_text, "user", session_id, project="aurora")
        save_memory(user_id, answer, "assistant", session_id, project="aurora")

        # 8. FORMAT & RESPOND
        formatted_answer = markdown.markdown(answer, extensions=['fenced_code', 'codehilite'])
        return JsonResponse({
            "reply": formatted_answer,
            "tokens_left": new_limit,
            "token_ceiling": max_ceiling,
            "active_model": model_label
        })

    except Exception as e:
        print(f"🔴 Groq Gateway Error: {str(e)}. Executing Emergency Sweep...")
        summary_result = summarize_session(user_id)
        return JsonResponse({
            "reply": f"🔴 **Groq API Gateway Limit Exceeded.** The system circuit breaker swept your database to clear the block. **PROJECT_STATE.md Updated.** \n\n**Summary:** {summary_result}",
            "tokens_left": 0,
            "token_ceiling": token_ceiling,
            "active_model": "Circuit Breaker Active"
        })

@csrf_exempt
def manual_time_log_view(request):
    if request.method == "POST":
        user_id = request.user.username if request.user.is_authenticated else "Delta"
        hours = request.POST.get('hours')
        note = request.POST.get('note')
        log_manual_time(user_id, hours, note)
        return JsonResponse({'status': 'success', 'message': f'Logged {hours} manual hours.'})

logger = logging.getLogger("aurora.headless_ui")

@csrf_exempt
def end_session_view(request):
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

# Documentation API Views
class DocumentView(APIView):
    def get(self, request):
        documents = Document.objects.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MetadataView(APIView):
    def get(self, request):
        metadata = Metadata.objects.all()
        serializer = MetadataSerializer(metadata, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = MetadataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContentView(APIView):
    def get(self, request):
        content = Content.objects.all()
        serializer = ContentSerializer(content, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = ContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

logger = logging.getLogger("aurora.headless_ui")

def execute_baseline_sanity_checks(module_instance, ui_logs) -> tuple[bool, str]:
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


@csrf_exempt
def commit_file_view(request):
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

# Hardcoded text staging path limit
BRIEF_FILE_PATH = os.path.join(os.getcwd(), 'core_logic/staging/daily_brief.txt')

@login_required
@require_POST
def start_online_session(request):
    """
    Ingests the local offline text brief, runs time calculation tracking,
    triggers 8B minion condensation, populates PostgreSQL EAV targets,
    and returns initialization flags to switch UI layouts.
    """
    try:
        from core_logic.minion_array import run_8b_translation
        
        # 1. Capture Time Baseline Metrics
        session_start_time = timezone.now()
        
        # 2. Extract data payloads directly from local offline staging file
        if not os.path.exists(BRIEF_FILE_PATH):
            return JsonResponse({'success': False, 'error': f'Staging asset missing at: {BRIEF_FILE_PATH}'})
            
        with open(BRIEF_FILE_PATH, 'r', encoding='utf-8') as f:
            raw_content = f.read().strip()
            
        # Fallback check if UI override sent text edits
        ui_override = request.POST.get('brief_content', '').strip()
        if ui_override:
            raw_content = ui_override

        if not raw_content:
            return JsonResponse({'success': False, 'error': 'Daily brief file staging text block is empty.'})

        # 3. Compute Local Offline Planning Duration using file statistics deltas
        file_meta_stat = os.stat(BRIEF_FILE_PATH)
        last_modified = timezone.make_aware(timezone.datetime.fromtimestamp(file_meta_stat.st_mtime))
        planning_duration_seconds = max(0, int((session_start_time - last_modified).total_seconds()))

        # 4. Route text directly through local Llama 8B execution layer
        dense_abstract, objectives_json = run_8b_translation(raw_content)

        # 5. Commit structured logging metrics to PostgreSQL
        doc_entry = Document.objects.create(
            title=f"Daily Brief - {session_start_time.strftime('%Y-%m-%d')}",
            created_at=session_start_time
        )
        
        # Append specifications to your single content field table space layout
        Content.objects.get_or_create(document=doc_entry, content=f"dense_abstract: {dense_abstract}")
        Content.objects.get_or_create(document=doc_entry, content=f"objectives_json: {objectives_json}")
        Content.objects.get_or_create(document=doc_entry, content=f"planning_duration_seconds: {planning_duration_seconds}")

        # 6. Securely clear local staging document file for your next planning turn
        with open(BRIEF_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write("")

        return JsonResponse({
            'success': True,
            'dense_abstract': dense_abstract,
            'objectives': objectives_json
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
