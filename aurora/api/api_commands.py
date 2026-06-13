# ======================================================================
# FILE: aurora/api/api_commands.py (PATCH 1 OF 5)
# START: INITIAL_CONFIGURATIONS_SYSTEM_IMPORTS_AND_ROUTER_ENTRY
# ======================================================================
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from aurora.models import ComponentRegistry

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
# END: INITIAL_CONFIGURATIONS_SYSTEM_IMPORTS_AND_ROUTER_ENTRY (PATCH 1 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/api/api_commands.py (PATCH 2 OF 5)
# START: DELTA_NOTES_ENDPOINT_POST_ACTIONS
# ======================================================================
    elif request.method == "POST":
        from aurora.models import DeltaNotesEntry  # Standardized model reference injection
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
            PageSkeletonBuilder.emit_log("[BACKLOG] Commencing compilation of master project.md footprint...\n")
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
                PageSkeletonBuilder.emit_log(f"[SUCCESS] Export sequence finalized. Updated file: {file_path}\n")
                return JsonResponse({
                    "status": "success",
                    "message": "Project file 'project.md' compiled successfully from current active backlog.",
                    "telemetry_stream": PageSkeletonBuilder.flush_telemetry()
                })
            except Exception as e:
                PageSkeletonBuilder.emit_log(f"[ERROR] Failed to compile backlog: {str(e)}\n")
                return JsonResponse({
                    "status": "error", 
                    "message": f"File generation block fault: {str(e)}",
                    "telemetry_stream": PageSkeletonBuilder.flush_telemetry()
                }, status=500)
                
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
            action = parts[0].lower() if parts else ""
            PageSkeletonBuilder.emit_log(f"[COMMAND] Intercepted automation route directive: '{raw_cmd}'\n")
# ======================================================================
# END: DELTA_NOTES_ENDPOINT_POST_ACTIONS (PATCH 2 OF 5)
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
            
            PageSkeletonBuilder.emit_log(f"[INFO] Initializing forge sequence for page layout template: '{path}' [{vis}]\n")
            
            # Direct calculation builds layout and fills internal telemetry buffer array
            res = PageSkeletonBuilder.forge_page(c_app, c_page, vis)
            
            # Extract and flush internal memory logs to pass back to the frontend console interface
            captured_telemetry_logs = PageSkeletonBuilder.flush_telemetry()
            
            if res.get("status") == "error":
                return JsonResponse({
                    "status": "success",
                    "minion_log": f"Forge halted: {res.get('message')}",
                    "telemetry_stream": captured_telemetry_logs,
                    "validation": {"valid": False, "errors": [res.get('message')], "warnings": []}
                })
            
            asset = register_new_component(
                path, 
                f"{c_page}_layout", 
                vis, 
                request.user, 
                "COMPILER_MODULE", 
                f"Automated layout canvas configuration for {c_app}."
            )
            
            captured_telemetry_logs += f"[SUCCESS] Component system synced! Relational UUID: {str(asset.id)} | Graph network node attached.\n"
            
            return JsonResponse({
                "status": "success",
                "minion_log": f"FORGE SUCCESS: {res.get('message')} (Postgres UUID: {str(asset.id)} -> Graph synchronized).",
                "generated_code": f"<!-- Layout located at: {path} -->\n",
                "telemetry_stream": captured_telemetry_logs,
                "validation": {"valid": True, "errors": [], "warnings": []}
            })
# ======================================================================
# END: PAGE_BLUEPRINT_FORGE_SUBSYSTEM_ROUTING (PATCH 3 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/api/api_commands.py (PATCH 4 OF 5)
# START: UNIVERSAL_OBLITERATOR_ROUTING_AND_LOCK_VERIFICATION
# ======================================================================
        # SUB-ROUTE B: FUNCTIONAL API ENDPOINT FORGE
        # FIXED: Extraction now targets string index index token [0] safely
        elif parts and parts[0].lower() == "/api":
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
            
            PageSkeletonBuilder.emit_log(f"[INFO] Initializing forge sequence for API streaming endpoint: '{path}'\n")
            
            res = ApiSkeletonBuilder.forge_api(c_app, c_endpoint, vis)
            captured_telemetry_logs = PageSkeletonBuilder.flush_telemetry()
            
            if res.get("status") == "error":
                return JsonResponse({
                    "status": "success",
                    "minion_log": f"Forge halted: {res.get('message')}",
                    "telemetry_stream": captured_telemetry_logs,
                    "validation": {"valid": False, "errors": [res.get('message')], "warnings": []}
                })
            
            asset = register_new_component(
                path, 
                f"{f_name}", 
                vis, 
                request.user, 
                "ENTRY_POINT", 
                f"Automated function-based JSON stream endpoint inside {c_app}/api."
            )
            
            captured_telemetry_logs += f"[SUCCESS] API route generated successfully. Registry ID: {str(asset.id)}\n"
            return JsonResponse({
                "status": "success",
                "minion_log": f"FORGE SUCCESS: {res.get('message')} (Postgres UUID: {str(asset.id)} -> Graph synchronized).",
                "generated_code": f"# API Path registered: path('api/{c_endpoint}/', api_commands.{f_name})\n",
                "telemetry_stream": captured_telemetry_logs,
                "validation": {"valid": True, "errors": [], "warnings": []}
            })

        # SUB-ROUTE C: UNIVERSAL SURGICAL INFRASTRUCTURE OBLITERATOR
        # FIXED: Extraction now targets string index index token [0] safely
        elif parts and parts[0].lower() == "/destroy":
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
            
            PageSkeletonBuilder.emit_log(f"[INFO] Initializing obliteration check for asset tracking tree: '{name_raw}'\n")
            
            for target_path in [page_path, api_path]:
                try:
                    asset = ComponentRegistry.objects.get(file_path=target_path)
                    if asset.locked:
                        PageSkeletonBuilder.emit_log(f"[ERROR] Purge denied! Infrastructure asset is locked: {target_path}\n")
                        return JsonResponse({
                            "status": "success",
                            "minion_log": f"PURGE DENIED: '{name_raw}' path infrastructure is LOCKED.",
                            "telemetry_stream": PageSkeletonBuilder.flush_telemetry(),
                            "validation": {"valid": True, "errors": [], "warnings": []}
                        })
                except ComponentRegistry.DoesNotExist:
                    pass

            PageSkeletonBuilder.emit_log("[INFO] System validation passed. Commencing codebase purge operations...\n")
            p_res = PageSkeletonBuilder.purge_page(app_raw, name_raw)
            a_res = ApiSkeletonBuilder.purge_api(app_raw, name_raw)
            
            PageSkeletonBuilder.emit_log("[INFO] Detaching and flushing Neo4j network graph context loops...\n")
            from neomodel import db
            for target_path in [page_path, api_path]:
                try:
                    db.cypher_query("MATCH (n:ComponentNode) WHERE n.file_path = $path DETACH DELETE n", {"path": target_path})
                except Exception as e:
                    PageSkeletonBuilder.emit_log(f"[WARNING] Graph node cleanup anomaly: {str(e)}\n")

            PageSkeletonBuilder.emit_log("[INFO] Purging relational PostgreSQL metadata entries...\n")
            for target_path in [page_path, api_path]:
                ComponentRegistry.objects.filter(file_path=target_path).delete()
                
            PageSkeletonBuilder.emit_log(f"[SUCCESS] Infrastructure completely obliterated for module component context: '{name_raw}'\n")
            
            return JsonResponse({
                "status": "success",
                "minion_log": f"SURGICAL WIPE SUCCESS. Templates: {p_res.get('message')} | APIs: {a_res.get('message')} | Graph Nodes: Erased.",
                "generated_code": f"# Erased all local codebase artifacts for: {name_raw}\n",
                "telemetry_stream": PageSkeletonBuilder.flush_telemetry(),
                "validation": {"valid": True, "errors": [], "warnings": []}
            })

        elif action.startswith("/"):
            return JsonResponse({
                "status": "success",
                "minion_log": f"Unknown automation instruction: {action}",
                "validation": {"valid": True, "errors": [], "warnings": []}
            })
# ======================================================================
# END: UNIVERSAL_OBLITERATOR_ROUTING_AND_LOCK_VERIFICATION (PATCH 4 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/api/api_commands.py (PATCH 3 OF 5)
# START: PAGE_BLUEPRINT_FORGE_SUBSYSTEM_ROUTING
# ======================================================================
        # SUB-ROUTE A: CORE COMPONENT CANVAS LAYOUT FORGE
        # FIXED: Extraction now targets string index 0 token safely to avoid AttributeError list crashes
        if parts and parts[0].lower() == "/page":
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
            
            PageSkeletonBuilder.emit_log(f"[INFO] Initializing forge sequence for page layout template: '{path}' [{vis}]\n")
            
            # Direct calculation builds layout and fills internal telemetry buffer array
            res = PageSkeletonBuilder.forge_page(c_app, c_page, vis)
            
            # Extract and flush internal memory logs to pass back to the frontend console interface
            captured_telemetry_logs = PageSkeletonBuilder.flush_telemetry()
            
            if res.get("status") == "error":
                return JsonResponse({
                    "status": "success",
                    "minion_log": f"Forge halted: {res.get('message')}",
                    "telemetry_stream": captured_telemetry_logs,
                    "validation": {"valid": False, "errors": [res.get('message')], "warnings": []}
                })
            
            asset = register_new_component(
                path, 
                f"{c_page}_layout", 
                vis, 
                request.user, 
                "COMPILER_MODULE", 
                f"Automated layout canvas configuration for {c_app}."
            )
            
            captured_telemetry_logs += f"[SUCCESS] Component system synced! Relational UUID: {str(asset.id)} | Graph network node attached.\n"
            
            return JsonResponse({
                "status": "success",
                "minion_log": f"FORGE SUCCESS: {res.get('message')} (Postgres UUID: {str(asset.id)} -> Graph synchronized).",
                "generated_code": f"<!-- Layout located at: {path} -->\n",
                "telemetry_stream": captured_telemetry_logs,
                "validation": {"valid": True, "errors": [], "warnings": []}
            })
# ======================================================================
# END: PAGE_BLUEPRINT_FORGE_SUBSYSTEM_ROUTING (PATCH 3 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/api/api_commands.py (PATCH 4 OF 5)
# START: UNIVERSAL_OBLITERATOR_ROUTING_AND_LOCK_VERIFICATION
# ======================================================================
        # SUB-ROUTE B: FUNCTIONAL API ENDPOINT FORGE
        elif parts and parts[0].lower() == "/api":
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
            
            # FIXED: Updated entry log prefix signature from [INFO] to [FORGE_ENGINE]
            PageSkeletonBuilder.emit_log(f"[FORGE_ENGINE] Initializing forge sequence for API streaming endpoint: '{path}'\n")
            
            res = ApiSkeletonBuilder.forge_api(c_app, c_endpoint, vis)
            captured_telemetry_logs = PageSkeletonBuilder.flush_telemetry()
            
            if res.get("status") == "error":
                return JsonResponse({
                    "status": "success",
                    "minion_log": f"Forge halted: {res.get('message')}",
                    "telemetry_stream": captured_telemetry_logs,
                    "validation": {"valid": False, "errors": [res.get('message')], "warnings": []}
                })
            
            asset = register_new_component(
                path, 
                f"{f_name}", 
                vis, 
                request.user, 
                "ENTRY_POINT", 
                f"Automated function-based JSON stream endpoint inside {c_app}/api."
            )
            
            captured_telemetry_logs += f"[SUCCESS] API route generated successfully. Registry ID: {str(asset.id)}\n"
            return JsonResponse({
                "status": "success",
                "minion_log": f"FORGE SUCCESS: {res.get('message')} (Postgres UUID: {str(asset.id)} -> Graph synchronized).",
                "generated_code": f"# API Path registered: path('api/{c_endpoint}/', api_commands.{f_name})\n",
                "telemetry_stream": captured_telemetry_logs,
                "validation": {"valid": True, "errors": [], "warnings": []}
            })

        # SUB-ROUTE C: UNIVERSAL SURGICAL INFRASTRUCTURE OBLITERATOR
        elif parts and parts[0].lower() == "/destroy":
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
            
            # FIXED: Updated entry log prefix signature from [INFO] to [FORGE_ENGINE]
            PageSkeletonBuilder.emit_log(f"[FORGE_ENGINE] Initializing obliteration check for asset tracking tree: '{name_raw}'\n")
            
            for target_path in [page_path, api_path]:
                try:
                    asset = ComponentRegistry.objects.get(file_path=target_path)
                    if asset.locked:
                        PageSkeletonBuilder.emit_log(f"[ERROR] Purge denied! Infrastructure asset is locked: {target_path}\n")
                        return JsonResponse({
                            "status": "success",
                            "minion_log": f"PURGE DENIED: '{name_raw}' path infrastructure is LOCKED.",
                            "telemetry_stream": PageSkeletonBuilder.flush_telemetry(),
                            "validation": {"valid": True, "errors": [], "warnings": []}
                        })
                except ComponentRegistry.DoesNotExist:
                    pass

            PageSkeletonBuilder.emit_log("[FORGE_ENGINE] System validation passed. Commencing codebase purge operations...\n")
            p_res = PageSkeletonBuilder.purge_page(app_raw, name_raw)
            a_res = ApiSkeletonBuilder.purge_api(app_raw, name_raw)
            
            PageSkeletonBuilder.emit_log("[FORGE_ENGINE] Detaching and flushing Neo4j network graph context loops...\n")
            from neomodel import db
            for target_path in [page_path, api_path]:
                try:
                    db.cypher_query("MATCH (n:ComponentNode) WHERE n.file_path = $path DETACH DELETE n", {"path": target_path})
                except Exception as e:
                    PageSkeletonBuilder.emit_log(f"[WARNING] Graph node cleanup anomaly: {str(e)}\n")

            PageSkeletonBuilder.emit_log("[FORGE_ENGINE] Purging relational PostgreSQL metadata entries...\n")
            for target_path in [page_path, api_path]:
                ComponentRegistry.objects.filter(file_path=target_path).delete()
                
            PageSkeletonBuilder.emit_log(f"[SUCCESS] Infrastructure completely obliterated for module component context: '{name_raw}'\n")
            
            return JsonResponse({
                "status": "success",
                "minion_log": f"SURGICAL WIPE SUCCESS. Templates: {p_res.get('message')} | APIs: {a_res.get('message')} | Graph Nodes: Erased.",
                "generated_code": f"# Erased all local codebase artifacts for: {name_raw}\n",
                "telemetry_stream": PageSkeletonBuilder.flush_telemetry(),
                "validation": {"valid": True, "errors": [], "warnings": []}
            })
# ======================================================================
# END: UNIVERSAL_OBLITERATOR_ROUTING_AND_LOCK_VERIFICATION (PATCH 4 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/api/api_commands.py (PATCH 5 OF 5)
# START: AI_ORCHESTRATION_GATEWAY_AND_EXCEPTION_HANDLER
# ======================================================================
        # TIER 2: AI INTELLECTUAL ORCHESTRATION GATEWAY (Plain English Fallback Mode)
        else:
            PageSkeletonBuilder.emit_log("[INFO] Routing command string to conversational pipeline processing layer...\n")
            return JsonResponse({
                "status": "success",
                "minion_log": "Wu engine is ready. Cloud gateway waiting for plain English commands.",
                "generated_code": "# Wu Active\n",
                "telemetry_stream": PageSkeletonBuilder.flush_telemetry(),
                "validation": {"valid": True, "errors": [], "warnings": []}
            })
            
    except Exception as e:
        error_msg = f"Forge process view fault: {str(e)}"
        PageSkeletonBuilder.emit_log(f"[FAIL] Core architectural router exception intercepted: {error_msg}\n")
        return JsonResponse({
            "status": "success",
            "minion_log": error_msg,
            "generated_code": "",
            "telemetry_stream": PageSkeletonBuilder.flush_telemetry(),
            "validation": {"valid": False, "errors": [str(e)], "warnings": []}
        })

@csrf_exempt
@login_required
def unlocked_components_endpoint(request):
    """
    Decoupled standalone registry view managing component tracking records.
    Operates outside the main execute_blueprint_api string log stream buffer layer.
    """
    if request.method == "GET":
        # FIXED: Corrected ordering field key parameter from created_at to date_created
        unlocked_assets = ComponentRegistry.objects.filter(locked=False).order_by('-date_created')
        payload = [{"id": str(asset.id), "name": asset.name, "path": asset.file_path} for asset in unlocked_assets]
        return JsonResponse({"status": "success", "components": payload})
        
    elif request.method == "POST":
        target_id = request.POST.get("component_id")
        if target_id:
            # Mutate row lock status directly in the database
            ComponentRegistry.objects.filter(id=target_id).update(locked=True)
            PageSkeletonBuilder.emit_log(f"[SUCCESS] Security state mutated. Locked registry record token UUID: {target_id}\n")
            return JsonResponse({
                "status": "success", 
                "telemetry_stream": PageSkeletonBuilder.flush_telemetry()
            })
        return JsonResponse({"status": "error", "message": "Missing component_id parameter."}, status=400)
        
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
# ======================================================================
# END: AI_ORCHESTRATION_GATEWAY_AND_EXCEPTION_HANDLER (PATCH 5 OF 5)
# ======================================================================
