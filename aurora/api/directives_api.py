# ======================================================================
# FILE: aurora/api/directives_api.py (PATCH 1 OF 2)
# START: DIRECTIVES_COCKPIT_BACKEND_CONTROLLER_GET
# ======================================================================
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from aurora.models import DeltaDirectives

@login_required
def directives_endpoint(request):
    """
    Unified JSON API router handling secure AJAX operations 
    for the standalone DeltaDirectives prompt configuration panel.
    """
    if request.method == 'GET':
        status_scope = request.GET.get('status', 'all')
        id_query = request.GET.get('id', None)
        
        if id_query:
            try:
                asset = DeltaDirectives.objects.get(id=id_query)
                return JsonResponse({
                    'status': 'SUCCESS',
                    'asset': {
                        'id': str(asset.id),
                        'directive_name': asset.directive_name,
                        'instructions': asset.instructions,
                        'constraints': asset.constraints,
                        'is_active': asset.is_active,
                        'author': asset.created_by.username,
                        'date_modified': asset.date_modified.strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
            except DeltaDirectives.DoesNotExist:
                return JsonResponse({'status': 'ERROR', 'message': 'Requested prompt configuration missing.'}, status=404)
        
        # Pull records cleanly sorted alphabetically by minion name
        queryset = DeltaDirectives.objects.all().order_by('directive_name')
        if status_scope == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_scope == 'inactive':
            queryset = queryset.filter(is_active=False)
            
        payload = [{
            'id': str(item.id),
            'directive_name': item.directive_name,
            'is_active': item.is_active,
            'date_modified': item.date_modified.strftime('%m/%d %H:%M')
        } for item in queryset]
        return JsonResponse({'status': 'SUCCESS', 'inventory': payload})
# ======================================================================
# END: DIRECTIVES_COCKPIT_BACKEND_CONTROLLER_GET (PATCH 1 OF 2)
# ======================================================================

# ======================================================================
# FILE: aurora/api/directives_api.py (PATCH 2 OF 2)
# START: DIRECTIVES_COCKPIT_BACKEND_CONTROLLER_MUTATIONS
# ======================================================================
    elif request.method == 'POST':
        try:
            raw_data = json.loads(request.body)
            asset_id = raw_data.get('id', None)
            name = raw_data.get('directive_name', '').strip()
            constraints = raw_data.get('constraints', {})
            is_active = raw_data.get('is_active', True)
            instructions = raw_data.get('instructions', '')
            
            if not name or not instructions:
                return JsonResponse({'status': 'ERROR', 'message': 'Missing validation parameters.'}, status=400)
                
            if asset_id:
                asset = DeltaDirectives.objects.get(id=asset_id)
                asset.directive_name = name
                asset.constraints = constraints
                asset.is_active = is_active
                asset.instructions = instructions
                asset.save()
                log_action = "UPDATED"
            else:
                asset = DeltaDirectives.objects.create(
                    directive_name=name,
                    constraints=constraints,
                    is_active=is_active,
                    instructions=instructions,
                    created_by=request.user
                )
                log_action = "INSTANTIATED"
                
            return JsonResponse({
                'status': 'SUCCESS',
                'action': log_action,
                'id': str(asset.id),
                'message': "Directive structural sequence successfully saved."
            })
        except Exception as e:
            return JsonResponse({'status': 'ERROR', 'message': str(e)}, status=500)

    elif request.method == 'DELETE':
        try:
            raw_data = json.loads(request.body)
            asset_id = raw_data.get('id', None)
            asset = DeltaDirectives.objects.get(id=asset_id)
            asset.delete()
            return JsonResponse({'status': 'SUCCESS', 'message': 'Asset pruned.'})
        except Exception as e:
            return JsonResponse({'status': 'ERROR', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'ERROR', 'message': 'Method not allowed.'}, status=405)
# ======================================================================
# END: DIRECTIVES_COCKPIT_BACKEND_CONTROLLER_MUTATIONS (PATCH 2 OF 2)
# ======================================================================
