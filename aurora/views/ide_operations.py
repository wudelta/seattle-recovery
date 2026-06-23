# ======================================================================
# FILE: aurora/views/ide_operations.py (PATCH 1 OF 3)
# START: TOTAL_IDE_OPERATIONS_BACKEND_PART1
# ======================================================================
import os
import json
import docker
import tempfile
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def get_file_tree(path="/app"):
    """Scans the local filesystem to generate a hierarchical JSON structure."""
    name = os.path.basename(path)
    ignored = {'.git', '__pycache__', 'node_modules', '.pytest_cache', 'postgres_data', 'staticfiles', '.venv', 'venv'}
    
    if os.path.isdir(path):
        try:
            items = os.listdir(path)
        except PermissionError:
            return None
            
        children = []
        for x in items:
            if x in ignored:
                continue
            child_node = get_file_tree(os.path.join(path, x))
            if child_node:
                children.append(child_node)
                
        # Force folders to start cleanly collapsed instead of flooding the display
        return {
            "text": name if name else "Workspace Root",
            "type": "folder",
            "children": children,
            "state": {"opened": False},
            "data": {"path": path}  # Securely encapsulates path from jsTree ingestion
        }
    else:
        # Determine explicit file extensions to handle custom layout icons
        ext = name.split('.')[-1].lower() if '.' in name else ''
        file_type = "file"
        
        if ext == 'py':
            file_type = "python"
        elif ext in ['html', 'htm']:
            file_type = "html"
        elif ext == 'css':
            file_type = "css"
        elif ext in ['js', 'ts']:
            file_type = "js"
        elif ext in ['json', 'yaml', 'yml', 'ini', 'cfg']:
            file_type = "config"
            
        return {
            "text": name,
            "type": file_type,
            "data": {"path": path}  # Securely encapsulates path from jsTree ingestion
        }

@csrf_exempt
def file_tree_api(request):
    """API Endpoint returning a strict JSON array root format for jsTree."""
    root_structure = get_file_tree("/app")
    if root_structure:
        return JsonResponse([root_structure], safe=False)
    return JsonResponse([], safe=False)
# ======================================================================
# END: TOTAL_IDE_OPERATIONS_BACKEND_PART1 (PATCH 1 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/views/ide_operations.py (PATCH 2 OF 3)
# START: TOTAL_IDE_OPERATIONS_BACKEND_PART2
# ======================================================================
@csrf_exempt
def file_operation_api(request):
    """API Endpoint handling reading and writing files safely to the host mount."""
    if request.method == 'GET':
        file_path = request.GET.get('path')
        if not file_path or not os.path.exists(file_path):
            return JsonResponse({'error': 'File not found'}, status=404)
            
        # Guard clause: Prevent reading non-text/binary formats that crash string parsers
        binary_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.pyc', '.pdf', '.zip', '.tar', '.gz'}
        if any(file_path.lower().endswith(ext) for ext in binary_extensions):
            return JsonResponse({'content': '# Binary Asset detected. Contents hidden inside text viewport.'})
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return JsonResponse({'content': f.read()})
        except Exception as e:
            return JsonResponse({'error': f'Could not decode file: {str(e)}'}, status=500)
            
    elif request.method == 'POST':
        data = json.loads(request.body)
        file_path = data.get('path')
        content = data.get('content', '')
        
        if not file_path:
            return JsonResponse({'error': 'No file path provided'}, status=400)
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': f'Failed to write file: {str(e)}'}, status=500)
# ======================================================================
# END: TOTAL_IDE_OPERATIONS_BACKEND_PART2 (PATCH 2 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/views/ide_operations.py (PATCH 3 OF 3)
# START: TOTAL_IDE_OPERATIONS_BACKEND_PART3
# ======================================================================
@csrf_exempt
def run_code_api(request):
    """Executes code safely inside a restricted Docker sandbox."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    data = json.loads(request.body)
    code = data.get('code', '')
    client = docker.from_env()
    
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
        temp_file.write(code.encode('utf-8'))
        temp_file_path = temp_file.name
        
    try:
        container_output = client.containers.run(
            image="python:3.11-slim",
            command="python /app/script.py",
            volumes={temp_file_path: {'bind': '/app/script.py', 'mode': 'ro'}},
            network_disabled=True,
            mem_limit="128m",
            nano_cpus=500000000,
            timeout=5,
            remove=True
        )
        output = container_output.decode('utf-8')
    except docker.errors.ContainerError as e:
        output = e.stderr.decode('utf-8')
    except Exception as e:
        output = f"Execution timed out or failed: {str(e)}"
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
    return JsonResponse({'output': output})

@csrf_exempt
def lint_code_api(request):
    """Runs flake8 validation rules against the code text bundle."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    data = json.loads(request.body)
    code = data.get('code', '')
    
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
        temp_file.write(code.encode('utf-8'))
        temp_file_path = temp_file.name
        
    result = subprocess.run(
        ['flake8', temp_file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
        
    clean_errors = result.stdout.replace(temp_file_path, "current_file.py")
    return JsonResponse({'errors': clean_errors if clean_errors else "✅ No linting issues found!"})
# ======================================================================
# END: TOTAL_IDE_OPERATIONS_BACKEND_PART3 (PATCH 3 OF 3)
# ======================================================================
