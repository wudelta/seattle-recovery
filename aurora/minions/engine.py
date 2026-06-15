# ======================================================================
# FILE: aurora/minions/engine.py (PATCH 1 OF 1)
# START: RATE_LIMIT_AWARE_GROQ_FLEET_ENGINE
# ======================================================================
import os
import sys
import time
import requests
from django.conf import settings
from aurora.models import DeltaDirectives

class MinionRunner:
    """Universal Cloud-Driven AI Execution Engine with Rate-Limit Backoff handling."""
    def __init__(self):
        self.cloud_api_url = "https://api.groq.com/openai/v1/chat/completions"

        self.api_key = getattr(settings, "GROQ_API_KEY", "")
        if not self.api_key:
            self.api_key = os.environ.get("GROQ_API_KEY", "")
        if not self.api_key:
            self.api_key = os.environ.get("MINION_CLOUD_API_KEY", "")

    def query_groq_llm(self, model_tag: str, system_directive: str, user_prompt: str, temperature: float = 0.3) -> str:
        """Sends a request to Groq with an automatic 9-second backoff for 429 errors."""
        if not self.api_key:
            sys.stderr.write("[WARNING] Groq API Key (settings.GROQ_API_KEY) is missing.\n")
            return "Error: Groq API Key unassigned."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_tag,
            "messages": [
                {"role": "system", "content": system_directive},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "stream": False
        }
        
        max_retries = 3
        current_attempt = 0
        
        while current_attempt < max_retries:
            try:
                response = requests.post(self.cloud_api_url, json=payload, headers=headers, timeout=45)
                
                # Check for rate limit status codes cleanly
                if response.status_code == 429:
                    current_attempt += 1
                    sys.stderr.write(f"⏳ [RATE LIMIT REACHED] Hit TPM ceiling. Sleeping 9 seconds before retry {current_attempt}/{max_retries}...\n")
                    time.sleep(9)
                    continue
                
                if response.status_code == 200:
                    choices = response.json().get("choices", [])
                    if choices and isinstance(choices, list):
                        first_choice = choices[0]
                        return first_choice.get("message", {}).get("content", "").strip()
                    return "Error: Received empty choices array from Groq endpoint response structure."
                
                error_msg = f"Error: [GROQ API FAULT] Status {response.status_code}: {response.text}"
                sys.stderr.write(f"{error_msg}\n")
                return error_msg
                
            except requests.exceptions.RequestException as err:
                error_catch = f"Error: [CONNECTION ERROR] Groq connection failed: {str(err)}"
                sys.stderr.write(f"{error_catch}\n")
                return error_catch
                
        return "Error: Exceeded maximum rate limit retry attempts on Groq API gateway."

    def run_minion_task(self, minion_name: str, task_input: str) -> str:
        """Loads minion settings out of DeltaDirectives and processes the work."""
        try:
            directive = DeltaDirectives.objects.get(directive_name=minion_name, is_active=True)
        except DeltaDirectives.DoesNotExist:
            return f"Error: Minion configuration row '{minion_name}' is missing or inactive."

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
# END: RATE_LIMIT_AWARE_GROQ_FLEET_ENGINE (PATCH 1 OF 1)
# ======================================================================
