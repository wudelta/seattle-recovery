# ======================================================================
# FILE: aurora/subsystems/planning/io/exceptions.py
# START: PLANNING_IO_EXCEPTIONS
# ======================================================================
class PlanningIOError(Exception):
    """Base exception for deterministic planning import and export failures."""


class PlanningSchemaError(PlanningIOError):
    """Raised when a planning document violates the supported schema."""


class PlanningImportError(PlanningIOError):
    """Raised when a validated planning document cannot be imported."""


class PlanningExportError(PlanningIOError):
    """Raised when planning data cannot be exported."""
# ======================================================================
# END: PLANNING_IO_EXCEPTIONS
# ======================================================================