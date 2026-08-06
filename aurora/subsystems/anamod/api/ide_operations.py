# ======================================================================
# FILE: aurora/api/ide_operations.py
# START: TOTAL_IDE_OPERATIONS_BACKEND_PART1
# ======================================================================
import json
import subprocess
import tempfile

import docker
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from aurora.subsystems.anamod.services.workspace_service import (
    WorkspaceOperationError,
    build_file_tree,
    create_workspace_node,
    delete_workspace_node,
    read_workspace_file,
    rename_workspace_node,
    update_workspace_file,
)


@csrf_exempt
def file_tree_api(request):
    """Return the Anamod workspace hierarchy in jsTree root format."""
    root_structure = build_file_tree()

    if root_structure:
        return JsonResponse(
            [root_structure],
            safe=False,
        )

    return JsonResponse(
        [],
        safe=False,
    )
# ======================================================================
# FILE: aurora/api/ide_operations.py
# END: TOTAL_IDE_OPERATIONS_BACKEND_PART1
# ======================================================================

# ======================================================================
# FILE: aurora/api/ide_operations.py
# START: TOTAL_IDE_OPERATIONS_BACKEND_PART2
# ======================================================================
@csrf_exempt
def file_operation_api(request):
    """Adapt Anamod file-operation requests to the workspace service."""
    try:
        if request.method == "GET":
            file_path = request.GET.get("path")

            if not file_path:
                return JsonResponse(
                    {"error": "No file path provided"},
                    status=400,
                )

            content = read_workspace_file(file_path)

            return JsonResponse({
                "content": content,
            })

        data = json.loads(request.body)

        if request.method == "POST":
            file_path = data.get("path")
            node_type = data.get("type", "file")
            content = data.get("content", "")

            if not file_path:
                return JsonResponse(
                    {"error": "No file path provided"},
                    status=400,
                )

            result = create_workspace_node(
                file_path=file_path,
                node_type=node_type,
                content=content,
            )

            return JsonResponse(result)

        if request.method == "PATCH":
            file_path = data.get("path")
            content = data.get("content")

            if not file_path:
                return JsonResponse(
                    {"error": "No file path provided"},
                    status=400,
                )

            if content is None:
                return JsonResponse(
                    {"error": "No file content provided"},
                    status=400,
                )

            result = update_workspace_file(
                file_path=file_path,
                content=content,
            )

            return JsonResponse(result)

        if request.method == "PUT":
            file_path = data.get("path")
            new_name = data.get("new_name")

            if not file_path or not new_name:
                return JsonResponse(
                    {
                        "error": (
                            "Missing source path or new name payload"
                        ),
                    },
                    status=400,
                )

            result = rename_workspace_node(
                file_path=file_path,
                new_name=new_name,
            )

            return JsonResponse(result)

        if request.method == "DELETE":
            file_path = data.get("path")

            if not file_path:
                return JsonResponse(
                    {
                        "error": (
                            "No targeting path provided for purge action"
                        ),
                    },
                    status=400,
                )

            result = delete_workspace_node(file_path)

            return JsonResponse(result)

        return JsonResponse(
            {"error": "Method not allowed"},
            status=405,
        )

    except WorkspaceOperationError as exc:
        return JsonResponse(
            {"error": exc.message},
            status=exc.status,
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON request body"},
            status=400,
        )
# ======================================================================
# FILE: aurora/api/ide_operations.py
# END: TOTAL_IDE_OPERATIONS_BACKEND_PART2
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
        container = client.containers.create(
            image="python:3.11-slim",
            command=["python", "-c", code],
            network_disabled=True,
            mem_limit="128m",
            nano_cpus=500000000
        )
        container.start()
        
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
    """Aggregates syntax checks and runs a strictly filtered flake8 pass targeting logical errors."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    data = json.loads(request.body)
    code = data.get('code', '')
    
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
        temp_file.write(code.encode('utf-8'))
        temp_file_path = temp_file.name
        
    try:
        # LAYER 1: Immediate compilation pass to find crash-inducing syntax issues
        compile_result = subprocess.run(
            ['python', '-m', 'py_compile', temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2
        )
        
        syntax_errors = ""
        if compile_result.returncode != 0:
            raw_err = compile_result.stderr or compile_result.stdout
            cleaned_err = raw_err.replace(temp_file_path, "current_file.py").strip()
            syntax_errors = f"❌ [FATAL SYNTAX ERROR / CRASH RISK]\n{cleaned_err}\n"

        # LAYER 2: Filtered Flake8 analysis ignoring cosmetic layout or length conventions
        style_warnings = ""
        try:
            flake_result = subprocess.run(
                [
                    'flake8', 
                    '--ignore=E301,E302,E303,E304,E305,E306,E501,W291,W292,W293,E111,E114,E121,E122,E123,E124,E125,E126,E127,E128', 
                    temp_file_path
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=3
            )
            
            if flake_result.returncode != 0:
                style_warnings = flake_result.stdout.replace(temp_file_path, "current_file.py").strip()
        except FileNotFoundError:
            style_warnings = "⚠️ [ENVIRONMENT WARNING] 'flake8' command was not found inside the active container. Install it with 'pip install flake8' to see critical reference warnings."
        except Exception as e:
            style_warnings = f"⚠️ [LINTER EXECUTION ERROR] Failed running flake8 analysis: {str(e)}"

        # Build clean structural report
        output_buffer = []
        if syntax_errors:
            output_buffer.append(syntax_errors)
        else:
            output_buffer.append("✅ [SYNTAX CHECK] Python file compiles cleanly.")
            
        if style_warnings:
            output_buffer.append(f"\n🎨 [LOGICAL FLAWS & WARNINGS]\n{style_warnings}")

        final_report = "\n".join(output_buffer)
    except subprocess.TimeoutExpired:
        final_report = "[ERROR] Code validation pipeline processing timeout."
    except Exception as e:
        final_report = f"[CRITICAL EXCEPTION] Verification engine failure: {str(e)}"
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
    return JsonResponse({'errors': final_report})
# ======================================================================
# END: TOTAL_IDE_OPERATIONS_BACKEND_PART3 (PATCH 3 OF 3)
# ======================================================================
