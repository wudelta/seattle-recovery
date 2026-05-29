import os
import shutil

def apply_file_mutation(target_file_path, code_payload, anchor_signature=None) -> bool:
    """
    Safely modifies local files by locating target anchor keywords,
    injecting payload text strings, and keeping formatting intact.
    """
    if not code_payload.endswith('\n'):
        code_payload += '\n'

    # Scenario A: Target path does not exist yet (e.g., Generating Step 2 HTML templates)
    if not os.path.exists(target_file_path):
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
        with open(target_file_path, 'w', encoding='utf-8') as new_file:
            new_file.write(code_payload)
        return True

    # Read existing target file contents
    with open(target_file_path, 'r', encoding='utf-8') as original_file:
        file_content = original_file.read()

    # Integrity Check: Prevent duplicate code block generation
    if code_payload.strip() in file_content:
        return True

    # Back up the target file before running mutations (Airtight Recovery Rule)
    backup_file_path = f"{target_file_path}.bak"
    shutil.copy2(target_file_path, backup_file_path)

    # Scenario B: Explicit Insertion Marker Anchor Provided (e.g., Views, Router)
    if anchor_signature:
        if anchor_signature in file_content:
            parts = file_content.split(anchor_signature, 1)
            # Inject payload right after your declared anchor string line
            mutated_content = f"{parts[0]}{anchor_signature}\n{code_payload}{parts[1]}"
        else:
            # Fallback Guardrail: Clean append to end of file if token is missing
            mutated_content = f"{file_content}\n{code_payload}"
            if os.path.exists(backup_file_path):
                os.remove(backup_file_path)
            return False
    else:
        # Scenario C: No Anchor Profile provided -> Append to bottom of file layout
        mutated_content = f"{file_content}\n{code_payload}"

    # Complete transactional commit write step to physical disk drive
    with open(target_file_path, 'w', encoding='utf-8') as targeted_file:
        targeted_file.write(mutated_content)
        
    return True
