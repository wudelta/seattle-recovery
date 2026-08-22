# ======================================================================
# FILE: aurora/subsystems/wu_chat/services/orchestration.py
# START: WU_SYNCHRONOUS_ORCHESTRATION_SERVICE
# ======================================================================

import asyncio
import hashlib
import sys
import traceback

from aurora.minions.engine import MinionRunner
from aurora.models import DeltaDirectives, PendingCodeChange
from aurora.subsystems.wu_chat.services.patch_parser import (
    PatchParseError,
    parse_patch_response,
    response_contains_patch_markers,
)
from aurora.subsystems.wu_chat.services.workspace_context import (
    WorkspaceContextError,
    resolve_workspace_context,
)


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
# END: WU_SYNCHRONOUS_ORCHESTRATION_SERVICE
# ======================================================================
