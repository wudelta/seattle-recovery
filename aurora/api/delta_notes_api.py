# ======================================================================
# FILE: aurora/api/delta_notes_api.py (PATCH 1 OF 2)
# START: PACKAGED_IMPORTS_AND_DEPENDENCIES
# ======================================================================
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from aurora.models import DeltaNotesEntry
# ======================================================================
# END: PACKAGED_IMPORTS_AND_DEPENDENCIES
# ======================================================================

# ======================================================================
# FILE: aurora/api/delta_notes_api.py (PATCH 2 OF 2)
# START: API_ENDPOINT_LOGIC
# ======================================================================
@login_required
def delta_notes_endpoint(request):
    """
    Unified JSON engine managing task additions, global session focus logging, 
    and direct markdown blueprint compilations with strict safety checks.
    """
    if request.method == "GET":
        notes = DeltaNotesEntry.objects.filter(user=request.user, processed=False).values(
            'id', 'text', 'total_seconds_logged', 'created_at'
        )
        return JsonResponse({"status": "success", "entries": list(notes)})

    elif request.method == "POST":
        action = request.POST.get("action")

        if action == "compile_blueprint":
            unprocessed_notes = DeltaNotesEntry.objects.filter(user=request.user, processed=False).order_by('created_at')
            if not unprocessed_notes.exists():
                return JsonResponse({"status": "success", "message": "No new notes to process. project.md remains pristine."})

            from pathlib import Path
            project_root = Path(settings.BASE_DIR).resolve()
            
            project_md_path = project_root / 'project.md'
            if not project_md_path.exists():
                project_md_path = project_root.parent / 'project.md'

            if not project_md_path.exists():
                return JsonResponse({
                    "status": "error", 
                    "message": f"Target project.md not found! Checked locations: '{project_root / 'project.md'}' and '{project_root.parent / 'project.md'}'. Database states preserved."
                }, status=404)

            append_buffer = f"\n\n## Added via DeltaNotes Lifecycle ({timezone.now().strftime('%Y-%m-%d %H:%M')})\n"
            for note in unprocessed_notes:
                append_buffer += f"* [ ] {note.text}\n"

            try:
                with open(project_md_path, 'a', encoding='utf-8') as f:
                    f.write(append_buffer)
                unprocessed_notes.update(processed=True, last_started_at=timezone.now())
                return JsonResponse({"status": "success", "message": f"Successfully compiled changes directly to: {project_md_path}"})
            except IOError as e:
                return JsonResponse({"status": "error", "message": f"Filesystem write failure: {str(e)}"}, status=500)

        elif action == "sync_timer":
            current_duration = request.POST.get("current_duration")
            if current_duration is None:
                return JsonResponse({"status": "error", "message": "Missing duration variable."}, status=400)

            try:
                duration_int = int(current_duration)
                if duration_int < 0:
                    return JsonResponse({"status": "error", "message": "Time intervals cannot be negative."}, status=400)
                
                # Dynamic Allocation: Bind global session seconds directly to your latest open task
                latest_note = DeltaNotesEntry.objects.filter(user=request.user, processed=False).order_by('-created_at').first()
                if latest_note:
                    latest_note.total_seconds_logged = duration_int
                    latest_note.save()
                    return JsonResponse({"status": "success", "total_seconds_logged": latest_note.total_seconds_logged})
                return JsonResponse({"status": "success", "message": "Time received, no active note to bind to."})
            except ValueError:
                return JsonResponse({"status": "error", "message": "Invalid tracking metrics parsing."}, status=400)

        elif action == "create_note":
            text = request.POST.get("text", "").strip()
            if not text:
                return JsonResponse({"status": "error", "message": "Note context cannot be empty."}, status=400)
            
            note = DeltaNotesEntry.objects.create(user=request.user, text=text)
            return JsonResponse({"status": "success", "note_id": note.id, "text": note.text})

    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)
# ======================================================================
# END: API_ENDPOINT_LOGIC
# ======================================================================
