# ======================================================================
# FILE: aurora/utils/graph_synchronizer.py (PATCH 1 OF 1)
# START: EXPLICIT_COMPONENT_GRAPH_SYNCHRONIZATION
# ======================================================================
"""Explicit bounded projection of ComponentRegistry records into Neo4j."""

from collections.abc import Iterable
from dataclasses import dataclass, field

from aurora.models import ComponentRegistry
from aurora.nodes import ComponentNode


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

    This service performs no repository discovery, dependency analysis,
    PostgreSQL mutation, AI execution, or whole-workspace scanning.
    """

    def synchronize_component(
        self,
        component: ComponentRegistry,
    ) -> ComponentNode:
        """Create or update one ComponentNode from one registry record."""
        if component.id is None:
            raise ValueError(
                "ComponentRegistry must be persisted before graph synchronization."
            )

        if not component.file_path:
            raise ValueError(
                "ComponentRegistry requires a file_path for graph synchronization."
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

    def synchronize_components(
        self,
        components: Iterable[ComponentRegistry],
    ) -> GraphSynchronizationReport:
        """Project only the explicitly supplied registry records."""
        report = GraphSynchronizationReport()

        for component in components:
            display_path = component.file_path or f"registry:{component.id}"

            try:
                self.synchronize_component(component)
                report.synchronized.append(display_path)
            except Exception as error:
                report.failures.append(
                    f"{display_path}: {type(error).__name__}: {error}"
                )

        return report
# ======================================================================
# END: EXPLICIT_COMPONENT_GRAPH_SYNCHRONIZATION (PATCH 1 OF 1)
# ======================================================================