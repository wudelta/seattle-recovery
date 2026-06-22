# ======================================================================
# FILE: aurora/views/__init__.py (PATCH 1 OF 1)
# START: CLEANED_VIEWS_NAMESPACE_INITIALIZATION
# ======================================================================
# 1. Base Framework Operations (Binds your active console panels)
from .landing import aurora_landing
from .console_view import ConsoleView

# 2. Integrated Code Editor & Sandbox API Endpoints
from .ide_operations import (
    file_tree_api,
    file_operation_api,
    run_code_api,
    lint_code_api
)

# ==============================================================================
# STRICT EXPORT LAYOUT DEFINITIONS (Change Control Guardrails)
# ==============================================================================
# This whitelist restricts public exports to exactly your registered views.
# It protects the Aurora AI parsing engine from namespace collisions.
# ==============================================================================
__all__ = [
    # 1. Base Framework Operations
    'aurora_landing',
    'ConsoleView',
    
    # 2. Integrated Code Editor & Sandbox API Endpoints
    'file_tree_api',
    'file_operation_api',
    'run_code_api',
    'lint_code_api',
]
# ======================================================================
# END: CLEANED_VIEWS_NAMESPACE_INITIALIZATION (PATCH 1 OF 1)
# ======================================================================
