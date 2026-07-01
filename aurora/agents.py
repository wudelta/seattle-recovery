# ====================================================================== #
# FILE: aurora/agents.py (PATCH 1 OF 2)                                  #
# START: MODEL ENGINE INITIALIZATION & SUB-AGENT PROMPT ARCHITECTURE      #
# ====================================================================== #
import os
from google import genai
from google.genai import types

# Initialize Gemini client using environment variable safely
# (Bypasses network if only local routing is invoked)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

AGENT_CONFIGS = {
    "Wu_Orchestrator": {
        "model": "gemini-2.5-flash",
        "temperature": 0.2,
        "system_prompt": (
            "You are Wu, the lead AI software architect for Aurora. "
            "Decompose plain-English instructions into structured JSON pipelines for subordinate Minions."
        )
    },
    "HTML_Minion": {
        "model": "gemini-2.5-flash",
        "temperature": 0.1,
        "system_prompt": (
            "You are the HTML Minion. Generate structural Django templates using fluid Bootstrap 5. "
            "STRICTLY forbidden from writing inline CSS or script blocks."
        )
    },
    "JS_Minion": {
        "model": "gemini-2.5-flash",
        "temperature": 0.1,
        "system_prompt": (
            "You are the JS Minion. Write isolated jQuery scripts inside static/aurora/js/. "
            "Capture form inputs and stream requests asynchronously via $.ajax."
        )
    },
    "API_Minion": {
        "model": "gemini-2.5-flash",
        "temperature": 0.1,
        "system_prompt": (
            "You are the API Minion. Build back-end views inside views/. "
            "Return ONLY JsonResponse payloads."
        )
    }
}
# ====================================================================== #
# END: MODEL ENGINE INITIALIZATION & SUB-AGENT PROMPT ARCHITECTURE      #
# ====================================================================== #

# ====================================================================== #
# FILE: aurora/agents.py (PATCH 2 OF 2)                                  #
# START: AGENT PAYLOAD DISPATCH & STRUCTURED COMPLETION ENGINE           #
# ====================================================================== #
def get_system_response(agent_role: str, user_command: str) -> str:
    """Dispatches processing requests down to explicit Gemini inference targets."""
    if not client:
        raise ValueError("Gemini Client API Key is missing from the environment configuration.")
    
    config = AGENT_CONFIGS[agent_role]
    
    # Configure Gemini content logic attributes
    gen_config = types.GenerateContentConfig(
        system_instruction=config["system_prompt"],
        temperature=config["temperature"],
    )
    
    # Request native structured data directly when addressing Wu
    if agent_role == "Wu_Orchestrator":
        gen_config.response_mime_type = "application/json"

    response = client.models.generate_content(
        model=config["model"],
        contents=user_command,
        config=gen_config
    )
    
    return response.text
# ====================================================================== #
# END: AGENT PAYLOAD DISPATCH & STRUCTURED COMPLETION ENGINE           #
# ====================================================================== #
