# ======================================================================
# FILE: aurora/subsystems/delta_directives/api/endpoint.py
# START: API_ENDPOINT_LOGIC
# ======================================================================
import json
import asyncio
import traceback
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from asgiref.sync import sync_to_async
from aurora.models import DeltaDirectives
from aurora.minions.engine import MinionRunner
from aurora.api.dev_streamer_api import async_send_to_console

@login_required
def directives_endpoint(request):
    """
    Unified JSON API router handling secure AJAX operations for the standalone 
    DeltaDirectives prompt configuration panel with streaming refinement optimization.
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

    elif request.method == 'POST':
        try:
            raw_data = json.loads(request.body)
            action = raw_data.get('action', 'save').strip().lower()
            
            # --- ATOMIC REWRITE MATRIX: DISPATCHED TO DATABASE MINION_AI_WRITER ---
            if action == 'optimize_prompt':
                user_rambling = raw_data.get('instructions', '').strip()
                minion_target = raw_data.get('directive_name', 'unknown_minion')
                record_id = raw_data.get('id', None)
                
                if not user_rambling:
                    return JsonResponse({'status': 'ERROR', 'message': 'No prompt instructions provided to optimize.'}, status=400)
                
                # Dynamic Database Lookup: Fetch existing text if editing a record to prevent obliteration
                existing_instructions = ""
                if record_id:
                    try:
                        target_row = DeltaDirectives.objects.get(id=record_id)
                        existing_instructions = target_row.instructions
                    except DeltaDirectives.DoesNotExist:
                        pass

                # Formulate structural task payload containing instructions history blocks
                composite_prompt = (
                    f"You are the minion_AI_writer. Your task is to analyze a conversational modification request "
                    f"and update the instruction profile for the fleet minion: '{minion_target}'.\n\n"
                    f"CURRENT INSTRUCTIONS IN DATABASE:\n"
                    f"{existing_instructions if existing_instructions else '[None - Fresh Creation]'}\n\n"
                    f"DEVELOPER MODIFICATION REQUEST:\n"
                    f"{user_rambling}\n\n"
                    f"CRITICAL EXECUTION CONSTRAINTS:\n"
                    f"1. Analyze the current instructions against the developer modification request.\n"
                    f"2. If the request adds guidelines or parameters, surgically integrate them cleanly.\n"
                    f"3. If it requests to delete or modify rules, strip them out without altering the remaining text.\n"
                    f"4. Retain all other existing unedited prompt rules completely intact.\n"
                    f"5. Output ONLY the final optimized instruction set. Do NOT provide preamble notes, conversational "
                    f"filler, explanations, or wrap your code in triple markdown backticks."
                )
                
                runner = MinionRunner()
                
                async def run_optimization_stream():
                    await async_send_to_console(f"📝 [WRITER] Executing atomic merge for minion: {minion_target}...")
                    await async_send_to_console("\n✨ [DISTILLED LIVE PROMPT UPDATE]:\n")
                    
                    async for token in runner.run_minion_task_stream("minion_AI_writer", composite_prompt):
                        await async_send_to_console(token)
                        
                    await async_send_to_console("\n[SYSTEM] Prompt optimization finalized.\n")

                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop and loop.is_running():
                    loop.create_task(run_optimization_stream())
                else:
                    from asgiref.sync import async_to_sync
                    async_to_sync(run_optimization_stream)()
                    
                return JsonResponse({'status': 'SUCCESS', 'message': 'Optimization stream dispatched to telemetry channel.'})

            # --- PRESERVED BASE SYSTEM ACTIONS ---
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
# END: API_ENDPOINT_LOGIC
# ======================================================================
