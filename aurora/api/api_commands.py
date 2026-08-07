# ======================================================================
# FILE: aurora/api/api_commands.py
# START: MODULAR_GATEWAY_EXPORTS_AND_ROUTING_BRIDGE
# ======================================================================
"""
Compatibility bridge for remaining legacy Aurora API exports.
"""

from aurora.api.blueprint import execute_blueprint_api
from aurora.api.endpoints import unlocked_components_endpoint


__all__ = [
    "execute_blueprint_api",
    "unlocked_components_endpoint",
]
# ======================================================================
# END: MODULAR_GATEWAY_EXPORTS_AND_ROUTING_BRIDGE
# ======================================================================