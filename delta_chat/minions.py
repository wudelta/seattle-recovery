import os
from groq import Groq

# Initialize a standard client pointed strictly at the lightweight 8B model
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MINION_MODEL = "llama-3.1-8b-instant"

def spawn_html_minion(component_need, current_html=""):
    """Spawns a specialized frontend worker minion to write or fix raw layout code."""
    system_prompt = (
        "You are a Minion Frontend Developer Asset. Your only job is to output clean, valid HTML/CSS code. "
        "Do not include any conversational intro, text explanation, or wrap the output in markdown block strings. "
        "Output ONLY the raw code string."
    )
    
    user_prompt = f"Component Request: {component_need}\n\nExisting Code Context:\n{current_html}"
    
    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model=MINION_MODEL,
        temperature=0.2
    )
    return completion.choices[0].message.content

def spawn_patch_minion(file_context, error_traceback):
    """Spawns a debugging worker minion to fix specific line crashes in code blocks."""
    system_prompt = (
        "You are a Minion Debugging Asset. Analyze the given code context and the exact terminal traceback error. "
        "Return ONLY the corrected python code lines that replace the broken segment. Do not talk or explain."
    )
    
    user_prompt = f"Code Base Context:\n{file_context}\n\nTerminal Crash Traceback:\n{error_traceback}"
    
    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        model=MINION_MODEL,
        temperature=0.1
    )
    return completion.choices[0].message.content
