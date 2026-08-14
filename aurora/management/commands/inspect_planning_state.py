# ======================================================================
# FILE: aurora/management/commands/inspect_planning_state.py
# START: PLANNING_STATE_INSPECTION_COMMAND
# ======================================================================

from pprint import pformat

from django.core.management.base import BaseCommand, CommandError

from aurora.subsystems.planning.services.reconciliation import (
    build_initiative_reconciliation_snapshot,
    build_planning_reconciliation_snapshot,
    build_planning_reconciliation_summary,
)


class Command(BaseCommand):
    """Emit persisted Planning evidence for human/AI reconciliation."""

    help = (
        "Print compact Planning reconciliation evidence. "
        "Use --initiative for one Initiative. Add --full for forensic detail."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--initiative",
            type=int,
            help=(
                "Restrict reconciliation evidence to one "
                "Initiative primary key."
            ),
        )

        parser.add_argument(
            "--full",
            action="store_true",
            help=(
                "Print forensic detail. With --initiative, print the full "
                "Initiative hierarchy. Without --initiative, print the "
                "complete Planning snapshot."
            ),
        )

    def handle(self, *args, **options):
        initiative_id = options.get("initiative")
        full = options["full"]

        try:
            if initiative_id is not None:
                snapshot = build_initiative_reconciliation_snapshot(
                    initiative_id,
                    full=full,
                )
            elif full:
                snapshot = build_planning_reconciliation_snapshot()
            else:
                snapshot = build_planning_reconciliation_summary()

        except ValueError as error:
            raise CommandError(str(error)) from error

        self.stdout.write(
            pformat(
                snapshot,
                sort_dicts=False,
                width=100,
            )
        )

# ======================================================================
# FILE: aurora/management/commands/inspect_planning_state.py
# END: PLANNING_STATE_INSPECTION_COMMAND
# ======================================================================