# ======================================================================
# FILE: aurora/management/commands/import_planning_dictionary.py
# START: IMPORT_PLANNING_DICTIONARY_COMMAND
# ======================================================================
from ast import literal_eval
from pathlib import Path
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from aurora.subsystems.planning.io.exceptions import (
    PlanningImportError,
    PlanningSchemaError,
)
from aurora.subsystems.planning.io.updater import update_planning_document


User = get_user_model()


class Command(BaseCommand):
    """Validate or apply a planning dictionary update."""

    help = (
        "Validate or create a Project and append Initiatives, Phases, and "
        "Steps from a Python-literal planning dictionary."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "path",
            type=Path,
            help=(
                "Repository-relative or absolute path to a file containing "
                "one Python-literal planning dictionary."
            ),
        )
        parser.add_argument(
            "--user",
            required=True,
            help="Natural key of the user creating and receiving the added work.",
        )

        mode = parser.add_mutually_exclusive_group(required=True)
        mode.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate the update and report counts without writing records.",
        )
        mode.add_argument(
            "--apply",
            action="store_true",
            help=(
                "Validate and transactionally create the planning records. "
                "Canonical temporary planning dictionaries are removed after "
                "a successful apply."
            ),
        )

    def handle(self, *args: Any, **options: Any) -> None:
        path: Path = options["path"]
        apply: bool = options["apply"]

        try:
            document = self._load_dictionary(path)
            user = self._get_user(options["user"])
            result = update_planning_document(
                document,
                user=user,
                apply=apply,
            )
        except (
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

        if result.applied:
            self._remove_applied_transport_artifact(
                path=path,
                project_slug=result.project_slug,
            )

    def _load_dictionary(self, path: Path) -> Any:
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise CommandError(
                f'Unable to read planning dictionary "{path}": {exc}'
            ) from exc

        try:
            return literal_eval(source)
        except (SyntaxError, ValueError) as exc:
            raise CommandError(
                f'Planning dictionary "{path}" is not a valid Python literal: '
                f"{exc}"
            ) from exc

    def _get_user(self, natural_key: str) -> User:
        try:
            return User._default_manager.get_by_natural_key(natural_key)
        except User.DoesNotExist as exc:
            raise CommandError(
                f'User "{natural_key}" does not exist.'
            ) from exc

    def _remove_applied_transport_artifact(
        self,
        *,
        path: Path,
        project_slug: str,
    ) -> None:
        """
        Remove one successfully applied canonical planning transport artifact.

        Files outside the repository-owned planning_imports directory are
        deliberately preserved.
        """
        repository_root = Path.cwd().resolve()

        canonical_directory = (
            repository_root
            / "docs"
            / project_slug
            / "management"
            / "planning_imports"
        ).resolve()

        candidate = (
            path
            if path.is_absolute()
            else repository_root / path
        ).resolve()

        try:
            candidate.relative_to(
                canonical_directory
            )
        except ValueError:
            self.stdout.write(
                self.style.WARNING(
                    "PRESERVED: applied planning dictionary is outside the "
                    f'canonical temporary directory "{canonical_directory}".'
                )
            )
            return

        if candidate.parent != canonical_directory:
            self.stdout.write(
                self.style.WARNING(
                    "PRESERVED: applied planning dictionary is not directly "
                    "inside the canonical planning_imports directory."
                )
            )
            return

        try:
            candidate.unlink()
        except FileNotFoundError:
            return
        except OSError as exc:
            raise CommandError(
                "Planning records were applied successfully, but the temporary "
                f'planning dictionary "{candidate}" could not be removed: {exc}'
            ) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"REMOVED: temporary planning dictionary {candidate}"
            )
        )


# ======================================================================
# END: IMPORT_PLANNING_DICTIONARY_COMMAND
# ======================================================================