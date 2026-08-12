# ======================================================================
# FILE: aurora/views/landing.py
# START: ROOT_PORTAL_ENTRANCE_VIEW_ENGINE_CONFIGURATION
# ======================================================================

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from aurora.access import can_access_aurora


@login_required(login_url="aurora:login")
def aurora_landing(request):
    """Render the Aurora landing page for authorized developers."""

    if not can_access_aurora(request.user):
        raise PermissionDenied

    return render(request, "aurora/landing.html")

# ======================================================================
# END: ROOT_PORTAL_ENTRANCE_VIEW_ENGINE_CONFIGURATION
# ======================================================================