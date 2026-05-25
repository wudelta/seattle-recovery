import os
import json
import logging
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from ..models import DeltaNote, DeltaChange, DeltaDirective  # Models fully aligned

logger = logging.getLogger("aurora.sessions")
logger.setLevel(logging.INFO)

@csrf_exempt
@require_POST
def start_online_session(request):
    """
    Delta Process Flow Headless Session Startup Engine.
    Processes offline brain dumps via 8B worker, pulls review states, and configures Wu.
    """
    session_start_time = timezone.now()
    print(f"\n🚀 [START SESSION] Delta Process Flow triggered at {session_start_time.isoformat()}")

    try:
        # --- 0. AUTHENTICATION PROTECTION matrix ---
        if not request.user.is_authenticated:
            print("❌ [STAGE 0 FAIL] Unauthenticated client request intercepted.")
            return JsonResponse({'success': False, 'error': 'Unauthorized entry.'}, status=401)

        user = request.user
        user_id = user.username.lower()

        # --- 1. MINION ARRAY IMPORT CHECK ---
        print("🔍 [STAGE 1] Loading minion translation library dependencies...")
        try:
            from core_logic.minion_array import run_8b_translation
            print("✅ [STAGE 1] run_8b_translation imported successfully.")
        except ImportError as imp_err:
            print(f"❌ [CRITICAL IMP] Environment missing worker scripts: {str(imp_err)}")
            return JsonResponse({'success': False, 'error': 'Internal system engine missing module.'}, status=500)

        # --- 2. COMPILE UNPROCESSED OFFLINE NOTES ---
        print("🔍 [STAGE 2] Querying PostgreSQL for raw unprocessed DeltaNotes...")
        unprocessed_notes = DeltaNote.objects.filter(user=user, is_processed=False).order_by('created_at')
        notes_count = unprocessed_notes.count()
        print(f"📥 [STAGE 2] Discovered {notes_count} pending offline notes inside database.")

        # --- 3. INITIATE 8B MINION INTERPRETATION LOOP ---
        if notes_count > 0:
            print("🔍 [STAGE 3] Dispatching text sequences to Llama 8B translation worker array...")
            for note in unprocessed_notes:
                print(f"🔍 [STAGE 3.1] Processing Note ID {note.id} bytes...")
                try:
                    dense_abstract, objectives_json = run_8b_translation(note.raw_text)
                    
                    # Wu Note: 8B Minion splits input to generate a PENDING_REVIEW change row
                    DeltaChange.objects.create(
                        user=user,
                        assigned_to='MINION',
                        minion_type='CORE_PY',  # Defaults parsing target to Python core layer
                        dense_instructions=f"Abstract: {dense_abstract}\nObjectives: {objectives_json}",
                        status='PENDING_REVIEW'
                    )
                    
                    # Commit step tracking state change
                    note.is_processed = True
                    note.processed_at = session_start_time
                    note.save()
                    print(f"✅ [STAGE 3.2] Note ID {note.id} securely updated to is_processed=True.")
                except Exception as model_err:
                    print(f"❌ [STAGE 3 CRASH] Note ID {note.id} inference loop failure: {str(model_err)}")
                    continue
        else:
            print("ℹ️ [STAGE 3] Database log contains zero unprocessed tokens. Skipping.")

        # --- 4. ACCUMULATE HEADLESS REVIEW BLOCKS ---
        print("🔍 [STAGE 4] Assembling Delta's Human-in-the-Loop approval components...")
        pending_changes = DeltaChange.objects.filter(user=user, status='PENDING_REVIEW')
        pending_directives = DeltaDirective.objects.filter(user=user, is_approved=False)

        # --- 5. EXTRACT DESIGN DIRECTIVES TO GUIDE WU ---
        print("🔍 [STAGE 5] Injecting approved systemic boundary guardrails into current thread...")
        active_directives = DeltaDirective.objects.filter(
            user=user, 
            is_approved=True, 
            assigned_to__in=['WU', 'BOTH']
        )
        
        directives_payload = []
        for directive in active_directives:
            directives_payload.append(f"[{directive.directive_name}]: {directive.dense_instructions}")
        formatted_directives = "\n".join(directives_payload) if directives_payload else "No current systemic rules loaded."

        # --- 6. ASSEMBLE DECOUPLED RUNTIME PROMPT ENVELOPE ---
        print("🔍 [STAGE 6] Engineering system instruction envelope matrix...")
        system_runtime_instructions = (
            f"You are Wu, Lead Architect Core (70B). Cooperating with human operator Delta (User: {user_id}).\n"
            f"Active Workspace Context Clock: {session_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "== APPROVED COGNITIVE DIRECTIVES IN MEMORY ==\n"
            f"{formatted_directives}\n\n"
            "MANDATORY TRANSITION RULE:\n"
            "Do not execute any local code mutations until Delta issues an HTTP status='APPROVED' command sequence."
        )

        print("✅ [FINALIZE] Session startup successfully compiled with heavy logging validation.\n")
        return JsonResponse({
            'success': True,
            'session_status': 'active',
            'notes_processed_count': notes_count,
            'review_deck': {
                'changes': [
                    {
                        'id': c.id, 
                        'app_affected': c.app_affected, 
                        'assigned_to': c.assigned_to, 
                        'minion_type': c.minion_type, 
                        'instructions': c.dense_instructions
                    } for c in pending_changes
                ],
                'directives': [
                    {
                        'id': d.id, 
                        'name': d.directive_name, 
                        'assigned_to': d.assigned_to, 
                        'instructions': d.dense_instructions
                    } for d in pending_directives
                ]
            },
            'system_prompt_envelope': system_runtime_instructions
        }, status=200)

    except Exception as e:
        print(f"💥 [SYSTEM EXCEPTION] Catastrophic operational breakdown: {str(e)}")
        return JsonResponse({'success': False, 'error': f"Headless execution exception: {str(e)}"}, status=500)
