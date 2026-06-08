# ==============================================================================
# FILE: aurora/views/__init__.py (PATCH 1 OF 1)
# START: CLEANED_VIEWS_NAMESPACE_INITIALIZATION
# ==============================================================================
from .delta_notes_view import DeltaNotesView

# 1. Base Framework Operations (Binds your active console panels)
from .landing import aurora_landing
from .console_view import ConsoleView

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
    'DeltaNotesView',
]
# ==============================================================================
# END: CLEANED_VIEWS_NAMESPACE_INITIALIZATION
# ==============================================================================
