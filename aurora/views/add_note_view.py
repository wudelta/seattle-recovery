from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def add_note_view(request):
    """
    Renders the newly designed isolated Add Note workspace dashboard.
    Bypasses old daily_brief files to protect active development code layers.
    """
    return render(request, 'aurora/add_note.html')
