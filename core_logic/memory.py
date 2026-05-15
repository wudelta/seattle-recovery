from .neo4j_driver import db
from groq import Groq
from datetime import datetime, timezone
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def save_memory(user_id, text, role, session_id=None, project="aurora"):
    """Saves a memory node partitioned strictly by project ecosystem."""
    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    tokens = len(text) // 4
    
    # Dynamically apply the secondary project label (e.g., :Aurora or :HopeHub)
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
    WITH m
    OPTIONAL MATCH (s:Session {{uuid: $session_id}})
    FOREACH (ignoreMe IN CASE WHEN s IS NOT NULL THEN [1] ELSE [] END |
        CREATE (s)-[:CONTAINS]->(m)
    )
    """
    db.query(query, {
        "user_id": user_id,
        "text": text,
        "role": role,
        "tokens": tokens,
        "timestamp": timestamp_str,
        "session_id": session_id,
        "project": project.lower()
    })

def get_recent_context(user_id, limit=10, project="aurora"):
    """Fetches history and summaries isolated cleanly by the active project."""
    project_label = "HopeHub" if project.lower() == "hopehub" else "Aurora"
    
    # 1. Fetch only the specific project's latest soul/summary
    summary_query = f"""
    MATCH (u:User {{id: $user_id}})-[:HAS_SUMMARY]->(s:Summary:{project_label})
    RETURN s.content AS content
    ORDER BY s.timestamp DESC LIMIT 1
    """
    summary_results = db.query(summary_query, {"user_id": user_id})
    
    # 2. Fetch only the specific project's recent chatter
    memory_query = f"""
    MATCH (u:User {{id: $user_id}})-[:REMEMBERS {{project: $project}}]->(m:Memory:{project_label})
    RETURN m.content AS content, m.role AS role, m.timestamp AS timestamp
    ORDER BY m.timestamp DESC LIMIT $limit
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

def create_resource(user_id, data):
    """Logs resource JSON payloads to the graph engine using strict metadata formatting."""
    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    query = """
    MATCH (u:User {id: $user_id})
    CREATE (r:Resource {
        category: $category,
        quantity: $quantity,
        unit: $unit,
        location: point({latitude: $lat, longitude: $lon}),
        status: $status,
        urgency: $urgency,
        created_at: $created_at
    })
    CREATE (u)-[:PROVIDES]->(r)
    """
    coords = data.get('location_coords', {}).get('coordinates', [0, 0])
    db.query(query, {
        "user_id": user_id,
        "category": data.get('category'),
        "quantity": data.get('quantity', 0),
        "unit": data.get('unit', 'units'),
        "lat": coords[0],
        "lon": coords[1],
        "status": data.get('status', 'Available'),
        "urgency": data.get('urgency_level', 'Medium'),
        "created_at": timestamp_str
    })

def summarize_session(user_id):
    """
    Compresses current raw memories into a summary node and local fail-safe logs.
    Includes an explicit context-truncation engine to prevent Groq TPM 413 overflows.
    """
    state_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "PROJECT_STATE.md")
    chatter_text = ""

    # 1. CRASH-RESISTANT READ: Attempt to read from Neo4j
    try:
        raw_history = get_recent_context(user_id, limit=30)
        for msg in raw_history:
            if msg["role"] != "system":
                chatter_text += f"{msg['role'].upper()}: {msg['content']}\n"
    except Exception as db_read_err:
        chatter_text = f"[DATABASE CRASH FALLBACK] Neo4j is offline ({str(db_read_err)}).\n"
        if os.path.exists(state_file):
            with open(state_file, "r", encoding="utf-8") as f:
                chatter_text += f"Last Known Project State:\n{f.read()}"
        else:
            chatter_text += "No local PROJECT_STATE.md fallback file found."

    if not chatter_text.strip():
        return "No recent conversational chatter found to summarize."

    # 2. DYNAMIC CEILING SLICER: Stop Groq 413 (TPM) Breaches
    # Simple calculation: 1 word is roughly 1.3 tokens. 
    # We want to strictly enforce a 4,500-token limit for input history.
    max_estimated_tokens = 4500
    estimated_tokens = len(chatter_text) // 4
    
    if estimated_tokens > max_estimated_tokens:
        print(f"⚠️ History Alert: Context size ({estimated_tokens:,} tokens) breaches 8B limits.")
        # Slice text from the end to retain the most recent, relevant development chatter
        char_limit = max_estimated_tokens * 4
        chatter_text = "...[Oldest chatter truncated to fit Groq Free Tier limits]...\n" + chatter_text[-char_limit:]
        print("Context sliced safely to fit within the 6,000 TPM bucket.")

    summary_prompt = (
        "You are the Janitor (Llama 3.1 8B). Review the raw development logs or fallback states below.\n"
        "Generate a dense, technical engineering state summary. Include:\n"
        "1) Explicit progress made / features completed.\n"
        "2) Current component state and roadblocks.\n"
        "3) Targeted next actions for Delta and Wu.\n"
        "Keep it under 150 words, completely clear, and avoid conversational fluff."
    )

    # 3. RUN THE RE-CONFIGURED JANITOR LOOP
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

        # 4. WRITE LOCAL BACKUP FIRST (Guaranteed Safe)
        with open(state_file, "w", encoding="utf-8") as f:
            f.write(f"# Current Project State\n*Saved on: {timestamp_str}*\n\n{summary_text}")
        print("Success: Local PROJECT_STATE.md updated safely on hard drive.")

        # 5. CLEAR NEO4J MEMORY GRAPH SECOND (Risk Zone)
        try:
            summary_query = """
            MATCH (u:User {id: $user_id})
            CREATE (u)-[:HAS_SUMMARY]->(s:Summary {content: $text, timestamp: $timestamp})
            """
            db.query(summary_query, {
                "user_id": user_id,
                "text": summary_text,
                "timestamp": timestamp_str
            })

            cleanup_query = """
            MATCH (u:User {id: $user_id})-[:REMEMBERS]->(m:Memory)
            DETACH DELETE m
            """
            db.query(cleanup_query, {"user_id": user_id})
            print("Success: Neo4j database cleared and synchronized.")
        except Exception as db_write_err:
            return f"Saved LOCALLY to disk. Neo4j write failed: {str(db_write_err)}"

        return summary_text

    except Exception as groq_err:
        # 1. Save the raw text to your laptop hard drive so you lose absolutely nothing
        with open(state_file, "w", encoding="utf-8") as f:
            f.write(f"# EMERGENCY RAW LOG\nJanitor API failed but data was saved!\n\n{chatter_text}")
        
        # 2. FORCE CLEAN: Wipe Neo4j anyway so your token footprint resets to 0
        try:
            cleanup_query = "MATCH (u:User {id: $user_id})-[:REMEMBERS]->(m:Memory) DETACH DELETE m"
            db.query(cleanup_query, {"user_id": user_id})
            db_status = "Neo4j wiped successfully."
        except Exception as db_err:
            db_status = f"Neo4j wipe failed: {str(db_err)}"

        return f"Janitor Limit Intercepted ({str(groq_err)}). Raw text saved to PROJECT_STATE.md. Database state: {db_status}"
