import json
import logging
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ..models import DeltaNote

logger = logging.getLogger("aurora.delta_notes")
logger.setLevel(logging.INFO)

@csrf_exempt
@require_POST
def create_delta_note_api(request):
    """
    Headless API Endpoint to capture Delta's plain-English journal entries offline.
    Commits raw text strings directly to PostgreSQL without triggering AI processing.
    """
    timestamp = timezone.now()
    print(f"\n📝 [DELTA NOTE API] Intercepting raw offline journal payload at {timestamp.isoformat()}")

    try:
        # --- 0. SECURITY BOUNDARY GUARDRAIL ---
        if not request.user.is_authenticated:
            print("❌ [DELTA NOTE FAIL] Unauthorized headless entry transaction rejected.")
            return JsonResponse({'success': False, 'error': 'Authentication required.'}, status=401)

        # --- 1. EXTRACT DATA PAYLOAD ---
        raw_text = ""
        if request.body:
            try:
                json_payload = json.loads(request.body)
                raw_text = json_payload.get('raw_text', '').strip()
            except json.JSONDecodeError:
                pass
        
        if not raw_text:
            raw_text = request.POST.get('raw_text', '').strip()

        if not raw_text:
            print("❌ [DELTA NOTE FAIL] Rejected empty text string array.")
            return JsonResponse({'success': False, 'error': 'Note text cannot be empty.'}, status=400)

        # --- 2. RELATIONAL DATABASE COMMIT ---
        note_record = DeltaNote.objects.create(
            user=request.user,
            raw_text=raw_text,
            is_processed=False
        )
        print(f"✅ [DELTA NOTE SUCCESS] Raw text successfully committed to Note ID {note_record.pk}.")
        
        return JsonResponse({
            'success': True,
            'note_id': note_record.pk,
            'is_processed': note_record.is_processed,
            'message': 'Journal note saved securely to the offline database matrix.'
        }, status=201)

    except Exception as e:
        print(f"💥 [DELTA NOTE CRASH] Unhandled exception in intake pipeline: {str(e)}")
        logger.critical(f"Note entry crash trace: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
