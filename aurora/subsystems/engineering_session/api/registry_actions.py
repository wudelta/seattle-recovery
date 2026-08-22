# ======================================================================
# FILE: aurora/subsystems/engineering_session/api/registry_actions.py
# START: ENGINEERING_SESSION_COMPONENT_REGISTRY_ACTIONS
# ======================================================================

from asgiref.sync import async_to_sync
from django.http import JsonResponse

from aurora.subsystems.component_registry.services.documenter import (
    ComponentRegistryDocumenter,
)
from aurora.subsystems.component_registry.services.maintenance import (
    ComponentRegistryMaintenance,
)
from aurora.subsystems.engineering_session.api.serializers import (
    serialize_registry_enrichment,
    serialize_registry_maintenance,
)
from aurora.subsystems.engineering_session.services import (
    get_session_workflow_status,
)
from aurora.utils.telemetry_stream import async_send_to_console


REGISTRY_ACTIONS = {
    "refresh_component_registry",
    "enrich_component_registry",
}


def _emit_registry_telemetry(message: str) -> None:
    """Broadcast one Component Registry operational progress message."""

    async_to_sync(
        async_send_to_console
    )(message)


def _refresh_component_registry(request, action):
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
                "status": "error",
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
            "status": "success",
            "action": action,
            "maintenance": serialize_registry_maintenance(
                report
            ),
            "workflow": get_session_workflow_status(
                request.user
            ),
        }
    )


def _enrich_component_registry(request, action):
    """Run Component Registry AI enrichment."""

    _emit_registry_telemetry(
        "[REGISTRY] Component Registry AI enrichment started."
    )

    def emit_progress(message):
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
                "status": "error",
                "message": (
                    "Component Registry enrichment failed. "
                    f"{type(error).__name__}: {error}"
                ),
            },
            status=500,
        )

    serialized_report = serialize_registry_enrichment(
        report
    )

    if report.get("stopped"):
        _emit_registry_telemetry(
            "[REGISTRY] Enrichment stopped after an "
            "AI provider failure."
        )

        _emit_registry_telemetry(
            f"[REGISTRY] Resume from: "
            f"{report.get('restart_from')}"
        )

    elif report.get("failures"):
        _emit_registry_telemetry(
            "[REGISTRY] Enrichment completed with "
            f"{len(report['failures'])} failure(s)."
        )

        for failure in report["failures"]:
            _emit_registry_telemetry(
                f"[REGISTRY FAILURE] {failure}"
            )

    else:
        _emit_registry_telemetry(
            "[REGISTRY] Component Registry enrichment "
            "completed successfully."
        )

    return JsonResponse(
        {
            "status": "success",
            "action": action,
            "enrichment": serialized_report,
            "workflow": get_session_workflow_status(
                request.user
            ),
        }
    )


def handle_registry_action(request, action):
    """Handle Component Registry maintenance and enrichment actions."""

    if action == "refresh_component_registry":
        return _refresh_component_registry(
            request,
            action,
        )

    return _enrich_component_registry(
        request,
        action,
    )


# ======================================================================
# END: ENGINEERING_SESSION_COMPONENT_REGISTRY_ACTIONS
# ======================================================================
