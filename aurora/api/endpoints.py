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
# ======================================================================
# END: UNLOCKED_COMPONENTS_AND_BIND_COMMAND_ROUTING_VIEW (PATCH 3 OF 3)
# ======================================================================
