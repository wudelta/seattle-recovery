# aurora/views/console_view.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def aurora_console(request):
    """
    Renders the central High-Density Control Cockpit console.
    Protected via authentication to safeguard the development environment.
    """
    context = {
        "architect": request.user.username,
        "ai_lead": "Wu",
    }
    # Sync target to point directly to your console template
    return render(request, "aurora/aurora_console.html", context)
