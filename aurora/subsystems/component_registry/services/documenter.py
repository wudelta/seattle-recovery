# ======================================================================
# FILE: aurora/subsystems/component_registry/services/documenter.py
# START: DOCUMENTATION_PROGRESS_INFRASTRUCTURE
# ======================================================================
"""Bounded AI enrichment for pending ComponentRegistry descriptions."""

import hashlib
from collections.abc import Callable
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from aurora.minions.engine import MinionRunner
from aurora.models import ComponentRegistry
from aurora.utils.telemetry import TelemetryLogger


class ProviderExecutionError(RuntimeError):
    """Signal a provider failure that requires stopping the analysis batch."""


class ComponentRegistryDocumenter:
    """
    Generate descriptions for explicitly bounded pending components.

    Repository discovery and freshness detection remain deterministic concerns.
    Standing AI instructions belong exclusively to DeltaDirectives.
    """

    ANALYSIS_VERSION = "component-description-v2"
    DIRECTIVE_NAME = "component_registry_documenter"

    def __init__(self, runner: MinionRunner | None = None):
        self.runner = runner or MinionRunner()
        self.repository_root = Path(settings.BASE_DIR).resolve()

    def _eligible_components(
        self,
        *,
        path: str | None = None,
        limit: int | None = None,
    ) -> list[ComponentRegistry]:
        """Return stable active components currently awaiting AI analysis."""
        queryset = ComponentRegistry.objects.filter(
            status="ACTIVE",
            analysis_status="PENDING",
        ).order_by("file_path")

        if path:
            normalized_path = path.strip().replace("\\", "/").lstrip("/").rstrip("/")
            path_prefix = f"{normalized_path}/"

            queryset = (
                queryset.filter(file_path=normalized_path)
                | queryset.filter(file_path__startswith=path_prefix)
            ).order_by("file_path")

        if limit is not None:
            if limit < 1:
                raise ValueError("Analysis limit must be greater than zero.")
            queryset = queryset[:limit]

        return list(queryset)

    def _resolve_source_path(self, repository_path: str) -> Path:
        """Resolve one repository-relative path without permitting traversal."""
        source_path = (self.repository_root / repository_path).resolve()

        try:
            source_path.relative_to(self.repository_root)
        except ValueError as error:
            raise ValueError(
                f"Component path escapes the repository root: {repository_path}"
            ) from error

        return source_path

    @staticmethod
    def _read_source(source_path: Path) -> tuple[str, str]:
        """Read UTF-8 source and return its exact SHA-256 digest."""
        source_bytes = source_path.read_bytes()
        source_text = source_bytes.decode("utf-8")
        source_hash = hashlib.sha256(source_bytes).hexdigest()
        return source_text, source_hash

    @staticmethod
    def _build_task_context(
        component: ComponentRegistry,
        source_text: str,
    ) -> str:
        """Provide factual task data without embedding minion instructions."""
        return (
            f"FILE_PATH: {component.file_path}\n"
            f"PERSONA: {component.persona}\n"
            "SOURCE:\n"
            f"{source_text}"
        )

    @staticmethod
    def _emit_progress(
        message: str,
        progress_callback: Callable[[str], None] | None,
    ) -> None:
        """Emit one canonical event to telemetry and the active caller."""
        TelemetryLogger.emit(f"{message}\n")

        if progress_callback:
            progress_callback(message)
# ======================================================================
# END: DOCUMENTATION_PROGRESS_INFRASTRUCTURE
# ======================================================================

# ======================================================================
# FILE: aurora/subsystems/component_registry/services/documenter.py
# START: DESCRIPTION_VALIDATION_AND_RUN_INITIALIZATION
# ======================================================================
    def _validate_description(self, description: str) -> str:
        """Reject execution faults and empty results before database mutation."""
        normalized_description = description.strip()

        if self.runner.last_provider_error:
            raise ProviderExecutionError(
                f"AI provider failed: {self.runner.last_provider_error}"
            )

        error_markers = (
            "💥 [REGISTRY ERROR]",
            "💥 [AI PROVIDER ERROR]",
        )

        if any(marker in normalized_description for marker in error_markers):
            raise ProviderExecutionError(normalized_description)

        if not normalized_description:
            raise RuntimeError("AI provider returned an empty description.")

        return normalized_description

    def analyze_pending(
        self,
        *,
        apply: bool = False,
        path: str | None = None,
        limit: int | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> dict[str, object]:
        """
        Preview or analyze a bounded set of pending components.

        AI results are committed only when the file hash still matches the
        ComponentRegistry hash captured by deterministic synchronization.
        """
        components = self._eligible_components(path=path, limit=limit)
        total = len(components)

        report = {
            "apply": apply,
            "candidates": [component.file_path for component in components],
            "completed": [],
            "skipped": [],
            "failures": [],
            "stopped": False,
            "last_completed": None,
            "failure_point": None,
            "restart_from": None,
            "remaining": total,
        }

        if not apply:
            return report

        self._emit_progress(
            (
                f"Documentation run started: {total} candidate(s), "
                f"analysis version {self.ANALYSIS_VERSION}."
            ),
            progress_callback,
        )
# ======================================================================
# END: DESCRIPTION_VALIDATION_AND_RUN_INITIALIZATION
# ======================================================================

# ======================================================================
# FILE: aurora/subsystems/component_registry/services/documenter.py
# START: COMPONENT_ANALYSIS_PROGRESS_LOOP
# ======================================================================
        for position, component in enumerate(components, start=1):
            prefix = f"[{position}/{total}]"

            self._emit_progress(
                f"{prefix} STARTED   {component.file_path}",
                progress_callback,
            )

            try:
                source_path = self._resolve_source_path(component.file_path)

                if not source_path.is_file():
                    message = f"{component.file_path}: source file is missing"
                    report["failures"].append(message)

                    self._emit_progress(
                        (
                            f"{prefix} FAILED    {component.file_path}\n"
                            "            FileNotFoundError: source file is missing"
                        ),
                        progress_callback,
                    )
                    continue

                source_text, observed_hash = self._read_source(source_path)

                if observed_hash != component.source_hash:
                    message = f"{component.file_path}: source hash is stale"
                    report["skipped"].append(message)

                    self._emit_progress(
                        (
                            f"{prefix} SKIPPED   {component.file_path}\n"
                            "            Source hash is stale."
                        ),
                        progress_callback,
                    )
                    continue

                try:
                    description = self.runner.run_minion_task(
                        self.DIRECTIVE_NAME,
                        self._build_task_context(component, source_text),
                    )
                except Exception as error:
                    raise ProviderExecutionError(
                        f"{type(error).__name__}: {error}"
                    ) from error

                description = self._validate_description(description)

                _, current_hash = self._read_source(source_path)

                if current_hash != observed_hash:
                    message = (
                        f"{component.file_path}: source changed during analysis"
                    )
                    report["skipped"].append(message)

                    self._emit_progress(
                        (
                            f"{prefix} SKIPPED   {component.file_path}\n"
                            "            Source changed during analysis."
                        ),
                        progress_callback,
                    )
                    continue

                updated_count = ComponentRegistry.objects.filter(
                    id=component.id,
                    source_hash=observed_hash,
                    analysis_status="PENDING",
                ).update(
                    description=description,
                    analysis_status="COMPLETE",
                    analysis_version=self.ANALYSIS_VERSION,
                    last_analyzed_at=timezone.now(),
                )

                if updated_count == 1:
                    report["completed"].append(component.file_path)
                    report["last_completed"] = component.file_path

                    self._emit_progress(
                        f"{prefix} COMPLETE  {component.file_path}",
                        progress_callback,
                    )
                    continue

                message = (
                    f"{component.file_path}: "
                    "registry state changed during analysis"
                )
                report["skipped"].append(message)

                self._emit_progress(
                    (
                        f"{prefix} SKIPPED   {component.file_path}\n"
                        "            Registry state changed during analysis."
                    ),
                    progress_callback,
                )
# ======================================================================
# END: COMPONENT_ANALYSIS_PROGRESS_LOOP
# ======================================================================

# ======================================================================
# FILE: aurora/subsystems/component_registry/services/documenter.py
# START: COMPONENT_FAILURE_RECOVERY_AND_RUN_SUMMARY
# ======================================================================
            except Exception as error:
                ComponentRegistry.objects.filter(
                    id=component.id,
                    source_hash=component.source_hash,
                    analysis_status="PENDING",
                ).update(
                    analysis_status="FAILED",
                    analysis_version=self.ANALYSIS_VERSION,
                    last_analyzed_at=timezone.now(),
                )

                message = (
                    f"{component.file_path}: "
                    f"{type(error).__name__}: {error}"
                )
                report["failures"].append(message)

                self._emit_progress(
                    (
                        f"{prefix} FAILED    {component.file_path}\n"
                        f"            {type(error).__name__}: {error}"
                    ),
                    progress_callback,
                )

                if isinstance(error, ProviderExecutionError):
                    report["stopped"] = True
                    report["failure_point"] = component.file_path
                    report["restart_from"] = component.file_path

                    self._emit_progress(
                        "Stopping after provider failure.",
                        progress_callback,
                    )
                    break

        processed_count = (
            len(report["completed"])
            + len(report["skipped"])
            + len(report["failures"])
        )
        report["remaining"] = max(total - processed_count, 0)

        self._emit_progress(
            (
                "Documentation run finished.\n"
                f"Candidates: {total}\n"
                f"Completed: {len(report['completed'])}\n"
                f"Skipped: {len(report['skipped'])}\n"
                f"Failed: {len(report['failures'])}\n"
                f"Remaining: {report['remaining']}\n"
                f"Last completed: {report['last_completed'] or 'None'}\n"
                f"Failure point: {report['failure_point'] or 'None'}\n"
                f"Restart from: {report['restart_from'] or 'None'}\n"
                f"Analysis version: {self.ANALYSIS_VERSION}"
            ),
            progress_callback,
        )

        return report
# ======================================================================
# END: COMPONENT_FAILURE_RECOVERY_AND_RUN_SUMMARY
# ======================================================================