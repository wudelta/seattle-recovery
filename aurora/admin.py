# ======================================================================
# FILE: aurora/admin.py
# START: SUBSYSTEM_ADMIN_REGISTRATION
# ======================================================================

"""
Django admin registration surface for Aurora subsystem-owned admin modules.

Admin configuration lives with the subsystem that owns each model.
Importing these modules registers their ModelAdmin classes with Django.
"""

from aurora.subsystems.component_registry import (
    admin as component_registry_admin,
)
from aurora.subsystems.content import admin as content_admin
from aurora.subsystems.delta_directives import (
    admin as delta_directives_admin,
)
from aurora.subsystems.delta_notes import admin as delta_notes_admin
from aurora.subsystems.planning import admin as planning_admin
from aurora.subsystems.wu_chat import admin as wu_chat_admin


__all__ = [
    "component_registry_admin",
    "content_admin",
    "delta_directives_admin",
    "delta_notes_admin",
    "planning_admin",
    "wu_chat_admin",
]


# ======================================================================
# END: SUBSYSTEM_ADMIN_REGISTRATION
# ======================================================================