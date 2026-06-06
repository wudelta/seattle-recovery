# ======================================================================
# FILE: aurora/agents.py (PATCH 1 OF 2)
# START: MODEL ENGINE INITIALIZATION & SUB-AGENT PROMPT ARCHITECTURE
# ======================================================================
import os
from groq import Groq

# Initialize Groq client using environment variable safely
# (Bypasses network if only local routing is invoked)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

AGENT_CONFIGS = {
    "Wu_Orchestrator": {
        "model": "llama3-70b-8192",
        "temperature": 0.2,
        "system_prompt": (
            "You are Wu, the lead AI software architect for Aurora. "
            "Decompose plain-English instructions into structured JSON pipelines for subordinate Minions."
        )
    },
    "HTML_Minion": {
        "model": "llama3-8b-8192",
        "temperature": 0.1,
        "system_prompt": (
            "You are the HTML Minion. Generate structural Django templates using fluid Bootstrap 5. "
            "STRICTLY forbidden from writing inline CSS or script blocks."
        )
    },
    "JS_Minion": {
        "model": "llama3-8b-8192",
        "temperature": 0.1,
        "system_prompt": (
            "You are the JS Minion. Write isolated jQuery scripts inside static/aurora/js/. "
            "Capture form inputs and stream requests asynchronously via $.ajax."
        )
    },
    "API_Minion": {
        "model": "llama3-8b-8192",
        "temperature": 0.1,
        "system_prompt": (
            "You are the API Minion. Build back-end views inside views/. "
            "Return ONLY JsonResponse payloads."
        )
    }
}
# ======================================================================
# END: MODEL ENGINE INITIALIZATION & SUB-AGENT PROMPT ARCHITECTURE
# ======================================================================

# ======================================================================
# FILE: aurora/agents.py (PATCH 2 OF 2)
# START: AGENT PAYLOAD DISPATCH & STRUCTURED COMPLETION ENGINE
# ======================================================================
def get_system_response(agent_role: str, user_command: str) -> str:
    """Dispatches processing requests down to explicit Groq inference targets."""
    if not client:
        raise ValueError("Groq Client API Key is missing from the environment configuration.")
        
    config = AGENT_CONFIGS[agent_role]
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": config["system_prompt"]},
            {"role": "user", "content": user_command}
        ],
        model=config["model"],
        temperature=config["temperature"],
        # Request native structured data directly when addressing Wu
        response_format={"type": "json_object"} if agent_role == "Wu_Orchestrator" else None
    )
    return response.choices.message.content
# ======================================================================
# END: AGENT PAYLOAD DISPATCH & STRUCTURED COMPLETION ENGINE
# ======================================================================
