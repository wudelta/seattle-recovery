import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, jsonify, render_template_string
import requests
from datetime import datetime, timezone
from neo4j import GraphDatabase
from groq import Groq

app = Flask(__name__)

# --- CONFIGURATION ---
DJANGO_WU_URL = "http://localhost:8000/delta/api/"
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = os.getenv('NEO4J_PASS')

# Initialize Drivers
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
groq_client = Groq(api_key=GROQ_API_KEY)

# --- LOCAL IN-MEMORY METRICS MEMORY FOR LIFEBOAT ---
# Allows Flask to remember remaining token quotas across rapid manual entries
lifeboat_token_quota = 12000
lifeboat_token_ceiling = 12000

# --- SYSTEM PERSONA ALIGNMENT ---
WU_SYSTEM_PROMPT = """You are Wu, the lead architect. Speaking to: delta. Current Brain: Architect (70B). Mission: Provide practical, life-changing aid by solving daily challenges. Keep answers structural, precise, and format all code blocks explicitly."""

# --- IMMUTABLE TERMINAL INTERFACE ---
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HopeHub Lifeboat</title>
    <!-- Explicit UMD/Browser Distribution Deliverables -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.6.0/dist/styles/default.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked@4.3.0/dist/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/highlight.js@11.6.0/dist/highlight.min.js"></script>
    <style>
        body { background: #111116; color: #e2e8f0; font-family: 'Courier New', Courier, monospace; padding: 20px; margin: 0; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box; }
        h1 { color: #00ffcc; font-size: 1.5rem; margin: 0 0 15px 0; text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid #334155; padding-bottom: 10px; }
        #chat { border: 1px solid #334155; flex-grow: 1; overflow-y: auto; padding: 20px; margin-bottom: 15px; background: #09090d; border-radius: 4px; }
        .msg-row { margin-bottom: 20px; display: flex; flex-direction: column; }
        .label { font-weight: bold; font-size: 12px; text-transform: uppercase; margin-bottom: 4px; }
        .delta-label { color: #38bdf8; }
        .wu-label { color: #00ffcc; }
        .system-label { color: #ef4444; }
        .bubble { background: #1e293b; padding: 12px 18px; border-radius: 4px; border: 1px solid #334155; line-height: 1.6; max-width: 95%; }
        .wu-bubble { background: #13151a; border-color: #1e293b; }
        .rich-text p { margin: 0 0 12px 0; }
        .rich-text p:last-child { margin-bottom: 0; }
        .rich-text code { background: #27272a; color: #f43f5e; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
        .rich-text pre { background: #18181b !important; padding: 15px; border-radius: 4px; border: 1px solid #27272a; overflow-x: auto; margin: 12px 0; position: relative; }
        .rich-text pre code { background: transparent; color: #e4e4e7; padding: 0; font-size: 13px; }
        .copy-btn { position: absolute; top: 5px; right: 5px; background: #27272a; color: #a1a1aa; border: 1px solid #3f3f46; padding: 3px 8px; font-size: 11px; border-radius: 3px; cursor: pointer; }
        .input-box { display: flex; gap: 10px; }
        #msg { flex-grow: 1; background: #18181b; color: #fff; border: 1px solid #334155; padding: 12px; font-family: monospace; font-size: 14px; border-radius: 4px; outline: none; }
        button.send-btn { padding: 0 25px; background: #00ffcc; color: #09090d; border: none; font-weight: bold; cursor: pointer; border-radius: 4px; text-transform: uppercase; }
    </style>
</head>
<body>
    <h1>Wu Lifeboat Terminal (Emergency Mode Ready)</h1>
    <div id="chat"></div>
    <div class="input-box">
        <input type="text" id="msg" placeholder="Talk to Wu..." autocomplete="off">
        <button class="send-btn" onclick="send()">Send</button>
    </div>
    <script>
        function parseMarkdown(rawMarkdown) {
            try { if (window.marked) { return marked.parse(rawMarkdown); } return rawMarkdown; } 
            catch (err) { return rawMarkdown; }
        }
        function appendRow(role, rawContent) {
            const chat = document.getElementById('chat');
            const row = document.createElement('div');
            row.className = 'msg-row';
            let labelClass = 'wu-label';
            let bubbleClass = 'wu-bubble';
            if (role === 'Delta') { labelClass = 'delta-label'; bubbleClass = ''; } 
            else if (role === 'System') { labelClass = 'system-label'; }
            const htmlParsed = (role === 'Delta') ? rawContent : parseMarkdown(rawContent);
            row.innerHTML = ` <span class="label ${labelClass}">${role}:</span> <div class="bubble ${bubbleClass} rich-text">${htmlParsed}</div> `;
            chat.appendChild(row);
            row.querySelectorAll('pre code').forEach((el) => { hljs.highlightElement(el); });
            row.querySelectorAll('pre').forEach((block) => {
                const btn = document.createElement('button');
                btn.innerText = 'Copy'; btn.className = 'copy-btn';
                btn.onclick = () => {
                    const codeEl = block.querySelector('code');
                    navigator.clipboard.writeText(codeEl ? codeEl.innerText.trim() : block.innerText.trim());
                    btn.innerText = 'Copied!'; setTimeout(() => btn.innerText = 'Copy', 2000);
                };
                block.appendChild(btn);
            });
            chat.scrollTop = chat.scrollHeight;
        }
        async function send() {
            const msgInput = document.getElementById('msg');
            const text = msgInput.value.trim();
            if(!text) return;
            appendRow('Delta', text);
            msgInput.value = '';
            try {
                const response = await fetch('/ask_wu', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await response.json();
                appendRow('Wu', data.reply);
            } catch (e) {
                appendRow('System', 'Connection lost to fallback gateway network.');
            }
        }
        document.getElementById('msg').addEventListener('keydown', function(e) { if (e.key === 'Enter') send(); });
    </script>
</body>
</html>
"""

def get_recent_context(user_id, limit=10):
    messages_payload = [{"role": "system", "content": WU_SYSTEM_PROMPT}]
    with neo4j_driver.session() as session:
        summary_query = "MATCH (u:User {id: $user_id})-[:HAS_SUMMARY]->(s:Summary) RETURN s.content AS content ORDER BY s.timestamp DESC LIMIT 1"
        summary_data = session.run(summary_query, {"user_id": user_id}).data()
        if summary_data and summary_data[0].get('content'):
            messages_payload.append({"role": "system", "content": f"CRITICAL CONTEXT: {summary_data[0]['content']}"})

        memory_query = """
        MATCH (u:User {id: $user_id})-[:REMEMBERS]->(m:Memory)
        RETURN m.content AS content, m.role AS role, m.timestamp AS timestamp
        ORDER BY m.timestamp DESC LIMIT $limit
        """
        memory_data = session.run(memory_query, {"user_id": user_id, "limit": limit}).data()
        for r in reversed(memory_data):
            api_role = "user" if r['role'] == "user" else "assistant"
            if r.get('content'):
                messages_payload.append({"role": api_role, "content": r['content']})
    return messages_payload

def get_latest_session(user_id):
    query = """
    MATCH (u:User {id: $user_id})-[r:HAS_SESSION]->(s:Session)
    RETURN s.uuid AS uuid ORDER BY s.timestamp DESC LIMIT 1
    """
    with neo4j_driver.session() as session:
        result = session.run(query, {"user_id": user_id}).data()
        return result[0]['uuid'] if result else None

def save_memory(user_id, text, role, session_id=None):
    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    query = """
    MERGE (u:User {id: $user_id})
    CREATE (m:Memory { content: $text, role: $role, timestamp: $timestamp, tokens: $tokens })
    CREATE (u)-[:REMEMBERS]->(m)
    WITH u, m
    OPTIONAL MATCH (s:Session {uuid: $session_id})
    FOREACH (ignoreMe IN CASE WHEN s IS NOT NULL THEN [1] ELSE [] END | CREATE (s)-[:CONTAINS]->(m) )
    """
    tokens = len(text) // 4
    with neo4j_driver.session() as session:
        session.run(query, {"user_id": user_id, "text": text, "role": role, "tokens": tokens, "timestamp": timestamp_str, "session_id": session_id})

@app.route('/')
def home():
    return render_template_string(HTML_INTERFACE)

@app.route('/ask_wu', methods=['POST'])
def ask_wu():
    global lifeboat_token_quota, lifeboat_token_ceiling
    user_message = request.json.get("message")
    user_id = "delta"
    
    try:
        # 1. TRY DJANGO FIRST
        r = requests.post(DJANGO_WU_URL, json={"message": user_message}, timeout=3)
        return jsonify(r.json())
    except Exception:
        # 2. EMERGENCY MODE
        try:
            # Added: Flat 1,200 token runway floor protection inside Flask
            if lifeboat_token_quota < 1200:
                return jsonify({
                    "reply": f"⚠️ **Groq Rate Limit Critical (Lifeboat Core).** Fuel ({lifeboat_token_quota:,}) is below the 1,200 token safety runway. Please pause for 30 seconds.",
                    "status": "offline"
                })

            messages_payload = get_recent_context(user_id)
            messages_payload.append({"role": "user", "content": user_message})

            # Execute Groq call via raw response context to read HTTP headers
            chat_completion = groq_client.chat.completions.with_raw_response.create(
                messages=messages_payload,
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=4096,
                top_p=0.95
            )
            
            # Extract header tokens data directly from Groq's API engine response
            lifeboat_token_quota = int(chat_completion.headers.get('x-ratelimit-remaining-tokens', lifeboat_token_quota))
            lifeboat_token_ceiling = int(chat_completion.headers.get('x-ratelimit-limit-tokens', lifeboat_token_ceiling))
            
            response_data = chat_completion.parse()
            wu_response = response_data.choices[0].message.content

            active_session_id = get_latest_session(user_id)
            save_memory(user_id, user_message, "user", active_session_id)
            save_memory(user_id, wu_response, "assistant", active_session_id)

            return jsonify({
                "reply": f"[EMERGENCY MODE] {wu_response}",
                "status": "offline"
            })
        except Exception as e:
            return jsonify({"reply": f"Lifeboat Brain Failure: {str(e)}", "status": "error"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
