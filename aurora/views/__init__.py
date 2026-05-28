# 1. Base Framework Operations (Binds your active console panels)
from .landing import aurora_landing
from .wu_orchestration import chat_api, console_dashboard, dashboard

# 2. Daily Automation Workflows
from .start_online_session import start_online_session
from .end_session_view import end_session_view

# FIXED INTERCEPT: Register and expose the new micro-sweeper module layout cleanly
from .micro_cleanup_view import micro_cleanup_view
from .daily_brief import daily_brief_view

# 3. Minion Array Coordination Scripts
from .minion_clicks import wu_director, manual_time_log_view
from .commit_file_view import commit_file_view, execute_baseline_sanity_checks

# 4. Data Models Documentation Systems
from .documentation import DocumentView, MetadataView, ContentView

# 5. Headless JSON API Engine Core
from .api_views import wu_data_stream
from .delta_notes_api import create_delta_note_api

# FIXED: Registered package entry point
from .add_note_view import add_note_view

# NEW WORKFLOW: Forge Pipeline Controller View Module Injection
from .automation_dashboard import AutomationDashboardView
from .process_minion_step import ProcessMinionStepView
from .finalize_feature import FinalizeFeatureView

# ==============================================================================
# STRICT EXPORT LAYOUT DEFINITIONS (Change Control Guardrails)
# ==============================================================================
# This whitelist restricts public exports to exactly your registered views.
# It protects the Aurora AI parsing engine from namespace collisions.
# ==============================================================================
__all__ = [
    # 1. Base Framework Operations
    'aurora_landing',
    'chat_api',
    'console_dashboard',
    'dashboard',
    
    # 2. Daily Automation Workflows
    'start_online_session',
    'end_session_view',
    'micro_cleanup_view',
    'daily_brief_view',
    
    # 3. Minion Array Coordination Scripts
    'wu_director',
    'manual_time_log_view',
    'commit_file_view',
    'execute_baseline_sanity_checks',
    
    # 4. Data Models Documentation Systems
    'DocumentView',
    'MetadataView',
    'ContentView',
    
    # 5. Headless JSON API Engine Core
    'wu_data_stream',
    'create_delta_note_api',
    'add_note_view',
    
    # New Active Module View
    'AutomationDashboardView',
    'ProcessMinionStepView',
    'FinalizeFeatureView',
]
