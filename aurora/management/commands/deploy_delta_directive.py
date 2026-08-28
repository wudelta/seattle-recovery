# ======================================================================
# FILE: aurora/management/commands/deploy_delta_directive.py
# START: DEPLOY_DELTA_DIRECTIVE_COMMAND
# ======================================================================
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from aurora.subsystems.delta_directives.services.deployment import (
    DirectiveDeploymentError,
    deploy_directive,
)


User = get_user_model()


class Command(BaseCommand):
    """Validate or deploy one complete Delta Directive."""

    help = (
        "Validate or atomically deploy one repository-owned directive "
        "artifact into canonical DeltaDirectives.instructions."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "directive_name",
            help=(
                "Directive identity. The deployment artifact is resolved as "
                "aurora/subsystems/delta_directives/directives/"
                "<directive_name>.md."
            ),
        )

        parser.add_argument(
            "--user",
            required=True,
            help="Natural key of the user authorizing the deployment.",
        )

        mode = parser.add_mutually_exclusive_group(required=True)

        mode.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Validate the directive artifact and report the proposed "
                "deployment without changing the database."
            ),
        )

        mode.add_argument(
            "--apply",
            action="store_true",
            help=(
                "Validate and atomically replace the complete canonical "
                "directive instructions."
            ),
        )

    def handle(self, *args: Any, **options: Any) -> None:
        directive_name: str = options["directive_name"]
        apply: bool = options["apply"]

        try:
            user = self._get_user(options["user"])

            result = deploy_directive(
                directive_name=directive_name,
                user=user,
                apply=apply,
            )
        except DirectiveDeploymentError as exc:
            raise CommandError(str(exc)) from exc

        mode = "APPLIED" if result.applied else "VALIDATED"

        self.stdout.write(
            self.style.SUCCESS(
                f"{mode}: directive={result.directive_name} "
                f"action={result.action} "
                f"characters={result.character_count} "
                f"artifact={result.source_path}"
            )
        )

    def _get_user(self, natural_key: str):
        try:
            return User._default_manager.get_by_natural_key(
                natural_key
            )
        except User.DoesNotExist as exc:
            raise CommandError(
                f'User "{natural_key}" does not exist.'
            ) from exc
# ======================================================================
# FILE: aurora/management/commands/deploy_delta_directive.py
# END: DEPLOY_DELTA_DIRECTIVE_COMMAND
# ======================================================================