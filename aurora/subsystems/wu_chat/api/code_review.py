# ======================================================================
# FILE: aurora/subsystems/wu_chat/api/code_review.py
# START: WU_CODE_REVIEW_ENDPOINTS
# ======================================================================

import hashlib
import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone

from aurora.models import PendingCodeChange
from aurora.subsystems.planning.services import (
    get_executable_step,
    record_actual_step_file,
)
from aurora.subsystems.wu_chat.services.workspace_context import (
    WorkspaceContextError,
    resolve_workspace_context,
)


@login_required
def approve_pending_code_change(request):
    """Apply one pending proposal after verifying the reviewed source."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        pending_change_id = data.get("pending_change_id")

        if not pending_change_id:
            return JsonResponse(
                {"error": "pending_change_id is required"},
                status=400,
            )

        with transaction.atomic():
            pending_change = (
                PendingCodeChange.objects.select_for_update()
                .get(
                    id=pending_change_id,
                    user=request.user,
                )
            )

            if pending_change.status != "PENDING":
                return JsonResponse(
                    {
                        "error": (
                            "This code change has already been reviewed."
                        ),
                        "status": pending_change.status,
                    },
                    status=409,
                )

            workspace_context = resolve_workspace_context(
                f"[READ_FILE: {pending_change.file_path}]"
            )

            if workspace_context is None:
                raise WorkspaceContextError(
                    "The pending repository path could not be resolved."
                )

            current_sha256 = hashlib.sha256(
                workspace_context.original_content.encode(
                    "utf-8"
                )
            ).hexdigest()

            if (
                current_sha256
                != pending_change.original_sha256
                or workspace_context.original_content
                != pending_change.original_content
            ):
                pending_change.status = "CONFLICT"
                pending_change.date_reviewed = timezone.now()
                pending_change.save(
                    update_fields=[
                        "status",
                        "date_reviewed",
                    ]
                )

                return JsonResponse(
                    {
                        "error": (
                            "The source file changed after review. "
                            "No repository write was performed."
                        ),
                        "status": "CONFLICT",
                    },
                    status=409,
                )

            active_step = get_executable_step(
                request.user
            )

            workspace_context.absolute_path.write_text(
                pending_change.proposed_content,
                encoding="utf-8",
            )

            reviewed_at = timezone.now()

            pending_change.status = "APPLIED"
            pending_change.date_reviewed = reviewed_at
            pending_change.date_applied = reviewed_at
            pending_change.save(
                update_fields=[
                    "status",
                    "date_reviewed",
                    "date_applied",
                ]
            )

            record_actual_step_file(
                step=active_step,
                file_path=pending_change.file_path,
                user=request.user,
                reason=(
                    "Repository mutation applied through Wu Chat "
                    "developer approval."
                ),
            )

        return JsonResponse(
            {
                "status": "APPLIED",
                "file_path": pending_change.file_path,
            }
        )

    except PendingCodeChange.DoesNotExist:
        return JsonResponse(
            {"error": "Pending code change was not found."},
            status=404,
        )
    except WorkspaceContextError as err:
        return JsonResponse(
            {"error": str(err)},
            status=400,
        )
    except (json.JSONDecodeError, ValueError) as err:
        return JsonResponse(
            {"error": str(err)},
            status=400,
        )
    except OSError:
        return JsonResponse(
            {
                "error": (
                    "The repository file could not be written."
                )
            },
            status=500,
        )


@login_required
def reject_pending_code_change(request):
    """Reject one pending proposal without mutating the repository."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        pending_change_id = data.get("pending_change_id")

        if not pending_change_id:
            return JsonResponse(
                {"error": "pending_change_id is required"},
                status=400,
            )

        updated_rows = PendingCodeChange.objects.filter(
            id=pending_change_id,
            user=request.user,
            status="PENDING",
        ).update(
            status="REJECTED",
            date_reviewed=timezone.now(),
        )

        if updated_rows == 0:
            return JsonResponse(
                {
                    "error": (
                        "Pending code change was not found or "
                        "has already been reviewed."
                    )
                },
                status=409,
            )

        return JsonResponse({"status": "REJECTED"})

    except (json.JSONDecodeError, ValueError) as err:
        return JsonResponse(
            {"error": str(err)},
            status=400,
        )
# ======================================================================

# ======================================================================
# END: WU_CODE_REVIEW_ENDPOINTS
# ======================================================================
