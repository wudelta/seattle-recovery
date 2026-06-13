# ======================================================================
# FILE: aurora/api/api_commands.py (PATCH 1 OF 5)
# START: INITIAL_CONFIGURATIONS_SYSTEM_IMPORTS_AND_ROUTER_ENTRY
# ======================================================================
import json
import os
import threading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from aurora.models import ComponentRegistry
from aurora.api.dev_streamer_api import send_to_console  # <-- ADDED: Live stream hook

# Relocated builders correctly out of separate files and into utils folder
from aurora.utils.page_skeleton import PageSkeletonBuilder
from aurora.utils.api_skeleton import ApiSkeletonBuilder
from aurora.utils.forge_registry import register_new_component

@login_required
def delta_notes_endpoint(request):
    """
    Handles granular multi-state tracking streams for the Delta Notes module layout.
    Coordinates GET lists and processes isolated POST state actions.
    Uses standardized runtime lazy-loading for the concrete DeltaNotesEntry model.
    """
    from aurora.models import DeltaNotesEntry  # Standardized model reference injection
    if request.method == "GET":
        # Extract all unprocessed directives belonging to the authenticated session user
        unprocessed_nodes = DeltaNotesEntry.objects.filter(user=request.user, processed=False).order_by('-created_at')
        # Extract directives processed during this session
        processed_nodes = DeltaNotesEntry.objects.filter(user=request.user, processed=True).order_by('-updated_at')[:50]
        
        # Standardized schema maps to pull the actual field property '.text'
        unprocessed_payload = [{"id": n.id, "text": n.text} for n in unprocessed_nodes]
        processed_payload = [{"id": n.id, "text": n.text} for n in processed_nodes]
        return JsonResponse({
            "status": "success",
            "unprocessed": unprocessed_payload,
            "processed": processed_payload
        })
# ======================================================================
# END: INITIAL_CONFIGURATIONS_SYSTEM_IMPORTS_AND_ROUTER_ENTRY
# ======================================================================

# ======================================================================
# FILE: aurora/api/api_commands.py (PATCH 2 OF 5)
# START: DELTA_NOTES_ENDPOINT_POST_ACTIONS
# ======================================================================
    elif request.method == "POST":
        from aurora.models import DeltaNotesEntry # Standardized model reference injection
        action = request.POST.get("action")
        if action == "create_note":
            text = request.POST.get("text", "").strip()
            if text:
                DeltaNotesEntry.objects.create(user=request.user, text=text, processed=False)
                return JsonResponse({"status": "success"})
        elif action == "edit_note":
            note_id = request.POST.get("note_id")
            text = request.POST.get("text", "").strip()
            if note_id and text:
                DeltaNotesEntry.objects.filter(user=request.user, id=note_id).update(text=text)
                return JsonResponse({"status": "success"})
        elif action == "delete_note":
            note_id = request.POST.get("note_id")
            if note_id:
                DeltaNotesEntry.objects.filter(user=request.user, id=note_id).delete()
                return JsonResponse({"status": "success"})
        elif action == "process_note":
            note_id = request.POST.get("note_id")
            if note_id:
                DeltaNotesEntry.objects.filter(user=request.user, id=note_id).update(processed=True)
                return JsonResponse({"status": "success"})
        elif action == "compile_blueprint":
            # DECOUPLED & NON-DESTRUCTIVE: Appends session notes gracefully to preserve history
            unprocessed_notes = DeltaNotesEntry.objects.filter(user=request.user, processed=False).order_by('created_at')
            file_path = "project.md"
            try:
                with open(file_path, "a", encoding="utf-8") as f:
                    from django.utils import timezone
                    current_time_str = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"\n\n## Backlog Export Session Cluster ({current_time_str})\n")
                    if not unprocessed_notes.exists():
                        f.write("* Workspace verified baseline. Zero active intentions flag.\n")
                    else:
                        for note in unprocessed_notes:
                            f.write(f"* [ ] {note.text}\n")
                return JsonResponse({
                    "status": "success",
                    "message": "Project file 'project.md' compiled successfully from current active backlog."
                })
            except Exception as e:
                return JsonResponse({"status": "error", "message": f"File generation block fault: {str(e)}"}, status=500)
        elif action == "sync_timer":
            return JsonResponse({"status": "success"})
        return JsonResponse({"status": "error", "message": f"Invalid action: {action}"}, status=400)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

# ======================================================================
# MASTER WORKSPACE SUB-ROUTING GATEWAY FOR AUTOMATED BLUEPRINT COMMANDS
# ======================================================================
@csrf_exempt
def execute_blueprint_api(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
    try:
        raw_cmd = request.POST.get("blueprint", "").strip()
        if not raw_cmd:
            try:
                data = json.loads(request.body.decode('utf-8'))
                raw_cmd = data.get("blueprint", "").strip()
            except Exception:
                pass
        if not raw_cmd:
            return JsonResponse({
                "status": "success",
                "minion_log": "System standing ready...",
                "generated_code": "",
                "validation": {"valid": True, "errors": [], "warnings": []}
            })
            
        if raw_cmd.startswith("/"):
            parts = raw_cmd.split()
            # FIXED: Proper index extraction layout with strict python comment syntax
            action = parts[0].lower() if parts else ""
            
            # Broadcast command initialization data immediately over the live channel
            send_to_console(f"[INFO] Intercepted blueprint command instruction input: '{raw_cmd}'")
# ======================================================================
# END: DELTA_NOTES_ENDPOINT_POST_ACTIONS
# ======================================================================

# ======================================================================
# FILE: aurora/api/api_commands.py (PATCH 3 OF 5)
# START: PAGE_BLUEPRINT_FORGE_SUBSYSTEM_ROUTING
# ======================================================================
            # SUB-ROUTE A: CORE COMPONENT CANVAS LAYOUT FORGE
            if action == "/page":
                if len(parts) < 3:
                    return JsonResponse({
                        "status": "success",
                        "minion_log": "Syntax: /page <app_name> <page_name> [visibility]",
                        "validation": {"valid": False, "errors": ["Missing parameters"], "warnings": []}
                    })
                app = parts[1].lower().strip()
                page = parts[2].lower().strip()
                vis = parts[3].lower().strip() if len(parts) > 3 else "private"
                c_app, c_page, c_name = PageSkeletonBuilder.clean_inputs(app, page)
                path = f"templates/{c_app}/{c_page}.html"

                # Direct execution prevents connection drops before broadcasts write to the wire
                res = PageSkeletonBuilder.forge_page(c_app, c_page, vis)
                if res.get("status") == "error":
                    return JsonResponse({
                        "status": "success",
                        "minion_log": f"Forge halted: {res.get('message')}",
                        "validation": {"valid": False, "errors": [res.get('message')], "warnings": []}
                    })

                asset = register_new_component(
                    path, f"{c_page}_layout", vis, request.user, "COMPILER_MODULE", 
                    f"Automated layout canvas configuration for {c_app}."
                )
                return JsonResponse({
                    "status": "success",
                    "minion_log": f"FORGE SUCCESS: {res.get('message')} (Postgres UUID: {str(asset.id)} -> Graph synchronized).",
                    "generated_code": f"<!-- Layout located at: {path} -->\n",
                    "validation": {"valid": True, "errors": [], "warnings": []}
                })
# ======================================================================
# END: PAGE_BLUEPRINT_FORGE_SUBSYSTEM_ROUTING
# ======================================================================

# ======================================================================
# FILE: aurora/api/api_commands.py (PATCH 4 OF 5)
# START: UNIVERSAL_OBLITERATOR_ROUTING_AND_LOCK_VERIFICATION
# ======================================================================
            # SUB-ROUTE B: FUNCTIONAL API ENDPOINT FORGE
            elif action == "/api":
                if len(parts) < 3:
                    return JsonResponse({
                        "status": "success",
                        "minion_log": "Syntax: /api <app_name> <endpoint_name> [visibility]",
                        "validation": {"valid": False, "errors": ["Missing parameters"], "warnings": []}
                    })
                app = parts[1].lower().strip()
                endpoint = parts[2].lower().strip()
                vis = parts[3].lower().strip() if len(parts) > 3 else "private"
                c_app, c_endpoint, f_name = ApiSkeletonBuilder.clean_inputs(app, endpoint)
                path = f"{c_app}/api/{c_endpoint}_api.py"

                # Direct synchronous call preserves the ASGI protocol channel mapping
                res = ApiSkeletonBuilder.forge_api(c_app, c_endpoint, vis)
                if res.get("status") == "error":
                    return JsonResponse({
                        "status": "success",
                        "minion_log": f"Forge halted: {res.get('message')}",
                        "validation": {"valid": False, "errors": [res.get('message')], "warnings": []}
                    })

                asset = register_new_component(
                    path, f"{f_name}", vis, request.user, "ENTRY_POINT", 
                    f"Automated function-based JSON stream endpoint inside {c_app}/api."
                )
                return JsonResponse({
                    "status": "success",
                    "minion_log": f"FORGE SUCCESS: {res.get('message')} (Postgres UUID: {str(asset.id)} -> Graph synchronized).",
                    "generated_code": f"# API Path registered: path('api/{c_endpoint}/', api_commands.{f_name})\n",
                    "validation": {"valid": True, "errors": [], "warnings": []}
                })

            # SUB-ROUTE C: UNIVERSAL SURGICAL INFRASTRUCTURE OBLITERATOR
            elif action == "/destroy":
                if len(parts) < 3:
                    return JsonResponse({
                        "status": "success",
                        "minion_log": "Syntax: /destroy <app_name> <component_name>",
                        "validation": {"valid": False, "errors": ["Missing parameters"], "warnings": []}
                    })
                app_raw = parts[1].lower().strip()
                name_raw = parts[2].lower().strip()
                c_app, c_page, _ = PageSkeletonBuilder.clean_inputs(app_raw, name_raw)
                _, c_endpoint, f_name = ApiSkeletonBuilder.clean_inputs(app_raw, name_raw)
                page_path = f"templates/{c_app}/{c_page}.html"
                api_path = f"{c_app}/api/{c_endpoint}_api.py"

                for target_path in [page_path, api_path]:
                    try:
                        asset = ComponentRegistry.objects.get(file_path=target_path)
                        if asset.locked:
                            return JsonResponse({
                                "status": "success",
                                "minion_log": f"PURGE DENIED: '{name_raw}' path infrastructure is LOCKED.",
                                "validation": {"valid": True, "errors": [], "warnings": []}
                            })
                    except ComponentRegistry.DoesNotExist:
                        pass

                # Direct execution ensures logs write before the socket closes
                p_res = PageSkeletonBuilder.purge_page(app_raw, name_raw)
                a_res = ApiSkeletonBuilder.purge_api(app_raw, name_raw)

                from neomodel import db
                for target_path in [page_path, api_path]:
                    try:
                        db.cypher_query("MATCH (n:ComponentNode) WHERE n.file_path = $path DETACH DELETE n", {"path": target_path})
                    except Exception:
                        pass

                for target_path in [page_path, api_path]:
                    ComponentRegistry.objects.filter(file_path=target_path).delete()

                return JsonResponse({
                    "status": "success",
                    "minion_log": f"SURGICAL WIPE SUCCESS. Templates: {p_res.get('message')} | APIs: {a_res.get('message')} | Graph Nodes: Erased.",
                    "generated_code": f"# Erased all local codebase artifacts for: {name_raw}\n",
                    "validation": {"valid": True, "errors": [], "warnings": []}
                })

            elif action.startswith("/"):
                return JsonResponse({
                    "status": "success",
                    "minion_log": f"Unknown automation instruction: {action}",
                    "validation": {"valid": True, "errors": [], "warnings": []}
                })
# ======================================================================
# END: UNIVERSAL_OBLITERATOR_ROUTING_AND_LOCK_VERIFICATION
# ======================================================================

# ======================================================================
# FILE: aurora/api/api_commands.py (PATCH 5 OF 5)
# START: AI_ORCHESTRATION_GATEWAY_AND_EXCEPTION_HANDLER
# ======================================================================
        # TIER 2: AI INTELLECTUAL ORCHESTRATION GATEWAY (Plain English Pipeline)
        else:
            send_to_console(f"[INFO] Routing command string to conversational pipeline processing layer...")
            return JsonResponse({
                "status": "success",
                "minion_log": "Wu engine is ready. Cloud gateway waiting for plain English commands.",
                "generated_code": "# Wu Active\n",
                "validation": {"valid": True, "errors": [], "warnings": []}
            })
            
    except Exception as e:
        error_msg = f"Forge process view fault: {str(e)}"
        send_to_console(f"[FAIL] Core architectural router exception intercepted: {error_msg}")
        return JsonResponse({
            "status": "success",
            "minion_log": error_msg,
            "generated_code": "",
            "validation": {"valid": False, "errors": [str(e)], "warnings": []}
        })
# ======================================================================
# END: AI_ORCHESTRATION_GATEWAY_AND_EXCEPTION_HANDLER
# ======================================================================
