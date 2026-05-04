import os
from pathlib import Path
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from dotenv import load_dotenv
from mem0 import Memory
from groq import Groq
from neo4j import GraphDatabase

# 1. SETUP: Force load the .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))


# 2. HELPER: The "Vibe" Memory (Chroma Only - No Graph here to avoid 1536 error)
def get_mem0():
    config = {
        "vector_store": {
            "provider": "chroma",
            "config": {
                "collection_name": "seattle_recovery_vault",
                "path": "local_memories"
            }
        },
        "llm": {
            "provider": "groq",
            "config": {
                "model": "llama-3.3-70b-versatile",
                "api_key": os.getenv("GROQ_API_KEY")
            }
        },
        "embedder": {
            "provider": "huggingface",
            "config": {
                "model": "sentence-transformers/all-MiniLM-L6-v2",
                "embedding_dims": 384
            }
        }
    }
    return Memory.from_config(config)


# 3. HELPER: The "Hard Fact" Memory (Direct Neo4j)
def write_to_graph(user_id, text):
    uri = "bolt://localhost:7687"
    # Make sure 'password123' matches your Docker command!
    driver = GraphDatabase.driver(uri, auth=("neo4j", "password123"))
    with driver.session() as session:
        session.run("""
            MERGE (u:User {id: $user_id})
            CREATE (m:Memory {content: $text, timestamp: datetime()})
            MERGE (u)-[:REMEMBERS]->(m)
        """, user_id=user_id, text=text)
    driver.close()


# 4. VIEW: Dashboard for Delta
@user_passes_test(lambda u: u.is_superuser)
def dashboard(request):
    return render(request, 'delta_chat/dashboard.html')


# 5. API: The Hybrid Brain
@csrf_exempt
def chat_api(request):
    # --- INITIALIZE ---
    m = get_mem0()

    if request.method == "POST":
        try:
            # --- IDENTITY ---
            if request.user.is_authenticated:
                user_id = request.user.username
            else:
                if not request.session.session_key:
                    request.session.create()
                user_id = f"guest_{request.session.session_key[:8]}"

            user_text = request.POST.get('text')
            if not user_text:
                return JsonResponse({"reply": "I'm listening..."})

            # --- SEARCH ---
            m = get_mem0()

            # --- SEARCH ---
            # We use the search WITHOUT the user_id argument to bypass the frozenset error
            memories = m.search(user_text, filters={"user_id": user_id})

            context_list = [
                mem['memory'] if isinstance(mem, dict) and 'memory' in mem else str(mem)
                for mem in memories
            ]
            context = "\n".join(context_list)

            # --- GENERATE ---
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            system_prompt = (
                f"You are Wu. You are talking to: {user_id}. "
                "Use the context below to answer. If empty, rely on your mission to "
                "replace despair with roadmaps for growth. NEVER mention Meta AI."
                f"\n\n--- VAULT CONTEXT ---\n{context}"
            )

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                model="llama-3.3-70b-versatile",
            )
            answer = chat_completion.choices[0].message.content

            # --- PERSIST ---
            m.add(user_text, metadata={"user_id": user_id})

            # 2. Save to Neo4j (Graph Circles)
            write_to_graph(user_id, user_text)

            return JsonResponse({"reply": answer})

        except Exception as e:
            print(f"--- COMMAND CENTER ERROR: {e} ---")
            return JsonResponse({"reply": f"FAILURE: {str(e)}"}, status=500)

    return JsonResponse({"reply": "POST only"}, status=405)
