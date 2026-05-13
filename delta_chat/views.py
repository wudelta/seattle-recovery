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

# Consolidated Core Graph Logic Imports (All active components restored)
from core_logic.memory import save_memory, get_recent_context, create_resource, summarize_session
from core_logic.sessions import start_session, end_session, log_manual_time

@csrf_exempt # Allows the Flask Lifeboat to post to Django without CSRF tokens
def wu_director(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        # This is where Wu's logic will eventually live. 
        # For now, we just echo back to test the connection.
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
        return JsonResponse({
            "reply": f"⚠️ **Groq Rate Limit Critical.** Fuel ({tokens_remaining:,}) is below the 1,200 token safety runway. Please pause for 30 seconds to allow the bucket to refill.",
            "tokens_left": tokens_remaining,
            "token_ceiling": token_ceiling,
            "active_model": "System Lockout"
        })

    # 3. FORCE HIGH CAPACITY ENGINE
    active_model = "llama-3.3-70b-versatile"
    model_label = "Architect (70B)"

    # 4. CONTEXT & SYSTEM RETRIEVAL
    history = get_recent_context(user_id, limit=10) 
    system_instructions = (
        f"You are Wu, the lead architect. Speaking to: {user_id}. "
        f"Current Brain: {model_label}. "
        "Mission: Provide practical, high-level structural aid. "
        "CRITICAL PROTOCOL: If Delta asks you to generate bulk boilerplate code, write complex HTML designs, "
        "or fix simple style errors, DO NOT write the code yourself. Instead, delegate the task by outputting "
        "exactly this structured token format: [DELEGATE: HTML_MINION | TASK: <describe the component need here>]. "
        "Do not output anything else if you delegate."
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
                task_details = answer.split("TASK:")[1].replace("]", "").strip()
                
                from .minions import spawn_html_minion
                minion_code = spawn_html_minion(task_details)
                
                save_memory(user_id, user_text, "user", session_id)
                save_memory(user_id, f"Delegated task to Minion: {task_details}", "assistant", session_id)
                
                formatted_minion_reply = f"🤖 **Minion Task Executed Successfully:**\n\n```html\n{minion_code}\n```"
                return JsonResponse({
                    "reply": formatted_minion_reply,
                    "tokens_left": new_limit,
                    "token_ceiling": max_ceiling,
                    "active_model": "Minion Array (8B)"
                })
            except Exception as minion_error:
                answer = f"Delegation routing pipeline anomaly: {str(minion_error)}"
        # --- END OF DELEGATION SWITCH ---

        # 7. PERSIST (Dual-Write to Neo4j)
        save_memory(user_id, user_text, "user", session_id)
        save_memory(user_id, answer, "assistant", session_id)

        # 8. FORMAT & RESPOND
        formatted_answer = markdown.markdown(answer, extensions=['fenced_code', 'codehilite'])
        return JsonResponse({
            "reply": formatted_answer,
            "tokens_left": new_limit,
            "token_ceiling": max_ceiling,
            "active_model": model_label
        })

    except Exception as e:
        return JsonResponse({
            "reply": f"🔴 **Groq API Gateway Rate Limit Exceeded:** {str(e)}",
            "tokens_left": 0,
            "token_ceiling": token_ceiling,
            "active_model": "Rate Limit Hit"
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
    
    if session_id:
        duration = end_session(session_id)
        
        # NEW: The "Clean Sweep"
        print(f"--- CLOSING SESSION: SUMMARIZING WORK FOR {user_id} ---")
        summarize_session(user_id) 
        
        del request.session['current_session_id']
        return JsonResponse({'status': 'success', 'duration': duration})
    
    return JsonResponse({'status': 'error', 'message': 'No active session'}, status=400)

# Define our documentation views
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