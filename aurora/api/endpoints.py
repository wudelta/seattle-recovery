# ======================================================================
# FILE: aurora/api/endpoints.py (PATCH 1 OF 2)
# START: STANDARD_DJANGO_WEB_VIEW_ENDPOINT_IMPORTS
# ======================================================================
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from aurora.models import ComponentRegistry
# ======================================================================
# END: STANDARD_DJANGO_WEB_VIEW_ENDPOINT_IMPORTS (PATCH 1 OF 2)
# ======================================================================

