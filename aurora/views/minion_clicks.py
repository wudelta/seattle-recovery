import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core_logic.sessions import log_manual_time

@csrf_exempt
def wu_director(request):
    print("🤖 [wu_director] Action triggered.")
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')
        return JsonResponse({
            "response": f"Director here. I received: '{user_message}'. Connection stable.",
            "status": "online"
        })
    
@csrf_exempt
def manual_time_log_view(request):
    print("🤖 [manual_time_log_view] Action triggered.")
    if request.method == "POST":
        user_id = request.user.username if request.user.is_authenticated else "Delta"
        hours = request.POST.get('hours')
        note = request.POST.get('note')
        log_manual_time(user_id, hours, note)
        return JsonResponse({'status': 'success', 'message': f'Logged {hours} manual hours.'})

