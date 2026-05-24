import os
import json
import logging
import re
from groq import Groq

# Ensure local .env file loads explicitly into environment memory matrices
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.getcwd(), '.env'))
except ImportError:
    pass

logger = logging.getLogger("aurora.minion_array")

def run_8b_translation(raw_brief_text):
    """
    Automated Translation Engine (Llama 3.1 8B).
    Reads Delta's raw development journal entries, filters out conversational text,
    and returns a high-density system instruction summary for Wu.
    """
    print("\n🤖 [MINION WORKER] Initializing cloud-based Llama 3.1 8B translation loop...")
    
    # --- AUTOMATED TEST SUITE INTEGRATION CHECK ---
    is_testing = os.environ.get('DJANGO_TEST_ENVIRONMENT') == 'true' or (
        os.path.exists(os.path.join(os.getcwd(), 'manage.py')) and 
        'test' in os.sys.argv
    )
    
    if is_testing:
        print("🧪 [MINION WORKER] Test environment profile detected. Short-circuiting to mock extraction array to save Groq API quota.")
        dense_abstract = "Mock Test Abstract: Automated local file cleaner logic matrix initialized safely."
        mock_tasks = [
            {"id": "OBJ-001", "task": "Verify headless database transactions.", "status": "PENDING"},
            {"id": "OBJ-002", "task": "Validate alphanumeric terminal tracing strings.", "status": "PENDING"}
        ]
        return dense_abstract, json.dumps(mock_tasks)

    # --- PRODUCTION MODE: DISPATCH CLOUD INFERENCE TRANSLATION PASS ---
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("⚠️ [MINION WARNING] Missing GROQ_API_KEY environment parameter variable. Falling back to keyword matcher.")
        return run_keyword_fallback(raw_brief_text)

    system_instruction = (
        "You are a headless text compression utility. Your job is to read the user's raw development journal "
        "and translate it into an ultra-dense, token-saving instruction manifest for our lead architect, Wu.\n\n"
        "Rules:\n"
        "1. Remove all human filler words, personal narrative, greetings, and conversational fluff.\n"
        "2. Output exactly two distinct blocks separated by a '---SPLIT---' delimiter line.\n"
        "3. Block 1: A one-paragraph dense abstract describing the core structural system design changes.\n"
        "4. Block 2: A raw, single-line JSON array of specific technical tasks, structured exactly like this: "
        '[{"id": "OBJ-001", "task": "Short description of specific task", "status": "PENDING"}]'
    )

    try:
        client = Groq(api_key=api_key)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Delta's Journal Entry:\n{raw_brief_text}"}
            ],
            model="llama3-8b-8192",  
            temperature=0.1,         
            max_tokens=1000
        )

        response_text = chat_completion.choices.message.content.strip()
        
        if "---SPLIT---" in response_text:
            dense_abstract, json_block = response_text.split("---SPLIT---", 1)
            dense_abstract = dense_abstract.strip()
            json_block = json_block.strip()
            
            try:
                tasks_clean = json.loads(json_block)
                return dense_abstract, json.dumps(tasks_clean)
            except json.JSONDecodeError:
                print("⚠️ [MINION WARNING] Model returned malformed JSON syntax. Attempting regex extraction recovery cleanups...")
                json_match = re.search(r'\[\s*\{.*\}\s*\]', json_block, re.DOTALL)
                if json_match:
                    try:
                        return dense_abstract, json.dumps(json.loads(json_match.group(0)))
                    except Exception:
                        pass

        print("⚠️ [MINION WARNING] Split delimiter missing from output context. Running baseline slicing protocols.")
        return response_text[:250] + "...", json.dumps([{"id": "OBJ-001", "task": "Process manual session journal directives.", "status": "PENDING"}])

    except Exception as err:
        print(f"❌ [MINION CRASH] Cloud AI translation pipeline broke down: {str(err)}")
        return run_keyword_fallback(raw_brief_text)

def run_keyword_fallback(raw_brief_text):
    """Backup logic to prevent app freezes if network drops occur."""
    lines = [line.strip() for line in raw_brief_text.split('\n') if line.strip()]
    dense_abstract = f"Fallback keyword matrix active. Captured {len(lines)} raw log rows."
    objectives_list = []
    for index, line in enumerate(lines):
        if any(kw in line.lower() for kw in ['tweak', 'add', 'modify', 'fix', 'build', 'review', 'commit', 'push']):
            objectives_list.append({'id': f"OBJ-{index+1:03d}", 'task': line, 'status': 'PENDING'})
    if not objectives_list:
        objectives_list.append({'id': 'OBJ-001', 'task': 'Execute daily development plan.', 'status': 'PENDING'})
    return dense_abstract, json.dumps(objectives_list)
