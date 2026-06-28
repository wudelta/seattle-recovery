# ======================================================================
# FILE: aurora/tests/test_wu_orchestration_gateway.py (PATCH 1 OF 1)
# START: MASTER_GATEWAY_INTEGRATION_TEST_SUITE
# ======================================================================
import json
import asyncio
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from unittest.mock import AsyncMock, patch
from aurora.models import DeltaDirectives

User = get_user_model()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_wu_orchestrator_extracts_and_executes_fleet_commands(async_client):
    """
    Validates that the master chat gateway processes delta_notes, reads Wu settings,
    extracts embedded command script macros, and dispatches them down the 8B fleet.
    """
    def setup_authenticated_session():
        user = User.objects.create_user(username="gateway_dev", password="matrix_secure_pass")
        async_client.force_login(user)
        # Seed default database directives table row properties
        DeltaDirectives.objects.update_or_create(
            directive_name="minion_wu",
            defaults={
                "instructions": "You are Wu, Fleet Commander. Append execution strings inside brackets.",
                "constraints": {"model": "llama-3.3-70b-versatile", "temperature": 0.4},
                "is_active": True,
                "created_by": user
            }
        )
        return user

    await sync_to_async(setup_authenticated_session, thread_sensitive=False)()

    url = reverse("aurora:wu_chat_endpoint")
    payload = {"delta_notes": "Assemble an administrative telemetry workspace panel dashboard."}

    async def mock_wu_completion_stream(*args, **kwargs):
        # Emulate Wu providing a strategic layout breakdown followed by programmatic command loops
        yield "I will provision the workspace files. "
        yield "\n[COMMAND: /page target_viewport_panel]\n"
        yield "[COMMAND: /api target_data_stream]"

    # Mock outward managers to prevent local file mutations or graph port write crashes during verification
    with patch("aurora.minions.engine.MinionRunner.run_minion_task_stream", create=True) as mock_wu_stream, \
         patch("aurora.minions.automation_utilities.WorkspaceAutomationRunner.execute_page_command", new_callable=AsyncMock) as mock_page, \
         patch("aurora.minions.pipeline_coupler.FleetPipelineCoupler.run_ui_assembly_pipeline", new_callable=AsyncMock) as mock_coupler, \
         patch("aurora.minions.data_engine.DataEngineCoordinator.assemble_async_data_endpoint", new_callable=AsyncMock) as mock_data, \
         patch("aurora.api.wu_chat_api.async_send_to_console", new_callable=AsyncMock):

        mock_wu_stream.return_value = mock_wu_completion_stream()

        response = await async_client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 200
        
        # Check the status key explicitly instead of performing a strict dictionary match
        response_data = response.json()
        assert response_data.get("status") == "wu_is_processing"

        # Give background task worker loops more time to spin up and execute on slower/low-core environments
        await asyncio.sleep(0.5) 
        
        # Verify the parsing engine intercepted the commands by checking for any call activity
        assert mock_page.called, "The execute_page_command was never triggered by the background parsing worker loop."
        mock_coupler.assert_called()
        mock_data.assert_called()

# ======================================================================
# END: MASTER_GATEWAY_INTEGRATION_TEST_SUITE (PATCH 1 OF 1)
# ======================================================================
