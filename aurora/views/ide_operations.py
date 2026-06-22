# ======================================================================
# FILE: aurora/views/ide_operations.py (PATCH 1 OF 1)
# START: IDE_AND_SANDBOX_CORE_LOGIC
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
    ignored = {'.git', '__pycache__', 'node_modules', '.pytest_cache', 'postgres_data'}
    
    if os.path.isdir(path):
        return {
            "text": name if name else "Project Root",
            "type": "folder",
            "path": path,
            "children": [
                get_file_tree(os.path.join(path, x)) 
                for x in os.listdir(path) if x not in ignored
            ]
        }
    else:
        return {
            "text": name,
            "type": "file",
            "path": path,
            "icon": "jstree-file"
        }

@csrf_exempt
def file_tree_api(request):
    """API Endpoint returning the JSON project folder tree."""
    return JsonResponse(get_file_tree("/app"))

@csrf_exempt
def file_operation_api(request):
    """API Endpoint handling reading and writing files to the host mount."""
    if request.method == 'GET':
        file_path = request.GET.get('path')
        if not file_path or not os.path.exists(file_path):
            return JsonResponse({'error': 'File not found'}, status=404)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return JsonResponse({'content': f.read()})
            
    elif request.method == 'POST':
        data = json.loads(request.body)
        file_path = data.get('path')
        content = data.get('content', '')
        
        if not file_path:
            return JsonResponse({'error': 'No file path provided'}, status=400)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return JsonResponse({'status': 'success'})

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
# END: IDE_AND_SANDBOX_CORE_LOGIC (PATCH 1 OF 1)
# ======================================================================
