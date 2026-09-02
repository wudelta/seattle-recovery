# ======================================================================
# FILE: aurora/subsystems/component_registry/services/maintenance.py
# START: COMPONENT_REGISTRY_MAINTENANCE_SERVICE
# ======================================================================
"""Routine deterministic maintenance for Component Registry."""

from dataclasses import dataclass, field

from aurora.subsystems.component_registry.services.component_policy import (
    CLASSIFICATION_ARCHIVE,
    CLASSIFICATION_EXCLUDE,
    CLASSIFICATION_KEEP,
    CLASSIFICATION_REGISTER,
    CLASSIFICATION_REVIEW,
    CLASSIFICATION_UPDATE,
)
from aurora.subsystems.component_registry.services.reconciler import (
    ReconciliationItem,
    WorkspaceReconciler,
)
from aurora.subsystems.component_registry.services.synchronizer import (
    SynchronizationReport,
    WorkspaceSynchronizer,
)


@dataclass
class ComponentRegistryMaintenanceReport:
    """Combined result from one deterministic registry maintenance pass."""

    updated: list[str] = field(default_factory=list)
    registered: list[str] = field(default_factory=list)
    archived: list[str] = field(default_factory=list)
    kept: list[str] = field(default_factory=list)
    excluded: list[str] = field(default_factory=list)
    review: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)

    @property
    def counts(self) -> dict[str, int]:
        """Return a stable maintenance summary."""
        return {
            "UPDATED": len(self.updated),
            "REGISTERED": len(self.registered),
            "ARCHIVED": len(self.archived),
            "KEEP": len(self.kept),
            "EXCLUDE": len(self.excluded),
            "REVIEW": len(self.review),
            "SKIPPED": len(self.skipped),
            "FAILURES": len(self.failures),
            "TOTAL": (
                len(self.updated)
                + len(self.registered)
                + len(self.archived)
                + len(self.kept)
                + len(self.excluded)
                + len(self.review)
                + len(self.skipped)
                + len(self.failures)
            ),
        }


class _SnapshotReconciler:
    """Expose one reconciliation snapshot through the reconciler interface."""

    def __init__(self, items: list[ReconciliationItem]):
        self._items = items

    def reconcile(self) -> list[ReconciliationItem]:
        """Return the existing snapshot without rescanning the repository."""
        return self._items


class ComponentRegistryMaintenance:
    """
    Converge Component Registry with repository reality in one routine pass.

    Maintenance is deterministic and does not perform AI enrichment.

    Newly registered or changed components remain PENDING for the separate
    Component Registry enrichment workflow.
    """

    def __init__(
        self,
        reconciler: WorkspaceReconciler | None = None,
    ):
        self.reconciler = reconciler or WorkspaceReconciler()

    @staticmethod
    def _merge_synchronization_report(
        maintenance_report: ComponentRegistryMaintenanceReport,
        synchronization_report: SynchronizationReport,
    ) -> None:
        """Merge one synchronization result into the maintenance report."""
        maintenance_report.updated.extend(synchronization_report.updated)
        maintenance_report.registered.extend(synchronization_report.registered)
        maintenance_report.archived.extend(synchronization_report.archived)
        maintenance_report.skipped.extend(synchronization_report.skipped)
        maintenance_report.failures.extend(synchronization_report.failures)

    @staticmethod
    def _classify_non_mutating_items(
        items: list[ReconciliationItem],
        report: ComponentRegistryMaintenanceReport,
    ) -> None:
        """Record reconciliation results that require no automatic mutation."""
        for item in items:
            if item.classification == CLASSIFICATION_KEEP:
                report.kept.append(item.path)
            elif item.classification == CLASSIFICATION_EXCLUDE:
                report.excluded.append(item.path)
            elif item.classification == CLASSIFICATION_REVIEW:
                report.review.append(item.path)

    def refresh_from_items(
        self,
        items: list[ReconciliationItem],
    ) -> ComponentRegistryMaintenanceReport:
        """Apply one existing reconciliation snapshot without rescanning."""
        report = ComponentRegistryMaintenanceReport()
        self._classify_non_mutating_items(items, report)

        snapshot_reconciler = _SnapshotReconciler(items)
        synchronizer = WorkspaceSynchronizer(reconciler=snapshot_reconciler)

        update_report = synchronizer.apply_updates()
        self._merge_synchronization_report(report, update_report)

        registration_report = synchronizer.apply_registrations()
        self._merge_synchronization_report(report, registration_report)

        archive_report = synchronizer.apply_archives()
        self._merge_synchronization_report(report, archive_report)

        return report

    def refresh(self) -> ComponentRegistryMaintenanceReport:
        """
        Reconcile once and apply all safe registry synchronization classes.

        Automatic maintenance applies UPDATE, REGISTER, and ARCHIVE.
        KEEP and EXCLUDE require no mutation. REVIEW remains for human review.
        """
        items = self.reconciler.reconcile()
        return self.refresh_from_items(items)


# ======================================================================
# END: COMPONENT_REGISTRY_MAINTENANCE_SERVICE
# ======================================================================
