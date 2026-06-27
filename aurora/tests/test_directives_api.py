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

User = get_user_model()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_directives_endpoint_dispatches_prompt_optimization(async_client):
    """
    Verifies that posting an optimize_prompt action payload to the directivesview
    invokes the async minion_AI_writer stream runner cleanly without errors.
    """
    def setup_authenticated_session():
        user = User.objects.create_user(username="prompt_engineer", password="matrix_secure_pass")
        async_client.force_login(user)
        return user

    await sync_to_async(setup_authenticated_session, thread_sensitive=False)()
    
    url = reverse("aurora:directives_endpoint")
    payload = {
        "action": "optimize_prompt",
        "directive_name": "minion_test_worker",
        "instructions": "I want a simple minion that parses text and splits it up. Make it follow strict rules."
    }

    async def mock_writer_stream(*args, **kwargs):
        yield "Structured instructions block."

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
# ======================================================================
# END: DIRECTIVES_COCKPIT_BACKEND_TEST_SUITE (PATCH 1 OF 1)
# ======================================================================
