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
    """API Endpoint handling reading, writing, renaming, and deleting files safely."""
    if request.method == 'GET':
        file_path = request.GET.get('path')
        if not file_path:
            return JsonResponse({'error': 'No file path provided'}, status=400)
            
        if not file_path.startswith('/app/'):
            file_path = os.path.join('/app', file_path.lstrip('/'))

        if not os.path.exists(file_path):
            return JsonResponse({'error': f'File not found: {file_path}'}, status=404)

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

        if not file_path.startswith('/app/'):
            file_path = os.path.join('/app', file_path.lstrip('/'))

        try:
            parent_dir = os.path.dirname(file_path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': f'Failed to write file: {str(e)}'}, status=500)

    elif request.method == 'PUT':
        data = json.loads(request.body)
        file_path = data.get('path')
        new_name = data.get('new_name')

        if not file_path or not new_name:
            return JsonResponse({'error': 'Missing source path or new name payload'}, status=400)

        if not file_path.startswith('/app/'):
            file_path = os.path.join('/app', file_path.lstrip('/'))

        if not os.path.exists(file_path):
            return JsonResponse({'error': 'Target file to rename does not exist'}, status=404)

        try:
            parent_dir = os.path.dirname(file_path)
            new_file_path = os.path.join(parent_dir, new_name)
            
            # Execute filesystem migration
            os.rename(file_path, new_file_path)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': f'Rename tracking failure: {str(e)}'}, status=500)

    elif request.method == 'DELETE':
        data = json.loads(request.body)
        file_path = data.get('path')

        if not file_path:
            return JsonResponse({'error': 'No targeting path provided for purge action'}, status=400)

        if not file_path.startswith('/app/'):
            file_path = os.path.join('/app', file_path.lstrip('/'))

        if not os.path.exists(file_path):
            return JsonResponse({'error': 'File already absent from disk hierarchy'}, status=404)

        try:
            if os.path.isdir(file_path):
                import shutil
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': f'Purge validation routine failure: {str(e)}'}, status=500)
# ======================================================================
# END: TOTAL_IDE_OPERATIONS_BACKEND_PART2 (PATCH 2 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/views/ide_operations.py (PATCH 3 OF 3)
# START: TOTAL_IDE_OPERATIONS_BACKEND_PART3
# ======================================================================
@csrf_exempt
def run_code_api(request):
    """Executes code safely inside a restricted Docker sandbox using direct string execution."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    data = json.loads(request.body)
    code = data.get('code', '')
    
    client = docker.from_env()
    container = None
    try:
        # Pipe raw text through python -c to eliminate host-to-container volume mount constraints
        container = client.containers.create(
            image="python:3.11-slim",
            command=["python", "-c", code],
            network_disabled=True,
            mem_limit="128m",
            nano_cpus=500000000
        )
        container.start()
        
        # Enforce execution time ceiling limit block
        result = container.wait(timeout=5)
        output = container.logs(stdout=True, stderr=True).decode('utf-8')
        
        if not output.strip() and result.get('StatusCode') == 0:
            output = "✅ Execution completed successfully with no output returns."
    except Exception as e:
        output = f"Execution timed out or failed: {str(e)}"
        if container:
            try:
                container.kill()
            except Exception:
                pass
    finally:
        if container:
            try:
                container.remove(force=True)
            except Exception:
                pass
            
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
        
    try:
        result = subprocess.run(
            ['flake8', temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5
        )
        
        if result.returncode == 127 or "No such file or directory" in result.stderr:
            clean_errors = "[CRITICAL LINTER ERROR] flake8 is missing inside the active backend container.\nRun 'pip install flake8' in the container to resolve."
        elif result.stderr:
            clean_errors = f"[LINTER DESCRIPTOR FAILURE]\n{result.stderr}"
        else:
            clean_errors = result.stdout.replace(temp_file_path, "current_file.py")
    except subprocess.TimeoutExpired:
        clean_errors = "[ERROR] Linter execution timed out."
    except Exception as e:
        clean_errors = f"[CRITICAL EXCEPTION] Linter subsystem failure: {str(e)}"
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
    return JsonResponse({'errors': clean_errors if clean_errors.strip() else "✅ No linting issues found!"})
# ======================================================================
# END: TOTAL_IDE_OPERATIONS_BACKEND_PART3 (PATCH 3 OF 3)
# ======================================================================
