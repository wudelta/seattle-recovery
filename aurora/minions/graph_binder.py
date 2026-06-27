# ======================================================================
# FILE: aurora/minions/graph_binder.py (PATCH 1 OF 1)
# START: WORKSPACE_GRAPH_BINDER_COMPILER
# ======================================================================
import asyncio
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from aurora.api.dev_streamer_api import async_send_to_console
from aurora.api.handlers.bind import BindCommandHandler

class WorkspaceGraphBinder:
    """Orchestrates relational graph compilers and hooks dependencies across workspaces."""

    def __init__(self, user):
        self.user = user
        self.handler = BindCommandHandler()

    async def execute_workspace_binding(self, app_name: str, function_name: str, api_name: str) -> bool:
        """
        Executes the physical /bind script using a clean mock request container,
        then flushes structural dependency paths cleanly into the active Neo4j matrix.
        """
        clean_app = app_name.strip().lower()
        clean_func = function_name.strip().lower()
        clean_api = api_name.strip().lower()

        await async_send_to_console(f"🔗 [BIND_ENGINE] Compiling relational matrices across your directory structure...")

        # Formulate execution part arguments mirroring shell protocol inputs
        parts = ["/bind", clean_app, clean_func, clean_api]
        raw_cmd = f"/bind {clean_app} {clean_func} {clean_api}"

        # Mock a minimal Django request context block for the handler's execute method
        class DummyRequest:
            def __init__(self, user):
                self.user = user
                self.method = "POST"

        dummy_req = DummyRequest(self.user)

        # Offload physical file generation and tracking to a thread-isolated execution block
        def run_handler_sync():
            response = self.handler.execute(dummy_req, parts, raw_cmd)
            import json
            return json.loads(response.content.decode())

        result_payload = await sync_to_async(run_handler_sync, thread_sensitive=False)()
        
        # Route historical trace logs directly to the live dashboard console stream
        if "telemetry_stream" in result_payload:
            await async_send_to_console(result_payload["telemetry_stream"])

        validation = result_payload.get("validation", {})
        if not validation.get("valid", False):
            await async_send_to_console(f"❌ [BIND_ENGINE] Binding failed. Errors: {validation.get('errors', [])}")
            return False

        # --- Phase 2: Neo4j Graph Relational Synthesis ---
        await async_send_to_console("🕸️ [GRAPH_MATRIX] Flushing relational code mappings into Neo4j graph context...")
        
        def commit_graph_relationships():
            # Use neomodel's built-in transaction pool safely matching your settings layout
            from neomodel import db
            
            cypher_query = (
                "MERGE (p:ComponentNode {file_path: $page_path}) "
                "SET p.name = $page_name, p.persona = 'UI_LAYOUT' "
                "MERGE (a:ComponentNode {file_path: $api_path}) "
                "SET a.name = $api_name, a.persona = 'ENTRY_POINT' "
                "MERGE (p)-[r:DEPENDS_ON {type: 'API_FETCH_STREAM'}]->(a) "
                "RETURN count(r) as relationship_count"
            )
            
            params = {
                "page_path": f"templates/{clean_app}/{clean_func}.html",
                "page_name": f"page_{clean_func}",
                "api_path": f"{clean_app}/api/{clean_api}_api.py",
                "api_name": f"api_{clean_api}"
            }
            
            db.cypher_query(cypher_query, params)
            return True

        await sync_to_async(commit_graph_relationships, thread_sensitive=False)()
        await async_send_to_console("🎉 [BIND SUCCESS] Global structural dependency compilation sweep complete. Full-stack feature live.")
        return True
# ======================================================================
# END: WORKSPACE_GRAPH_BINDER_COMPILER (PATCH 1 OF 1)
# ======================================================================
