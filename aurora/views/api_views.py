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
        return JsonResponse({"status": "error"}, status=405)
        
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
                "status": "success", "minion_log": "System standing ready...",
                "generated_code": "", "validation": {"valid": True, "errors": [], "warnings": []}
            })

        if raw_cmd.startswith("/"):
            parts = raw_cmd.split()
            action = parts[0].lower() if parts else ""

            # ==============================================================================
            # ROUTE A: TEMPLATE AND CBV GENERATION
            # ==============================================================================
            if action == "/page":
                if len(parts) < 3:
                    return JsonResponse({
                        "status": "success", "minion_log": "Syntax: /page <app_name> <page_name> [visibility]",
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
                        "status": "success", "minion_log": f"Forge halted: {res.get('message')}",
                        "validation": {"valid": False, "errors": [res.get('message')], "warnings": []}
                    })
                
                # FIXED: Passed description positional parameter matching forge_registry schema
                asset = register_new_component(
                    path, f"{c_page}_layout", vis, "COMPILER_MODULE", 
                    f"Automated canvas layout template for {c_app} UI."
                )
                
                return JsonResponse({
                    "status": "success",
                    "minion_log": f"FORGE SUCCESS: {res.get('message')} (Postgres UUID: {str(asset.id)} -> Neo4j Node synchronized).",
                    "generated_code": f"<!-- Template located at: {path} -->\n",
                    "validation": {"valid": True, "errors": [], "warnings": []}
                })

            # ==============================================================================
            # ROUTE B: FUNCTIONAL API ENDPOINT GENERATION
            # ==============================================================================
            elif action == "/api":
                if len(parts) < 3:
                    return JsonResponse({
                        "status": "success", "minion_log": "Syntax: /api <app_name> <endpoint_name> [visibility]",
                        "validation": {"valid": False, "errors": ["Missing parameters"], "warnings": []}
                    })
                
                app = parts[1].lower().strip()
                endpoint = parts[2].lower().strip()
                vis = parts[3].lower().strip() if len(parts) > 3 else "private"
                
                c_app, c_endpoint, f_name = ApiSkeletonBuilder.clean_inputs(app, endpoint)
                path = f"{c_app}/views/{c_endpoint}_view.py"
                
                res = ApiSkeletonBuilder.forge_api(c_app, c_endpoint, vis)
                if res.get("status") == "error":
                    return JsonResponse({
                        "status": "success", "minion_log": f"Forge halted: {res.get('message')}",
                        "validation": {"valid": False, "errors": [res.get('message')], "warnings": []}
                    })
                
                # FIXED: Passed description positional parameter matching forge_registry schema
                asset = register_new_component(
                    path, f"{f_name}", vis, "ENTRY_POINT", 
                    f"Automated function-based JSON stream endpoint for {c_app} layer."
                )
                
                return JsonResponse({
                    "status": "success",
                    "minion_log": f"FORGE SUCCESS: {res.get('message')} (Postgres UUID: {str(asset.id)} -> Neo4j Node synchronized).",
                    "generated_code": f"# API Path registered: path('api/{c_endpoint}/', views.{f_name})\n",
                    "validation": {"valid": True, "errors": [], "warnings": []}
                })

            # ==============================================================================
            # ROUTE C: UNIVERSAL SURGICAL PURGE UTILITY
            # ==============================================================================
            elif action == "/destroy":
                if len(parts) < 3:
                    return JsonResponse({
                        "status": "success", "minion_log": "Syntax: /destroy <app_name> <component_name>",
                        "validation": {"valid": False, "errors": ["Missing parameters"], "warnings": []}
                    })
                
                app = parts[1].lower().strip()
                name = parts[2].lower().strip()
                
                page_path = f"templates/{app}/{name}.html"
                api_path = f"{app}/views/{name}_view.py"
                
                for target_path in [page_path, api_path]:
                    try:
                        asset = ComponentRegistry.objects.get(file_path=target_path)
                        if asset.locked:
                            return JsonResponse({
                                "status": "success", "minion_log": f"PURGE DENIED: '{name}' path is LOCKED.",
                                "validation": {"valid": True, "errors": [], "warnings": []}
                            })
                    except ComponentRegistry.DoesNotExist:
                        pass
                
                p_res = PageSkeletonBuilder.purge_page(app, name)
                a_res = ApiSkeletonBuilder.purge_api(app, name)
                
                ComponentRegistry.objects.filter(file_path=page_path).delete()
                ComponentRegistry.objects.filter(file_path=api_path).delete()
                
                return JsonResponse({
                    "status": "success",
                    "minion_log": f"SURGICAL WIPE SUCCESS. Templates: {p_res.get('message')} | APIs: {a_res.get('message')}",
                    "generated_code": f"# All local file branches erased for: {name}\n",
                    "validation": {"valid": True, "errors": [], "warnings": []}
                })

            else:
                return JsonResponse({
                    "status": "success", "minion_log": f"Unknown action: {action}",
                    "validation": {"valid": True, "errors": [], "warnings": []}
                })

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
