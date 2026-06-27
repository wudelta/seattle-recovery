# ======================================================================
# FILE: aurora/tests/test_page_api_automation.py (PATCH 1 OF 1)
# START: WORKSPACE_AUTOMATION_UTILITIES_TEST_SUITE
# ======================================================================
import os
import pytest
from unittest.mock import AsyncMock, patch
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from aurora.models import ComponentRegistry
from aurora.minions.automation_utilities import WorkspaceAutomationRunner

User = get_user_model()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_workspace_automation_runner_provisions_resources():
    """
    Validates that WorkspaceAutomationRunner provisions structural layout templates
    and backend asynchronous files on disk, updating the ComponentRegistry tracking system.
    """
    def create_test_user():
        return User.objects.create_user(username="automation_commander", password="matrix_secure_pass")

    test_user = await sync_to_async(create_test_user, thread_sensitive=False)()
    runner = WorkspaceAutomationRunner(user=test_user)
    
    unique_suffix = "test_run_verify"
    
    # Use AsyncMock to isolate network logs and catch console telemetry frames
    with patch("aurora.minions.automation_utilities.async_send_to_console", new_callable=AsyncMock) as mock_send:
        # 1. Test /page Command Execution
        page_success = await runner.execute_page_command(unique_suffix)
        assert page_success is True, f"execute_page_command failed. Logs: {mock_send.mock_calls}"
        
        # Verify page record mapping inside PostgreSQL matches schema profiles
        page_registry = await ComponentRegistry.objects.aget(name=f"page_{unique_suffix}")
        assert page_registry.persona == "UI_LAYOUT"
        assert os.path.exists(os.path.join(runner.base_dir, page_registry.file_path))
        
        # 2. Test /api Command Execution
        api_success = await runner.execute_api_command(unique_suffix)
        assert api_success is True, f"execute_api_command failed. Logs: {mock_send.mock_calls}"
        
        # Verify API record mapping inside PostgreSQL matches schema profiles
        api_registry = await ComponentRegistry.objects.aget(name=f"api_{unique_suffix}")
        assert api_registry.persona == "COMPILER_MODULE"
        assert os.path.exists(os.path.join(runner.base_dir, api_registry.file_path))
        
        # Clean up files created during test run execution to leave workspace unpolluted
        try:
            os.remove(os.path.join(runner.base_dir, page_registry.file_path))
            os.remove(os.path.join(runner.base_dir, api_registry.file_path))
        except OSError:
            pass
# ======================================================================
# END: WORKSPACE_AUTOMATION_UTILITIES_TEST_SUITE (PATCH 1 OF 1)
# ======================================================================
