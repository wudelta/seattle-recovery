# ======================================================================
# FILE: aurora/management/commands/export_planning_plan.py
# START: EXPORT_PLANNING_PLAN_COMMAND
# ======================================================================
from pathlib import Path
from typing import Any

import yaml
from django.core.management.base import BaseCommand, CommandError

from aurora.models import Project
from aurora.subsystems.planning.io.exceptions import (
    PlanningExportError,
    PlanningSchemaError,
)
from aurora.subsystems.planning.io.exporter import export_planning_document
from aurora.subsystems.planning.io.schema import validate_planning_document


class Command(BaseCommand):
    """Export one persisted planning hierarchy as versioned YAML."""

    help = (
        "Export a Project, Initiative, Phase, and Step hierarchy "
        "to a versioned planning YAML document."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "slug",
            help="Slug of the Project to export.",
        )
        parser.add_argument(
            "path",
            type=Path,
            help="Repository-relative or absolute output path.",
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Replace an existing output file.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        slug: str = options["slug"]
        path: Path = options["path"]
        overwrite: bool = options["overwrite"]

        project = self._get_project(slug)
        self._validate_output_path(path, overwrite)

        try:
            document = export_planning_document(project)
            validate_planning_document(document)

            serialized = yaml.safe_dump(
                document,
                sort_keys=False,
                allow_unicode=True,
                default_flow_style=False,
            )

            path.write_text(serialized, encoding="utf-8")
        except (PlanningExportError, PlanningSchemaError) as exc:
            raise CommandError(str(exc)) from exc
        except OSError as exc:
            raise CommandError(
                f"Unable to write planning document: {path}"
            ) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"EXPORTED: project={slug} path={path}"
            )
        )

    def _get_project(self, slug: str) -> Project:
        try:
            return Project.objects.get(slug=slug)
        except Project.DoesNotExist as exc:
            raise CommandError(
                f'Project with slug "{slug}" does not exist.'
            ) from exc

    def _validate_output_path(
        self,
        path: Path,
        overwrite: bool,
    ) -> None:
        if path.exists() and path.is_dir():
            raise CommandError(
                f"Export path is a directory: {path}"
            )

        if path.exists() and not overwrite:
            raise CommandError(
                f"Export path already exists: {path}. "
                "Use --overwrite to replace it."
            )

        if not path.parent.exists():
            raise CommandError(
                f"Export directory does not exist: {path.parent}"
            )

        if not path.parent.is_dir():
            raise CommandError(
                f"Export parent is not a directory: {path.parent}"
            )
# ======================================================================
# END: EXPORT_PLANNING_PLAN_COMMAND
# ======================================================================