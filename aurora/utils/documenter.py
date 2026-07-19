# ======================================================================
# FILE: aurora/utils/documenter.py (PATCH 1 OF 1)
# START: BOUNDED_COMPONENT_DESCRIPTION_ANALYZER
# ======================================================================
"""Bounded AI enrichment for pending ComponentRegistry descriptions."""

import hashlib
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from aurora.minions.engine import MinionRunner
from aurora.models import ComponentRegistry


class WorkspaceDocumenter:
    """
    Generate descriptions for explicitly bounded pending components.

    Repository discovery and freshness detection remain deterministic concerns.
    Standing AI instructions belong exclusively to DeltaDirectives.
    """

    ANALYSIS_VERSION = "component-description-v1"
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

    def _validate_description(self, description: str) -> str:
        """Reject execution faults and empty results before database mutation."""
        normalized_description = description.strip()

        if self.runner.last_provider_error:
            raise RuntimeError(
                f"AI provider execution failed: {self.runner.last_provider_error}"
            )

        error_markers = (
            "💥 [REGISTRY ERROR]",
            "💥 [AI PROVIDER ERROR]",
        )

        if any(marker in normalized_description for marker in error_markers):
            raise RuntimeError(normalized_description)

        if not normalized_description:
            raise RuntimeError("AI provider returned an empty description.")

        return normalized_description

    def analyze_pending(
        self,
        *,
        apply: bool = False,
        path: str | None = None,
        limit: int | None = None,
    ) -> dict[str, object]:
        """
        Preview or analyze a bounded set of pending components.

        AI results are committed only when the file hash still matches the
        ComponentRegistry hash captured by deterministic synchronization.
        """
        components = self._eligible_components(path=path, limit=limit)
        report = {
            "apply": apply,
            "candidates": [component.file_path for component in components],
            "completed": [],
            "skipped": [],
            "failures": [],
        }

        if not apply:
            return report

        for component in components:
            try:
                source_path = self._resolve_source_path(component.file_path)

                if not source_path.is_file():
                    report["failures"].append(
                        f"{component.file_path}: source file is missing"
                    )
                    continue

                source_text, observed_hash = self._read_source(source_path)

                if observed_hash != component.source_hash:
                    report["skipped"].append(
                        f"{component.file_path}: source hash is stale"
                    )
                    continue

                description = self.runner.run_minion_task(
                    self.DIRECTIVE_NAME,
                    self._build_task_context(component, source_text),
                )
                description = self._validate_description(description)

                _, current_hash = self._read_source(source_path)

                if current_hash != observed_hash:
                    report["skipped"].append(
                        f"{component.file_path}: source changed during analysis"
                    )
                    continue

                analyzed_at = timezone.now()
                updated_count = ComponentRegistry.objects.filter(
                    id=component.id,
                    source_hash=observed_hash,
                    analysis_status="PENDING",
                ).update(
                    description=description,
                    analysis_status="COMPLETE",
                    analysis_version=self.ANALYSIS_VERSION,
                    last_analyzed_at=analyzed_at,
                )

                if updated_count == 1:
                    report["completed"].append(component.file_path)
                else:
                    report["skipped"].append(
                        f"{component.file_path}: registry state changed during analysis"
                    )

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
                report["failures"].append(
                    f"{component.file_path}: {type(error).__name__}: {error}"
                )

        return report
# ======================================================================
# END: BOUNDED_COMPONENT_DESCRIPTION_ANALYZER (PATCH 1 OF 1)
# ======================================================================