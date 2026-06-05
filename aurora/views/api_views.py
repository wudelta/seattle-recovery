import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from aurora.models import ComponentRegistry
from aurora.page_skeleton import PageSkeletonBuilder
from aurora.utils.forge_registry import register_new_component

@csrf_exempt
def execute_blueprint_api(request):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=405)
        
    try:
        # 1. Extract the raw console text payload from the form field
        raw_cmd = request.POST.get("blueprint", "").strip()
        
        # JSON fallback reader for API integrations
        if not raw_cmd:
            try:
                data = json.loads(request.body.decode('utf-8'))
                raw_cmd = data.get("blueprint", "").strip()
            except Exception:
                pass

        if not raw_cmd:
            return JsonResponse({
                "status": "success", "minion_log": "System standing ready...",
                "generated_code": "", "validation": {"valid": True, "errors": [], "warnings": []}
            })

        # ==============================================================================
        # AUTOMATION COMMANDS ENGINE (TIER 1)
        # ==============================================================================
        if raw_cmd.startswith("/"):
            parts = raw_cmd.split()
            action = parts[0].lower() if parts else ""

            # ROUTE A: STRUCTURE GENERATION
            if action == "/page":
                if len(parts) < 3:
                    return JsonResponse({
                        "status": "success", 
                        "minion_log": "Syntax Error. Expected format: /page <app_name> <page_name> [visibility]", 
                        "validation": {"valid": False, "errors": ["Missing parameters"], "warnings": []}
                    })
                
                app = parts[1].lower().strip()
                page = parts[2].lower().strip()
                vis = parts[3].lower().strip() if len(parts) > 3 else "private"
                
                c_app, c_page, c_name = PageSkeletonBuilder.clean_inputs(app, page)
                path = f"templates/{c_app}/{c_page}.html"
                
                # Execute disk writing sequence
                res = PageSkeletonBuilder.forge_page(c_app, c_page, vis)
                if res.get("status") == "error":
                    return JsonResponse({
                        "status": "success", 
                        "minion_log": f"Forge halted: {res.get('message')}", 
                        "validation": {"valid": False, "errors": [res.get('message')], "warnings": []}
                    })
                
                # Commit tandem database entries (Postgres save auto-syncs Neo4j via signal)
                asset = register_new_component(path, f"{c_page}_layout", vis, "PageSkeletonBuilder", "Auto layout canvas.")
                
                return JsonResponse({
                    "status": "success",
                    "minion_log": f"FORGE SUCCESS: Built structural layout assets for {c_name} inside {c_app}. Registries synchronized (Postgres ID: {str(asset.id)}).",
                    "generated_code": f"<!-- {path} Built Successfully -->\n",
                    "validation": {"valid": True, "errors": [], "warnings": []}
                })

            # ROUTE B: SURGICAL INFRASTRUCTURE PURGE
            elif action == "/destroy":
                if len(parts) < 3:
                    return JsonResponse({
                        "status": "success", 
                        "minion_log": "Syntax Error. Expected format: /destroy <app_name> <page_name>", 
                        "validation": {"valid": False, "errors": ["Missing parameters"], "warnings": []}
                    })
                
                app = parts[1].lower().strip()
                page = parts[2].lower().strip()
                
                c_app, c_page, c_name = PageSkeletonBuilder.clean_inputs(app, page)
                # Ensure the path matches your PageSkeletonBuilder convention precisely
                path = f"templates/{c_app}/{c_page}.html"
                
                # Safety Guardrail Lock Verification
                try:
                    asset = ComponentRegistry.objects.get(file_path=path)
                    if asset.locked:
                        return JsonResponse({
                            "status": "success", 
                            "minion_log": f"PURGE DENIED: Component '{c_page}' is LOCKED in Postgres.", 
                            "validation": {"valid": True, "errors": [], "warnings": []}
                        })
                except ComponentRegistry.DoesNotExist:
                    pass
                
                # Execute surgical file erasure loop on local disk
                p_res = PageSkeletonBuilder.purge_page(c_app, c_page)
                if p_res.get("status") == "error":
                    return JsonResponse({
                        "status": "success",
                        "minion_log": f"Purge error: {p_res.get('message')}",
                        "validation": {"valid": False, "errors": [p_res.get('message')], "warnings": []}
                    })
                
                # Clear metadata tracking entry out of tables (Signals handle Neo4j node delete)
                ComponentRegistry.objects.filter(file_path=path).delete()
                
                return JsonResponse({
                    "status": "success",
                    "minion_log": f"SURGICAL WIPE SUCCESS: {p_res.get('message')} | Metadata profiles cleared from tandem database tables.",
                    "generated_code": f"# Erased component: {c_name} from {c_app}\n",
                    "validation": {"valid": True, "errors": [], "warnings": []}
                })

            else:
                return JsonResponse({
                    "status": "success", 
                    "minion_log": f"Unknown action: {action}", 
                    "validation": {"valid": True, "errors": [], "warnings": []}
                })

        # ==============================================================================
        # AI ORCHESTRATION ENGINE GATEWAY (TIER 2)
        # ==============================================================================
        else:
            return JsonResponse({
                "status": "success",
                "minion_log": "Wu engine is ready. Cloud gateway waiting for plain English commands.",
                "generated_code": "# Wu Active\n",
                "validation": {"valid": True, "errors": [], "warnings": []}
            })

    except Exception as e:
        return JsonResponse({
            "status": "success", "minion_log": f"Forge process view fault: {str(e)}",
            "generated_code": "", "validation": {"valid": False, "errors": [str(e)], "warnings": []}
        })
