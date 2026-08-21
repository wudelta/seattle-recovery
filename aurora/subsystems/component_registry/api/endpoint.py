# ======================================================================
# FILE: aurora/subsystems/component_registry/api/endpoint.py
# START: COMPONENT_REGISTRY_LOOKUP_AND_OPERATIONS_ENDPOINT
# ======================================================================

import json
from pathlib import Path

from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from aurora.subsystems.component_registry.models import (
    ComponentRegistry,
)
from aurora.subsystems.component_registry.services.documenter import (
    ComponentRegistryDocumenter,
)
from aurora.subsystems.component_registry.services.maintenance import (
    ComponentRegistryMaintenance,
)
from aurora.subsystems.component_registry.services.reconciler import (
    calculate_source_hash,
)
from aurora.utils.telemetry_stream import async_send_to_console


def _emit_registry_telemetry(message: str) -> None:
    """Broadcast one Component Registry operational message."""

    async_to_sync(
        async_send_to_console
    )(message)


def _serialize_maintenance_report(report) -> dict[str, object]:
    """Return a stable maintenance summary for browser clients."""

    return {
        "counts": report.counts,
        "review": list(report.review),
        "failures": list(report.failures),
    }


def _serialize_enrichment_report(
    report: dict[str, object],
) -> dict[str, object]:
    """Return a stable enrichment summary for browser clients."""

    return {
        "candidates": len(report.get("candidates", [])),
        "completed": len(report.get("completed", [])),
        "skipped": len(report.get("skipped", [])),
        "failures": len(report.get("failures", [])),
        "stopped": bool(report.get("stopped", False)),
        "last_completed": report.get("last_completed"),
        "failure_point": report.get("failure_point"),
        "restart_from": report.get("restart_from"),
        "remaining": report.get("remaining", 0),
    }


def _handle_registry_refresh() -> JsonResponse:
    """Run deterministic Component Registry maintenance."""

    _emit_registry_telemetry(
        "[REGISTRY] Component Registry maintenance started."
    )

    try:
        report = ComponentRegistryMaintenance().refresh()
    except Exception as error:
        _emit_registry_telemetry(
            "[REGISTRY ERROR] Maintenance failed: "
            f"{type(error).__name__}: {error}"
        )

        return JsonResponse(
            {
                "status": "ERROR",
                "message": (
                    "Component Registry maintenance failed. "
                    f"{type(error).__name__}: {error}"
                ),
            },
            status=500,
        )

    counts = report.counts

    _emit_registry_telemetry(
        "Summary: "
        + " | ".join(
            f"{key}={value}"
            for key, value in counts.items()
        )
    )

    if report.review:
        _emit_registry_telemetry(
            f"[REGISTRY] REVIEW required for "
            f"{len(report.review)} component(s)."
        )

        for path in report.review:
            _emit_registry_telemetry(
                f"[REGISTRY REVIEW] {path}"
            )

    if report.failures:
        for failure in report.failures:
            _emit_registry_telemetry(
                f"[REGISTRY FAILURE] {failure}"
            )

    pending_count = (
        counts["UPDATED"]
        + counts["REGISTERED"]
    )

    if pending_count:
        _emit_registry_telemetry(
            f"[REGISTRY] {pending_count} component(s) "
            "require AI enrichment."
        )

    _emit_registry_telemetry(
        "[REGISTRY] Component Registry maintenance completed."
    )

    return JsonResponse(
        {
            "status": "SUCCESS",
            "message": (
                "Component Registry refresh completed: "
                f"updated {counts['UPDATED']}, "
                f"registered {counts['REGISTERED']}, "
                f"archived {counts['ARCHIVED']}, "
                f"review {counts['REVIEW']}, "
                f"failures {counts['FAILURES']}."
            ),
            "maintenance": _serialize_maintenance_report(
                report
            ),
        }
    )


def _handle_registry_enrichment() -> JsonResponse:
    """Run Component Registry AI enrichment with live telemetry."""

    _emit_registry_telemetry(
        "[REGISTRY] Component Registry AI enrichment started."
    )

    def emit_progress(message: str) -> None:
        _emit_registry_telemetry(
            f"[REGISTRY] {message}"
        )

    try:
        report = (
            ComponentRegistryDocumenter()
            .analyze_pending(
                apply=True,
                progress_callback=emit_progress,
            )
        )
    except Exception as error:
        _emit_registry_telemetry(
            "[REGISTRY ERROR] Enrichment failed: "
            f"{type(error).__name__}: {error}"
        )

        return JsonResponse(
            {
                "status": "ERROR",
                "message": (
                    "Component Registry enrichment failed. "
                    f"{type(error).__name__}: {error}"
                ),
            },
            status=500,
        )

    serialized = _serialize_enrichment_report(
        report
    )

    if report.get("stopped"):
        _emit_registry_telemetry(
            "[REGISTRY] Enrichment stopped after an "
            "AI provider failure."
        )

        _emit_registry_telemetry(
            "[REGISTRY] Resume from: "
            f"{report.get('restart_from')}"
        )

        message = (
            "Component Registry enrichment stopped before "
            "completion."
        )

    elif report.get("failures"):
        for failure in report["failures"]:
            _emit_registry_telemetry(
                f"[REGISTRY FAILURE] {failure}"
            )

        message = (
            "Component Registry enrichment completed with "
            f"{len(report['failures'])} failure(s)."
        )

    else:
        _emit_registry_telemetry(
            "[REGISTRY] Component Registry enrichment "
            "completed successfully."
        )

        message = (
            "Component Registry enrichment completed: "
            f"completed {len(report.get('completed', []))}, "
            f"skipped {len(report.get('skipped', []))}, "
            f"remaining {report.get('remaining', 0)}, "
            f"failures {len(report.get('failures', []))}."
        )

    return JsonResponse(
        {
            "status": "SUCCESS",
            "message": message,
            "enrichment": serialized,
        }
    )


def _handle_registry_lookup(request) -> JsonResponse:
    """
    Return current Component Registry context for one repository file.

    Freshness is evaluated only for the requested file. This does not perform
    repository-wide reconciliation or mutate Component Registry state.
    """

    file_path = (
        request.GET.get("file_path", "")
        .strip()
        .replace("\\", "/")
        .replace("/app/", "", 1)
        .lstrip("/")
    )

    if not file_path:
        return JsonResponse(
            {
                "status": "ERROR",
                "message": "file_path is required.",
            },
            status=400,
        )

    component = (
        ComponentRegistry.objects
        .filter(
            file_path=file_path,
            status="ACTIVE",
        )
        .first()
    )

    if component is None:
        return JsonResponse(
            {
                "status": "NOT_FOUND",
                "file_path": file_path,
                "message": (
                    "No active Component Registry record exists "
                    "for this file."
                ),
            },
            status=404,
        )

    repository_path = (
        Path(settings.BASE_DIR)
        / component.file_path
    ).resolve()

    repository_root = Path(
        settings.BASE_DIR
    ).resolve()

    is_stale = True
    source_available = False
    freshness_message = ""

    try:
        repository_path.relative_to(
            repository_root
        )
    except ValueError:
        freshness_message = (
            "Component Registry path resolves outside "
            "the repository root."
        )
    else:
        if not repository_path.is_file():
            freshness_message = (
                "The registered source file is no longer "
                "present in the repository."
            )
        else:
            source_available = True

            try:
                observed_hash = calculate_source_hash(
                    repository_path
                )
            except OSError:
                freshness_message = (
                    "The source file could not be read for "
                    "freshness validation."
                )
            else:
                is_stale = (
                    not component.source_hash
                    or observed_hash
                    != component.source_hash
                )

                if is_stale:
                    freshness_message = (
                        "Component Registry description is stale. "
                        "Refresh and enrich the registry to update it."
                    )

    if (
        not is_stale
        and component.analysis_status != "COMPLETE"
    ):
        freshness_message = (
            "Component Registry description is not current "
            f"because analysis status is "
            f"{component.analysis_status}."
        )

    description_is_current = (
        source_available
        and not is_stale
        and component.analysis_status == "COMPLETE"
        and bool(component.description.strip())
    )

    return JsonResponse(
        {
            "status": "SUCCESS",
            "component": {
                "file_path": component.file_path,
                "description": (
                    component.description
                    if description_is_current
                    else ""
                ),
                "analysis_status": component.analysis_status,
                "analysis_version": component.analysis_version,
                "is_stale": is_stale,
                "source_available": source_available,
                "description_is_current": (
                    description_is_current
                ),
                "freshness_message": freshness_message,
            },
        }
    )


@login_required
def component_registry_endpoint(request):
    """Serve Component Registry lookup and operational actions."""

    if request.method == "GET":
        return _handle_registry_lookup(
            request
        )

    if request.method == "POST":
        try:
            payload = json.loads(
                request.body or b"{}"
            )
        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "status": "ERROR",
                    "message": "Invalid JSON request body.",
                },
                status=400,
            )

        action = (
            payload.get("action", "")
            .strip()
            .lower()
        )

        if action == "refresh":
            return _handle_registry_refresh()

        if action == "enrich":
            return _handle_registry_enrichment()

        return JsonResponse(
            {
                "status": "ERROR",
                "message": (
                    "Unsupported Component Registry action."
                ),
            },
            status=400,
        )

    return JsonResponse(
        {
            "status": "ERROR",
            "message": "Method not allowed.",
        },
        status=405,
    )

# ======================================================================
# END: COMPONENT_REGISTRY_LOOKUP_AND_OPERATIONS_ENDPOINT
# ======================================================================
