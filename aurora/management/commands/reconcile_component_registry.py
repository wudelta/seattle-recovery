# ======================================================================
# FILE: aurora/management/commands/reconcile_component_registry.py
# START: COMMAND_IMPORTS_AND_ARGUMENT_CONTRACT
# ======================================================================
"""Component Registry reconciliation and bounded synchronization command."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from aurora.subsystems.component_registry.services.component_policy import (
    ALLOWED_ROOTS,
)
from aurora.subsystems.component_registry.services.reconciler import (
    WorkspaceReconciler,
)
from aurora.subsystems.component_registry.services.synchronizer import (
    WorkspaceSynchronizer,
)


UserModel = get_user_model()


class Command(BaseCommand):
    """
    Compare business-relevant repository files with ComponentRegistry.

    Reconciliation remains read-only by default. ComponentRegistry mutation
    requires an explicit synchronization operation and --apply.
    """

    help = (
        "Reports deterministic Component Registry differences and optionally "
        "applies one explicitly bounded synchronization operation."
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
            help="Limit the number of displayed or synchronized items.",
        )
        parser.add_argument(
            "--operation",
            choices=(
                "reconcile",
                "update",
                "register",
                "archive",
            ),
            default="reconcile",
            help=(
                "Choose read-only reconciliation, existing-row updates, "
                "new-row registration, or archival of missing components."
            ),
        )
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Explicitly permit the selected synchronization operation.",
        )
        parser.add_argument(
            "--user",
            help=(
                "Username assigned as created_by for new registrations. "
                "Required when applying registration."
            ),
        )

    def _validate_options(self, options):
        requested_path = options.get("path")
        limit = options.get("limit")
        operation = options.get("operation")
        apply = options.get("apply")
        username = options.get("user")

        if requested_path:
            normalized_path = requested_path.strip().replace("\\", "/")
            if (
                normalized_path.startswith("/")
                or ".." in normalized_path.split("/")
            ):
                raise CommandError(
                    "--path must be a safe repository-relative path."
                )

            options["path"] = normalized_path.rstrip("/")
            requested_path = options["path"]

        if limit is not None and limit < 1:
            raise CommandError("--limit must be greater than zero.")

        if operation == "reconcile" and apply:
            raise CommandError(
                "--apply cannot be used with the reconcile operation."
            )

        if operation == "register" and apply:
            if not username:
                raise CommandError(
                    "--user is required when applying registration."
                )

            if not requested_path and limit is None:
                raise CommandError(
                    "Registration requires --path or a positive --limit "
                    "when using --apply."
                )

        if operation != "register" and username:
            raise CommandError(
                "--user is only valid with the register operation."
            )

    @staticmethod
    def _resolve_user(username: str):
        """Resolve one explicit owner from the configured user model."""
        try:
            return UserModel.objects.get(username=username)
        except UserModel.DoesNotExist as error:
            raise CommandError(
                f"User '{username}' does not exist."
            ) from error

# ======================================================================
# END: COMMAND_IMPORTS_AND_ARGUMENT_CONTRACT
# ======================================================================

# ======================================================================
# FILE: aurora/management/commands/reconcile_component_registry.py
# START: BOUNDED_REPORT_FILTERING_AND_SYNCHRONIZATION
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

    def _run_synchronization(self, options) -> dict[str, object]:
        """Preview or apply one explicitly bounded synchronization operation."""
        self._validate_options(options)

        operation = options["operation"]
        apply = options["apply"]
        requested_path = options.get("path")
        limit = options.get("limit")
        username = options.get("user")

        user_instance = None

        if operation == "register" and apply:
            user_instance = self._resolve_user(username)

        return WorkspaceSynchronizer().run(
            apply=apply,
            operation=operation,
            user_instance=user_instance,
            path=requested_path,
            limit=limit,
        )

# ======================================================================
# END: BOUNDED_REPORT_FILTERING_AND_SYNCHRONIZATION
# ======================================================================

# ======================================================================
# FILE: aurora/management/commands/reconcile_component_registry.py
# START: COMMAND_EXECUTION_AND_REPORT_OUTPUT
# ======================================================================
    def handle(self, *args, **options):
        """Execute reconciliation or one explicit synchronization operation."""
        operation = options["operation"]

        if operation != "reconcile":
            result = self._run_synchronization(options)
            apply = result["apply"]
            candidates = result["candidates"]
            counts = result["counts"]

            mode = "APPLY" if apply else "PREVIEW"

            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    f"Component Registry Synchronization — "
                    f"{operation.upper()} {mode}"
                )
            )
            self.stdout.write(
                "Boundaries: "
                f"path={options.get('path') or '*'} "
                f"limit={options.get('limit') or '*'}"
            )
            self.stdout.write("")

            self.stdout.write(
                self.style.HTTP_INFO(
                    f"CANDIDATES ({len(candidates)})"
                )
            )

            if not candidates:
                self.stdout.write("  —")
            else:
                for candidate in candidates:
                    candidate_path = getattr(
                        candidate,
                        "path",
                        None,
                    ) or getattr(
                        candidate,
                        "file_path",
                        "",
                    )

                    candidate_reason = getattr(
                        candidate,
                        "reason",
                        None,
                    )

                    metadata = []

                    candidate_name = getattr(candidate, "name", None)
                    candidate_persona = getattr(candidate, "persona", None)
                    candidate_registry_id = getattr(
                        candidate,
                        "registry_id",
                        None,
                    ) or getattr(
                        candidate,
                        "id",
                        None,
                    )

                    if candidate_name:
                        metadata.append(f"name={candidate_name}")

                    if candidate_persona:
                        metadata.append(f"persona={candidate_persona}")

                    if candidate_registry_id:
                        metadata.append(
                            f"registry_id={candidate_registry_id}"
                        )

                    metadata_text = (
                        f" | {' | '.join(metadata)}"
                        if metadata
                        else ""
                    )

                    reason_text = (
                        f" | {candidate_reason}"
                        if candidate_reason
                        else ""
                    )

                    self.stdout.write(
                        f"  {candidate_path}"
                        f"{reason_text}"
                        f"{metadata_text}"
                    )

            self.stdout.write("")

            if not apply:
                self.stdout.write(
                    self.style.WARNING(
                        "Preview complete. No ComponentRegistry "
                        "changes were performed."
                    )
                )
                return

            report = result["report"]

            for failure in report.failures:
                self.stderr.write(
                    self.style.ERROR(
                        f"COMPONENT REGISTRY FAILURE: {failure}"
                    )
                )

            self.stdout.write(
                self.style.SUCCESS(
                    "Summary: "
                    + " | ".join(
                        f"{key}={value}"
                        for key, value in counts.items()
                    )
                )
            )

            if report.failures:
                self.stdout.write(
                    self.style.WARNING(
                        "Synchronization completed with "
                        "ComponentRegistry failures."
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        "Synchronization completed successfully."
                    )
                )

            return

        report = self._build_filtered_report(options)
        filters = report["filters"]

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Component Registry Reconciliation — DRY RUN"
            )
        )
        self.stdout.write(
            f"Repository: {report['repository_root']}"
        )
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
            "ARCHIVE",
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
                    metadata.append(
                        f"registry_id={item.registry_id}"
                    )

                metadata_text = (
                    f" | {' | '.join(metadata)}"
                    if metadata
                    else ""
                )

                self.stdout.write(
                    f"  {item.path} | "
                    f"{item.reason}"
                    f"{metadata_text}"
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
                "Dry run complete. No repository or "
                "ComponentRegistry changes were performed."
            )
        )

# ======================================================================
# END: COMMAND_EXECUTION_AND_REPORT_OUTPUT
# ======================================================================