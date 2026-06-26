# ======================================================================
# FILE: aurora/api/__init__.py (PATCH 1 OF 1)
# START: MODULE_ROUTING_REGISTRATION_FOOTPRINT
# ======================================================================
from .directives_api import directives_endpoint
from .content_api import content_endpoint

# Consolidated imports from the unified api_commands.py file layer
from .api_commands import delta_notes_endpoint, execute_blueprint_api, unlocked_components_endpoint
# FIXED: Updated reference to track our new native asynchronous coroutine engine
from .dev_streamer_api import trigger_pipeline, run_development_pipeline_async

__all__ = [
    'delta_notes_endpoint',
    'execute_blueprint_api',
    'unlocked_components_endpoint',
    'trigger_pipeline',
    'run_development_pipeline_async',  # FIXED: Target the async reference here
    'content_endpoint',
    'directives_endpoint',
]
# ======================================================================
# END: MODULE_ROUTING_REGISTRATION_FOOTPRINT (PATCH 1 OF 1)
# ======================================================================
