# ======================================================================
# FILE: aurora/management/commands/maintain_component_registry.py
# START: COMPONENT_REGISTRY_MAINTENANCE_COMMAND
# ======================================================================

"""Run routine deterministic Component Registry maintenance."""

from django.core.management.base import BaseCommand, CommandError

from aurora.subsystems.component_registry.services.maintenance import (
    ComponentRegistryMaintenance,
)


class Command(BaseCommand):
    """
    Converge Component Registry with current repository state.

    This command performs deterministic maintenance only.

    AI enrichment remains a separate required final-stage operation.
    """

    help = (
        "Refresh Component Registry from repository reality by applying "
        "safe UPDATE, REGISTER, and ARCHIVE changes in one maintenance pass."
    )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Component Registry Maintenance"
            )
        )

        try:
            report = ComponentRegistryMaintenance().refresh()
        except Exception as error:
            raise CommandError(
                "Component Registry maintenance failed. "
                f"{type(error).__name__}: {error}"
            ) from error

        counts = report.counts

        self.stdout.write(
            "Summary: "
            + " | ".join(
                f"{key}={value}"
                for key, value in counts.items()
            )
        )

        if report.review:
            self.stdout.write(
                self.style.WARNING(
                    f"REVIEW required for {len(report.review)} component(s)."
                )
            )

            for path in report.review:
                self.stdout.write(f"  {path}")

        if report.failures:
            self.stdout.write(
                self.style.ERROR(
                    f"FAILURES={len(report.failures)}"
                )
            )

            for failure in report.failures:
                self.stderr.write(
                    self.style.ERROR(
                        f"COMPONENT REGISTRY FAILURE: {failure}"
                    )
                )

            raise CommandError(
                "Component Registry maintenance completed with failures."
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Component Registry maintenance completed successfully."
            )
        )

        pending_count = (
            counts["UPDATED"]
            + counts["REGISTERED"]
        )

        if pending_count:
            self.stdout.write(
                self.style.WARNING(
                    f"{pending_count} component(s) require AI enrichment."
                )
            )
            self.stdout.write(
                "Run document_component_registry --apply when online "
                "and ready to process pending descriptions."
            )

# ======================================================================
# END: COMPONENT_REGISTRY_MAINTENANCE_COMMAND
# ======================================================================