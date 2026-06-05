# hopehub/views/bed_locator_view.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def bed_locator_endpoint(request):
    """Automated test payload endpoint forged by Aurora Forge Engine."""
    payload = {
        "status": "success",
        "visibility": "private",
        "endpoint": "bed_locator",
        "app": "hopehub"
    }
    return JsonResponse(payload)
