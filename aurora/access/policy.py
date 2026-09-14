# ======================================================================
# FILE: aurora/access/policy.py
# START: AURORA_APPLICATION_ACCESS_POLICY
# ======================================================================

AURORA_DEVELOPER_GROUP = "developers"

AURORA_INITIATIVE_OWNER_GROUP = "initiative_owner"
AURORA_PHASE_OWNER_GROUP = "phase_owner"
AURORA_STEP_OWNER_GROUP = "step_owner"


def can_access_aurora(user) -> bool:
    """Return whether an authenticated user may access Aurora."""

    if not user or not getattr(user, "is_authenticated", False):
        return False

    if user.is_superuser:
        return True

    return user.groups.filter(
        name=AURORA_DEVELOPER_GROUP,
    ).exists()


def can_reconcile_decision_engine(user) -> bool:
    """Return whether a user has Decision Engine reconciliation capability."""

    if not can_access_aurora(user):
        return False

    return user.has_perm("aurora.change_initiative")


# ======================================================================
# END: AURORA_APPLICATION_ACCESS_POLICY
# ======================================================================