import os
import markdown  # Added for clean code blocks
from pathlib import Path
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from dotenv import load_dotenv
from groq import Groq
from neo4j import GraphDatabase

# 1. SETUP: Force load the .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))


def write_to_graph(user_id, text):
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "password123"))
    with driver.session() as session:
        session.run("""
            MERGE (u:User {id: $user_id})
            CREATE (m:Memory {content: $text, user_id: $user_id, timestamp: datetime()})
            MERGE (u)-[:REMEMBERS]->(m)
        """, user_id=user_id, text=text)
    driver.close()


# 3. VIEW: Dashboard for Delta
@user_passes_test(lambda u: u.is_superuser)
def dashboard(request):
    return render(request, 'delta_chat/dashboard.html')


# --- API: The Hybrid Brain ---
@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        try:
            # 1. IDENTITY
            if request.user.is_authenticated:
                user_id = request.user.username
            else:
                if not request.session.session_key:
                    request.session.create()
                user_id = f"guest_{request.session.session_key[:8]}"

            user_text = request.POST.get('text')

            # Silent Logger: If it's a system time log, save it and exit
            if "SYSTEM_LOG" in user_text:
                write_to_graph(user_id, user_text)
                return JsonResponse({"status": "Session logged"})

            if not user_text:
                return JsonResponse({"reply": "I'm listening..."})

            # 2. THE VAULT (Expanded to 10 nodes for better "Code Memory")
            context_list = []
            uri = "bolt://localhost:7687"
            driver = GraphDatabase.driver(uri, auth=("neo4j", "password123"))
            with driver.session() as session:
                # Optimized Query: Pulls both Delta's facts AND Wu's previous logic
                result = session.run("""
                    MATCH (m:Memory)
                    WHERE m.user_id = $user_id OR m.user_id = 'Wu'
                    RETURN m.content AS content
                    ORDER BY m.timestamp DESC LIMIT 10
                """, user_id=user_id)
                # We reverse it so the oldest info is at the top for the LLM
                context_list = [record["content"] for record in result][::-1]
            driver.close()

            context = "\n".join(context_list)

            # 3. GENERATE (Groq)
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            system_prompt = (
                f"You are Wu. You are talking to: {user_id}. "
                "Use the context below to maintain conversation flow. If the context "
                "contains code you sent previously, acknowledge it. Mission: replace despair with growth."
                f"\n\n--- CONVERSATION LOG ---\n{context}"
            )

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                model="llama-3.3-70b-versatile",
            )
            answer = chat_completion.choices[0].message.content

            # --- MARKDOWN CONVERSION ---
            formatted_answer = markdown.markdown(
                answer,
                extensions=['fenced_code', 'codehilite']
            )

            # 4. PERSIST (Dual-Write)
            # Save User's input
            write_to_graph(user_id, user_text)
            # Save Wu's response so he can reference it in the next turn
            write_to_graph("Wu", answer)

            return JsonResponse({"reply": formatted_answer})

        except Exception as e:
            print(f"--- COMMAND CENTER ERROR: {e} ---")
            return JsonResponse({"reply": f"FAILURE: {str(e)}"}, status=500)

    return JsonResponse({"reply": "POST only"}, status=405)
