# ======================================================================
# FILE: aurora/management/commands/import_planning_plan.py
# START: IMPORT_PLANNING_PLAN_COMMAND
# ======================================================================
from pathlib import Path
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from aurora.subsystems.planning.io.exceptions import (
    PlanningImportError,
    PlanningSchemaError,
)
from aurora.subsystems.planning.io.importer import import_planning_document
from aurora.subsystems.planning.io.loader import (
    PlanningDocumentLoadError,
    load_planning_document,
)


User = get_user_model()


class Command(BaseCommand):
    """Validate or import a versioned planning YAML document."""

    help = (
        "Validate or import a Project, Initiative, Phase, and Step hierarchy "
        "from a planning YAML document."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "path",
            type=Path,
            help="Repository-relative or absolute path to the planning YAML file.",
        )
        parser.add_argument(
            "--user",
            required=True,
            help="Natural key of the user creating and receiving the imported plan.",
        )

        mode = parser.add_mutually_exclusive_group(required=True)
        mode.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate the document and report counts without writing records.",
        )
        mode.add_argument(
            "--apply",
            action="store_true",
            help="Validate and transactionally create the planning hierarchy.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        path: Path = options["path"]
        apply: bool = options["apply"]

        try:
            document = load_planning_document(path)
            user = self._get_user(options["user"])
            result = import_planning_document(
                document,
                user=user,
                apply=apply,
            )
        except (
            PlanningDocumentLoadError,
            PlanningSchemaError,
            PlanningImportError,
        ) as exc:
            raise CommandError(str(exc)) from exc

        mode = "APPLIED" if result.applied else "VALIDATED"

        self.stdout.write(
            self.style.SUCCESS(
                f"{mode}: project={result.project_slug} "
                f"projects={result.projects} "
                f"initiatives={result.initiatives} "
                f"phases={result.phases} "
                f"steps={result.steps}"
            )
        )

    def _get_user(self, natural_key: str) -> User:
        try:
            return User._default_manager.get_by_natural_key(natural_key)
        except User.DoesNotExist as exc:
            raise CommandError(
                f'User "{natural_key}" does not exist.'
            ) from exc
# ======================================================================
# END: IMPORT_PLANNING_PLAN_COMMAND
# ======================================================================