import os

def global_find_and_replace(target_directory):
    # Map the exact replacement parameters we need to switch ecosystems
    replacements = {
        "from aurora": "from aurora",
        "from hopehub": "from hopehub"
    }
    
    exclude_dirs = {'.git', '__pycache__', 'venv', '.venv', '.spyproject', '.idea'}
    file_count = 0
    change_count = 0

    print("🚀 Initializing Global App-Rename Compiler Sweep...")

    for root, dirs, files in os.walk(target_directory):
        # Skip heavy dependency or virtual environment folders
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            # Target only human-written configuration/script files
            if file.endswith(('.py', '.js', '.html', '.md', '.txt')):
                file_path = os.path.join(root, file)
                file_count += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if any replacement terms exist inside this file
                    modified_content = content
                    file_changed = False
                    
                    for find_str, replace_str in replacements.items():
                        if find_str in modified_content:
                            modified_content = modified_content.replace(find_str, replace_str)
                            file_changed = True
                    
                    # Overwrite file only if structural content has modified
                    if file_changed:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(modified_content)
                        print(f"💾 Modified Imports in: {os.path.relpath(file_path, target_directory)}")
                        change_count += 1
                        
                except Exception as e:
                    print(f"⚠️ Could not read {file}: {str(e)}")

    print(f"\n✅ Sweep complete. Scanned {file_count} files. Modified imports inside {change_count} files.")

if __name__ == "__main__":
    # Runs directly inside your current seattle-recovery working directory root
    global_find_and_replace(os.getcwd())
