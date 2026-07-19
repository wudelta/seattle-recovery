# ======================================================================
# FILE: aurora/utils/workspace_synchronizer.py (PATCH 1 OF 3)
# START: SYNCHRONIZATION_TYPES_AND_INITIALIZATION
# ======================================================================
"""Controlled application of approved workspace reconciliation changes."""

from dataclasses import dataclass, field
from pathlib import Path

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from aurora.models import ComponentRegistry
from aurora.utils.component_policy import (
    CLASSIFICATION_EXCLUDE,
    CLASSIFICATION_KEEP,
    CLASSIFICATION_REGISTER,
    CLASSIFICATION_REVIEW,
    CLASSIFICATION_STAGE,
    CLASSIFICATION_UPDATE,
)
from aurora.utils.forge_registry import register_new_component
from aurora.utils.graph_synchronizer import GraphSynchronizer
from aurora.utils.workspace_reconciler import (
    ReconciliationItem,
    WorkspaceReconciler,
)


UserModel = get_user_model()


@dataclass
class SynchronizationReport:
    """Results from one bounded ComponentRegistry synchronization run."""

    updated: list[str] = field(default_factory=list)
    registered: list[str] = field(default_factory=list)
    graph_synchronized: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    graph_failures: list[str] = field(default_factory=list)

    @property
    def counts(self) -> dict[str, int]:
        """Return stable synchronization summary counts."""
        return {
            "UPDATED": len(self.updated),
            "REGISTERED": len(self.registered),
            "GRAPH_SYNCHRONIZED": len(self.graph_synchronized),
            "SKIPPED": len(self.skipped),
            "FAILURES": len(self.failures),
            "GRAPH_FAILURES": len(self.graph_failures),
            "TOTAL": (
                len(self.updated)
                + len(self.registered)
                + len(self.graph_synchronized)
                + len(self.skipped)
                + len(self.failures)
                + len(self.graph_failures)
            ),
        }


class WorkspaceSynchronizer:
    """
    Apply bounded reconciliation changes to ComponentRegistry.

    PostgreSQL mutation and Neo4j projection remain explicit operations.
    Repository files are never modified.
    """

    def __init__(
        self,
        reconciler: WorkspaceReconciler | None = None,
        graph_synchronizer: GraphSynchronizer | None = None,
    ):
        self.reconciler = reconciler or WorkspaceReconciler()
        self.graph_synchronizer = graph_synchronizer or GraphSynchronizer()

    def _eligible_updates(self) -> list[ReconciliationItem]:
        """Return existing registry records classified for safe update."""
        return [
            item
            for item in self.reconciler.reconcile()
            if (
                item.classification == CLASSIFICATION_UPDATE
                and item.registry_id is not None
                and item.source_hash is not None
            )
        ]

    def _eligible_registrations(self) -> list[ReconciliationItem]:
        """Return repository files classified for safe registration."""
        return [
            item
            for item in self.reconciler.reconcile()
            if (
                item.classification == CLASSIFICATION_REGISTER
                and item.registry_id is None
                and item.source_hash is not None
            )
        ]

    @staticmethod
    def _component_name(item: ReconciliationItem) -> str:
        """Derive a stable initial component name from its repository path."""
        return Path(item.path).stem

    def _eligible_graph_components(
        self,
        *,
        limit: int | None = None,
    ):
        """Return pending, failed, or stale active graph projections."""
        return self.graph_synchronizer.eligible_components(limit=limit)
# ======================================================================
# END: SYNCHRONIZATION_TYPES_AND_INITIALIZATION (PATCH 1 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/utils/workspace_synchronizer.py (PATCH 2 OF 3)
# START: BOUNDED_DATABASE_AND_GRAPH_SYNCHRONIZATION
# ======================================================================
    @staticmethod
    def _apply_boundaries(
        items,
        *,
        path: str | None = None,
        limit: int | None = None,
    ):
        """Apply stable repository-path and result-count boundaries."""
        bounded_items = items

        if path:
            normalized_path = path.strip().replace("\\", "/").rstrip("/")
            path_prefix = f"{normalized_path}/"
            bounded_items = [
                item
                for item in bounded_items
                if (
                    item.path == normalized_path
                    or item.path.startswith(path_prefix)
                )
            ]

        if limit is not None:
            if limit < 1:
                raise ValueError(
                    "Synchronization limit must be greater than zero."
                )
            bounded_items = bounded_items[:limit]

        return bounded_items

    @staticmethod
    def _apply_component_boundaries(
        components,
        *,
        path: str | None = None,
        limit: int | None = None,
    ) -> list[ComponentRegistry]:
        """Apply path and count boundaries to registry graph candidates."""
        bounded_components = components

        if path:
            normalized_path = path.strip().replace("\\", "/").rstrip("/")
            path_prefix = f"{normalized_path}/"
            bounded_components = bounded_components.filter(
                file_path__startswith=path_prefix,
            ) | bounded_components.filter(
                file_path=normalized_path,
            )

            bounded_components = bounded_components.order_by("file_path")

        if limit is not None:
            if limit < 1:
                raise ValueError(
                    "Synchronization limit must be greater than zero."
                )
            bounded_components = bounded_components[:limit]

        return list(bounded_components)

    def apply_updates(
        self,
        *,
        path: str | None = None,
        limit: int | None = None,
    ) -> SynchronizationReport:
        """Persist existing UPDATE results without model save signals."""
        report = SynchronizationReport()
        updates = self._apply_boundaries(
            self._eligible_updates(),
            path=path,
            limit=limit,
        )
        observed_at = timezone.now()

        for item in updates:
            try:
                update_values = {
                    "source_hash": item.source_hash,
                    "last_observed_at": observed_at,
                    "status": "ACTIVE",
                    "analysis_status": "PENDING",
                }

                if item.persona:
                    update_values["persona"] = item.persona

                with transaction.atomic():
                    updated_count = ComponentRegistry.objects.filter(
                        id=item.registry_id,
                        file_path=item.path,
                    ).update(**update_values)

                if updated_count == 1:
                    report.updated.append(item.path)
                else:
                    report.skipped.append(item.path)

            except Exception as error:
                report.failures.append(
                    f"{item.path}: {type(error).__name__}: {error}"
                )

        return report

    def apply_registrations(
        self,
        *,
        user_instance: UserModel,
        path: str | None = None,
        limit: int | None = None,
        synchronize_graph: bool = True,
    ) -> SynchronizationReport:
        """
        Register bounded REGISTER candidates and explicitly project them.

        PostgreSQL registration succeeds independently of Neo4j projection.
        Graph failures are persisted and reported for deliberate retry.
        """
        report = SynchronizationReport()
        registrations = self._apply_boundaries(
            self._eligible_registrations(),
            path=path,
            limit=limit,
        )
        observed_at = timezone.now()

        for item in registrations:
            try:
                with transaction.atomic():
                    component = register_new_component(
                        file_path=item.path,
                        name=self._component_name(item),
                        visibility="PRIVATE",
                        user_instance=user_instance,
                        persona=item.persona or "COMPILER_MODULE",
                    )

                    ComponentRegistry.objects.filter(
                        id=component.id,
                    ).update(
                        source_hash=item.source_hash,
                        last_observed_at=observed_at,
                        status="ACTIVE",
                    )

                component.refresh_from_db()
                report.registered.append(item.path)

            except Exception as error:
                report.failures.append(
                    f"{item.path}: {type(error).__name__}: {error}"
                )
                continue

            if not synchronize_graph:
                continue

            graph_report = self.graph_synchronizer.synchronize_components(
                [component],
            )
            report.graph_synchronized.extend(
                graph_report.synchronized
            )
            report.graph_failures.extend(
                graph_report.failures
            )
            report.skipped.extend(
                graph_report.skipped
            )

        return report

    def apply_graph_synchronization(
        self,
        *,
        path: str | None = None,
        limit: int | None = None,
    ) -> SynchronizationReport:
        """
        Project bounded eligible ComponentRegistry records into Neo4j.

        Repository files remain unchanged. PostgreSQL graph synchronization
        state is updated after each projection attempt.
        """
        report = SynchronizationReport()
        components = self._apply_component_boundaries(
            self._eligible_graph_components(),
            path=path,
            limit=limit,
        )

        graph_report = self.graph_synchronizer.synchronize_components(
            components,
        )

        report.graph_synchronized.extend(graph_report.synchronized)
        report.graph_failures.extend(graph_report.failures)
        report.skipped.extend(graph_report.skipped)

        return report
# ======================================================================
# END: BOUNDED_DATABASE_AND_GRAPH_SYNCHRONIZATION (PATCH 2 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/utils/workspace_synchronizer.py (PATCH 3 OF 3)
# START: EXPLICIT_SYNCHRONIZATION_ENTRY_POINT
# ======================================================================
    def synchronize_path(
        self,
        path: str,
        *,
        user_instance: UserModel | None = None,
        synchronize_graph: bool = True,
    ) -> dict[str, object]:
        """
        Reconcile and synchronize exactly one repository-relative file.

        The reconciler determines desired state. This synchronizer applies
        registration or update mutations and then refreshes graph projection.
        """
        normalized_path = path.strip().replace("\\", "/").lstrip("/")

        if not normalized_path:
            raise ValueError(
                "A repository-relative path is required for synchronization."
            )

        matching_items = [
            item
            for item in self.reconciler.reconcile()
            if item.path == normalized_path
        ]

        if len(matching_items) != 1:
            raise ValueError(
                "Path synchronization requires exactly one reconciliation "
                f"result for '{normalized_path}'."
            )

        item = matching_items[0]
        report = SynchronizationReport()

        if item.classification == CLASSIFICATION_REGISTER:
            if user_instance is None:
                raise ValueError(
                    "user_instance is required when registering a new path."
                )

            report = self.apply_registrations(
                user_instance=user_instance,
                path=normalized_path,
                limit=1,
                synchronize_graph=synchronize_graph,
            )

        elif item.classification == CLASSIFICATION_UPDATE:
            update_report = self.apply_updates(
                path=normalized_path,
                limit=1,
            )
            report.updated.extend(update_report.updated)
            report.skipped.extend(update_report.skipped)
            report.failures.extend(update_report.failures)

            if (
                synchronize_graph
                and not update_report.failures
                and normalized_path in update_report.updated
            ):
                graph_report = self.apply_graph_synchronization(
                    path=normalized_path,
                    limit=1,
                )
                report.graph_synchronized.extend(
                    graph_report.graph_synchronized
                )
                report.skipped.extend(graph_report.skipped)
                report.graph_failures.extend(
                    graph_report.graph_failures
                )

        elif item.classification == CLASSIFICATION_KEEP:
            if synchronize_graph:
                graph_report = self.apply_graph_synchronization(
                    path=normalized_path,
                    limit=1,
                )
                report.graph_synchronized.extend(
                    graph_report.graph_synchronized
                )
                report.skipped.extend(graph_report.skipped)
                report.graph_failures.extend(
                    graph_report.graph_failures
                )

            if (
                not report.graph_synchronized
                and not report.graph_failures
                and normalized_path not in report.skipped
            ):
                report.skipped.append(normalized_path)

        elif item.classification in {
            CLASSIFICATION_EXCLUDE,
            CLASSIFICATION_REVIEW,
            CLASSIFICATION_STAGE,
        }:
            report.failures.append(
                f"{normalized_path}: path classified as "
                f"{item.classification} ({item.reason})"
            )

        else:
            report.failures.append(
                f"{normalized_path}: unsupported reconciliation "
                f"classification '{item.classification}'"
            )

        return {
            "path": normalized_path,
            "classification": item.classification,
            "reason": item.reason,
            "item": item,
            "report": report,
            "counts": report.counts,
        }

    def run(
        self,
        *,
        apply: bool = False,
        operation: str = "update",
        user_instance: UserModel | None = None,
        path: str | None = None,
        limit: int | None = None,
        synchronize_graph: bool = True,
    ) -> dict[str, object]:
        """
        Preview or explicitly apply one bounded synchronization operation.

        Supported operations:
        - update: refresh existing ComponentRegistry records
        - register: create new ComponentRegistry records
        - graph: project existing active registry records into Neo4j

        Mutation occurs only when apply=True is supplied.
        """
        normalized_operation = operation.strip().lower()

        if normalized_operation == "update":
            candidates = self._apply_boundaries(
                self._eligible_updates(),
                path=path,
                limit=limit,
            )

            if not apply:
                return {
                    "apply": False,
                    "operation": normalized_operation,
                    "candidates": candidates,
                    "counts": {
                        "CANDIDATES": len(candidates),
                        "UPDATED": 0,
                        "REGISTERED": 0,
                        "GRAPH_SYNCHRONIZED": 0,
                        "SKIPPED": 0,
                        "FAILURES": 0,
                        "GRAPH_FAILURES": 0,
                    },
                }

            synchronization_report = self.apply_updates(
                path=path,
                limit=limit,
            )

        elif normalized_operation == "register":
            candidates = self._apply_boundaries(
                self._eligible_registrations(),
                path=path,
                limit=limit,
            )

            if not apply:
                return {
                    "apply": False,
                    "operation": normalized_operation,
                    "candidates": candidates,
                    "counts": {
                        "CANDIDATES": len(candidates),
                        "UPDATED": 0,
                        "REGISTERED": 0,
                        "GRAPH_SYNCHRONIZED": 0,
                        "SKIPPED": 0,
                        "FAILURES": 0,
                        "GRAPH_FAILURES": 0,
                    },
                }

            if user_instance is None:
                raise ValueError(
                    "user_instance is required when applying registrations."
                )

            synchronization_report = self.apply_registrations(
                user_instance=user_instance,
                path=path,
                limit=limit,
                synchronize_graph=synchronize_graph,
            )

        elif normalized_operation == "graph":
            candidates = self._apply_component_boundaries(
                self._eligible_graph_components(),
                path=path,
                limit=limit,
            )

            if not apply:
                return {
                    "apply": False,
                    "operation": normalized_operation,
                    "candidates": candidates,
                    "counts": {
                        "CANDIDATES": len(candidates),
                        "UPDATED": 0,
                        "REGISTERED": 0,
                        "GRAPH_SYNCHRONIZED": 0,
                        "SKIPPED": 0,
                        "FAILURES": 0,
                        "GRAPH_FAILURES": 0,
                    },
                }

            synchronization_report = self.apply_graph_synchronization(
                path=path,
                limit=limit,
            )

        else:
            raise ValueError(
                "Unsupported synchronization operation. "
                "Expected 'update', 'register', or 'graph'."
            )

        return {
            "apply": True,
            "operation": normalized_operation,
            "candidates": candidates,
            "report": synchronization_report,
            "counts": synchronization_report.counts,
        }
# ======================================================================
# END: EXPLICIT_SYNCHRONIZATION_ENTRY_POINT (PATCH 3 OF 3)
# ======================================================================