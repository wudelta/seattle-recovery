# ======================================================================
# FILE: aurora/management/commands/validate_hansel.py
# START: VALIDATE_HANSEL_COMMAND
# ======================================================================

from typing import Any

from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from aurora.subsystems.hansel.services import (
    validate_hansel_repository,
)


class Command(BaseCommand):
    """Validate every canonical subsystem Hansel contract."""

    help = (
        "Run deterministic Hansel contract validation across all "
        "recognized Aurora subsystems."
    )

    def handle(
        self,
        *args: Any,
        **options: Any,
    ) -> None:
        result = validate_hansel_repository()

        for validation in result.results:
            subsystem = (
                validation.contract_path
                .split("/")[2]
            )

            status = (
                "VALID"
                if validation.is_valid
                else "INVALID"
            )

            self.stdout.write(
                f"{subsystem}: {status}"
            )

            for issue in validation.issues:
                self.stdout.write(
                    f"  {issue.code}: {issue.message}"
                )

        self.stdout.write(
            ""
        )

        self.stdout.write(
            (
                "SUMMARY "
                f"total={len(result.results)} "
                f"valid={result.valid_count} "
                f"invalid={result.invalid_count}"
            )
        )

        if not result.is_valid:
            raise CommandError(
                "Hansel repository validation failed."
            )

        self.stdout.write(
            self.style.SUCCESS(
                "VALIDATED: all canonical Hansel contracts are valid"
            )
        )


# ======================================================================
# END: VALIDATE_HANSEL_COMMAND
# ======================================================================