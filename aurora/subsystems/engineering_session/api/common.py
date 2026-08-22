# ======================================================================
# FILE: aurora/subsystems/engineering_session/api/common.py
# START: ENGINEERING_SESSION_API_COMMON_HELPERS
# ======================================================================

import json

from aurora.subsystems.engineering_session.services import (
    EngineeringSessionError,
    EngineeringSessionPlanningError,
    get_active_session,
)


def require_active_session(user):
    """Require an active Engineering Session for workflow mutations."""

    session = get_active_session(user)

    if session is None:
        raise EngineeringSessionError(
            "An active engineering session is required."
        )

    return session


def parse_planning_document(value):
    """Parse one browser-submitted Planning dictionary."""

    if not isinstance(value, str) or not value.strip():
        raise EngineeringSessionPlanningError(
            "Planning proposal document is required."
        )

    try:
        document = json.loads(
            value
        )
    except json.JSONDecodeError as error:
        raise EngineeringSessionPlanningError(
            "Planning proposal document is not valid JSON."
        ) from error

    if not isinstance(document, dict):
        raise EngineeringSessionPlanningError(
            "Planning proposal document must be an object."
        )

    return document


# ======================================================================
# END: ENGINEERING_SESSION_API_COMMON_HELPERS
# ======================================================================
