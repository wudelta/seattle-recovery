# ======================================================================
# FILE: aurora/subsystems/content/api/endpoint.py
# START: CONTENT_COCKPIT_BACKEND_CONTROLLER
# ======================================================================
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from aurora.models import StaticContent

@login_required
def content_endpoint(request):
    """
    Unified JSON API router handling secure AJAX operations 
    for the standalone content_console_panel framework.
    """
    if request.method == 'GET':
        app_scope = request.GET.get('application', 'all')
        id_query = request.GET.get('id', None)
        
        if id_query:
            try:
                asset = StaticContent.objects.get(id=id_query)
                return JsonResponse({
                    'status': 'SUCCESS',
                    'asset': {
                        'id': str(asset.id),
                        'title': asset.title,
                        'application': asset.application,
                        'html_content': asset.html_content,
                        'author': asset.created_by.username,
                        'date_modified': asset.date_modified.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
            except StaticContent.DoesNotExist:
                return JsonResponse({'status': 'ERROR', 'message': 'Requested resource missing.'}, status=404)
        
        # UPDATED: Sorting structure altered from date to application then title fields
        queryset = StaticContent.objects.all().order_by('application', 'title')
        if app_scope != 'all':
            queryset = queryset.filter(application=app_scope)
            
        payload = [{
            'id': str(item.id),
            'title': item.title,
            'application': item.application,
            'date_modified': item.date_modified.strftime('%m/%d %H:%M')
        } for item in queryset]
        return JsonResponse({'status': 'SUCCESS', 'inventory': payload})

    elif request.method == 'POST':
        try:
            raw_data = json.loads(request.body)
            asset_id = raw_data.get('id', None)
            title = raw_data.get('title', '').strip()
            application = raw_data.get('application', 'aurora')
            html_content = raw_data.get('html_content', '')
            
            if not title or not html_content:
                return JsonResponse({'status': 'ERROR', 'message': 'Missing validation parameters.'}, status=400)
                
            if asset_id:
                asset = StaticContent.objects.get(id=asset_id)
                asset.title = title
                asset.application = application
                asset.html_content = html_content
                asset.save()
                log_action = "UPDATED"
            else:
                asset = StaticContent.objects.create(
                    title=title,
                    application=application,
                    html_content=html_content,
                    created_by=request.user
                )
                log_action = "INSTANTIATED"
                
            return JsonResponse({
                'status': 'SUCCESS',
                'action': log_action,
                'id': str(asset.id),
                'message': "Asset structural sequence successfully saved."
            })
        except Exception as e:
            return JsonResponse({'status': 'ERROR', 'message': str(e)}, status=500)

    elif request.method == 'DELETE':
        try:
            raw_data = json.loads(request.body)
            asset_id = raw_data.get('id', None)
            asset = StaticContent.objects.get(id=asset_id)
            asset.delete()
            return JsonResponse({'status': 'SUCCESS', 'message': 'Asset pruned.'})
        except Exception as e:
            return JsonResponse({'status': 'ERROR', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'ERROR', 'message': 'Method not allowed.'}, status=405)
# ======================================================================
# END: CONTENT_COCKPIT_BACKEND_CONTROLLER (PATCH 1 OF 1)
# ======================================================================
