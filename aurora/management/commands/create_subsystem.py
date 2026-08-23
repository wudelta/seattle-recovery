# ======================================================================
# FILE: aurora/management/commands/create_subsystem.py
# START: CREATE_SUBSYSTEM_COMMAND
# ======================================================================

from typing import Any

from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from aurora.subsystems.hansel.services import (
    SubsystemGenerationError,
    generate_subsystem,
)


class Command(BaseCommand):
    """Create the minimum deterministic scaffold for one Aurora subsystem."""

    help = (
        "Validate or create the minimum repository scaffold "
        "for a new Aurora subsystem."
    )

    def add_arguments(
        self,
        parser,
    ) -> None:
        parser.add_argument(
            "subsystem",
            help=(
                "Lowercase snake_case identifier for the new subsystem."
            ),
        )

        mode = parser.add_mutually_exclusive_group(
            required=True
        )

        mode.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Validate and report the exact scaffold without "
                "modifying the repository."
            ),
        )

        mode.add_argument(
            "--apply",
            action="store_true",
            help=(
                "Validate and create the subsystem scaffold."
            ),
        )

    def handle(
        self,
        *args: Any,
        **options: Any,
    ) -> None:
        subsystem: str = options[
            "subsystem"
        ]

        apply: bool = options[
            "apply"
        ]

        try:
            result = generate_subsystem(
                subsystem,
                apply=apply,
            )
        except SubsystemGenerationError as exc:
            raise CommandError(
                str(exc)
            ) from exc

        mode = (
            "CREATED"
            if result.applied
            else "VALIDATED"
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"{mode}: subsystem={result.subsystem}"
            )
        )

        self.stdout.write(
            f"DESTINATION: {result.destination}"
        )

        for directory in result.directories:
            self.stdout.write(
                f"DIRECTORY: {directory}"
            )

        for file_path in result.files:
            self.stdout.write(
                f"FILE: {file_path}"
            )


# ======================================================================
# END: CREATE_SUBSYSTEM_COMMAND
# ======================================================================