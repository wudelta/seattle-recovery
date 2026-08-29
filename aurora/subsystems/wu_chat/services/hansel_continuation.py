# ======================================================================
# FILE: aurora/subsystems/wu_chat/services/hansel_continuation.py
# START: HANSEL_CONTINUATION_SERVICE
# ======================================================================

import asyncio
import threading
import time
import traceback

from aurora.subsystems.wu_chat.services.application_resource import (
    ApplicationResourceError,
    build_application_resource_continuation,
    resolve_application_resource_request,
)
from aurora.subsystems.wu_chat.services.workspace_context import (
    WorkspaceContextError,
    resolve_repository_request,
)


MAX_HANSEL_CONTINUATIONS = 8


# ======================================================================
# START: WU_INVOCATION
# ======================================================================

def _invoke_wu(runner, task_input, invocation_economics):
    """Run one Wu invocation and record its observable runtime economics."""
    response_text = ""
    invocation_started_at = time.perf_counter()

    stream_generator = runner.run_minion_task_stream(
        "minion_wu",
        task_input,
    )

    async def consume_stream():
        nonlocal response_text

        async for token in stream_generator:
            response_text += token

    def run_async_in_thread():
        new_loop = asyncio.new_event_loop()

        try:
            return new_loop.run_until_complete(
                consume_stream()
            )
        finally:
            new_loop.close()

    thread = threading.Thread(
        target=run_async_in_thread
    )
    thread.start()
    thread.join()

    invocation_elapsed_ms = round(
        (
            time.perf_counter()
            - invocation_started_at
        )
        * 1000,
        2,
    )

    invocation_economics.append(
        {
            "sequence": len(invocation_economics) + 1,
            "provider": runner.last_provider_name,
            "model": runner.last_model_name,
            "input_tokens": runner.last_input_tokens,
            "output_tokens": runner.last_output_tokens,
            "total_tokens": runner.last_tokens_consumed,
            "elapsed_ms": invocation_elapsed_ms,
            "provider_latency_ms": runner.last_latency_ms,
            "provider_cost": getattr(
                runner,
                "last_cost",
                None,
            ),
            "provider_error": runner.last_provider_error,
        }
    )

    return response_text


# ======================================================================
# END: WU_INVOCATION
# ======================================================================


# ======================================================================
# START: HANSEL_NAVIGATION_METRICS
# ======================================================================

def _format_continuation_trace(continuation_paths):
    return (
        "Hansel continuation path:\n"
        + "\n".join(
            f"{index}. {file_path}"
            for index, file_path in enumerate(
                continuation_paths,
                start=1,
            )
        )
    )


def _build_hansel_navigation_metrics(
    hansel_transitions,
    cumulative_repository_context_characters,
    cumulative_repository_context_bytes,
    invocation_economics,
    navigation_started_at,
    application_resources=None,
):
    hydrated = [
        transition
        for transition in hansel_transitions
        if transition["outcome"] == "HYDRATED"
    ]
    duplicate_requests = [
        transition
        for transition in hansel_transitions
        if transition.get("duplicate_request")
    ]
    backtracks = [
        transition
        for transition in hansel_transitions
        if transition.get("backtrack")
    ]
    failed_routes = [
        transition
        for transition in hansel_transitions
        if transition["outcome"] != "HYDRATED"
    ]
    unnecessary_load_candidates = [
        transition
        for transition in hydrated
        if transition.get("unnecessary_load_candidate")
    ]

    navigation_elapsed_ms = round(
        (
            time.perf_counter()
            - navigation_started_at
        )
        * 1000,
        2,
    )
    known_costs = [
        invocation["provider_cost"]
        for invocation in invocation_economics
        if invocation.get("provider_cost") is not None
    ]
    provider_cost_available = (
        len(known_costs) == len(invocation_economics)
        and bool(invocation_economics)
    )

    application_resources = application_resources or []

    return {
        "transition_count": len(hansel_transitions),
        "authority_hop_count": len(hydrated),
        "duplicate_load_count": 0,
        "duplicate_request_count": len(duplicate_requests),
        "failed_route_count": len(failed_routes),
        "backtrack_count": len(backtracks),
        "unnecessary_authority_load_count": len(
            unnecessary_load_candidates
        ),
        "unique_repository_context_characters": sum(
            transition.get("context_characters", 0)
            for transition in hydrated
        ),
        "unique_repository_context_bytes": sum(
            transition.get("context_bytes", 0)
            for transition in hydrated
        ),
        "cumulative_repository_context_characters": (
            cumulative_repository_context_characters
        ),
        "cumulative_repository_context_bytes": (
            cumulative_repository_context_bytes
        ),
        "application_resource_count": len(application_resources),
        "application_resource_characters": sum(
            resource.get("context_characters", 0)
            for resource in application_resources
        ),
        "application_resource_bytes": sum(
            resource.get("context_bytes", 0)
            for resource in application_resources
        ),
        "application_resources": application_resources,
        "economics": {
            "invocation_count": len(invocation_economics),
            "elapsed_ms": navigation_elapsed_ms,
            "human_intervention_count": 0,
            "input_tokens": sum(
                invocation.get("input_tokens") or 0
                for invocation in invocation_economics
            ),
            "output_tokens": sum(
                invocation.get("output_tokens") or 0
                for invocation in invocation_economics
            ),
            "total_tokens": sum(
                invocation.get("total_tokens") or 0
                for invocation in invocation_economics
            ),
            "provider_cost_available": provider_cost_available,
            "provider_cost": (
                sum(known_costs)
                if provider_cost_available
                else None
            ),
            "provider_cost_unavailable_reason": (
                None
                if provider_cost_available
                else (
                    "The active provider runtime did not report monetary "
                    "cost for every invocation."
                )
            ),
            "invocations": invocation_economics,
        },
        "transitions": hansel_transitions,
    }


# ======================================================================
# END: HANSEL_NAVIGATION_METRICS
# ======================================================================


# ======================================================================
# START: HANSEL_CONTINUATION_TASK
# ======================================================================

def _build_continuation_task(
    repository_file,
    hydrated_authorities,
    original_task,
):
    previous_authority_blocks = []

    for authority in hydrated_authorities:
        trailing_newline = (
            ""
            if authority.original_content.endswith("\n")
            else "\n"
        )
        previous_authority_blocks.append(
            "[AUTHORITY_FILE_START]\n"
            f"FILE_PATH: {authority.file_path}\n"
            f"{authority.original_content}"
            f"{trailing_newline}"
            "[AUTHORITY_FILE_END]"
        )

    previous_authority_context = ""

    if previous_authority_blocks:
        previous_authority_context = (
            "[PREVIOUS_AUTHORITY_TRAIL_START]\n"
            + "\n".join(previous_authority_blocks)
            + "\n"
            "[PREVIOUS_AUTHORITY_TRAIL_END]\n"
        )

    requested_file_newline = (
        ""
        if repository_file.original_content.endswith("\n")
        else "\n"
    )

    return (
        "[AURORA_HANSEL_CONTINUATION]\n"
        f"REQUESTED_FILE: {repository_file.file_path}\n"
        "[ORIGINAL_TASK_START]\n"
        f"{original_task.strip()}\n"
        "[ORIGINAL_TASK_END]\n"
        f"{previous_authority_context}"
        "[REQUESTED_FILE_START]\n"
        f"{repository_file.original_content}"
        f"{requested_file_newline}"
        "[REQUESTED_FILE_END]\n"
        "[/AURORA_HANSEL_CONTINUATION]"
    )


# ======================================================================
# END: HANSEL_CONTINUATION_TASK
# ======================================================================


# ======================================================================
# START: HANSEL_CONTINUATION_EXECUTION
# ======================================================================

def execute_hansel_continuation(
    *,
    runner,
    initial_task_input,
    original_task,
    user=None,
):
    """Execute Wu through bounded repository and application continuation."""
    navigation_started_at = time.perf_counter()
    invocation_economics = []
    continuation_count = 0
    application_resource_count = 0
    continuation_paths = []
    hansel_transitions = []
    application_resources = []
    hydrated_authorities = []
    hydrated_paths = set()
    hydrated_resource_paths = set()
    cumulative_repository_context_characters = 0
    cumulative_repository_context_bytes = 0
    last_context_label = None

    complete_response_text = _invoke_wu(
        runner,
        initial_task_input,
        invocation_economics,
    )

    def navigation_metrics():
        return _build_hansel_navigation_metrics(
            hansel_transitions,
            cumulative_repository_context_characters,
            cumulative_repository_context_bytes,
            invocation_economics,
            navigation_started_at,
            application_resources,
        )

    while True:
        try:
            repository_file = resolve_repository_request(
                complete_response_text
            )
        except WorkspaceContextError as err:
            hansel_transitions.append(
                {
                    "sequence": len(hansel_transitions) + 1,
                    "from_authority": last_context_label,
                    "to_authority": None,
                    "outcome": "FAILED_ROUTE",
                    "duplicate_request": False,
                    "backtrack": False,
                    "unnecessary_load_candidate": False,
                    "context_characters": 0,
                    "context_bytes": 0,
                    "error": str(err),
                }
            )
            return {
                "status": "ERROR",
                "message": str(err),
                "trace": traceback.format_exc(),
                "hansel_navigation": navigation_metrics(),
            }

        try:
            application_resource = resolve_application_resource_request(
                complete_response_text,
                user=user,
            )
        except ApplicationResourceError as err:
            return {
                "status": "ERROR",
                "message": str(err),
                "trace": traceback.format_exc(),
                "hansel_navigation": navigation_metrics(),
            }

        if repository_file is not None and application_resource is not None:
            return {
                "status": "ERROR",
                "message": (
                    "Wu requested repository authority and an Aurora "
                    "application resource in the same continuation response. "
                    "Request exactly one continuation resource at a time."
                ),
                "trace": _format_continuation_trace(continuation_paths),
                "hansel_navigation": navigation_metrics(),
            }

        if repository_file is None and application_resource is None:
            break

        if application_resource is not None:
            resource_path = application_resource.resource_path
            continuation_paths.append(f"RESOURCE:{resource_path}")

            try:
                continuation_task, resource_metric = (
                    build_application_resource_continuation(
                        application_resource=application_resource,
                        hydrated_authorities=hydrated_authorities,
                        hydrated_resource_paths=hydrated_resource_paths,
                        application_resource_count=(
                            application_resource_count
                        ),
                        original_task=original_task,
                    )
                )
            except ApplicationResourceError as err:
                return {
                    "status": "ERROR",
                    "message": str(err),
                    "trace": _format_continuation_trace(
                        continuation_paths
                    ),
                    "hansel_navigation": navigation_metrics(),
                }

            application_resources.append(resource_metric)
            hydrated_resource_paths.add(resource_path)
            application_resource_count += 1
            last_context_label = f"RESOURCE:{resource_path}"

            complete_response_text = _invoke_wu(
                runner,
                continuation_task,
                invocation_economics,
            )
            continue

        requested_path = repository_file.file_path
        previous_paths = [
            authority.file_path
            for authority in hydrated_authorities
        ]
        duplicate_request = requested_path in hydrated_paths
        backtrack = (
            len(previous_paths) >= 2
            and requested_path == previous_paths[-2]
        )

        continuation_paths.append(requested_path)

        if duplicate_request:
            hansel_transitions.append(
                {
                    "sequence": len(hansel_transitions) + 1,
                    "from_authority": last_context_label,
                    "to_authority": requested_path,
                    "outcome": "REJECTED_CYCLE",
                    "duplicate_request": True,
                    "backtrack": backtrack,
                    "unnecessary_load_candidate": False,
                    "context_characters": 0,
                    "context_bytes": 0,
                }
            )
            return {
                "status": "ERROR",
                "message": (
                    "Wu entered a Hansel continuation cycle by requesting "
                    "repository authority that had already been hydrated "
                    "during this execution: "
                    f"{requested_path}"
                ),
                "trace": _format_continuation_trace(continuation_paths),
                "hansel_navigation": navigation_metrics(),
            }

        if continuation_count >= MAX_HANSEL_CONTINUATIONS:
            hansel_transitions.append(
                {
                    "sequence": len(hansel_transitions) + 1,
                    "from_authority": last_context_label,
                    "to_authority": requested_path,
                    "outcome": "REJECTED_LIMIT",
                    "duplicate_request": False,
                    "backtrack": False,
                    "unnecessary_load_candidate": False,
                    "context_characters": 0,
                    "context_bytes": 0,
                }
            )
            return {
                "status": "ERROR",
                "message": (
                    "Wu exceeded the bounded Hansel continuation limit of "
                    f"{MAX_HANSEL_CONTINUATIONS} repository requests."
                ),
                "trace": _format_continuation_trace(continuation_paths),
                "hansel_navigation": navigation_metrics(),
            }

        context_characters = len(repository_file.original_content)
        context_bytes = len(
            repository_file.original_content.encode("utf-8")
        )

        continuation_task = _build_continuation_task(
            repository_file=repository_file,
            hydrated_authorities=hydrated_authorities,
            original_task=original_task,
        )

        hydrated_authorities.append(repository_file)
        hydrated_paths.add(requested_path)
        continuation_count += 1

        hansel_transitions.append(
            {
                "sequence": len(hansel_transitions) + 1,
                "from_authority": last_context_label,
                "to_authority": requested_path,
                "outcome": "HYDRATED",
                "duplicate_request": False,
                "backtrack": False,
                "unnecessary_load_candidate": False,
                "context_characters": context_characters,
                "context_bytes": context_bytes,
            }
        )

        cumulative_repository_context_characters += sum(
            len(authority.original_content)
            for authority in hydrated_authorities
        )
        cumulative_repository_context_bytes += sum(
            len(authority.original_content.encode("utf-8"))
            for authority in hydrated_authorities
        )
        last_context_label = requested_path

        complete_response_text = _invoke_wu(
            runner,
            continuation_task,
            invocation_economics,
        )

    hansel_navigation = navigation_metrics()

    if not complete_response_text.strip():
        return {
            "status": "ERROR",
            "message": (
                "Wu produced no terminal response after continuation "
                "completed."
            ),
            "trace": _format_continuation_trace(continuation_paths),
            "hansel_navigation": hansel_navigation,
        }

    return {
        "status": "SUCCESS",
        "wu_response": complete_response_text,
        "hansel_navigation": hansel_navigation,
    }


# ======================================================================
# END: HANSEL_CONTINUATION_EXECUTION
# ======================================================================


# ======================================================================
# END: HANSEL_CONTINUATION_SERVICE
# ======================================================================
