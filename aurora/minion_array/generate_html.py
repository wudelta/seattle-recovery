# FILE: aurora/generate_html.py
"""
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T21:12:26.939627+00:00
 PROJECT ECOSYSTEM: AURORA
 FILE PATH: aurora/minion_array/generate_html.py
 TECHNICAL MATRIX: Python Module. Exported Logic Components: run

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[generate_html.py] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[AURORA]
 ```
"""
import os
from groq import Groq

def run(task_details, fallback_context=""):
    """Generates pure HTML skeleton components."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    system_prompt = (
        "You are an isolated Minion Frontend structural layout asset. "
        "Your only job is to output valid, semantic HTML component code. "
        "Do not write styling tags (<style>) or interactive script tags (<script>). "
        "Do not include conversational filler, notes, or markdown block strings (```). "
        "Output ONLY the raw HTML elements."
    )
    
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Structure needed: {task_details}\nContext: {fallback_context}"}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"<!-- HTML Minion Error: {str(e)} -->"