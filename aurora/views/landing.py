# ======================================================================
# FILE: aurora/views/landing.py (PATCH 1 OF 1)
# START: ROOT PORTAL ENTRANCE VIEW ENGINE CONFIGURATION
# ======================================================================
from django.shortcuts import render

def aurora_landing(request):
    """Renders the public gateway entry portal interface for Aurora."""
    return render(request, 'aurora/landing.html')
# ======================================================================
# END: ROOT PORTAL ENTRANCE VIEW ENGINE CONFIGURATION
# ======================================================================
