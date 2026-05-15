import os
import json
import markdown
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from groq import Groq
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# Consolidated Models and Serializers
from .models import Document, Metadata, Content
from .serializers import DocumentSerializer, MetadataSerializer, ContentSerializer

# Consolidated Core Graph Logic Imports
from core_logic.memory import save_memory, get_recent_context, create_resource, summarize_session
from core_logic.sessions import start_session, end_session, log_manual_time

@csrf_exempt
def wu_director(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')
        return JsonResponse({
            "response": f"Director here. I received: '{user_message}'. Connection stable.",
            "status": "online"
        })

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@user_passes_test(lambda u: u.is_superuser)
def dashboard(request):
    """The command center for Delta."""
    return render(request, 'delta_chat/dashboard.html')

@csrf_exempt
def chat_api(request):
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
        "1. If Delta requests bulk layouts, structural templates, style rules, or scripts, output EXACTLY: "
        "[DELEGATE: <minion_module> | TASK: <instruction>] (where minion_module is generate_html, generate_css, or generate_js).\n"
        "2. IF DELTA SPECIFIES A LOCAL FILE PATH, you MUST append the file path tracking parameter right inside the brackets like this: "
        "[DELEGATE: generate_html | TASK: <instruction> | FILE: <relative_file_path>].\n"
        "3. If Delta passes a Python file crash tracker, a terminal exception line, or an absolute traceback, output EXACTLY: "
        "[DELEGATE: patch_debugger | TASK: <pasted error or traceback description>].\n"
        "Do not write code blocks yourself when utilizing these structural tags."
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

        # --- DELEGATION SWITCH ROUTE ---
        if answer.startswith("[DELEGATE:"):
            try:
                # Safely parse worker_type and task out of token string without replacement bugs
                header_segment = answer.split("|")[0]  # Extracts "[DELEGATE: generate_html "
                worker_part = header_segment.split(":")[-1].strip().lower() # Extracts "generate_html"
                
                # Extract the execution task instructions cleanly
                task_details = answer.split("TASK:")[-1].split("]")[0].strip()
                
                # Import dynamic module traffic cop router
                from .minion_array.router import dispatch_to_minion
                minion_code = dispatch_to_minion(
                    worker_type=worker_part, 
                    task_details=task_details, 
                    fallback_context=""
                )
                
                # Persistent logs written to partitioned Aurora space
                save_memory(user_id, user_text, "user", session_id, project="aurora")
                save_memory(user_id, f"Delegated task to {worker_part}: {task_details}", "assistant", session_id, project="aurora")
                
                return JsonResponse({
                    "reply": minion_code,
                    "tokens_left": new_limit,
                    "token_ceiling": max_ceiling,
                    "active_model": f"Minion Array ({worker_part})"
                })
            except Exception as minion_error:
                answer = f"Delegation routing pipeline anomaly: {str(minion_error)}"
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

@csrf_exempt
def manual_time_log_view(request):
    if request.method == "POST":
        user_id = request.user.username if request.user.is_authenticated else "Delta"
        hours = request.POST.get('hours')
        note = request.POST.get('note')
        log_manual_time(user_id, hours, note)
        return JsonResponse({'status': 'success', 'message': f'Logged {hours} manual hours.'})

@csrf_exempt
def end_session_view(request):
    user_id = request.user.username.lower() if request.user.is_authenticated else "delta"
    session_id = request.session.get('current_session_id')
    
    print(f"--- MANUAL SHUTDOWN TRIPPED: CLEAN SWEEP FOR {user_id} ---")
    summary_result = summarize_session(user_id)
    
    if session_id:
        duration = end_session(session_id)
        del request.session['current_session_id']
    else:
        duration = "No active SQL session found. Cleaned graph state anyway."
        
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.method == "POST":
        return JsonResponse({
            'status': 'success', 
            'duration': duration, 
            'summary': summary_result
        })
        
    return render(request, 'delta_chat/session_closed.html', {
        'summary': summary_result, 
        'duration': duration
    })

# Documentation API Views
class DocumentView(APIView):
    def get(self, request):
        documents = Document.objects.all()
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MetadataView(APIView):
    def get(self, request):
        metadata = Metadata.objects.all()
        serializer = MetadataSerializer(metadata, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = MetadataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContentView(APIView):
    def get(self, request):
        content = Content.objects.all()
        serializer = ContentSerializer(content, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = ContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
