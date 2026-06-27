# ======================================================================
# FILE: aurora/tests/test_directives_api.py (PATCH 1 OF 1)
# START: DIRECTIVES_COCKPIT_BACKEND_TEST_SUITE
# ======================================================================
import json
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from unittest.mock import AsyncMock, patch
from aurora.models import DeltaDirectives

User = get_user_model()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_directives_endpoint_dispatches_prompt_optimization(async_client):
    """
    Verifies that posting an optimize_prompt payload to the directives view 
    reads existing settings and the minion_AI_writer rules from the database, 
    executing a non-destructive refinement stream.
    """
    def setup_authenticated_session():
        user = User.objects.create_user(username="prompt_engineer", password="matrix_secure_pass")
        async_client.force_login(user)
        
        # Seed minion_AI_writer inside the DB table to satisfy your database-driven architecture
        DeltaDirectives.objects.update_or_create(
            directive_name="minion_AI_writer",
            defaults={
                "instructions": (
                    "You are minion_AI_writer. Analyze current instructions alongside new modification requests. "
                    "Surgically merge, append, or remove rules without obliterating unedited structures."
                ),
                "constraints": {"model": "llama-3.1-8b-instant", "temperature": 0.1},
                "is_active": True,
                "created_by": user
            }
        )
        
        # Pre-seed an existing minion profile to test the context-aware modification merge layer
        target_minion = DeltaDirectives.objects.create(
            directive_name="minion_data_endpoint",
            instructions="Rule 1: Use async managers. Rule 2: Return JSON responses.",
            constraints={"model": "llama-3.1-8b-instant"},
            is_active=True,
            created_by=user
        )
        return target_minion

    target_row = await sync_to_async(setup_authenticated_session, thread_sensitive=False)()
    
    url = reverse("aurora:directives_endpoint")
    payload = {
        "action": "optimize_prompt",
        "id": str(target_row.id),
        "directive_name": "minion_data_endpoint",
        "instructions": "Add a new constraint: Ensure raw backticks are forbidden. Remove Rule 2."
    }

    async def mock_writer_stream(*args, **kwargs):
        yield "Rule 1: Use async managers. New Constraint: Ensure raw backticks are forbidden."

    # Use strict module string reference with create=True to override local memory cache blocks safely
    with patch("aurora.minions.engine.MinionRunner.run_minion_task_stream", create=True) as mock_stream, \
         patch("aurora.api.directives_api.async_send_to_console", new_callable=AsyncMock):
         
        mock_stream.return_value = mock_writer_stream()

        response = await async_client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json"
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "SUCCESS"
        assert "Optimization stream dispatched" in response.json()["message"]
        
        # Verify the context builder correctly evaluated the inputs and triggered the runner task
        assert mock_stream.call_count == 1
        
        # FIX: Align the substring verification checks with the exact text layout used in the controller view
        called_args, called_kwargs = mock_stream.call_args
        target_task_name = called_args[0]
        composite_payload_string = called_args[1]
        
        assert target_task_name == "minion_AI_writer"
        assert "CURRENT INSTRUCTIONS IN DATABASE" in composite_payload_string
        assert "Rule 1: Use async managers." in composite_payload_string
# ======================================================================
# END: DIRECTIVES_COCKPIT_BACKEND_TEST_SUITE (PATCH 1 OF 1)
# ======================================================================
