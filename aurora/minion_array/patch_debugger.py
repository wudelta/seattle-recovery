import os
from groq import Groq

def run(task_details, fallback_context=""):
    """
    Analyzes Python trackbacks alongside file contents to generate clean bug fixes.
    task_details: The raw terminal traceback error string.
    fallback_context: The text content of the broken python file.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    system_prompt = (
        "You are an isolated Minion Python Debugging Asset. "
        "Analyze the user's codebase context and the exact terminal traceback error. "
        "Identify the broken code lines and output ONLY the clean, corrected Python code segment "
        "that fixes the crash. Do not include conversational notes, intros, markdown code fences (```), "
        "or explanations. Provide only the direct executable lines."
    )
    
    user_prompt = (
        f"Terminal Traceback Error:\n{task_details}\n\n"
        f"--- BROKEN FILE CONTENT CONTEXT ---\n{fallback_context}\n---------------------------"
    )
    
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"# Patch Debugger Execution Error: {str(e)}"
