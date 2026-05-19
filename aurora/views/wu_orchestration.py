import os
import json
import markdown
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from groq import Groq
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test, login_required

from core_logic.memory import save_memory, get_recent_context, create_resource, summarize_session
from core_logic.sessions import start_session

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@csrf_exempt
def chat_api(request):
    print(f"\n📥 [INCOMING CHAT] Query received: {request}")

    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
        
    user_id = request.user.username.lower() if request.user.is_authenticated else "delta"
    user_text = request.POST.get('text', '').strip()
    session_id = request.session.get('current_session_id')

    # 1. RESOURCE DETECTOR (JSON Blobs)
    if user_text.startswith('{') and user_text.endswith('}'):
        try:
            resource_data = json.loads(user_text)
            if "category" in resource_data:
                create_resource(user_id, resource_data)
                return JsonResponse({
                    "reply": "📦 **Resource Node Created.** Entry documented in the graph.",
                    "tokens_left": cache.get(f'tokens_{user_id}', 18000),
                    "token_ceiling": cache.get(f'token_ceiling_{user_id}', 18000),
                    "active_model": "System (Local)"
                })
        except json.JSONDecodeError:
            pass

    # Session Handshake
    if not request.session.session_key:
        request.session.create()
    if not session_id:
        session_id = start_session(user_id)
        request.session['current_session_id'] = session_id

    # =========================================================================
    # 🪐 CONVERSATION PROTOCOL GUARD (PRE-LLM INTERCEPTOR)
    # =========================================================================
    clean_text = user_text.lower().strip("?!. ")
    if clean_text in ["are you there", "hi", "hello", "hey", "status check", "yo", "u there"]:
        print("🛡️ [GUARD] Conversational ping caught. Bypassing API calls completely.")
        return JsonResponse({
            "reply": "I am right here, Delta. Core systems are operational and listening.",
            "tokens_left": int(cache.get(f'tokens_{user_id}', 12000)),
            "token_ceiling": int(cache.get(f'token_ceiling_{user_id}', 12000)),
            "active_model": "System Core (Direct)"
        })
    # =========================================================================

    # 2. HARD COGNITIVE PROTECTION OVERHEAT CHECK
    tokens_remaining = int(cache.get(f'tokens_{user_id}', 12000))
    token_ceiling = int(cache.get(f'token_ceiling_{user_id}', 12000))
    
    if tokens_remaining < 1200:
        print("Fuel critical. Auto-triggering Janitor cleanup...")
        summary = summarize_session(user_id)
        return JsonResponse({
            "reply": f"⚠️ **Groq Rate Limit Critical.** Fuel ({tokens_remaining:,}) dropped below safety limits. System flushed history to preserve quotas. **Latest State Saved to Disk:**\n\n{summary}",
            "tokens_left": tokens_remaining,
            "token_ceiling": token_ceiling,
            "active_model": "System Flash-Clear"
        })

    # 3. FORCE HIGH CAPACITY ENGINE
    active_model = "llama-3.3-70b-versatile"
    model_label = "Architect (70B)"

    # 4. CONTEXT & SYSTEM RETRIEVAL (Partitioned strictly to Aurora ecosystem)
    history = get_recent_context(user_id, limit=10, project="aurora")

    system_instructions = (
        f"You are Wu, the lead architect. Speaking to: {user_id}. "
        f"Current Brain: {model_label}. Active Ecosystem Workspace: AURORA ENGINE BUILDER. "
        "Mission: Provide practical, high-level structural aid for the application builder itself. "
        "CRITICAL PROTOCOLS FOR DELEGATION:\n"
        "1. You are strictly forbidden from outputting delegation tags unless the user explicitly typing the word 'DELEGATE' in their query.\n"
        "2. If and only if 'DELEGATE' is in the user query, and they request a layout or script, output EXACTLY: "
        "[DELEGATE: <minion_module> | TASK: <instruction>]\n"
        "3. Look for matching filenames inside minion_array if provided. If no matching minion matches the request context, output a friendly message stating the capability does not exist yet."
    )
    
    messages = [{"role": "system", "content": system_instructions}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    try:
        # 5. EXECUTE VIA RAW RESPONSE FOR LIVE QUOTA READING
        chat_completion = client.chat.completions.with_raw_response.create(
            messages=messages,
            model=active_model,
            temperature=0.1
        )
        
        # 6. EXTRACT HEADERS & SET CACHE
        response_data = chat_completion.parse()
        new_limit = int(chat_completion.headers.get('x-ratelimit-remaining-tokens', tokens_remaining))
        max_ceiling = int(chat_completion.headers.get('x-ratelimit-limit-tokens', token_ceiling))
        cache.set(f'tokens_{user_id}', new_limit, 3600)
        cache.set(f'token_ceiling_{user_id}', max_ceiling, 3600)
        
        answer = response_data.choices[0].message.content

        # --- DELEGATION SWITCH ROUTE REFACTOR INSIDE aurora/views.py ---
        if answer.startswith("[DELEGATE:"):
            try:
                header_segment = answer.split("|")[0]
                worker_part = header_segment.split(":")[-1].strip().lower().replace("generate_", "")

                # 🟢 UPGRADED FUZZY MATCHERS
                alive_minions = [m for m in scan_available_minions()]
                matched_minion_file = None
                
                for file_name in alive_minions:
                    clean_file = file_name.lower()
                    # Checks if 'js' is in 'generate_js' OR if 'generate_js' contains 'js'
                    if worker_part in clean_file or clean_file in worker_part:
                        matched_minion_file = file_name
                        break
        
                if not matched_minion_file:
                    print(f"❌ [ROUTING ERROR] Wu targeted '{worker_part}', but no matching file exists in minion_array.")
                    return JsonResponse({
                        "reply": f"Delta, I attempted to delegate to **{worker_part}**, but I could not find a matching script in your `minion_array/` directory. Available scripts are: `{alive_minions}`. Should we create it?",
                        "tokens_left": new_limit,
                        "token_ceiling": max_ceiling,
                        "active_model": model_label
                    })

                task_details = answer.split("TASK:")[-1].split("]")[0].strip()
                
                # Import the dynamic module traffic cop router
                from .minion_array.router import dispatch_to_minion
                
                # Call the router with headless=True to protect your disk files
                minion_payload = dispatch_to_minion(
                    worker_type=worker_part,
                    task_details=task_details,
                    fallback_context="",
                    headless=True # <-- Forces in-memory execution tracking
                )
                
                # Persistent memory sync logs written to partitioned Aurora space
                save_memory(user_id, user_text, "user", session_id, project="aurora")
                save_memory(user_id, f"Delegated task to {worker_part}: {task_details}", "assistant", session_id, project="aurora")
                
                # Return a structured JSON response to your frontend web panel
                return JsonResponse({
                    "status": minion_payload.get("status", "pending_approval"),
                    "worker_type": minion_payload.get("worker_type", worker_part),
                    "target_file_path": minion_payload.get("target_file_path", "unknown"),
                    "raw_code": minion_payload.get("raw_code", ""),
                    "validation_logs": minion_payload.get("validation_logs", ""),
                    "tokens_left": new_limit,
                    "token_ceiling": max_ceiling,
                    "active_model": f"Minion Array ({worker_part})"
                })
                
            except Exception as minion_error:
                return JsonResponse({"status": "error", "message": f"Delegation pipeline anomaly: {str(minion_error)}"}, status=500)
        # --- END OF DELEGATION SWITCH ---

        # 7. PERSIST (Dual-Write to Neo4j partitioned space)
        save_memory(user_id, user_text, "user", session_id, project="aurora")
        save_memory(user_id, answer, "assistant", session_id, project="aurora")

        # 8. FORMAT & RESPOND
        formatted_answer = markdown.markdown(answer, extensions=['fenced_code', 'codehilite'])
        return JsonResponse({
            "reply": formatted_answer,
            "tokens_left": new_limit,
            "token_ceiling": max_ceiling,
            "active_model": model_label
        })

    except Exception as e:
        print(f"🔴 Groq Gateway Error: {str(e)}. Executing Emergency Sweep...")
        summary_result = summarize_session(user_id)
        return JsonResponse({
            "reply": f"🔴 **Groq API Gateway Limit Exceeded.** The system circuit breaker swept your database to clear the block. **PROJECT_STATE.md Updated.** \n\n**Summary:** {summary_result}",
            "tokens_left": 0,
            "token_ceiling": token_ceiling,
            "active_model": "Circuit Breaker Active"
        })

# Hardcoded text staging path limit
BRIEF_FILE_PATH = os.path.join(os.getcwd(), 'core_logic/staging/daily_brief.txt')

@login_required
def console_dashboard(request):
    print(f"\n📥 [console_dashboard] Query received: {request}")
    """
    Renders the central core dashboard cockpit, pre-loading 
    the un-ingested offline daily brief plain-text staging block.
    """
    local_brief_content = ""
    
    # Read the current physical offline file state to display on screen
    if os.path.exists(BRIEF_FILE_PATH):
        with open(BRIEF_FILE_PATH, 'r', encoding='utf-8') as f:
            local_brief_content = f.read()
            
    context = {
        'local_brief_content': local_brief_content,
        'session_active': False,  # Keeps the staging panel visible on initial load
    }
    # FIXED: Swapped console.html out for dashboard.html to target your pristine template asset
    return render(request, 'aurora/dashboard.html', context)

@user_passes_test(lambda u: u.is_superuser)
def dashboard(request):
    print(f"\n📥 [dashboard] Query received: {request}")
    """The command center for Delta."""
    return render(request, 'aurora/dashboard.html')

def scan_available_minions():
    """Dynamically lists all minion files in the aurora/minion_array directory."""
    aurora_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    minions_dir = os.path.join(aurora_dir, "minion_array") 
    minions = []
    
    try:
        if os.path.exists(minions_dir):
            for filename in os.listdir(minions_dir):
                if filename.endswith(".py") and filename != "__init__.py":
                    # Grab index 0 to get the clean module name string
                    clean_name = os.path.splitext(filename)[0]
                    minions.append(clean_name)
        else:
            print(f"⚠️ [SCANNER] Minion directory not found at: {minions_dir}")
    except Exception as e:
        print(f"⚠️ [SCANNER] Failed to scan minion directory: {e}")
        
    return minions

def determine_orchestration_path(user_message):
    """
    Evaluates whether the user explicitly initiated a delegation.
    Returns: (action_state, context_payload)
    """
    # 1. Hard Check: If 'DELEGATE' isn't explicitly typed, Wu MUST handle it himself
    if "DELEGATE" not in user_message:
        print("💬 [CORE EXECUTION] Direct request. Wu retaining full control.")
        return "wu_self", None

    print("🔀 [DELEGATION PROTOCOL] 'DELEGATE' keyword captured. Scanning available tools...")
    
    # 2. Grab the live list of available files from our dynamic scanner
    available_minions = scan_available_minions() # Returns clean filenames like ['minion_clicks', 'commit_file_view']
    message_lower = user_message.lower()
    
    # 3. Match user hints to scanned file names
    for minion in available_minions:
        # Strip prefixes/suffixes to create a loose keyword token (e.g. 'minion_clicks' -> 'clicks')
        keyword_token = minion.replace("minion_", "").replace("_view", "")
        
        if keyword_token in message_lower:
            print(f"🎯 [MATCH FOUND] Context matched minion file: '{minion}.py'")
            return "minion_handoff", minion

    # 4. Fallback Error: You said DELEGATE, but Wu couldn't find a file matching your keyword hint
    print("❌ [MATCH FAILED] 'DELEGATE' requested, but no matching minion file discovered.")
    return "handoff_failed", available_minions
