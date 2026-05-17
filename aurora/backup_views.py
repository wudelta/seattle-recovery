# FILE: aurora/backup_views.py
"""
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T20:22:45.053688+00:00
 PROJECT ECOSYSTEM: AURORA
 FILE PATH: aurora/backup_views.py
 TECHNICAL MATRIX: Python Module. Exported Logic Components: dashboard, chat_api, manual_time_log_view, end_session_view, get, post, get, post, get, post

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[backup_views.py] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[AURORA]
 ```
"""
import os
import markdown
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.core.cache import cache
from groq import Groq
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Document, Metadata, Content
from .serializers import DocumentSerializer, MetadataSerializer, ContentSerializer


# Import our custom core logic
from core_logic.memory import save_memory, get_recent_context, create_resource
from core_logic.sessions import start_session, end_session, log_manual_time

# Initialize Groq Client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@user_passes_test(lambda u: u.is_superuser)
def dashboard(request):
    """The command center for Delta."""
    return render(request, 'aurora/dashboard.html')

@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        user_id = request.user.username.lower() if request.user.is_authenticated else "delta"
        user_text = request.POST.get('text', '').strip()
        session_id = request.session.get('current_session_id')

        # 1. JSON DETECTION: Check if Delta is sending a Resource Blob
        if user_text.startswith('{') and user_text.endswith('}'):
            try:
                resource_data = json.loads(user_text)
                if "category" in resource_data:
                    create_resource(user_id, resource_data)
                    return JsonResponse({
                        "reply": "📦 **Resource Node Created.** Entry successfully linked to your profile and documented in the graph.",
                        "tokens_left": cache.get(f'tokens_{user_id}', 15000),
                        "active_model": "System (Local)"
                    })
            except json.JSONDecodeError:
                pass # Not valid JSON, proceed to AI chat

    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        # 1. IDENTITY & SESSION
        if request.user.is_authenticated:
            user_id = request.user.username.lower() if request.user.is_authenticated else "delta"
        else:
            if not request.session.session_key:
                request.session.create()
            user_id = f"guest_{request.session.session_key[:8]}"

        user_text = request.POST.get('text')
        if not user_text:
            return JsonResponse({"reply": "I'm listening..."})

        # NEW: SESSION TRACKING
        session_id = request.session.get('current_session_id')
        if not session_id:
            session_id = start_session(user_id)
            request.session['current_session_id'] = session_id
            print(f"--- NEW SESSION STARTED: {session_id} ---")
            
        # 2. THE CIRCUIT BREAKER (Fuel Gauge Logic)
        # Check cache for remaining tokens; default to 6000 (standard tier)
        tokens_remaining = cache.get(f'tokens_{user_id}', 6000)
        
        # If tokens are below 15% (approx 900), switch to the 8B Janitor
        if int(tokens_remaining) < 900:
            active_model = "llama-3.1-8b-instant" # This one is usually still active
            model_label = "Janitor (8B)"
        else:
            active_model = "llama-3.3-70b-versatile" 
            model_label = "Architect (70B)"

        # 3. CONTEXT RETRIEVAL
        # Fetches last 10 messages from Neo4j (using our core_logic)
        history = get_recent_context(user_id, limit=10)

        # 4. SYSTEM INSTRUCTIONS
        system_instructions = (
            f"You are Wu, the lead architect. Speaking to: {user_id}. "
            f"Current Brain: {model_label}. "
            "Mission: Provide practical, life-changing aid by solving daily challenges."
        )

        # Build message stack
        messages = [{"role": "system", "content": system_instructions}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_text})

        # 5. GENERATE (Groq Call)
        # Note: We use the raw_response to ensure we can see the headers
        chat_completion = client.chat.completions.with_raw_response.create(
            messages=messages,
            model=active_model,
        )
        
        # 6. UPDATE FUEL GAUGE (Headers)
        # We extract the JSON data and the headers from the raw response
        response_data = chat_completion.parse() # This is the actual AI message object
        new_limit = chat_completion.headers.get('x-ratelimit-remaining-tokens', 0)
        
        cache.set(f'tokens_{user_id}', new_limit, 3600)
        
        answer = response_data.choices[0].message.content

        # 7. PERSIST (Dual-Write to Neo4j)
        # Pass session_id so memories are linked to the time block
        save_memory(user_id, user_text, "user", session_id)
        save_memory(user_id, answer, "assistant", session_id)

        # 8. FORMAT & RESPOND
        formatted_answer = markdown.markdown(
            answer, 
            extensions=['fenced_code', 'codehilite']
        )

        return JsonResponse({
            "reply": formatted_answer,
            "tokens_left": new_limit,
            "active_model": model_label
        })

    except Exception as e:
        print(f"--- COMMAND CENTER ERROR: {e} ---")
        return JsonResponse({"reply": f"FAILURE: {str(e)}"}, status=500)

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
    session_id = request.session.get('current_session_id')
    if session_id:
        duration = end_session(session_id)
        # Clear the session so the next message starts a new one
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