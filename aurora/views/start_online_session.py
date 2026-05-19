import os
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from ..models import Document, Content

# Hardcoded text staging path limit
BRIEF_FILE_PATH = os.path.join(os.getcwd(), 'core_logic/staging/daily_brief.txt')

@login_required
@require_POST
def start_online_session(request):
    print("🤖 [start_online_session] Action triggered.")
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
