import os
import json
import logging
from datetime import timezone as datetime_timezone # Absolute native UTC reference
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from ..models import Document, Content

# Setup structured file and terminal logger
logger = logging.getLogger("aurora.sessions")
logger.setLevel(logging.INFO)

# Hardcoded text staging path limit
BRIEF_FILE_PATH = os.path.join(os.getcwd(), 'core_logic/staging/daily_brief.txt')

@csrf_exempt
@require_POST
def start_online_session(request):
    """
    Initialize an online session and perform necessary setup tasks.
    """
    session_start_time = timezone.now()
    logger.info("Session sequence initiated.")
    print(f"\n🚀 [START SESSION] Initialization triggered at {session_start_time.isoformat()}")
    
    try:
        # --- 0. DECOUPLED AUTHENTICATION INTERCEPT ---
        if not request.user.is_authenticated:
            print("❌ [STAGE 0 FAIL] Terminating transaction. Unauthenticated headless client request.")
            return JsonResponse({'success': False, 'error': 'Unauthorized entry. Valid token or login required.'}, status=401)

        # --- 1. CORE LIBRARY INTERCEPT CHECK ---
        print("🔍 [STAGE 1] Loading minion array local dependencies...")
        try:
            from core_logic.minion_array import run_8b_translation
            print("✅ [STAGE 1] run_8b_translation successfully imported.")
        except ImportError as imp_err:
            print(f"❌ [CRITICAL IMP] Failed to import minion array logic: {str(imp_err)}")
            logger.error(f"ImportError in minion_array execution: {str(imp_err)}")
            return JsonResponse({'success': False, 'error': f"Internal environment import failure: {str(imp_err)}"}, status=500)

        # --- 2. EXTRACT PAYLOAD DATA ---
        print("🔍 [STAGE 2] Checking incoming request payload types...")
        user_id = request.user.username.lower()
        raw_content = ""
        
        try:
            if request.body:
                json_payload = json.loads(request.body)
                raw_content = json_payload.get('brief_content', '').strip()
                user_id = json_payload.get('user_id', user_id).lower()
                print(f"📥 [STAGE 2] Extracted valid headless JSON data. Payload length: {len(raw_content)} chars.")
        except json.JSONDecodeError:
            print("⚠️ [STAGE 2] Request body is not JSON. Falling back to traditional POST form parsing.")
            raw_content = request.POST.get('brief_content', '').strip()

        # Extract context from local staging file if no direct text override exists
        if not raw_content:
            print(f"📂 [STAGE 2] Reading raw content from local disk matrix: {BRIEF_FILE_PATH}")
            if os.path.exists(BRIEF_FILE_PATH):
                with open(BRIEF_FILE_PATH, 'r', encoding='utf-8') as f:
                    raw_content = f.read().strip()
                print(f"💾 [STAGE 2] Read {len(raw_content)} chars from brief staging file.")
            else:
                print(f"⚠️ [STAGE 2] Local disk file missing at: {BRIEF_FILE_PATH}")

        if not raw_content:
            print("❌ [STAGE 2 FAIL] Handshake execution aborted. Daily brief source payload text is blank.")
            return JsonResponse({'success': False, 'error': 'Daily brief target text data payload is empty.'}, status=400)

        # --- 3. COMPUTE PLANNING DURATION ---
        print("🔍 [STAGE 3] Computing offline session planning duration metrics...")
        planning_duration_seconds = 0
        if os.path.exists(BRIEF_FILE_PATH):
            file_meta_stat = os.stat(BRIEF_FILE_PATH)
            # FIXED: Extracted direct timezone-aware object without wrapping inside make_aware
            last_modified = timezone.datetime.fromtimestamp(file_meta_stat.st_mtime, datetime_timezone.utc)
            planning_duration_seconds = max(0, int((session_start_time - last_modified).total_seconds()))
            print(f"⏱️ [STAGE 3] Calculated offline planning duration: {planning_duration_seconds} seconds.")

        # --- 4. CONDENSE TEXT VIA 8B MINION (TOKEN SAVER ROUTINE) ---
        print("🔍 [STAGE 4] Routing raw text chunk directly to local Llama 8B translation worker matrix...")
        try:
            dense_abstract, objectives_json = run_8b_translation(raw_content)
            print("✅ [STAGE 4] 8B translation model execution finalized successfully.")
            logger.debug(f"Abstract generated: {dense_abstract[:40]}...")
        except Exception as model_err:
            print(f"❌ [STAGE 4 CRASH] Local model inference broke: {str(model_err)}")
            return JsonResponse({'success': False, 'error': f"Local 8B Model inference anomaly: {str(model_err)}"}, status=502)

        # --- 5. COMMIT LOGGING METRICS TO POSTGRESQL (EAV TARGETS) ---
        print("🔍 [STAGE 5] Committing structured operational tables data to PostgreSQL targets...")
        try:
            doc_entry = Document.objects.create(
                title=f"Daily Brief - {session_start_time.strftime('%Y-%m-%d')}",
                created_at=session_start_time
            )
            Content.objects.get_or_create(document=doc_entry, content=f"dense_abstract: {dense_abstract}")
            Content.objects.get_or_create(document=doc_entry, content=f"objectives_json: {objectives_json}")
            Content.objects.get_or_create(document=doc_entry, content=f"planning_duration_seconds: {planning_duration_seconds}")
            print(f"📁 [STAGE 5] Successfully created Document ID {doc_entry.pk} inside Postgres.")
        except Exception as db_err:
            print(f"❌ [STAGE 5 CRASH] Database commit tracking failure: {str(db_err)}")
            return JsonResponse({'success': False, 'error': f"Database layer state error: {str(db_err)}"}, status=500)

        # --- 6. SECURELY ERASE LOCAL TEMPORARY FILE STAGING ZONE ---
        print("🔍 [STAGE 6] Clearing local temporary disk staging workspace...")
        if os.path.exists(BRIEF_FILE_PATH):
            with open(BRIEF_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write("")
            print("🧹 [STAGE 6] Local files erased securely.")

        # --- 7. RECONSTRUCT THE 5-DAY CONTEXT & SYSTEM ENVELOPE ---
        print("🔍 [STAGE 7] Querying recent abstract tables to collect historical context...")
        historical_summaries = []
        try:
            recent_docs = Document.objects.filter(title__contains="Daily Brief").order_by('-created_at')[:5]
            if recent_docs.exists():
                for doc in reversed(recent_docs):
                    content_records = Content.objects.filter(document=doc)
                    for record in content_records:
                        if record.content and record.content.startswith("dense_abstract:"):
                            abstract_text = record.content.replace("dense_abstract:", "").strip()
                            date_string = doc.created_at.strftime('%Y-%m-%d')
                            historical_summaries.append(f"--- HISTORICAL BRIEF: {date_string} ---\n{abstract_text}")
                print(f"📚 [STAGE 7] Context extraction ready. Packed {len(historical_summaries)} historical abstracts.")
            else:
                print("ℹ️ [STAGE 7 INFO] No historical daily brief rows found in database. Initializing baseline context.")
        except Exception as context_err:
            print(f"⚠️ [STAGE 7 WARNING] Context collector bypassed: {str(context_err)}")
            historical_summaries = ["No historical summaries discoverable in this database environment."]

        # Combine text elements safely
        if len(historical_summaries) > 0:
            formatted_history = "\n\n".join(historical_summaries)
        else:
            formatted_history = "No previous session context logged."

        # Build clean structural prompt string without any nested ternary quote tricks
        system_runtime_instructions = (
            f"You are Wu, Lead Architect. Speaking to: {user_id}.\n"
            f"Session Initialization: {session_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            "ACTIVE WORKSPACE ENVIRONMENT PROTOCOLS:\n"
            "1. Coordinate file updates using headless worker array loops.\n"
            "2. Track the execution milestones outlined in objectives_json precisely.\n\n"
            f"== RECENT HISTORICAL SESSIONS SUMMARY CONTEXT ==\n{formatted_history}\n\n"
            f"== TODAY'S TARGET WORKSPACE OBJECTIVES ==\n{dense_abstract}"
        )

        print("🏁 [FINALIZE] Headless startup transaction complete. Handing clean JSON payload to network pipeline.\n")
        return JsonResponse({
            'success': True,
            'session_status': 'active',
            'session_start_time': session_start_time.isoformat(),
            'dense_abstract': dense_abstract,
            'objectives': objectives_json,
            'system_prompt_envelope': system_runtime_instructions
        })

    except Exception as e:
        print(f"💥 [SYSTEM EXCEPTION] General unhandled runtime breakdown: {str(e)}")
        logger.critical(f"Unhandled operational trace anomaly: {str(e)}", exc_info=True)
        return JsonResponse({'success': False, 'error': f"Unhandled layout matrix breakdown: {str(e)}"}, status=500)
