# ======================================================================
# FILE: aurora/tests/test_fleet_pipeline_coupler.py (PATCH 1 OF 1)
# START: FLEET_PIPELINE_COUPLER_TEST_SUITE
# ======================================================================
import os
import pytest
from unittest.mock import AsyncMock, patch
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from aurora.minions.pipeline_coupler import FleetPipelineCoupler

User = get_user_model()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_ui_assembly_pipeline_executes_workers_in_series():
    """
    Validates that FleetPipelineCoupler sequentially moves tasks through the 
    specialized 8B minion fleet and accurately saves the combined output to disk.
    """
    def create_test_user():
        return User.objects.create_user(username="pipeline_commander", password="matrix_secure_pass")

    test_user = await sync_to_async(create_test_user, thread_sensitive=False)()
    coupler = FleetPipelineCoupler(user=test_user)
    
    target_app = "aurora"
    page_name = "test_pipeline_output"
    
    template_dir = os.path.join(coupler.base_dir, target_app, "templates", target_app)
    os.makedirs(template_dir, exist_ok=True)
    template_abs_path = os.path.join(template_dir, f"{page_name}.html")
    
    with open(template_abs_path, "w") as f:
        f.write("{% block content %}\n<!-- START: FORGED_UI_CONSOLE_CONTAINER -->\n<!-- END: FORGED_UI_CONSOLE_CONTAINER -->\n{% endblock %}")

    async def mock_layout_stream(*args, **kwargs):
        yield "<button id='action-btn'>"
        yield "Click Me"
        yield "</button>"

    async def mock_style_stream(*args, **kwargs):
        yield "#action-btn { color: gold; "
        yield "background: black; }"

    async def mock_logic_stream(*args, **kwargs):
        yield "console.log('Action engaged');"

    # FIX: Switched from class patch.object to runtime module string patching with create=True
    # This bypasses python in-memory container caching and forces the mock stream injection
    with patch("aurora.minions.engine.MinionRunner.run_minion_task_stream", create=True) as mock_runner_stream, \
         patch("aurora.minions.pipeline_coupler.async_send_to_console", new_callable=AsyncMock):
         
        mock_runner_stream.side_effect = [
            mock_layout_stream(),  # Call 1: minion_UI_layout
            mock_style_stream(),   # Call 2: minion_UI_style
            mock_logic_stream()    # Call 3: minion_UI_logic
        ]

        # Execute the full pipeline cascade
        success = await coupler.run_ui_assembly_pipeline(
            target_app=target_app,
            page_name=page_name,
            layout_instructions="Build a gold action button frame asset."
        )
        
        assert success is True
        assert mock_runner_stream.call_count == 3
        
        with open(template_abs_path, "r") as f:
            compiled_output = f.read()
            
        assert "<button id='action-btn'>Click Me</button>" in compiled_output
        assert "#action-btn { color: gold; background: black; }" in compiled_output
        assert "console.log('Action engaged');" in compiled_output

    try:
        os.remove(template_abs_path)
    except OSError:
        pass
# ======================================================================
# END: FLEET_PIPELINE_COUPLER_TEST_SUITE (PATCH 1 OF 1)
# ======================================================================
