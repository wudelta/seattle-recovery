# ======================================================================
# FILE: aurora/api/api_commands.py (PATCH 1 OF 1)
# START: MODULAR_GATEWAY_EXPORTS_AND_ROUTING_BRIDGE
# ======================================================================
"""
Unified Entry Point Configuration Bridge.
Redirects legacy system import chains down to the decoupled, 
refactored modular layout scripts.
"""

from aurora.api.endpoints import (
    delta_notes_endpoint,
    unlocked_components_endpoint
)
from aurora.api.blueprint import execute_blueprint_api

# Explicitly expose view vectors to satisfy local routing configurations
__all__ = [
    'delta_notes_endpoint',
    'unlocked_components_endpoint',
    'execute_blueprint_api',
]
# ======================================================================
# END: MODULAR_GATEWAY_EXPORTS_AND_ROUTING_BRIDGE (PATCH 1 OF 1)
# ======================================================================

