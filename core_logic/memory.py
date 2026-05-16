# core_logic/memory.py
import os
import sys
from datetime import datetime, timezone
from groq import Groq
from google import genai  # Correct modern SDK package import namespace
from .neo4j_driver import db

# Initialize the Groq client for the 8B Janitor routine
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =====================================================================
# PERSISTENT LORE LAYER: CUSTOM NANO-EMBEDDING VECTOR ENGINE
# =====================================================================
class IsolatedMemoryEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IsolatedMemoryEngine, cls).__new__(cls)
            cls._instance._initialize_engine()
        return cls._instance

    def _initialize_engine(self):
        """Initializes the unified modern Google Gen AI SDK client."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("[FATAL] GEMINI_API_KEY is missing from environment variables.")
        
        # Instantiate client object; automatically pulls the key from standard variables
        self.ai_client = genai.Client(api_key=api_key)
        print("[SUCCESS] Modern Nano-Vector Engine active via google-genai Client.")

    def store_development_fact(self, user_id, text, project_scope="aurora"):
        """Generates cloud embeddings and stores them natively in the local Neo4j instance."""
        try:
            response = self.ai_client.models.embed_content(
                model="gemini-embedding-2",
                contents=text
            )
            
            # Extract the raw float list from the ContentEmbedding container object
            embedding = response.embeddings[0].values
            
            timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            project_label = "HopeHub" if project_scope.lower() == "hopehub" else "Aurora"
            
            query = f"""
            MERGE (u:User {{id: $user_id}})
            CREATE (m:VectorMemory:{project_label} {{
                content: $text,
                embedding: $embedding,
                timestamp: $timestamp,
                project: $project
            }})
            CREATE (u)-[:REMEMBERS_LORE {{project: $project}}]->(m)
            RETURN m.timestamp as committed_at
            """
            
            db.query(query, {
                "user_id": user_id,
                "text": text,
                "embedding": embedding,
                "timestamp": timestamp_str,
                "project": project_scope.lower()
            })
            return {"status": "success", "message": "Vector fact written locally to graph."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def search_relevant_context(self, user_id, query, project_scope="aurora"):
        """Executes a native Neo4j vector search to fetch semantically close milestones."""
        try:
            response = self.ai_client.models.embed_content(
                model="gemini-embedding-2",
                contents=query
            )
            
            # Extract the raw float list from the ContentEmbedding container object
            query_embedding = response.embeddings[0].values
            
            project_label = "HopeHub" if project_scope.lower() == "hopehub" else "Aurora"
            
            # Realigned query using native vector space function tracking
            cypher_query = f"""
            MATCH (m:VectorMemory:{project_label} {{project: $project}})
            WHERE m.embedding IS NOT NULL
            WITH m, vector.similarity.cosine(m.embedding, $query_embedding) AS score
            ORDER BY score DESC
            LIMIT 5
            RETURN m.content AS content, score
            """
            
            results = db.query(cypher_query, {
                "project": project_scope.lower(),
                "query_embedding": query_embedding
            })
            return results if results else []
        except Exception as e:
            print(f"⚠️ Vector search issue: {str(e)}")
            return []

# =====================================================================
# VOLATILE CONTEXT LAYER: RAW CHATTER & TRANSIENT SESSION LOGS
# =====================================================================
def save_memory(user_id, text, role, session_id=None, project="aurora"):
    """Saves a temporary session chatter node partitioned strictly by project."""
    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    tokens = len(text) // 4
    project_label = "HopeHub" if project.lower() == "hopehub" else "Aurora"
    
    query = f"""
    MERGE (u:User {{id: $user_id}})
    CREATE (m:Memory:{project_label} {{
        content: $text,
        role: $role,
        timestamp: $timestamp,
        tokens: $tokens,
        project: $project
    }})
    CREATE (u)-[:REMEMBERS {{project: $project}}]->(m)
    """
    db.query(query, {
        "user_id": user_id,
        "text": text,
        "role": role,
        "tokens": tokens,
        "timestamp": timestamp_str,
        "project": project.lower()
    })

def get_recent_context(user_id, limit=10, project="aurora"):
    """Fetches short-term transient conversational history isolated cleanly by project."""
    project_label = "HopeHub" if project.lower() == "hopehub" else "Aurora"
    
    summary_query = f"""
    MATCH (u:User {{id: $user_id}})-[:HAS_SUMMARY]->(s:Summary:{project_label})
    RETURN s.content AS content
    ORDER BY s.timestamp DESC
    LIMIT 1
    """
    summary_results = db.query(summary_query, {"user_id": user_id})
    
    memory_query = f"""
    MATCH (u:User {{id: $user_id}})-[:REMEMBERS {{project: $project}}]->(m:Memory:{project_label})
    RETURN m.content AS content, m.role AS role, m.timestamp AS timestamp
    ORDER BY m.timestamp DESC
    LIMIT $limit
    """
    memory_results = db.query(memory_query, {
        "user_id": user_id,
        "limit": limit,
        "project": project.lower()
    })
    
    context = []
    if summary_results and len(summary_results) > 0:
        latest_summary = summary_results[0].get('content')
        if latest_summary:
            context.append({
                "role": "system",
                "content": f"CRITICAL {project_label.upper()} PROJECT CONTEXT: {latest_summary}"
            })
            
    for r in reversed(memory_results):
        api_role = "user" if r.get("role") == "user" else "assistant"
        if r.get("content"):
            context.append({"role": api_role, "content": r["content"]})
    return context

def summarize_session(user_id):
    """Compresses volatile chat into technical summaries, keeping vector points completely immune."""
    state_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "PROJECT_STATE.md")
    chatter_text = ""
    
    try:
        raw_history = get_recent_context(user_id, limit=30)
        for msg in raw_history:
            if msg["role"] != "system":
                chatter_text += f"{msg['role'].upper()}: {msg['content']}\n"
    except Exception as db_read_err:
        chatter_text = f"[DATABASE CRASH FALLBACK] Neo4j is offline ({str(db_read_err)}).\n"
                
    if not chatter_text.strip():
        return "No recent conversational chatter found to summarize."

    # Dynamic input history text ceiling slicer
    max_estimated_tokens = 4500
    estimated_tokens = len(chatter_text) // 4
    if estimated_tokens > max_estimated_tokens:
        char_limit = max_estimated_tokens * 4
        chatter_text = "...[Truncated]...\n" + chatter_text[-char_limit:]
        
    summary_prompt = (
        "You are the Janitor (Llama 3.1 8B). Review the raw development logs.\n"
        "Generate a dense, technical engineering state summary under 150 words."
    )

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": summary_prompt},
                {"role": "user", "content": chatter_text}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.2
        )
        summary_text = completion.choices[0].message.content.strip()
        timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        with open(state_file, "w", encoding="utf-8") as f:
            f.write(f"# Current Project State\n\n{summary_text}")
        
        # Only clear volatile chat nodes, leaving VectorMemory untouched
        summary_query = "MATCH (u:User {id: $user_id}) CREATE (u)-[:HAS_SUMMARY]->(s:Summary {content: $text, timestamp: $timestamp})"
        db.query(summary_query, {"user_id": user_id, "text": summary_text, "timestamp": timestamp_str})
        
        cleanup_query = "MATCH (u:User {id: $user_id})-[:REMEMBERS]->(m:Memory) DETACH DELETE m"
        db.query(cleanup_query, {"user_id": user_id})
        return summary_text
    except Exception as e:
        return f"Saved locally. Graph synchronizer error: {str(e)}"
