# ====================================================================== #
# FILE: aurora/api/__init__.py (PATCH 1 OF 1)                            #
# START: MODULE_ROUTING_REGISTRATION_FOOTPRINT                           #
# ====================================================================== #
from .directives_api import directives_endpoint
from .content_api import content_endpoint
from .planning_api import planning_endpoint

# Consolidated imports from the unified api_commands.py file layer
from .api_commands import (
    delta_notes_endpoint,
    execute_blueprint_api,
    unlocked_components_endpoint,
)

# FIXED: Updated reference to track our new native asynchronous coroutine engine
from .dev_streamer_api import (
    trigger_pipeline,
    run_development_pipeline_async,
)

from .wu_chat_api import (
    approve_pending_code_change,
    reject_pending_code_change,
    wu_chat_endpoint,
)

# 2. Integrated Code Editor & Sandbox API Endpoints
from .ide_operations import (
    file_tree_api,
    file_operation_api,
    run_code_api,
    lint_code_api,
)

__all__ = [
    "delta_notes_endpoint",
    "execute_blueprint_api",
    "unlocked_components_endpoint",
    "trigger_pipeline",
    "run_development_pipeline_async",
    "content_endpoint",
    "directives_endpoint",
    "planning_endpoint",
    "wu_chat_endpoint",
    "approve_pending_code_change",
    "reject_pending_code_change",
    "file_tree_api",
    "file_operation_api",
    "run_code_api",
    "lint_code_api",
]
# ====================================================================== #
# END: MODULE_ROUTING_REGISTRATION_FOOTPRINT (PATCH 1 OF 1)              #
# ====================================================================== #