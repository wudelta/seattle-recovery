# FILE: aurora/generate_css.py
"""
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T21:12:26.808234+00:00
 PROJECT ECOSYSTEM: AURORA
 FILE PATH: aurora/minion_array/generate_css.py
 TECHNICAL MATRIX: Python Module. Exported Logic Components: run

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[generate_css.py] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[AURORA]
 ```
"""
import os
from groq import Groq

def run(task_details, fallback_context=""):
    """Generates pure CSS layout rules wrapped inside an executable style tag."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    system_prompt = (
        "You are an isolated Minion UI styling asset. "
        "Your only job is to output modern, responsive CSS rules wrapped inside an opening <style> and closing </style> tag. "
        "Do not include conversational notes, explanations, or markdown block fences (```). "
        "Output ONLY the <style>...</style> block directly."
    )
    
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Styling instructions: {task_details}\nHTML Context to Target: {fallback_context}"}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"<!-- CSS Minion Error: {str(e)} -->"