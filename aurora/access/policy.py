# ======================================================================
# FILE: aurora/access/policy.py
# START: AURORA_APPLICATION_ACCESS_POLICY
# ======================================================================

AURORA_DEVELOPER_GROUP = "developers"


def can_access_aurora(user) -> bool:
    """Return whether an authenticated user may access Aurora."""

    if not user or not getattr(user, "is_authenticated", False):
        return False

    if user.is_superuser:
        return True

    return user.groups.filter(
        name=AURORA_DEVELOPER_GROUP,
    ).exists()

# ======================================================================
# END: AURORA_APPLICATION_ACCESS_POLICY
# ======================================================================