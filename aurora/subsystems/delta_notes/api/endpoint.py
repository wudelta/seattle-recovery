# ======================================================================
# FILE: aurora/subsystems/delta_notes/api/endpoint.py
# START: DELTA_NOTES_POST_IT_ENDPOINT
# ======================================================================
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from aurora.models import DeltaNotesEntry


@csrf_exempt
def delta_notes_endpoint(request):
    """
    Manage Delta Notes as a lightweight Post-it capture system.

    Supported lifecycle:
    - capture;
    - display;
    - edit;
    - delete;
    - mark processed.
    """
    if request.method == "GET":
        unprocessed_notes = (
            DeltaNotesEntry.objects
            .filter(
                user=request.user,
                processed=False,
            )
            .order_by("-created_at")
        )

        processed_notes = (
            DeltaNotesEntry.objects
            .filter(
                user=request.user,
                processed=True,
            )
            .order_by("-updated_at")[:50]
        )

        return JsonResponse({
            "status": "success",
            "unprocessed": [
                {
                    "id": note.id,
                    "text": note.text,
                }
                for note in unprocessed_notes
            ],
            "processed": [
                {
                    "id": note.id,
                    "text": note.text,
                }
                for note in processed_notes
            ],
        })

    if request.method != "POST":
        return JsonResponse(
            {
                "status": "error",
                "message": "Method not allowed",
            },
            status=405,
        )

    action = request.POST.get("action")

    if action == "create_note":
        text = request.POST.get("text", "").strip()

        if not text:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Note text cannot be empty.",
                },
                status=400,
            )

        note = DeltaNotesEntry.objects.create(
            user=request.user,
            text=text,
            processed=False,
        )

        return JsonResponse({
            "status": "success",
            "note_id": note.id,
            "text": note.text,
        })

    if action == "edit_note":
        note_id = request.POST.get("note_id")
        text = request.POST.get("text", "").strip()

        if not note_id or not text:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Missing note id or text.",
                },
                status=400,
            )

        updated = DeltaNotesEntry.objects.filter(
            user=request.user,
            id=note_id,
        ).update(
            text=text,
        )

        if not updated:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Note not found.",
                },
                status=404,
            )

        return JsonResponse({
            "status": "success",
        })

    if action == "delete_note":
        note_id = request.POST.get("note_id")

        if not note_id:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Missing note id.",
                },
                status=400,
            )

        deleted, _ = DeltaNotesEntry.objects.filter(
            user=request.user,
            id=note_id,
        ).delete()

        if not deleted:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Note not found.",
                },
                status=404,
            )

        return JsonResponse({
            "status": "success",
        })

    if action == "process_note":
        note_id = request.POST.get("note_id")

        if not note_id:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Missing note id.",
                },
                status=400,
            )

        updated = DeltaNotesEntry.objects.filter(
            user=request.user,
            id=note_id,
        ).update(
            processed=True,
        )

        if not updated:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Note not found.",
                },
                status=404,
            )

        return JsonResponse({
            "status": "success",
        })

    return JsonResponse(
        {
            "status": "error",
            "message": f"Unknown action: {action}",
        },
        status=400,
    )
# ======================================================================
# FILE: aurora/subsystems/delta_notes/api/endpoint.py
# END: DELTA_NOTES_POST_IT_ENDPOINT
# ======================================================================