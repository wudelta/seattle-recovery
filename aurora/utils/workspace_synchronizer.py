# ======================================================================
# FILE: aurora/utils/workspace_synchronizer.py (PATCH 1 OF 3)
# START: SYNCHRONIZATION_TYPES_AND_INITIALIZATION
# ======================================================================
"""Controlled PostgreSQL application of approved reconciliation updates."""

from dataclasses import dataclass, field

from django.db import transaction
from django.utils import timezone

from aurora.models import ComponentRegistry
from aurora.utils.component_policy import CLASSIFICATION_UPDATE
from aurora.utils.workspace_reconciler import (
    ReconciliationItem,
    WorkspaceReconciler,
)


@dataclass
class SynchronizationReport:
    """Results from one bounded ComponentRegistry synchronization run."""

    updated: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)

    @property
    def counts(self) -> dict[str, int]:
        """Return stable synchronization summary counts."""
        return {
            "UPDATED": len(self.updated),
            "SKIPPED": len(self.skipped),
            "FAILURES": len(self.failures),
            "TOTAL": (
                len(self.updated)
                + len(self.skipped)
                + len(self.failures)
            ),
        }


class WorkspaceSynchronizer:
    """
    Apply bounded reconciliation updates to ComponentRegistry.

    This initial implementation updates existing rows only and deliberately
    avoids model save signals, Neo4j synchronization, registration, staging,
    repository mutation, and AI execution.
    """

    def __init__(self, reconciler: WorkspaceReconciler | None = None):
        self.reconciler = reconciler or WorkspaceReconciler()

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
# ======================================================================
# END: SYNCHRONIZATION_TYPES_AND_INITIALIZATION (PATCH 1 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/utils/workspace_synchronizer.py (PATCH 2 OF 3)
# START: BOUNDED_EXISTING_RECORD_UPDATE
# ======================================================================
    def apply_updates(
        self,
        *,
        path: str | None = None,
        limit: int | None = None,
    ) -> SynchronizationReport:
        """
        Persist existing UPDATE results without triggering model save signals.

        Optional path and limit boundaries constrain the live write set.
        """
        report = SynchronizationReport()
        updates = self._eligible_updates()

        if path:
            normalized_path = path.strip().replace("\\", "/").rstrip("/")
            path_prefix = f"{normalized_path}/"
            updates = [
                item
                for item in updates
                if (
                    item.path == normalized_path
                    or item.path.startswith(path_prefix)
                )
            ]

        if limit is not None:
            if limit < 1:
                raise ValueError("Synchronization limit must be greater than zero.")
            updates = updates[:limit]

        observed_at = timezone.now()

        for item in updates:
            try:
                update_values = {
                    "source_hash": item.source_hash,
                    "last_observed_at": observed_at,
                    "status": "ACTIVE",
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
# ======================================================================
# END: BOUNDED_EXISTING_RECORD_UPDATE (PATCH 2 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/utils/workspace_synchronizer.py (PATCH 3 OF 3)
# START: EXPLICIT_SYNCHRONIZATION_ENTRY_POINT
# ======================================================================
    def run(
        self,
        *,
        apply: bool = False,
        path: str | None = None,
        limit: int | None = None,
    ) -> dict[str, object]:
        """
        Preview or explicitly apply bounded existing-record updates.

        Database mutation occurs only when apply=True is supplied.
        """
        updates = self._eligible_updates()

        if path:
            normalized_path = path.strip().replace("\\", "/").rstrip("/")
            path_prefix = f"{normalized_path}/"
            updates = [
                item
                for item in updates
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
            updates = updates[:limit]

        if not apply:
            return {
                "apply": False,
                "candidates": updates,
                "counts": {
                    "CANDIDATES": len(updates),
                    "UPDATED": 0,
                    "SKIPPED": 0,
                    "FAILURES": 0,
                },
            }

        synchronization_report = self.apply_updates(
            path=path,
            limit=limit,
        )

        return {
            "apply": True,
            "candidates": updates,
            "report": synchronization_report,
            "counts": synchronization_report.counts,
        }
# ======================================================================
# END: EXPLICIT_SYNCHRONIZATION_ENTRY_POINT (PATCH 3 OF 3)
# ======================================================================