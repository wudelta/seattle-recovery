# ======================================================================
# FILE: aurora/subsystems/wu_chat/services/application_resource.py
# START: AURORA_APPLICATION_RESOURCE_RESOLUTION
# ======================================================================

import json
import re
from dataclasses import dataclass

from aurora.subsystems.planning.api.worker_resources import (
    PlanningWorkerResourceError,
    get_initiative_worker_resource,
)


_REQUEST_AURORA_RESOURCE_PATTERN = re.compile(
    r"\[REQUEST_AURORA_RESOURCE:\s*(?P<resource>[^\]\r\n]+?)\s*\]",
    re.IGNORECASE,
)

_PLANNING_INITIATIVE_PATTERN = re.compile(
    r"^planning/initiatives/(?P<initiative_id>[1-9][0-9]*)$",
    re.IGNORECASE,
)

MAX_AURORA_RESOURCE_CONTINUATIONS = 4


class ApplicationResourceError(ValueError):
    """Raised when a worker application-resource request is invalid."""


@dataclass(frozen=True)
class AuroraApplicationResource:
    """One bounded Aurora-owned application resource hydrated for Wu."""

    resource_path: str
    content_type: str
    content: str


def _extract_resource_request(response_text: str) -> str | None:
    matches = list(
        _REQUEST_AURORA_RESOURCE_PATTERN.finditer(response_text)
    )

    if not matches:
        return None

    if len(matches) > 1:
        raise ApplicationResourceError(
            "Wu requested multiple Aurora application resources in one "
            "continuation response."
        )

    return matches[0].group("resource").strip()


def _resolve_planning_initiative(
    resource_path: str,
    *,
    user,
) -> AuroraApplicationResource | None:
    match = _PLANNING_INITIATIVE_PATTERN.fullmatch(resource_path)

    if match is None:
        return None

    initiative_id = int(match.group("initiative_id"))

    try:
        payload = get_initiative_worker_resource(
            initiative_id,
            user=user,
        )
    except PlanningWorkerResourceError as exc:
        raise ApplicationResourceError(str(exc)) from exc

    return AuroraApplicationResource(
        resource_path=f"planning/initiatives/{initiative_id}",
        content_type="application/json",
        content=json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            default=str,
        ),
    )


def resolve_application_resource_request(
    response_text: str,
    *,
    user,
) -> AuroraApplicationResource | None:
    """Resolve one explicitly registered Aurora application resource."""
    resource_path = _extract_resource_request(response_text)

    if resource_path is None:
        return None

    for resolver in (_resolve_planning_initiative,):
        resource = resolver(
            resource_path,
            user=user,
        )

        if resource is not None:
            return resource

    raise ApplicationResourceError(
        "The requested Aurora application resource is not registered: "
        f"{resource_path}"
    )


# ======================================================================
# END: AURORA_APPLICATION_RESOURCE_RESOLUTION
# ======================================================================


# ======================================================================
# START: AURORA_APPLICATION_RESOURCE_CONTINUATION
# ======================================================================


def build_application_resource_continuation(
    *,
    application_resource: AuroraApplicationResource,
    hydrated_authorities,
    hydrated_resource_paths: set[str],
    application_resource_count: int,
    original_task: str,
) -> tuple[str, dict[str, object]]:
    """Validate and build one bounded application-resource continuation."""
    resource_path = application_resource.resource_path

    if resource_path in hydrated_resource_paths:
        raise ApplicationResourceError(
            "Wu entered an application-resource continuation cycle by "
            "requesting a resource that had already been hydrated during "
            f"this execution: {resource_path}"
        )

    if application_resource_count >= MAX_AURORA_RESOURCE_CONTINUATIONS:
        raise ApplicationResourceError(
            "Wu exceeded the bounded Aurora application-resource "
            "continuation limit of "
            f"{MAX_AURORA_RESOURCE_CONTINUATIONS} requests."
        )

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

    resource_newline = (
        ""
        if application_resource.content.endswith("\n")
        else "\n"
    )

    task = (
        "[AURORA_RESOURCE_CONTINUATION]\n"
        f"REQUESTED_RESOURCE: {resource_path}\n"
        f"CONTENT_TYPE: {application_resource.content_type}\n"
        "[ORIGINAL_TASK_START]\n"
        f"{original_task.strip()}\n"
        "[ORIGINAL_TASK_END]\n"
        f"{previous_authority_context}"
        "[REQUESTED_RESOURCE_START]\n"
        f"{application_resource.content}"
        f"{resource_newline}"
        "[REQUESTED_RESOURCE_END]\n"
        "[/AURORA_RESOURCE_CONTINUATION]"
    )

    metric = {
        "sequence": application_resource_count + 1,
        "resource": resource_path,
        "content_type": application_resource.content_type,
        "context_characters": len(application_resource.content),
        "context_bytes": len(
            application_resource.content.encode("utf-8")
        ),
    }

    return task, metric


# ======================================================================
# END: AURORA_APPLICATION_RESOURCE_CONTINUATION
# ======================================================================
