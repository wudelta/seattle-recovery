# ======================================================================
# FILE: aurora/subsystems/component_registry/services/graph_projection.py
# START: EXPLICIT_COMPONENT_GRAPH_SYNCHRONIZATION
# ======================================================================
"""Explicit bounded projection of ComponentRegistry records into Neo4j."""

from collections.abc import Iterable
from dataclasses import dataclass, field

from django.db.models import F, Q, QuerySet
from django.utils import timezone

from aurora.models import ComponentRegistry
from aurora.nodes import ComponentNode
from aurora.subsystems.component_registry.services.dependency_analyzer import (
    DependencyAnalyzer,
)


@dataclass
class GraphSynchronizationReport:
    """Results from one bounded PostgreSQL-to-Neo4j projection run."""

    synchronized: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)

    @property
    def counts(self) -> dict[str, int]:
        """Return stable graph synchronization summary counts."""
        return {
            "SYNCHRONIZED": len(self.synchronized),
            "SKIPPED": len(self.skipped),
            "FAILURES": len(self.failures),
            "TOTAL": (
                len(self.synchronized)
                + len(self.skipped)
                + len(self.failures)
            ),
        }


class GraphSynchronizer:
    """
    Project authoritative ComponentRegistry records into Neo4j.

    This service performs no repository discovery, AI execution,
    or whole-workspace scanning.
    """

    def __init__(
        self,
        dependency_analyzer: DependencyAnalyzer | None = None,
    ):
        self.dependency_analyzer = (
            dependency_analyzer or DependencyAnalyzer()
        )

    def eligible_components(
        self,
        limit: int | None = None,
    ) -> QuerySet[ComponentRegistry]:
        """Return active records whose graph projection is pending or stale."""
        components = (
            ComponentRegistry.objects
            .filter(status="ACTIVE")
            .filter(
                Q(graph_sync_status__in=("PENDING", "FAILED"))
                | ~Q(source_hash=F("graph_sync_hash"))
            )
            .order_by("file_path")
        )

        if limit is not None:
            if limit < 1:
                raise ValueError(
                    "Graph synchronization limit must be positive."
                )
            return components[:limit]

        return components

    def component_is_eligible(
        self,
        component: ComponentRegistry,
    ) -> bool:
        """Return whether one registry record requires graph projection."""
        return (
            component.status == "ACTIVE"
            and (
                component.graph_sync_status in {"PENDING", "FAILED"}
                or component.source_hash != component.graph_sync_hash
            )
        )

    def synchronize_component(
        self,
        component: ComponentRegistry,
    ) -> ComponentNode:
        """Create or update one ComponentNode from one registry record."""
        if component.id is None:
            raise ValueError(
                "ComponentRegistry must be persisted before graph "
                "synchronization."
            )

        if not component.file_path:
            raise ValueError(
                "ComponentRegistry requires a file_path for graph "
                "synchronization."
            )

        postgres_id = str(component.id)

        try:
            node = ComponentNode.nodes.get(postgres_id=postgres_id)
        except ComponentNode.DoesNotExist:
            try:
                node = ComponentNode.nodes.get(
                    file_path=component.file_path,
                )
            except ComponentNode.DoesNotExist:
                node = ComponentNode(
                    postgres_id=postgres_id,
                    file_path=component.file_path,
                )

        node.postgres_id = postgres_id
        node.file_path = component.file_path
        node.name = component.name or ""
        node.persona = component.persona or ""
        node.status = component.status or ""
        node.description = component.description or ""
        node.save()

        return node

    def synchronize_dependencies(
        self,
        component: ComponentRegistry,
        source_node: ComponentNode,
    ) -> list[str]:
        """
        Replace one component's outgoing dependencies with current analysis.

        Dependency nodes are created or refreshed when necessary, but their
        PostgreSQL graph synchronization state remains independently managed.
        """
        dependencies = self.dependency_analyzer.resolve_dependencies(
            component
        )

        target_nodes: list[ComponentNode] = []

        for dependency in dependencies:
            target_nodes.append(
                self.synchronize_component(dependency)
            )

        source_node.depends_on.disconnect_all()

        for target_node in target_nodes:
            source_node.depends_on.connect(target_node)

        return [
            dependency.file_path
            for dependency in dependencies
        ]

    def synchronize_components(
        self,
        components: Iterable[ComponentRegistry],
    ) -> GraphSynchronizationReport:
        """Project eligible explicitly supplied registry records."""
        report = GraphSynchronizationReport()

        for component in components:
            display_path = (
                component.file_path or f"registry:{component.id}"
            )

            if not self.component_is_eligible(component):
                report.skipped.append(display_path)
                continue

            try:
                source_node = self.synchronize_component(component)
                self.synchronize_dependencies(
                    component,
                    source_node,
                )

                component.graph_sync_status = "COMPLETE"
                component.graph_sync_hash = component.source_hash
                component.graph_synced_at = timezone.now()
                component.graph_sync_error = ""
                component.save(
                    update_fields=[
                        "graph_sync_status",
                        "graph_sync_hash",
                        "graph_synced_at",
                        "graph_sync_error",
                    ]
                )
                report.synchronized.append(display_path)

            except Exception as error:
                failure = f"{type(error).__name__}: {error}"
                component.graph_sync_status = "FAILED"
                component.graph_sync_error = failure
                component.save(
                    update_fields=[
                        "graph_sync_status",
                        "graph_sync_error",
                    ]
                )
                report.failures.append(
                    f"{display_path}: {failure}"
                )

        return report
# ======================================================================
# END: EXPLICIT_COMPONENT_GRAPH_SYNCHRONIZATION
# ======================================================================