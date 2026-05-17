# FILE: aurora/generate_js.py
"""
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T21:12:26.830416+00:00
 PROJECT ECOSYSTEM: AURORA
 FILE PATH: aurora/minion_array/generate_js.py
 TECHNICAL MATRIX: Python Module. Exported Logic Components: run

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[generate_js.py] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[AURORA]
 ```
"""
import os
from groq import Groq

def run(task_details, fallback_context=""):
    """Generates pure vanilla JavaScript logic wrapped inside an executable script tag."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    system_prompt = (
        "You are an isolated Minion interactivity asset. "
        "Your only job is to output vanilla client-side JavaScript wrapped inside an opening <script> and closing </script> tag. "
        "Target standard DOM event interactions. Do not use complex external library dependencies. "
        "Do not include any text explanations, descriptions, or markdown fences (```). "
        "Output ONLY the <script>...</script> block directly."
    )
    
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Behavior required: {task_details}\nDOM Target Context: {fallback_context}"}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"<!-- JS Minion Error: {str(e)} -->"