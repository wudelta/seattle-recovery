# ======================================================================
# FILE: aurora/management/commands/document_workspace.py (PATCH 1 OF 1)
# START: BOUNDED_COMPONENT_ANALYSIS_COMMAND
# ======================================================================
from django.core.management.base import BaseCommand, CommandError

from aurora.utils.documenter import WorkspaceDocumenter


class Command(BaseCommand):
    """Preview or execute bounded AI description generation."""

    help = (
        "Generates concise AI descriptions for active ComponentRegistry rows "
        "whose analysis_status is PENDING."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Execute AI analysis and database updates. Default is preview only.",
        )
        parser.add_argument(
            "--path",
            type=str,
            help="Restrict analysis to one repository-relative file or directory.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Restrict the number of pending components processed.",
        )

    def handle(self, *args, **options):
        try:
            report = WorkspaceDocumenter().analyze_pending(
                apply=options["apply"],
                path=options.get("path"),
                limit=options.get("limit"),
            )
        except ValueError as error:
            raise CommandError(str(error)) from error

        mode = "APPLY" if report["apply"] else "PREVIEW"
        candidates = report["candidates"]

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"Component description analysis — {mode}"
            )
        )

        if not candidates:
            self.stdout.write(
                self.style.WARNING("No pending components matched the boundary.")
            )
            return

        self.stdout.write(f"Candidates: {len(candidates)}")
        for file_path in candidates:
            self.stdout.write(f"  {file_path}")

        if not report["apply"]:
            self.stdout.write(
                self.style.WARNING(
                    "\nPreview only. Re-run with --apply to execute AI analysis."
                )
            )
            return

        completed = report["completed"]
        skipped = report["skipped"]
        failures = report["failures"]

        self.stdout.write(
            self.style.SUCCESS(f"\nCompleted: {len(completed)}")
        )
        for file_path in completed:
            self.stdout.write(f"  {file_path}")

        if skipped:
            self.stdout.write(
                self.style.WARNING(f"\nSkipped: {len(skipped)}")
            )
            for message in skipped:
                self.stdout.write(f"  {message}")

        if failures:
            self.stdout.write(
                self.style.ERROR(f"\nFailures: {len(failures)}")
            )
            for message in failures:
                self.stdout.write(f"  {message}")
# ======================================================================
# END: BOUNDED_COMPONENT_ANALYSIS_COMMAND (PATCH 1 OF 1)
# ======================================================================