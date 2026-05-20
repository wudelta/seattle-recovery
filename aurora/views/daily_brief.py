import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect

FILE_PATH = os.path.join(settings.BASE_DIR, 'core_logic', 'staging', 'daily_brief.txt')

@csrf_protect
def daily_brief_view(request):
    """
    STANDALONE BRIEF WORKSPACE: Full-page text file controller.
    """
    # --- HANDLE SAVE WORKFLOW (POST) ---
    if request.method == 'POST':
        updated_text = request.POST.get('brief_text', '')
        
        # Save updates directly to your local hard drive offline
        os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(updated_text)
            
        # Redirect back to the same workspace to prevent double-submit loops
        return redirect('aurora:aurora_daily_brief')

    # --- HANDLE READ/LOAD WORKFLOW (GET) ---
    else:
        # Create an empty template text file if missing from disk
        if not os.path.exists(FILE_PATH):
            os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
            with open(FILE_PATH, 'w', encoding='utf-8') as f:
                f.write("SYSTEM STATUS SUMMARY:\n- Start entering your telemetry documentation here...")
        
        # Pull the file content
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            file_content = f.read()
            
        return render(request, "aurora/daily_brief.html", {"brief_content": file_content})
