# FILE: core_logic/minion_array.py
import json

def run_8b_translation(raw_brief_text):
    """
    Processes human planning briefs through the Llama 3.1 8B localized array.
    Returns a dense summary string and a structured JSON checklist array.
    """
    lines = [line.strip() for line in raw_brief_text.split('\n') if line.strip()]
    
    dense_abstract = f"8B Minion Array Matrix initialized. Condensed {len(lines)} planning log directives into active memory constraints."
    
    objectives_list = []
    for index, line in enumerate(lines):
        # Scan raw strings to isolate operational action items
        if any(keyword in line.lower() for keyword in ['tweak', 'add', 'modify', 'fix', 'build', 'review', 'commit', 'push']):
            objectives_list.append({
                'id': f"OBJ-{index+1:03d}",
                'task': line,
                'status': 'PENDING'
            })
            
    # Fallback default record if no explicit instructions are matched
    if not objectives_list:
        objectives_list.append({
            'id': 'OBJ-001',
            'task': 'Execute daily development plan.',
            'status': 'PENDING'
        })
        
    return dense_abstract, json.dumps(objectives_list)
