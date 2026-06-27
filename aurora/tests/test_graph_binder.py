# ======================================================================
# FILE: aurora/tests/test_graph_binder.py (PATCH 1 OF 1)
# START: WORKSPACE_GRAPH_BINDER_TEST_SUITE
# ======================================================================
import os
import json
import pytest
from unittest.mock import AsyncMock, patch
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from neomodel import db
from aurora.minions.graph_binder import WorkspaceGraphBinder

User = get_user_model()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_workspace_graph_binder_compiles_relational_mappings():
    """
    Validates that WorkspaceGraphBinder executes physical binding routines,
    routes logs cleanly, and synchronizes node connections into Neo4j context.
    """
    def create_test_user():
        return User.objects.create_user(username="graph_commander", password="matrix_secure_pass")

    test_user = await sync_to_async(create_test_user, thread_sensitive=False)()
    binder = WorkspaceGraphBinder(user=test_user)
    
    target_app = "aurora"
    func_name = "test_bind_view"
    api_name = "test_bind_data"
    
    expected_page_path = f"templates/{target_app}/{func_name}.html"
    expected_api_path = f"{target_app}/api/{api_name}_api.py"

    def isolate_graph_environment():
        cleanup_query = (
            "MATCH (n:ComponentNode) WHERE n.file_path = $p_path OR n.file_path = $a_path "
            "DETACH DELETE n"
        )
        db.cypher_query(cleanup_query, {"p_path": expected_page_path, "a_path": expected_api_path})

    await sync_to_async(isolate_graph_environment, thread_sensitive=False)()

    mock_response_data = {
        "status": "success",
        "minion_log": "SUCCESS: Testing binding channel active.",
        "telemetry_stream": "[TEST_LOGGER] File modification write tracking committed.",
        "validation": {"valid": True, "errors": [], "warnings": []}
    }

    with patch.object(binder.handler, "execute") as mock_handler_execute, \
         patch("aurora.minions.graph_binder.async_send_to_console", new_callable=AsyncMock) as mock_console:
         
        class PseudoResponse:
            # FIX: Switched from unstable string mutation replacements to strict, robust json.dumps byte streams
            content = bytes(json.dumps(mock_response_data), "utf-8")
            
        mock_handler_execute.return_value = PseudoResponse()

        success = await binder.execute_workspace_binding(
            app_name=target_app,
            function_name=func_name,
            api_name=api_name
        )
        
        assert success is True
        assert mock_handler_execute.call_count == 1
        mock_console.assert_any_call("[TEST_LOGGER] File modification write tracking committed.")

        def verify_graph_dependency():
            lookup_query = (
                "MATCH (p:ComponentNode {file_path: $p_path})-[r:DEPENDS_ON]->(a:ComponentNode {file_path: $a_path}) "
                "RETURN p.name AS p_name, a.name AS a_name, r.type AS rel_type"
            )
            results, meta = db.cypher_query(lookup_query, {"p_path": expected_page_path, "a_path": expected_api_path})
            return results

        graph_records = await sync_to_async(verify_graph_dependency, thread_sensitive=False)()
        
        assert len(graph_records) == 1
        # Extract individual tracking dimensions safely from multi-matrix results array
        assert graph_records[0][0] == f"page_{func_name}"
        assert graph_records[0][1] == f"api_{api_name}"
        assert graph_records[0][2] == "API_FETCH_STREAM"

    await sync_to_async(isolate_graph_environment, thread_sensitive=False)()
# ======================================================================
# END: WORKSPACE_GRAPH_BINDER_TEST_SUITE (PATCH 1 OF 1)
# ======================================================================
