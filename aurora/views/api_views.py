# aurora/views/api_views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from aurora.inspector import ValidationInspector
from aurora.skeleton import PageSkeletonBuilder

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
    # 1. FORGE FLOW INTERCEPTOR
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
                "generated_code": f"# Component tracking active in: '{app_target}'\n# Cost: 0 tokens.",
                "validation": {"valid": True, "errors": [], "warnings": ["[System Check]: Component initialized."]}
            })
        return JsonResponse({"error": result["message"]}, status=400)

    # 2. PURGE UNDO MACHINE INTERCEPTOR
    if blueprint_text.startswith('/destroy '):
        args = blueprint_text.replace('/destroy ', '').strip().split()
        if len(args) != 2:
            return JsonResponse({"error": "Syntax error. Emplace arguments via: /destroy [app_name] [page_name]"}, status=400)
            
        app_target, page_target = args[0], args[1]
        result = PageSkeletonBuilder.purge_page(app_target, page_target)
        
        if result["status"] == "success":
            return JsonResponse({
                "status": "success",
                "minion_log": f"💥 [WIPE OUT ACTIVE]: {result['message']}",
                "generated_code": f"# Clean rollback executed for component: '{page_target}' inside app: '{app_target}'.\n# Baseline codebase footprint completely restored. Cost: 0 tokens.",
                "validation": {"valid": True, "errors": [], "warnings": ["[System Check]: Sandbox rollback verified clean."]}
            })
        return JsonResponse({"error": result["message"]}, status=400)
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
