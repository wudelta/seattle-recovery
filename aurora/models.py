# ======================================================================
# FILE: aurora/models.py
# START: SUBSYSTEM_MODEL_EXPORTS
# ======================================================================

"""
Compatibility exports for Aurora subsystem-owned Django models.

Model implementations live with the subsystem that owns their lifecycle.
They remain part of the Aurora Django application and are re-exported here
to preserve existing imports from aurora.models.
"""

from aurora.subsystems.component_registry.models import ComponentRegistry
from aurora.subsystems.content.models import StaticContent
from aurora.subsystems.delta_directives.models import DeltaDirectives
from aurora.subsystems.delta_notes.models import DeltaNotesEntry
from aurora.subsystems.engineering_session.models import EngineeringSession
from aurora.subsystems.hansel.models import (
    HanselTrail,
    HanselTrailAuthority,
    HanselTrailOutcome,
)
from aurora.subsystems.planning.models import (
    EstimateConfidence,
    ExecutionStatus,
    Initiative,
    InitiativeSourceDeltaNote,
    InitiativePostMortem,
    Phase,
    Project,
    RiskLevel,
    Step,
    StepDocument,
    StepFile,
    StepValidation,
    TimeEntry,
    UserPosition,
)
from aurora.subsystems.wu_chat.models import (
    ChatLedgerEntry,
    PendingCodeChange,
)


__all__ = [
    "ChatLedgerEntry",
    "ComponentRegistry",
    "DeltaDirectives",
    "DeltaNotesEntry",
    "EngineeringSession",
    "EstimateConfidence",
    "ExecutionStatus",
    "HanselTrail",
    "HanselTrailAuthority",
    "HanselTrailOutcome",
    "Initiative",
    "InitiativeSourceDeltaNote",
    "InitiativePostMortem",
    "PendingCodeChange",
    "Phase",
    "Project",
    "RiskLevel",
    "StaticContent",
    "Step",
    "StepDocument",
    "StepFile",
    "StepValidation",
    "TimeEntry",
    "UserPosition",
]


# ======================================================================
# END: SUBSYSTEM_MODEL_EXPORTS
# ======================================================================