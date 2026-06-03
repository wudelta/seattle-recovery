# aurora/views/api_views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from aurora.inspector import ValidationInspector

@login_required
def execute_blueprint_api(request):
    """
    Handles asynchronous blueprint injection commands from the dashboard terminal.
    Executes real-time AST/Pyflakes validations on generated code strings.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
        
    blueprint_text = request.POST.get("blueprint", "").strip()
    if not blueprint_text:
        return JsonResponse({"error": "Empty architectural instruction blueprint"}, status=400)
        
    # Mock payload simulation representing Wu's script output generation cycle.
    # This will securely connect directly to your local generation pipelines.
    mock_wu_code = "import os\n\ndef forge_action():\n    print('HopeHub Core Live')\n"
    
    # Execute offline quality assurance and linting checks automatically
    inspection_results = ValidationInspector.check_syntax_and_imports(mock_wu_code)
    
    return JsonResponse({
        "status": "success",
        "minion_log": "[Minion-Core]: Blueprint accepted. Parsing syntax structure...",
        "generated_code": mock_wu_code,
        "validation": inspection_results
    })
