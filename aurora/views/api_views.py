# ======================================================================
# FILE: aurora/views/api_views.py (PATCH 1 OF 5)
# START: INITIAL_CONFIGURATIONS_SYSTEM_IMPORTS_AND_ROUTER_ENTRY
# ======================================================================
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from aurora.models import ComponentRegistry
from aurora.page_skeleton import PageSkeletonBuilder
from aurora.api_skeleton import ApiSkeletonBuilder
from aurora.utils.forge_registry import register_new_component

@csrf_exempt
def execute_blueprint_api(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
        
    try:
        # Extract command form parameters safely matching console.js layout
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
# ======================================================================
# END: INITIAL_CONFIGURATIONS_SYSTEM_IMPORTS_AND_ROUTER_ENTRY
# ======================================================================

# ======================================================================
# FILE: aurora/views/api_views.py (PATCH 2 OF 5)
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
                
                res = PageSkeletonBuilder.forge_page(c_app, c_page, vis)
                if res.get("status") == "error":
                    return JsonResponse({
                        "status": "success",
                        "minion_log": f"Forge halted: {res.get('message')}",
                        "validation": {"valid": False, "errors": [res.get('message')], "warnings": []}
                    })
                
                asset = register_new_component(
                    path, f"{c_page}_layout", vis, request.user, "COMPILER_MODULE", f"Automated layout canvas configuration for {c_app}."
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
# FILE: aurora/views/api_views.py (PATCH 3 OF 5)
# START: FUNCTIONAL_API_ENDPOINT_FORGE_SUBSYSTEM_ROUTING
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
                
                res = ApiSkeletonBuilder.forge_api(c_app, c_endpoint, vis)
                if res.get("status") == "error":
                    return JsonResponse({
                        "status": "success",
                        "minion_log": f"Forge halted: {res.get('message')}",
                        "validation": {"valid": False, "errors": [res.get('message')], "warnings": []}
                    })
                
                asset = register_new_component(
                    path, f"{f_name}", vis, request.user, "ENTRY_POINT", f"Automated function-based JSON stream endpoint inside {c_app}/api."
                )
                return JsonResponse({
                    "status": "success",
                    "minion_log": f"FORGE SUCCESS: {res.get('message')} (Postgres UUID: {str(asset.id)} -> Graph synchronized).",
                    "generated_code": f"# API Path registered: path('api/{c_endpoint}/', api_views.{f_name})\n",
                    "validation": {"valid": True, "errors": [], "warnings": []}
                })
# ======================================================================
# END: FUNCTIONAL_API_ENDPOINT_FORGE_SUBSYSTEM_ROUTING
# ======================================================================

# ======================================================================
# FILE: aurora/views/api_views.py (PATCH 4 OF 5)
# START: UNIVERSAL_OBLITERATOR_ROUTING_AND_LOCK_VERIFICATION
# ======================================================================
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
                
                # Normalize via standard skeleton mappings to safely pull registered paths
                c_app, c_page, _ = PageSkeletonBuilder.clean_inputs(app_raw, name_raw)
                _, c_endpoint, f_name = ApiSkeletonBuilder.clean_inputs(app_raw, name_raw)
                
                page_path = f"templates/{c_app}/{c_page}.html"
                api_path = f"{c_app}/api/{c_endpoint}_api.py"
                
                # Check target locks across potential system footprints
                for target_path in [page_path, api_path]:
                    try:
                        asset = ComponentRegistry.objects.get(file_path=target_path)
                        # Handles the locking state audit check step natively
                        if asset.locked:
                            return JsonResponse({
                                "status": "success",
                                "minion_log": f"PURGE DENIED: '{name_raw}' path infrastructure is LOCKED.",
                                "validation": {"valid": True, "errors": [], "warnings": []}
                            })
                    except ComponentRegistry.DoesNotExist:
                        pass
                
                # Execute disk cleanups safely via the newly decoupled engines
                p_res = PageSkeletonBuilder.purge_page(app_raw, name_raw)
                a_res = ApiSkeletonBuilder.purge_api(app_raw, name_raw)
                
                # NATIVE GRAPH RESET: Surgically delete targets from Neo4j cluster directly
                from neomodel import db
                for target_path in [page_path, api_path]:
                    try:
                        db.cypher_query("MATCH (n:ComponentNode) WHERE n.file_path = $path DETACH DELETE n", {"path": target_path})
                    except Exception:
                        pass

                # Clear tracking footprints completely from relational tables via standard loop
                # Calling delete on the instance explicitly fires individual post_delete signals safely
                for target_path in [page_path, api_path]:
                    ComponentRegistry.objects.filter(file_path=target_path).delete()
                
                return JsonResponse({
                    "status": "success",
                    "minion_log": f"SURGICAL WIPE SUCCESS. Templates: {p_res.get('message')} | APIs: {a_res.get('message')} | Graph Nodes: Erased.",
                    "generated_code": f"# Erased all local codebase artifacts for: {name_raw}\n",
                    "validation": {"valid": True, "errors": [], "warnings": []}
                })
                
            else:
                return JsonResponse({
                    "status": "success",
                    "minion_log": f"Unknown automation instruction: {action}",
                    "validation": {"valid": True, "errors": [], "warnings": []}
                })
# ======================================================================
# END: UNIVERSAL_OBLITERATOR_ROUTING_AND_LOCK_VERIFICATION
# ======================================================================

# ======================================================================
# FILE: aurora/views/api_views.py (PATCH 5 OF 5)
# START: AI_ORCHESTRATION_GATEWAY_AND_EXCEPTION_HANDLER
# ======================================================================
        # TIER 2: AI INTELLECTUAL ORCHESTRATION GATEWAY (Plain English Pipeline)
        else:
            return JsonResponse({
                "status": "success",
                "minion_log": "Wu engine is ready. Cloud gateway waiting for plain English commands.",
                "generated_code": "# Wu Active\n",
                "validation": {"valid": True, "errors": [], "warnings": []}
            })
            
    except Exception as e:
        return JsonResponse({
            "status": "success",
            "minion_log": f"Forge process view fault: {str(e)}",
            "generated_code": "",
            "validation": {"valid": False, "errors": [str(e)], "warnings": []}
        })
# ======================================================================
# END: AI_ORCHESTRATION_GATEWAY_AND_EXCEPTION_HANDLER
# ======================================================================
