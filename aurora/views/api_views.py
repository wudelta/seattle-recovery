import os
import json
import markdown
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from groq import Groq

# Initialize the Groq client exactly how you have it in your project initialization
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@csrf_exempt
def wu_data_stream(request):
    """
    Headless JSON Data Core.
    Receives raw text payloads and outputs pristine JSON strings.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

    try:
        # 1. Safely extract raw JSON payload fields from the incoming stream
        data = json.loads(request.body)
        user_text = data.get('text', '').strip()
        user_id = data.get('user_id', 'delta').lower()

        if not user_text:
            return JsonResponse({"error": "Empty text attribute parameter"}, status=400)

        # 2. Hardcode the system prompt architecture directly to guarantee zero import dependencies
        system_instructions = (
            f"You are Wu, the lead architect. Speaking to: {user_id}. "
            "Active Ecosystem Workspace: AURORA ENGINE BUILDER. "
            "Mission: Provide practical, high-level structural aid for the application builder itself."
        )

        messages = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": user_text}
        ]

        # 3. Call your primary model engine directly
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.1
        )
        
        answer = chat_completion.choices[0].message.content

        # 4. Formulate clean raw text and processed markdown html arrays
        return JsonResponse({
            "status": "success",
            "raw_text": answer,
            "html_text": markdown.markdown(answer, extensions=['fenced_code', 'codehilite']),
            "active_model": "Architect (70B)"
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Data engine fault: {str(e)}"}, status=500)
