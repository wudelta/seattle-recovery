from .neo4j_driver import db
from groq import Groq
from datetime import datetime, timezone
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def save_memory(user_id, text, role, session_id=None):
    """Saves a memory node using a uniform UTC string timestamp to match Django and Flask."""
    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    query = """
    MERGE (u:User {id: $user_id})
    CREATE (m:Memory {
        content: $text,
        role: $role,
        timestamp: $timestamp,
        tokens: $tokens
    })
    CREATE (u)-[:REMEMBERS]->(m)
    WITH m
    OPTIONAL MATCH (s:Session {uuid: $session_id})
    FOREACH (ignoreMe IN CASE WHEN s IS NOT NULL THEN [1] ELSE [] END |
        CREATE (s)-[:CONTAINS]->(m)
    )
    """
    tokens = len(text) // 4
    db.query(query, {
        "user_id": user_id,
        "text": text,
        "role": role,
        "tokens": tokens,
        "timestamp": timestamp_str,
        "session_id": session_id
    })

def get_recent_context(user_id, limit=10):
    """Fetches the global timeline for Django using the local 'db' driver wrapper."""
    # 1. FETCH THE PROJECT SOUL (Latest Summary)
    summary_query = """
    MATCH (u:User {id: $user_id})-[:HAS_SUMMARY]->(s:Summary)
    RETURN s.content AS content
    ORDER BY s.timestamp DESC
    LIMIT 1
    """
    summary_results = db.query(summary_query, {"user_id": user_id})
    
    # 2. FETCH THE RECENT CHATTER (Global timeline tracking)
    memory_query = """
    MATCH (u:User {id: $user_id})-[:REMEMBERS]->(m:Memory)
    RETURN m.content AS content, m.role AS role, m.timestamp AS timestamp
    ORDER BY m.timestamp DESC
    LIMIT $limit
    """
    memory_results = db.query(memory_query, {"user_id": user_id, "limit": limit})
    
    context = []
    
    # Check if a summary exists in your custom dict/list response object array
    if summary_results and len(summary_results) > 0:
        latest_summary = summary_results[0].get('content')
        if latest_summary:
            context.append({
                "role": "system",
                "content": f"CRITICAL PROJECT CONTEXT: {latest_summary}"
            })
        
    # Add the recent history (reversed to keep chronological ordering matching)
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
    """Compresses current raw memories into a summary node using the high-speed inference engine."""
    raw_history = get_recent_context(user_id, limit=20)
    
    # Safety Check: If there's nothing to process, exit to avoid writing empty summary nodes
    if not raw_history or len(raw_history) <= 1:
        return ""
        
    summary_prompt = (
        "Summarize the key architectural decisions and engineering progress from this chat history "
        "for a lead architect named Wu. Keep the summary dense and under 100 words."
    )
    
    # Construct complete payload structure using true role blocks
    payload = [{"role": "system", "content": summary_prompt}]
    payload.extend(raw_history)
    
    completion = client.chat.completions.create(
        messages=payload,
        model="llama-3.1-8b-instant",
        temperature=0.3
    )
    summary_text = completion.choices[0].message.content
    
    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    # Safe Merge Logic: Creates summary node and handles memory relations cleanly
    query = """
    MATCH (u:User {id: $user_id})
    OPTIONAL MATCH (u)-[r:REMEMBERS]->(m:Memory)
    CREATE (u)-[:HAS_SUMMARY]->(s:Summary {content: $text, timestamp: $timestamp})
    WITH r, m
    DELETE r
    DETACH DELETE m
    """
    db.query(query, {
        "user_id": user_id,
        "text": summary_text,
        "timestamp": timestamp_str
    })
    
    return summary_text
