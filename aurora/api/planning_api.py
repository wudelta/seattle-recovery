# ======================================================================
# FILE: aurora/api/planning_api.py 
# START: PLANNING_API_COMPATIBILITY_FACADE
# ======================================================================
"""Compatibility façade for the Planning subsystem API."""

from aurora.subsystems.planning.api import planning_endpoint

__all__ = ["planning_endpoint"]
# ======================================================================
# END: PLANNING_API_COMPATIBILITY_FACADE 
# ======================================================================