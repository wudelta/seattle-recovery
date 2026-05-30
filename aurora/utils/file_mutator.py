import os
import shutil

def apply_file_mutation(target_file_path, code_payload, anchor_signature=None) -> bool:
    """
    Safely modifies local files by locating target anchor keywords, injecting payload text strings,
    and keeping formatting intact. Automatically hooks __init__.py files for modular package directories.
    """
    if not code_payload.endswith('\n'):
        code_payload += '\n'

    target_dir = os.path.dirname(target_file_path)

    # Scenario A: Target path does not exist yet (e.g., Generating Step 2 HTML templates)
    if not os.path.exists(target_file_path):
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
        
        with open(target_file_path, 'w', encoding='utf-8') as new_file:
            new_file.write(code_payload)
            
        # SMART DIRECTORY INTERCEPTION HOOK (On fresh file creation)
        _handle_package_directory_interception(target_dir, target_file_path)
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

    # INITIALIZE DEFAULT PAYLOAD VALUE TO PREVENT UNBOUNDLOCALERROR TRAINS
    mutated_content = None

    # Scenario B: Explicit Insertion Marker Anchor Provided (e.g., Views, Router)
    if anchor_signature:
        if anchor_signature in file_content:
            lines = file_content.splitlines(keepends=True)
            mutated_lines = []
            mutation_applied = False

            for line in lines:
                mutated_lines.append(line)
                if anchor_signature in line and not mutation_applied:
                    # THE AUTOMATED FORCE MULTIPLIER FIX: 
                    # Extract the exact leading whitespace (spaces/tabs) from the anchor line
                    leading_whitespace = line[:len(line) - len(line.lstrip())]
                    
                    # Apply that identical indentation offset directly to the incoming code payload
                    indented_payload = f"{leading_whitespace}{code_payload.lstrip()}"
                    if not indented_payload.endswith('\n'):
                        indented_payload += '\n'
                        
                    mutated_lines.append(indented_payload)
                    mutation_applied = True
            mutated_content = "".join(mutated_lines)
        else:
            # Fallback Guardrail: Clean append to end of file if token is missing
            mutated_content = f"{file_content}\n{code_payload}"
    else:
        # Scenario C: No Anchor Profile provided -> Completely overwrite or clean replace
        mutated_content = code_payload

    # Double-check that we have data assigned to prevent disk writing loops from crashing
    if mutated_content is None:
        if os.path.exists(backup_file_path):
            os.remove(backup_file_path)
        return False

    # Complete transactional commit write step to physical disk drive
    with open(target_file_path, 'w', encoding='utf-8') as targeted_file:
        targeted_file.write(mutated_content)

    # SMART DIRECTORY INTERCEPTION HOOK (On modified existing file)
    _handle_package_directory_interception(target_dir, target_file_path)
    return True


def _handle_package_directory_interception(target_dir: str, target_file_path: str) -> None:
    """
    Internal helper to scan if a target folder is acting as a package 
    and automatically registers the new module into __init__.py if missing.
    """
    if not target_dir:
        return
        
    init_file_path = os.path.join(target_dir, "__init__.py")
    if os.path.exists(init_file_path):
        # Create an operational backup of the package initializer if none exists yet
        if not os.path.exists(f"{init_file_path}.bak"):
            shutil.copy2(init_file_path, f"{init_file_path}.bak")
        
        # FIX: Appended [0] to extract root module name string cleanly out of the splitext tuple!
        module_name = os.path.splitext(os.path.basename(target_file_path))[0]
        import_statement = f"from .{module_name} import *\n"

        # Safe transactional record stream check
        with open(init_file_path, 'r', encoding='utf-8') as init_file:
            init_content = init_file.read()
            
        if import_statement not in init_content:
            with open(init_file_path, 'a', encoding='utf-8') as init_file:
                # Guarantees it never appends directly onto an existing line text block
                init_file.write(f"\n{import_statement}")


def rollback_file_mutation(target_file_path: str) -> None:
    """
    SAFE PARSING ROLLBACK ENGINE:
    Scrubs the package initializer constructor strings BEFORE handling files, 
    and leverages File Target Preservation to keep Django from crashing during hot-reloads.
    """
    target_dir = os.path.dirname(target_file_path)
    # FIX: Appended [0] to extract root module name string cleanly out of the splitext tuple!
    module_name = os.path.splitext(os.path.basename(target_file_path))[0]
    import_statement = f"from .{module_name} import *\n"

    # 1. SCRUB INITIALIZER FIRST: Break the import loop before deleting/modifying any files
    if target_dir:
        init_file_path = os.path.join(target_dir, "__init__.py")
        if os.path.exists(init_file_path):
            with open(init_file_path, "r", encoding="utf-8") as f:
                content = f.read()
            if import_statement in content:
                content = content.replace(import_statement, "")
                with open(init_file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            
            # Revert entirely if an operational backup exists
            init_backup = f"{init_file_path}.bak"
            if os.path.exists(init_backup):
                shutil.move(init_backup, init_file_path)

    # 2. FILE TARGET PRESERVATION: Restore original or write a baseline placeholder
    backup_file_path = f"{target_file_path}.bak"
    if os.path.exists(backup_file_path):
        shutil.move(backup_file_path, target_file_path)
    elif os.path.exists(target_file_path):
        with open(target_file_path, "w", encoding="utf-8") as f:
            f.write("# Module baseline cleared by Aurora Rollback Engine\n")
