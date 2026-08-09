# ======================================================================
# FILE: aurora/subsystems/wu_chat/api/endpoint.py
# START: MODULE_RUN_IMPORTS_AND_DEPENDENCIES
# ======================================================================
import asyncio
import hashlib
import json
import sys
import time
import traceback
from collections import deque
from threading import Lock

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone

from aurora.minions.engine import MinionRunner
from aurora.models import DeltaDirectives, PendingCodeChange
from aurora.subsystems.wu_chat.services.execution_context import ExecutionContextResolver
from aurora.subsystems.wu_chat.services.patch_parser import (
    PatchParseError,
    parse_patch_response,
    response_contains_patch_markers,
)
from aurora.subsystems.wu_chat.services.workspace_context import (
    WorkspaceContextError,
    resolve_workspace_context,
)

from aurora.utils.telemetry_stream import async_send_to_console
# ======================================================================
# END: MODULE_RUN_IMPORTS_AND_DEPENDENCIES
# ======================================================================

# ======================================================================
# FILE: aurora/subsystems/wu_chat/api/endpoint.py
# START: SYNCHRONOUS_ORCHESTRATION_CORE_ENGINE
# ======================================================================

def process_wu_logic_synchronous(
    user_delta_notes,
    user,
    session_id="default_cockpit_thread",
):
    """Execute Wu and return normalized review and runtime telemetry."""
    try:
        runner = MinionRunner()

        try:
            DeltaDirectives.objects.get(
                directive_name="minion_wu",
                is_active=True,
            )
        except DeltaDirectives.DoesNotExist:
            error_msg = (
                "💥 [REGISTRY CRITICAL]: Master directive configuration "
                "'minion_wu' is missing or inactive in your database ledger!"
            )
            sys.stderr.write(f"{error_msg}\n")
            sys.stderr.flush()

            return {
                "status": "ERROR",
                "message": (
                    "Master orchestrator directive is missing "
                    "in database registry."
                ),
                "trace": error_msg,
            }

        from aurora.models import ChatLedgerEntry

        db_history = ChatLedgerEntry.objects.filter(
            session_id=session_id
        ).order_by("-created_at")[:6]

        history_buffer_lines = []

        for entry in reversed(db_history):
            if (
                entry.role == "user"
                and entry.text == user_delta_notes
            ):
                continue

            author_tag = (
                "Developer Intention"
                if entry.role == "user"
                else "Wu Response"
            )
            history_buffer_lines.append(
                f"--- PRIOR CONVERSATION STEP ({author_tag}) ---\n"
                f"{entry.text}"
            )

        history_context_block = (
            "\n\n".join(history_buffer_lines)
            if history_buffer_lines
            else ""
        )

        workspace_context = resolve_workspace_context(
            user_delta_notes
        )
        current_task_input = (
            workspace_context.hydrated_prompt
            if workspace_context
            else user_delta_notes
        )

        compiled_task_notes = current_task_input

        if history_context_block:
            compiled_task_notes = (
                f"{history_context_block}\n\n"
                "=== CURRENT LIVE WORKSPACE TASK INSTRUCTION ===\n"
                f"{current_task_input}"
            )

        complete_response_text = ""
        stream_generator = runner.run_minion_task_stream(
            "minion_wu",
            compiled_task_notes,
        )

        async def consume_stream():
            nonlocal complete_response_text

            async for token in stream_generator:
                complete_response_text += token

        def run_async_in_thread():
            new_loop = asyncio.new_event_loop()

            try:
                return new_loop.run_until_complete(
                    consume_stream()
                )
            finally:
                new_loop.close()

        import threading

        thread = threading.Thread(
            target=run_async_in_thread
        )
        thread.start()
        thread.join()

        patch_payload = None
        patch_error = None

        should_parse_patch = (
            workspace_context is not None
            and response_contains_patch_markers(
                complete_response_text
            )
        )

        if should_parse_patch:
            try:
                parsed_patch = parse_patch_response(
                    response_text=complete_response_text,
                    expected_file_path=(
                        workspace_context.file_path
                    ),
                    original_content=(
                        workspace_context.original_content
                    ),
                )
                patch_payload = parsed_patch.as_payload()

                pending_change = (
                    PendingCodeChange.objects.create(
                        user=user,
                        file_path=workspace_context.file_path,
                        original_content=(
                            workspace_context.original_content
                        ),
                        proposed_content=(
                            patch_payload["proposed_content"]
                        ),
                        original_sha256=hashlib.sha256(
                            workspace_context.original_content.encode(
                                "utf-8"
                            )
                        ).hexdigest(),
                    )
                )
                patch_payload["pending_change_id"] = str(
                    pending_change.id
                )

            except PatchParseError as err:
                patch_error = str(err)
                sys.stderr.write(
                    f"⚠️ [WU PATCH REVIEW ERROR]: "
                    f"{patch_error}\n"
                )
                sys.stderr.flush()

        execution_telemetry = {
            "provider": runner.last_provider_name,
            "model": runner.last_model_name,
            "input_tokens": runner.last_input_tokens,
            "output_tokens": runner.last_output_tokens,
            "total_tokens": runner.last_tokens_consumed,
            "latency_ms": runner.last_latency_ms,
            "provider_error": runner.last_provider_error,
        }

        r_limit = 15
        r_rem = runner.last_rpm_remaining
        t_limit = 1000000
        t_used = runner.last_tokens_consumed
        t_rem = max(0, t_limit - t_used)

        tokens_used_pct = (
            round((t_used / t_limit) * 100, 3)
            if t_limit > 0
            else 0.0
        )
        requests_used_pct = (
            round(
                ((r_limit - r_rem) / r_limit) * 100,
                1,
            )
            if r_limit > 0
            else 0.0
        )

        fuel_gauge_metrics = {
            "tokens_limit": t_limit,
            "tokens_remaining": t_rem,
            "tokens_used_pct": min(
                100.0,
                max(0.0, tokens_used_pct),
            ),
            "requests_limit": r_limit,
            "requests_remaining": r_rem,
            "requests_used_pct": min(
                100.0,
                max(0.0, requests_used_pct),
            ),
        }

        return {
            "status": "SUCCESS",
            "wu_response": complete_response_text,
            "patch": patch_payload,
            "patch_error": patch_error,
            "telemetry": execution_telemetry,
            "fuel_gauge": fuel_gauge_metrics,
        }

    except WorkspaceContextError as err:
        return {
            "status": "ERROR",
            "message": str(err),
            "trace": traceback.format_exc(),
        }
    except Exception as err:
        return {
            "status": "ERROR",
            "message": str(err),
            "trace": traceback.format_exc(),
        }

# ======================================================================
# END: SYNCHRONOUS_ORCHESTRATION_CORE_ENGINE
# ======================================================================

# ======================================================================
# FILE: aurora/subsystems/wu_chat/api/endpoint.py
# START: CHAT_REQUEST_AND_CODE_REVIEW_ENDPOINTS
# ======================================================================
@login_required
def wu_chat_endpoint(request):
    """
    Process Wu requests and return chat, review, and execution telemetry.
    """
    from aurora.models import ChatLedgerEntry

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        data = json.loads(request.body)
        delta_notes = data.get("delta_notes", "").strip()
        session_id = data.get(
            "session_id",
            "default_cockpit_thread",
        )

        if not delta_notes:
            return JsonResponse(
                {"error": "Empty delta notes provided"},
                status=400,
            )

        try:
            sanitized_notes = enforce_context_token_budget(
                delta_notes
            )
        except ValueError as rate_err:
            return JsonResponse(
                {
                    "error": (
                        "🛡️ [GATEWAY SHIELD]: "
                        f"{str(rate_err)}"
                    )
                },
                status=429,
            )

        ChatLedgerEntry.objects.create(
            user=request.user,
            session_id=session_id,
            role="user",
            text=sanitized_notes,
        )

        result = process_wu_logic_synchronous(
            sanitized_notes,
            request.user,
            session_id=session_id,
        )

        if result["status"] == "ERROR":
            return JsonResponse(
                {
                    "error": result["message"],
                    "traceback": result["trace"],
                },
                status=500,
            )

        model_reply = result.get(
            "wu_response",
            "",
        ).strip()

        if model_reply:
            ChatLedgerEntry.objects.create(
                user=request.user,
                session_id=session_id,
                role="model",
                text=model_reply,
            )

        return JsonResponse(
            {
                "status": "wu_is_processing",
                "direct_text_output": result["wu_response"],
                "patch": result.get("patch"),
                "patch_error": result.get("patch_error"),
                "telemetry": result.get("telemetry", {}),
                "fuel_gauge": result.get(
                    "fuel_gauge",
                    {},
                ),
            }
        )

    except Exception as err:
        return JsonResponse(
            {"error": str(err)},
            status=400,
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
# END: CHAT_REQUEST_AND_CODE_REVIEW_ENDPOINTS
# ======================================================================

# ======================================================================
# FILE: aurora/subsystems/wu_chat/api/endpoint.py
# START: PRE_SEND_TRAFFIC_SAFETY_MONITORING_METRICS
# ======================================================================
# Thread safety locks and allocation deques tracking network transaction states
OUTBOUND_TRAFFIC_LOG = deque()
TRAFFIC_LOCK = Lock()
# ======================================================================
# END: PRE_SEND_TRAFFIC_SAFETY_MONITORING_METRICS
# ======================================================================

# ======================================================================
# FILE: aurora/subsystems/wu_chat/api/endpoint.py
# START: UTILITY_CONTEXT_TOKEN_BUDGETER
# ======================================================================
def enforce_context_token_budget(raw_text_payload, max_tokens=150000):
    """
    Traps and analyzes outbound payloads before any API call is made.
    Logs absolute metrics and strips out massive text blocks dynamically.
    """
    if not raw_text_payload:
        sys.stderr.write(
            "📊 [TRAFFIC ANALYZER]: Received empty or null payload text.\n"
        )
        sys.stderr.flush()
        return ""

    # Measure exact inbound metrics before modification
    raw_char_count = len(raw_text_payload)
    estimated_raw_tokens = raw_char_count // 4

    sys.stderr.write(
        f"\n📊 [TRAFFIC ANALYZER PRE-SEND AUDIT]:\n"
        f"  -> Total Character Volume: {raw_char_count}\n"
        f"  -> Estimated Inbound Tokens: {estimated_raw_tokens}\n"
        f"  -> Safety Budget Target Limit: {max_tokens} tokens "
        f"(~{max_tokens * 4} chars)\n"
    )
    sys.stderr.flush()

    # If the payload fits comfortably within our budget boundaries, pass it intact
    max_chars = max_tokens * 4
    if raw_char_count <= max_chars:
        sys.stderr.write(
            "📊 [TRAFFIC ANALYZER]: "
            "Payload is clean. Forwarding completely intact.\n"
        )
        sys.stderr.flush()
        return raw_text_payload

    sys.stderr.write(
        "⚠️ [TRAFFIC ANALYZER]: Payload size boundary crossed! "
        "Executing surgical line-trimming...\n"
    )
    sys.stderr.flush()

    # Split the payload into lines to find what is inflating the string footprint
    lines = raw_text_payload.split("\n")
    sanitized_lines = []
    accumulated_chars = 0
    stripped_lines_count = 0

    for line in lines:
        line_len = len(line)

        # Guard 1: Drop individual giant string lines
        if line_len > 2000:
            stripped_lines_count += 1
            continue

        # Guard 2: Halt collection near the hard character ceiling
        if accumulated_chars + line_len + 1 > max_chars:
            stripped_lines_count += (
                len(lines)
                - len(sanitized_lines)
                - stripped_lines_count
            )
            break

        sanitized_lines.append(line)
        accumulated_chars += line_len + 1

    sanitized_text = "\n".join(sanitized_lines)

    # Append a clear system marker when truncation occurred
    if stripped_lines_count > 0:
        sanitized_text += (
            "\n\n... [🛡️ SECURITY INTERCEPT: "
            f"{stripped_lines_count} OVERSIZED/SURPLUS LINES STRIPPED "
            "TO PREVENT 429 LOCKOUT] ..."
        )

    sys.stderr.write(
        f"📊 [TRAFFIC ANALYZER POST-SANITIZATION SUMMARY]:\n"
        f"  -> Cleaned Character Footprint: {len(sanitized_text)}\n"
        f"  -> Cleaned Token Appx: {len(sanitized_text) // 4}\n"
        f"  -> Total Structural Lines Evicted: "
        f"{stripped_lines_count}\n\n"
    )
    sys.stderr.flush()

    return sanitized_text
# ======================================================================
# END: UTILITY_CONTEXT_TOKEN_BUDGETER
# ======================================================================