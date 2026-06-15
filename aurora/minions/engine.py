# ======================================================================
# FILE: aurora/minions/engine.py (PATCH 1 OF 1)
# START: UNIVERSAL_GROQ_FLEET_ENGINE
# ======================================================================
import os
import sys
import requests
from aurora.models import DeltaDirectives

class MinionRunner:
    """
    Universal Cloud-Driven AI Execution Engine.
    Dynamically loads instructions and parameter limits out of DeltaDirectives
    rows to execute any minion in your fleet using the Groq Cloud API.
    """

    def __init__(self):
        # Configured to use Groq's standard cloud compatibility layer endpoint
        self.cloud_api_url = "https://groq.com"
        self.api_key = os.environ.get("MINION_CLOUD_API_KEY", "")

    def query_groq_llm(self, model_tag: str, system_directive: str, user_prompt: str, temperature: float = 0.3) -> str:
        """Sends a structured chat request payload straight to the Groq Gateway."""
        if not self.api_key:
            sys.stderr.write("[WARNING] Groq API Key (MINION_CLOUD_API_KEY) is missing.\n")
            return "Error: Groq API Key unassigned."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model_tag,  # Dynamic identifier string loaded from DB
            "messages": [
                {"role": "system", "content": system_directive},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "stream": False
        }

        try:
            response = requests.post(self.cloud_api_url, json=payload, headers=headers, timeout=45)
            if response.status_code == 200:
                choices = response.json().get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "").strip()
            else:
                sys.stderr.write(f"[GROQ API FAULT] Status {response.status_code}: {response.text}\n")
        except requests.exceptions.RequestException as err:
            sys.stderr.write(f"[CONNECTION ERROR] Groq connection failed: {str(err)}\n")
        return ""

    def run_minion_task(self, minion_name: str, task_input: str) -> str:
        """
        Loads a specific minion row from DeltaDirectives and processes 
        the target work through its assigned model parameter tag.
        """
        try:
            directive = DeltaDirectives.objects.get(directive_name=minion_name, is_active=True)
        except DeltaDirectives.DoesNotExist:
            return f"Error: Minion configuration row '{minion_name}' is missing or inactive."

        # Fetch configurations stored in the database fields
        model_tag = directive.constraints.get("model", "llama-3.1-8b-instant")
        temperature = directive.constraints.get("temperature", 0.3)
        system_instructions = directive.instructions

        return self.query_groq_llm(
            model_tag=model_tag,
            system_directive=system_instructions,
            user_prompt=task_input,
            temperature=temperature
        )
# ======================================================================
# END: UNIVERSAL_GROQ_FLEET_ENGINE (PATCH 1 OF 1)
# ======================================================================
