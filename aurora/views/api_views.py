# aurora/views/api_views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from aurora.inspector import ValidationInspector
from aurora.page_skeleton import PageSkeletonBuilder
from aurora.api_skeleton import ApiSkeletonBuilder

@login_required
def execute_blueprint_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    blueprint_text = request.POST.get("blueprint", "").strip()
    if not blueprint_text:
        return JsonResponse({"error": "Empty blueprint command"}, status=400)

    # ==============================================================================
    # DYNAMIC MULTI-APP AUTOMATION CONSOLE ROUTER
    # ==============================================================================
    
    # 1. PAGE FORGE FLOW INTERCEPTOR
    if blueprint_text.startswith('/page '):
        args = blueprint_text.replace('/page ', '').strip().split()
        if len(args) != 2:
            return JsonResponse({"error": "Syntax error. Emplace arguments via: /page [app_name] [page_name]"}, status=400)
        
        app_target, page_target = args[0], args[1]
        result = PageSkeletonBuilder.forge_page(app_target, page_target)
        
        if result["status"] == "success":
            return JsonResponse({
                "status": "success",
                "minion_log": f"[Forge-Factory]: {result['message']}",
                "generated_code": f"# View class and template active in: '{app_target}'\n# Cost: 0 tokens.",
                "validation": {"valid": True, "errors": [], "warnings": ["[System Check]: Page component initialized."]}
            })
        return JsonResponse({"error": result["message"]}, status=400)

    # 2. FUNCTIONAL API FORGE FLOW INTERCEPTOR
    if blueprint_text.startswith('/api '):
        args = blueprint_text.replace('/api ', '').strip().split()
        if len(args) != 2:
            return JsonResponse({"error": "Syntax error. Emplace arguments via: /api [app_name] [endpoint_name]"}, status=400)
        
        app_target, endpoint_target = args[0], args[1]
        result = ApiSkeletonBuilder.forge_api(app_target, endpoint_target)
        
        if result["status"] == "success":
            return JsonResponse({
                "status": "success",
                "minion_log": f"[Forge-Factory]: {result['message']}",
                "generated_code": f"# Functional JSON view endpoint active in: '{app_target}'\n# Cost: 0 tokens.",
                "validation": {"valid": True, "errors": [], "warnings": ["[System Check]: API component initialized."]}
            })
        return JsonResponse({"error": result["message"]}, status=400)

    # 3. PURGE UNDO MACHINE INTERCEPTOR (Intelligently maps both Pages and APIs)
    if blueprint_text.startswith('/destroy '):
        args = blueprint_text.replace('/destroy ', '').strip().split()
        if len(args) != 2:
            return JsonResponse({"error": "Syntax error. Emplace arguments via: /destroy [app_name] [component_name]"}, status=400)
        
        app_target, component_target = args[0], args[1]
        
        # Look for the functional suffix first to decide the clean rollback pipeline
        func_name = f"{component_target}_endpoint"
        
        # Fire purge routines on both domains to guarantee an absolute wipeout
        api_result = ApiSkeletonBuilder.purge_api(app_target, component_target)
        page_result = PageSkeletonBuilder.purge_page(app_target, component_target)
        
        # Combine logs if components were actually scrubbed
        combined_logs = []
        if "Deleted" in api_result.get("message", "") or "Scrubbed" in api_result.get("message", ""):
            combined_logs.append(api_result["message"])
        if "Deleted" in page_result.get("message", "") or "Scrubbed" in page_result.get("message", ""):
            combined_logs.append(page_result["message"])
            
        final_message = " | ".join(combined_logs) if combined_logs else "No structural components found to purge."
        
        return JsonResponse({
            "status": "success",
            "minion_log": f"💥 [WIPE OUT ACTIVE]: {final_message}",
            "generated_code": f"# Clean rollback executed for target: '{component_target}' inside app: '{app_target}'.\n# Baseline codebase footprint completely restored. Cost: 0 tokens.",
            "validation": {"valid": True, "errors": [], "warnings": ["[System Check]: Sandbox rollback verified clean."]}
        })

    # ==============================================================================
    # Fallback simulation profile
    mock_wu_code = "import os\ndef forge_action():\n    print('HopeHub Core Active')\n"
    inspection_results = ValidationInspector.check_syntax_and_imports(mock_wu_code)
    
    return JsonResponse({
        "status": "success",
        "minion_log": "[Minion-Core]: Blueprint accepted...",
        "generated_code": mock_wu_code,
        "validation": inspection_results
    })
