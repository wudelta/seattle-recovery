# ======================================================================
# FILE: aurora/tests/test_data_engine.py (PATCH 1 OF 1)
# START: DATA_ENGINE_COORDINATOR_TEST_SUITE
# ======================================================================
import os
import pytest
from unittest.mock import AsyncMock, patch
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from aurora.minions.data_engine import DataEngineCoordinator

User = get_user_model()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_data_engine_coordinator_injects_query_logic():
    """
    Validates that DataEngineCoordinator successfully reads forged API skeletons,
    requests view logic blocks, and surgically merges them inside structural anchors.
    """
    def create_test_user():
        return User.objects.create_user(username="data_commander", password="matrix_secure_pass")

    test_user = await sync_to_async(create_test_user, thread_sensitive=False)()
    coordinator = DataEngineCoordinator(user=test_user)
    
    target_app = "aurora"
    endpoint_name = "test_data_query"
    func_name = f"{endpoint_name}_endpoint"
    
    api_dir = os.path.join(coordinator.automation.base_dir, target_app, "api")
    os.makedirs(api_dir, exist_ok=True)
    target_filepath = os.path.join(api_dir, f"{endpoint_name}_api.py")
    
    with open(target_filepath, "w") as f:
        f.write(
            f"# START: PACKAGED_IMPORTS_AND_DEPENDENCIES\n"
            f"from django.http import JsonResponse\n"
            f"# END: PACKAGED_IMPORTS_AND_DEPENDENCIES\n\n"
            f"# START: API_ENDPOINT_LOGIC\n"
            f"def {func_name}(request):\n"
            f"    return JsonResponse({{'status': 'placeholder'}}) \n"
            f"# END: API_ENDPOINT_LOGIC\n"
        )

    async def mock_query_stream(*args, **kwargs):
        yield "payload = {'query_status': 'complete'}\n"
        yield "return JsonResponse(payload)"

    # FIX: Switched from inline patch.object to strict module string reference with create=True
    # This completely overrides memory cache limitations across the container environment.
    with patch("aurora.minions.engine.MinionRunner.run_minion_task_stream", create=True) as mock_runner_stream, \
         patch.object(coordinator.automation, "execute_api_command", return_value=True), \
         patch("aurora.minions.data_engine.async_send_to_console", new_callable=AsyncMock):
         
        mock_runner_stream.return_value = mock_query_stream()

        # Execute data assembly step
        success = await coordinator.assemble_async_data_endpoint(
            target_app=target_app,
            endpoint_name=endpoint_name,
            query_instructions="Fetch complete cluster registry records."
        )
        
        assert success is True
        
        with open(target_filepath, "r") as f:
            compiled_view_code = f.read()
            
        assert "# START: API_ENDPOINT_LOGIC" in compiled_view_code
        assert "payload = {'query_status': 'complete'}" in compiled_view_code
        assert "return JsonResponse(payload)" in compiled_view_code
        assert "# END: API_ENDPOINT_LOGIC" in compiled_view_code

    try:
        os.remove(target_filepath)
    except OSError:
        pass
# ======================================================================
# END: DATA_ENGINE_COORDINATOR_TEST_SUITE (PATCH 1 OF 1)
# ======================================================================
