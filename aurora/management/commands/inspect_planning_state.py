# ======================================================================
# FILE: aurora/management/commands/inspect_planning_state.py
# START: PLANNING_STATE_INSPECTION_COMMAND
# ======================================================================

from pprint import pformat

from django.core.management.base import BaseCommand

from aurora.subsystems.planning.services.reconciliation import (
    build_planning_reconciliation_snapshot,
)


class Command(BaseCommand):
    """Emit persisted Planning state for human/AI reconciliation."""

    help = (
        "Print a read-only Python dictionary containing Planning hierarchy, "
        "assignment, lifecycle, time-entry, and navigation evidence."
    )

    def handle(self, *args, **options):
        snapshot = build_planning_reconciliation_snapshot()

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