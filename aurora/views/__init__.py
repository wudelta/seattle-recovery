# aurora/views/__init__.py

# 1. Base Framework Operations (Binds your active console panels)
from .landing import aurora_landing
from .console_view import ConsoleView

# 2. Automated AI Forge Automation (The API pipelines for Wu & minions)
from .api_views import execute_blueprint_api

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
    
    # 2. Automated AI Forge Automation
    'execute_blueprint_api',
]
