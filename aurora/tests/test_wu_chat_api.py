# ======================================================================
# FILE: aurora/tests/test_wu_chat_api.py (PATCH 1 OF 1)
# START: ASYNC_CHAT_ENDPOINT_STREAM_TEST_SUITE
# ======================================================================
import json
import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from aurora.models import DeltaDirectives, WorkspaceTransaction

User = get_user_model()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_wu_chat_endpoint_triggers_async_orchestration(async_client):
    """
    Verifies that posting valid delta_notes to the Wu chat endpoint saves the 
    active fleet orchestrator directives and returns an immediate status signal.
    """
    # Wrap user creation and force_login session writing inside a synchronous thread
    def setup_authenticated_session():
        user = User.objects.create_user(username="commander_dev", password="secure_matrix_pass")
        async_client.force_login(user)
        
        # Pre-seed an active directive row so the MinionRunner doesn't fail its internal get lookup
        DeltaDirectives.objects.update_or_create(
            directive_name="minion_wu",
            defaults={
                "instructions": "Initial baseline rules with 70B Orchestrator Fleet Commander directive instructions.",
                "constraints": {"model": "llama-3.3-70b-versatile", "temperature": 0.4},
                "is_active": True,
                "created_by": user
            }
        )
        return user

    user = await sync_to_async(setup_authenticated_session, thread_sensitive=False)()
    
    # Corrected namespace path lookup if matching a global routing mapping, or direct string fallback
    try:
        url = reverse("wu_chat_endpoint")
    except Exception:
        url = reverse("aurora:wu_chat_endpoint")
        
    payload = {"delta_notes": "Add a responsive user settings viewport panel with graph logging."}

    # Mock MinionRunner task stream to simulate a quick LLM execution block without running actual network streams
    async def mock_task_stream(*args, **kwargs):
        yield '[COMMAND: /page system_settings]'
        yield ' Orchestration complete text.'

    with patch('aurora.api.wu_chat_api.MinionRunner') as MockRunner:
        mock_runner_instance = MagicMock()
        mock_runner_instance.run_minion_task_stream = mock_task_stream
        MockRunner.return_value = mock_runner_instance

        response = await async_client.post(
            url, 
            data=json.dumps(payload), 
            content_type="application/json"
        )

    # Assert exact response text to inspect deep traceback context if a 400 persists
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}. Response text: {response.content.decode()}"
    
    response_data = response.json()
    assert response_data.get("status") == "wu_is_processing"
    assert "transaction_id" in response_data

    # Verify that the database recorded a corresponding transaction record safely
    def verify_transaction_records():
        return WorkspaceTransaction.objects.filter(user=user).exists()
        
    tx_exists = await sync_to_async(verify_transaction_records, thread_sensitive=False)()
    assert tx_exists is True

    # Verify that the minion_wu row was updated/seeded in the database state registry
    wu_directive = await DeltaDirectives.objects.aget(directive_name="minion_wu")
    assert wu_directive.is_active is True
    assert "70B Orchestrator Fleet Commander" in wu_directive.instructions
# ======================================================================
# END: ASYNC_CHAT_ENDPOINT_STREAM_TEST_SUITE (PATCH 1 OF 1)
# ======================================================================
