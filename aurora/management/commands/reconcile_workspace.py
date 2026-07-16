# ======================================================================
# FILE: aurora/management/commands/reconcile_workspace.py (PATCH 1 OF 3)
# START: COMMAND_IMPORTS_AND_ARGUMENT_CONTRACT
# ======================================================================
"""Read-only workspace reconciliation management command."""

from django.core.management.base import BaseCommand, CommandError

from aurora.utils.component_policy import ALLOWED_ROOTS
from aurora.utils.workspace_reconciler import WorkspaceReconciler


class Command(BaseCommand):
    """
    Compare business-relevant repository files with ComponentRegistry.

    This command is dry-run only. It never modifies repository files,
    PostgreSQL records, Neo4j nodes, or graph relationships.
    """

    help = (
        "Reports deterministic workspace and ComponentRegistry differences "
        "without performing writes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--root",
            choices=sorted(ALLOWED_ROOTS),
            help="Limit results to one approved application root.",
        )
        parser.add_argument(
            "--path",
            help=(
                "Limit results to one repository-relative file or "
                "directory path."
            ),
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Limit the number of displayed items in each classification.",
        )

    def _validate_options(self, options):
        requested_path = options.get("path")
        limit = options.get("limit")

        if requested_path:
            normalized_path = requested_path.strip().replace("\\", "/")
            if normalized_path.startswith("/") or ".." in normalized_path.split("/"):
                raise CommandError(
                    "--path must be a safe repository-relative path."
                )
            options["path"] = normalized_path.rstrip("/")

        if limit is not None and limit < 1:
            raise CommandError("--limit must be greater than zero.")
# ======================================================================
# END: COMMAND_IMPORTS_AND_ARGUMENT_CONTRACT (PATCH 1 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/management/commands/reconcile_workspace.py (PATCH 2 OF 3)
# START: BOUNDED_REPORT_FILTERING
# ======================================================================
    def _build_filtered_report(self, options) -> dict[str, object]:
        """Build the dry-run report and apply optional result boundaries."""
        self._validate_options(options)

        report = WorkspaceReconciler().build_report()
        requested_root = options.get("root")
        requested_path = options.get("path")
        limit = options.get("limit")

        matched_items = {}
        displayed_items = {}

        for classification, items in report["items"].items():
            selected_items = []

            for item in items:
                if requested_root:
                    root_prefix = f"{requested_root}/"
                    if (
                        item.path != requested_root
                        and not item.path.startswith(root_prefix)
                    ):
                        continue

                if requested_path:
                    path_prefix = f"{requested_path}/"
                    if (
                        item.path != requested_path
                        and not item.path.startswith(path_prefix)
                    ):
                        continue

                selected_items.append(item)

            matched_items[classification] = selected_items
            displayed_items[classification] = (
                selected_items[:limit]
                if limit is not None
                else selected_items
            )

        matched_counts = {
            classification: len(items)
            for classification, items in matched_items.items()
        }
        matched_counts["TOTAL"] = sum(matched_counts.values())

        displayed_counts = {
            classification: len(items)
            for classification, items in displayed_items.items()
        }
        displayed_counts["TOTAL"] = sum(displayed_counts.values())

        return {
            "repository_root": report["repository_root"],
            "dry_run": True,
            "counts": matched_counts,
            "displayed_counts": displayed_counts,
            "items": displayed_items,
            "filters": {
                "root": requested_root,
                "path": requested_path,
                "limit": limit,
            },
        }
# ======================================================================
# END: BOUNDED_REPORT_FILTERING (PATCH 2 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/management/commands/reconcile_workspace.py (PATCH 3 OF 3)
# START: COMMAND_EXECUTION_AND_REPORT_OUTPUT
# ======================================================================
    def handle(self, *args, **options):
        """Execute and print the bounded dry-run reconciliation report."""
        report = self._build_filtered_report(options)
        filters = report["filters"]

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Workspace Reconciliation — DRY RUN"
            )
        )
        self.stdout.write(f"Repository: {report['repository_root']}")
        self.stdout.write(
            "Filters: "
            f"root={filters['root'] or '*'} "
            f"path={filters['path'] or '*'} "
            f"limit={filters['limit'] or '*'}"
        )
        self.stdout.write("")

        display_order = (
            "KEEP",
            "UPDATE",
            "REGISTER",
            "STAGE",
            "EXCLUDE",
            "REVIEW",
        )

        for classification in display_order:
            items = report["items"][classification]
            matched_count = report["counts"][classification]
            displayed_count = report["displayed_counts"][classification]

            self.stdout.write(
                self.style.HTTP_INFO(
                    f"{classification} ({matched_count})"
                )
            )

            if not items:
                self.stdout.write("  —")
                continue

            for item in items:
                metadata = []

                if item.name:
                    metadata.append(f"name={item.name}")

                if item.persona:
                    metadata.append(f"persona={item.persona}")

                if item.registry_id:
                    metadata.append(f"registry_id={item.registry_id}")

                metadata_text = (
                    f" | {' | '.join(metadata)}"
                    if metadata
                    else ""
                )

                self.stdout.write(
                    f"  {item.path} | {item.reason}{metadata_text}"
                )

            omitted_count = matched_count - displayed_count
            if omitted_count > 0:
                self.stdout.write(
                    f"  ... {omitted_count} additional "
                    f"{classification} result(s) omitted by --limit"
                )

            self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Summary: "
                + " | ".join(
                    f"{classification}="
                    f"{report['counts'][classification]}"
                    for classification in display_order
                )
                + f" | TOTAL={report['counts']['TOTAL']}"
            )
        )
        self.stdout.write(
            self.style.WARNING(
                "Dry run complete. No repository, PostgreSQL, or Neo4j "
                "changes were performed."
            )
        )
# ======================================================================
# END: COMMAND_EXECUTION_AND_REPORT_OUTPUT (PATCH 3 OF 3)
# ======================================================================