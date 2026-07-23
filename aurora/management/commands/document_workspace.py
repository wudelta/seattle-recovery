# ======================================================================
# FILE: aurora/management/commands/document_workspace.py (PATCH 1 OF 1)
# START: STREAMING_COMPONENT_ANALYSIS_COMMAND
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
        apply_changes = options["apply"]
        mode = "APPLY" if apply_changes else "PREVIEW"

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"Component description analysis — {mode}"
            )
        )

        try:
            report = WorkspaceDocumenter().analyze_pending(
                apply=apply_changes,
                path=options.get("path"),
                limit=options.get("limit"),
                progress_callback=(
                    self.stdout.write if apply_changes else None
                ),
            )
        except ValueError as error:
            raise CommandError(str(error)) from error

        candidates = report["candidates"]

        if not candidates:
            self.stdout.write(
                self.style.WARNING("No pending components matched the boundary.")
            )
            return

        if not report["apply"]:
            self.stdout.write(f"Candidates: {len(candidates)}")

            for file_path in candidates:
                self.stdout.write(f"  {file_path}")

            self.stdout.write(
                self.style.WARNING(
                    "\nPreview only. Re-run with --apply to execute AI analysis."
                )
            )
            return

        if report["stopped"]:
            self.stdout.write(
                self.style.ERROR(
                    "\nDocumentation stopped after an AI provider failure."
                )
            )
            self.stdout.write(
                f"Failure point: {report['failure_point']}"
            )
            self.stdout.write(
                f"Last completed: {report['last_completed'] or 'None'}"
            )
            self.stdout.write(
                f"Restart from: {report['restart_from']}"
            )
            raise CommandError(
                "Restore provider connectivity, inspect the failed component, "
                "reset it to PENDING, and rerun the command."
            )

        if report["failures"]:
            self.stdout.write(
                self.style.WARNING(
                    "\nDocumentation completed with non-provider failures."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "\nDocumentation completed without failures."
                )
            )
# ======================================================================
# END: STREAMING_COMPONENT_ANALYSIS_COMMAND (PATCH 1 OF 1)
# ======================================================================