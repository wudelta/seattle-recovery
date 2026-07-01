# ======================================================================
# FILE: aurora/api/endpoints.py (PATCH 1 OF 3)
# START: STANDARD_DJANGO_WEB_VIEW_ENDPOINTS_IMPORTS_AND_GET_NOTES
# ======================================================================
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from aurora.models import ComponentRegistry
from aurora.utils.page_skeleton import PageSkeletonBuilder

@login_required
def delta_notes_endpoint(request):
    """
    Handles granular multi-state tracking streams for the Delta Notes module layout.
    Coordinates GET lists and processes isolated POST state actions.
    """
    from aurora.models import DeltaNotesEntry
    if request.method == "GET":
        unprocessed_nodes = DeltaNotesEntry.objects.filter(user=request.user, processed=False).order_by('-created_at')
        processed_nodes = DeltaNotesEntry.objects.filter(user=request.user, processed=True).order_by('-updated_at')[:50]
        unprocessed_payload = [{"id": n.id, "text": n.text} for n in unprocessed_nodes]
        processed_payload = [{"id": n.id, "text": n.text} for n in processed_nodes]
        return JsonResponse({
            "status": "success",
            "unprocessed": unprocessed_payload,
            "processed": processed_payload
        })
# ======================================================================
# END: STANDARD_DJANGO_WEB_VIEW_ENDPOINTS_IMPORTS_AND_GET_NOTES (PATCH 1 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/api/endpoints.py (PATCH 2 OF 3)
# START: DELTA_NOTES_POST_MUTATION_AND_COMPILATION
# ======================================================================
    elif request.method == "POST":
        action = request.POST.get("action")
        if action == "create_note":
            text = request.POST.get("text", "").strip()
            if text:
                DeltaNotesEntry.objects.create(user=request.user, text=text, processed=False)
            return JsonResponse({"status": "success"})
        elif action == "edit_note":
            note_id = request.POST.get("note_id")
            text = request.POST.get("text", "").strip()
            if note_id and text:
                DeltaNotesEntry.objects.filter(user=request.user, id=note_id).update(text=text)
            return JsonResponse({"status": "success"})
        elif action == "delete_note":
            note_id = request.POST.get("note_id")
            if note_id:
                DeltaNotesEntry.objects.filter(user=request.user, id=note_id).delete()
            return JsonResponse({"status": "success"})
        elif action == "process_note":
            note_id = request.POST.get("note_id")
            if note_id:
                DeltaNotesEntry.objects.filter(user=request.user, id=note_id).update(processed=True)
            return JsonResponse({"status": "success"})
        elif action == "compile_blueprint":
            PageSkeletonBuilder.emit_log("[BACKLOG] Commencing compilation of master project.md footprint...\n")
            unprocessed_notes = DeltaNotesEntry.objects.filter(user=request.user, processed=False).order_by('created_at')
            file_path = "project.md"
            try:
                with open(file_path, "a", encoding="utf-8") as f:
                    from django.utils import timezone
                    current_time_str = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
                    f.write(f"\n\n## Backlog Export Session Cluster ({current_time_str})\n")
                    if not unprocessed_notes.exists():
                        f.write("* Workspace verified baseline. Zero active intentions flag.\n")
                    else:
                        for note in unprocessed_notes:
                            f.write(f"* [ ] {note.text}\n")
                PageSkeletonBuilder.emit_log(f"[SUCCESS] Export sequence finalized. Updated file: {file_path}\n")
                return JsonResponse({
                    "status": "success",
                    "message": "Project file 'project.md' compiled successfully from current active backlog.",
                    "telemetry_stream": PageSkeletonBuilder.flush_telemetry()
                })
            except Exception as e:
                PageSkeletonBuilder.emit_log(f"[ERROR] Failed to compile backlog: {str(e)}\n")
                return JsonResponse({
                    "status": "error",
                    "message": f"File generation block fault: {str(e)}",
                    "telemetry_stream": PageSkeletonBuilder.flush_telemetry()
                }, status=500)
        elif action == "sync_timer":
            return JsonResponse({"status": "success"})
        return JsonResponse({"status": "error", "message": f"Invalid action: {action}"}, status=400)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
# ======================================================================
# END: DELTA_NOTES_POST_MUTATION_AND_COMPILATION (PATCH 2 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/api/endpoints.py (PATCH 3 OF 3)
# START: UNLOCKED_COMPONENTS_AND_BIND_COMMAND_ROUTING_VIEW
# ======================================================================
@csrf_exempt
@login_required
def unlocked_components_endpoint(request):
    """Decoupled standalone registry view managing component tracking records."""
    if request.method == "GET":
        unlocked_assets = ComponentRegistry.objects.filter(locked=False).order_by('-date_created')
        payload = [{"id": str(asset.id), "name": asset.name, "path": asset.file_path} for asset in unlocked_assets]
        return JsonResponse({"status": "success", "components": payload})
    elif request.method == "POST":
        target_id = request.POST.get("component_id")
        if target_id:
            ComponentRegistry.objects.filter(id=target_id).update(locked=True)
            PageSkeletonBuilder.emit_log(f"[SUCCESS] Security state mutated. Locked registry record token UUID: {target_id}\n")
            return JsonResponse({
                "status": "success",
                "telemetry_stream": PageSkeletonBuilder.flush_telemetry()
            })
        return JsonResponse({"status": "error", "message": "Missing component_id parameter."}, status=400)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@csrf_exempt
@login_required
def bind_command_endpoint(request):
    """Console bridge endpoint routing raw /bind strings to the standalone handler."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
    raw_cmd = request.POST.get("blueprint", "").strip()
    if not raw_cmd.startswith("/bind"):
        return JsonResponse({
            "status": "success",
            "minion_log": "Invalid console engine routing path. Expected /bind prefix.",
            "validation": {"valid": False, "errors": ["Invalid command format"], "warnings": []}
        })
    parts = [p.strip() for p in raw_cmd.split(" ") if p.strip()]
    from aurora.api.handlers.bind import BindCommandHandler
    handler = BindCommandHandler()
    return handler.execute(request, parts, raw_cmd)

@csrf_exempt
@login_required
def aurora_chat_stream(request):
    """
    Lightweight, stateless view orchestrating Gemini's 1-million token reasoning 
    engine with dynamic prompt parameters loaded straight from DeltaDirectives.
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    import os
    import json
    from google import genai
    from google.genai import types
    from aurora.models import DeltaDirectives

    # Setup explicit target paths inside the shared Docker volume
    DOCKER_SRC_ROOT = "/app"

    def read_workspace_file(filepath: str) -> str:
        """Reads a target code file from inside the active container mount point."""
        clean_path = filepath.lstrip("/")
        absolute_path = os.path.normpath(os.path.join(DOCKER_SRC_ROOT, clean_path))
        if not absolute_path.startswith(DOCKER_SRC_ROOT):
            return "Error: Security constraint violation. Path traversal blocked."
        try:
            with open(absolute_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file {filepath}: {str(e)}"

    def write_workspace_file(filepath: str, content: str) -> str:
        """Overwrites or instantiates structural Django codebase updates autonomously."""
        clean_path = filepath.lstrip("/")
        absolute_path = os.path.normpath(os.path.join(DOCKER_SRC_ROOT, clean_path))
        if not absolute_path.startswith(DOCKER_SRC_ROOT):
            return "Error: Security constraint violation. Path traversal blocked."
        try:
            os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
            with open(absolute_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully updated and saved {filepath} inside container storage."
        except Exception as e:
            return f"Error writing to file {filepath}: {str(e)}"

    try:
        # Load incoming payload vectors
        body_data = json.loads(request.body)
        user_prompt = body_data.get("prompt")
        incoming_history = body_data.get("history", [])

        if not user_prompt:
            return JsonResponse({"status": "error", "message": "Prompt parameter is missing."}, status=400)

        # Pull the gen-lang client secret from container execution parameters
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return JsonResponse({"status": "error", "message": "GEMINI_API_KEY environment variable is unmapped."}, status=500)

        # FIXED: Extract system rules directly out of your database records instead of hardcoding strings
        try:
            directive = DeltaDirectives.objects.get(directive_name="minion_wu", is_active=True)
            system_instruction = directive.instructions
            model_tag = directive.constraints.get("model", "gemini-2.5-flash")
            temperature = float(directive.constraints.get("temperature", 0.1))
        except DeltaDirectives.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Master system directive 'minion_wu' missing or inactive in database rows."}, status=500)

        client = genai.Client(api_key=api_key)
        workspace_tools = [read_workspace_file, write_workspace_file]

        # Build clean execution history arrays mapping straight to Google Cloud models
        gemini_history = []
        # ANTI-LOOP CONSTRAINT: Truncate context arrays down strictly to the last 6 message blocks
        for msg in incoming_history[-6:]:
            role = "user" if msg.get('role') == "user" else "model"
            gemini_history.append(
                types.Content(role=role, parts=[types.Part.from_text(text=msg.get('text', ''))])
            )

        # Initialize the persistent workspace session context tracking loop
        chat = client.chats.create(
            model=model_tag,
            history=gemini_history,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=workspace_tools,
                temperature=temperature
            )
        )

        # Execute text reasoning query
        response = chat.send_message(user_prompt)
        mutations_performed = []

        # Execute cascading agent function mutations on local storage
        if response.function_calls:
            for call in response.function_calls:
                tool_output = ""
                if call.name == "read_workspace_file":
                    tool_output = read_workspace_file(**call.args)
                    mutations_performed.append(f"Read {call.args.get('filepath')}")
                elif call.name == "write_workspace_file":
                    tool_output = write_workspace_file(**call.args)
                    mutations_performed.append(f"Mutated {call.args.get('filepath')}")

                # Pass operation outcomes straight back to complete explanations block
                response = chat.send_message(
                    types.Part.from_function_response(
                        name=call.name,
                        response={"result": tool_output}
                    )
                )

        # Export unified state metrics back down to frontend terminal layouts
        updated_history = []
        for content in chat.get_history():
            if content.parts and content.parts[0].text:
                updated_history.append({
                    "role": "user" if content.role == "user" else "assistant",
                    "text": content.parts[0].text
                })

        return JsonResponse({
            "status": "success",
            "reply": response.text,
            "mutations": mutations_performed,
            "history": updated_history
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Agent engine failure: {str(e)}"}, status=500)
# ======================================================================
# END: UNLOCKED_COMPONENTS_AND_BIND_COMMAND_ROUTING_VIEW (PATCH 3 OF 3)
# ======================================================================
