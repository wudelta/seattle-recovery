import os

def print_tree(startpath, max_depth=3):
    exclude = {'.git', '__pycache__', '.venv', '.env', 'node_modules'}
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in exclude]
        level = root.replace(startpath, '').count(os.sep)
        if level >= max_depth:
            continue
        indent = ' ' * 4 * (level)
        print(f'{indent}📁 {os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if not f.endswith(('.pyc', '.pyo', '.DS_Store')):
                print(f'{subindent}📄 {f}')

# Run this in your project root directory
print_tree(os.getcwd(), max_depth=3)
