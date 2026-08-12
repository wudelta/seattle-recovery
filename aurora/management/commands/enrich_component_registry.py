# ======================================================================
# FILE: aurora/management/commands/enrich_component_registry.py
# START: COMPONENT_REGISTRY_ENRICHMENT_COMMAND
# ======================================================================

"""Run the normal Component Registry AI enrichment queue."""

from django.core.management.base import BaseCommand, CommandError

from aurora.subsystems.component_registry.services.documenter import (
    ComponentRegistryDocumenter,
)


class Command(BaseCommand):
    """
    Enrich all pending active Component Registry records.

    This is the normal operational enrichment entry point.

    The command processes the durable PENDING queue until either:

    - all eligible components are enriched; or
    - an AI provider failure stops the run.

    Provider failures leave the interrupted component PENDING so the
    same command can be run again later to resume naturally.
    """

    help = (
        "Process all pending Component Registry AI enrichment work until "
        "the queue is exhausted or an AI provider failure stops the run."
    )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Component Registry Enrichment"
            )
        )

        try:
            report = ComponentRegistryDocumenter().analyze_pending(
                apply=True,
                progress_callback=self.stdout.write,
            )
        except ValueError as error:
            raise CommandError(str(error)) from error

        candidates = report["candidates"]

        if not candidates:
            self.stdout.write(
                self.style.SUCCESS(
                    "No pending Component Registry enrichment work."
                )
            )
            return

        if report["stopped"]:
            self.stdout.write(
                self.style.WARNING(
                    "Enrichment stopped after an AI provider failure."
                )
            )
            self.stdout.write(
                f"Failure point: {report['failure_point']}"
            )
            self.stdout.write(
                f"Last completed: {report['last_completed'] or 'None'}"
            )
            self.stdout.write(
                f"Resume from: {report['restart_from']}"
            )
            self.stdout.write(
                "The interrupted component remains PENDING."
            )
            self.stdout.write(
                "Run enrich_component_registry again when AI service "
                "is available."
            )
            raise CommandError(
                "Component Registry enrichment stopped before completion."
            )

        if report["failures"]:
            self.stdout.write(
                self.style.WARNING(
                    "Enrichment completed with component-specific failures."
                )
            )

            for failure in report["failures"]:
                self.stderr.write(
                    self.style.ERROR(
                        f"COMPONENT REGISTRY ENRICHMENT FAILURE: {failure}"
                    )
                )

            raise CommandError(
                "Component Registry enrichment completed with failures."
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Component Registry enrichment completed successfully."
            )
        )

# ======================================================================
# FILE: aurora/management/commands/enrich_component_registry.py
# END: COMPONENT_REGISTRY_ENRICHMENT_COMMAND
# ======================================================================