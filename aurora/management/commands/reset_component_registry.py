# ======================================================================
# FILE: aurora/management/commands/reset_component_registry.py
# START: EXPLICIT_COMPONENT_REGISTRY_RESET_COMMAND
# ======================================================================

"""Destructively clear Component Registry for explicit disaster recovery."""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from neomodel import db

from aurora.models import ComponentRegistry


class Command(BaseCommand):
    """
    Remove all Component Registry records and Neo4j projections.

    This is an emergency recovery tool, not a maintenance command.

    After reset, rebuild deterministic registry state with:

        daurora-cmd maintain_component_registry

    AI enrichment must then be restored separately when practical.
    """

    help = (
        "Delete all Neo4j ComponentNode projections and all PostgreSQL "
        "ComponentRegistry records for explicit disaster recovery. "
        "Requires --apply."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Perform the destructive registry reset.",
        )

    def handle(self, *args, **options):
        if not options["apply"]:
            registry_count = ComponentRegistry.objects.count()

            graph_results, _ = db.cypher_query(
                "MATCH (component:ComponentNode) "
                "RETURN count(component) AS component_count"
            )
            graph_count = graph_results[0][0] if graph_results else 0

            self.stdout.write(
                self.style.WARNING(
                    "Dry run only. No records were deleted."
                )
            )
            self.stdout.write(
                f"Neo4j ComponentNode records: {graph_count}"
            )
            self.stdout.write(
                f"PostgreSQL ComponentRegistry records: {registry_count}"
            )
            self.stdout.write(
                "This command is intended only for explicit registry "
                "disaster recovery."
            )
            self.stdout.write(
                "Run again with --apply to perform the destructive reset."
            )
            return

        try:
            graph_results, _ = db.cypher_query(
                "MATCH (component:ComponentNode) "
                "WITH collect(component) AS components "
                "WITH components, size(components) AS component_count "
                "FOREACH (component IN components | DETACH DELETE component) "
                "RETURN component_count"
            )
            graph_deleted = graph_results[0][0] if graph_results else 0
        except Exception as error:
            raise CommandError(
                "Neo4j ComponentNode reset failed. "
                "PostgreSQL records were not deleted. "
                f"{type(error).__name__}: {error}"
            ) from error

        try:
            with transaction.atomic():
                registry_deleted, _ = (
                    ComponentRegistry.objects.all().delete()
                )
        except Exception as error:
            raise CommandError(
                "PostgreSQL ComponentRegistry reset failed after Neo4j "
                "was cleared. "
                f"{type(error).__name__}: {error}"
            ) from error

        self.stdout.write(
            self.style.SUCCESS(
                "Component Registry disaster-recovery reset completed."
            )
        )
        self.stdout.write(
            f"Neo4j ComponentNode records deleted: {graph_deleted}"
        )
        self.stdout.write(
            "PostgreSQL ComponentRegistry records deleted: "
            f"{registry_deleted}"
        )
        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                "The Component Registry is now empty."
            )
        )
        self.stdout.write(
            "Rebuild deterministic registry state with:"
        )
        self.stdout.write(
            "  daurora-cmd maintain_component_registry"
        )
        self.stdout.write(
            "Then restore pending semantic enrichment when online with:"
        )
        self.stdout.write(
            "  daurora-cmd document_component_registry --apply"
        )

# ======================================================================
# FILE: aurora/management/commands/reset_component_registry.py
# END: EXPLICIT_COMPONENT_REGISTRY_RESET_COMMAND
# ======================================================================