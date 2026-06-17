# ======================================================================
# FILE: aurora/tests/test_api_commands.py (PATCH 1 OF 3)
# START: SYSTEM IMPORTS, MOCK FIXTURES & SAFE GRAPH SEPARATION
# ======================================================================
import json
import os
import uuid
import shutil
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from neomodel import db as neomodel_db
from aurora.models import ComponentRegistry, DeltaNotesEntry

class ExecuteBlueprintApiTests(TestCase):
    """Integration tests verifying the Dual-Tier View Stream Router and commands."""

    def setUp(self):
        """Configure clean testing sandboxes, user authentication, and endpoints safely."""
        super().setUp()
        
        # Unique runtime signature allocation to isolate disk folders and Neo4j graph nodes
        self.sandbox_suffix = uuid.uuid4().hex[:8]
        self.test_app = f"hopehub_sb_{self.sandbox_suffix}"
        self.client = Client()
        
        # Lock paths explicitly inside Django's settings configuration tree base root
        self.base_dir = settings.BASE_DIR
        self.test_dir = os.path.join(self.base_dir, self.test_app)

        # TRANSACT-GRAPH ISOLATION ENGINE: Pure transactional baseline sweep
        self.flush_graph_database()

        # Provision authenticated developer account footprint
        self.user = User.objects.create_user(username=f"dev_{self.sandbox_suffix}", password="secure_password_123")
        self.client.login(username=f"dev_{self.sandbox_suffix}", password="secure_password_123")

        # Build structural path nodes explicitly away from your real application root
        os.makedirs(self.test_dir, exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'views'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'api'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'templates', self.test_app), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'tests'), exist_ok=True)

        # Initialize necessary project index modules cleanly to enable scanning loops
        for path in [
            os.path.join(self.test_dir, 'views', '__init__.py'),
            os.path.join(self.test_dir, 'api', '__init__.py')
        ]:
            with open(path, 'w', encoding='utf-8') as f:
                f.write("__all__ = [\n]")

        with open(os.path.join(self.test_dir, 'urls.py'), 'w', encoding='utf-8') as f:
            f.write("urlpatterns = [\n]")

        self.url = reverse("aurora:api_command")
        self.notes_url = reverse("aurora:delta_notes_endpoint")

    def tearDown(self):
        """Wipe out simulated codebase additions completely to ensure test isolation."""
        # Absolute sweep tracking across any entries generated out-of-band during operations
        self.flush_graph_database()

        # Erase physical directory paths cleanly from disk infrastructure
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
        # Clean up stray diagnostic workspace documentation outputs if produced
        stray_md = os.path.join(self.base_dir, "test_project.md")
        if os.path.exists(stray_md):
            os.remove(stray_md)
            
        super().tearDown()

    def flush_graph_database(self):
        """Surgically purges Neo4j nodes containing our specific unique test suite signature identifier."""
        try:
            neomodel_db.cypher_query(
                "MATCH (n) WHERE n.file_path CONTAINS $signature DETACH DELETE n",
                {"signature": self.test_app}
            )
        except Exception:
            pass
# ======================================================================
# END: SYSTEM IMPORTS, MOCK FIXTURES & SAFE GRAPH SEPARATION (PATCH 1 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/tests/test_api_commands.py (PATCH 2 OF 3)
# START: GATING CHECKS, DIAGNOSTIC PAGE BLUEPRINT & API FORGE VALIDATION
# ======================================================================
    def test_http_method_gating_rejects_get_requests(self):
        """Verify stream router completely blocks GET requests with a 405 status."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_empty_or_missing_blueprint_command_returns_ready_status(self):
        """Verify empty command payload defaults cleanly to standard standby log."""
        response = self.client.post(self.url, {"blueprint": ""})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["minion_log"], "System standing ready...")
        self.assertTrue(data["validation"]["valid"])

    def test_page_command_forges_assets_and_registers_component(self):
        """Verify /page command generates file layers and adds Postgres entries."""
        cmd = f"/page {self.test_app} terminal_core public"
        response = self.client.post(self.url, {"blueprint": cmd})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        
        if not data["validation"]["valid"] or "FORGE SUCCESS" not in data["minion_log"]:
            print(f"\n[DIAGNOSTIC BACKEND ENGINE LOG]: {json.dumps(data, indent=4)}\n")
            
        self.assertIn("FORGE SUCCESS", data["minion_log"])
        self.assertTrue(data["validation"]["valid"])

        # Verify physical disk write operations inside randomized sandbox folder template tree
        html_path = os.path.join(self.test_dir, 'templates', self.test_app, 'terminal_core.html')
        self.assertTrue(os.path.exists(html_path))

        # Verify component database record registration matches sandboxed path tracking rules
        db_path = f"templates/{self.test_app}/terminal_core.html"
        self.assertTrue(ComponentRegistry.objects.filter(file_path=db_path).exists())

    def test_api_command_forges_assets_and_registers_component(self):
        """Verify /api command builds function modules and creates tracking records."""
        cmd = f"/api {self.test_app} telemetry_stream private"
        response = self.client.post(self.url, {"blueprint": cmd})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        
        if not data["validation"]["valid"] or "FORGE SUCCESS" not in data["minion_log"]:
            print(f"\n[DIAGNOSTIC API ENGINE LOG]: {json.dumps(data, indent=4)}\n")
            
        self.assertIn("FORGE SUCCESS", data["minion_log"])
        self.assertTrue(data["validation"]["valid"])

        # Verify physical disk code placement inside sandboxed api directory
        api_path = os.path.join(self.test_dir, 'api', 'telemetry_stream_api.py')
        self.assertTrue(os.path.exists(api_path))

        # Verify structural registration record exists inside database layer
        db_path = f"{self.test_app}/api/telemetry_stream_api.py"
        self.assertTrue(ComponentRegistry.objects.filter(file_path=db_path).exists())

    def test_invalid_blueprint_subcommand_returns_unknown_log(self):
        """Verify router gracefully isolates unmapped automation parameters."""
        response = self.client.post(self.url, {"blueprint": "/unknown_action parameter"})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertIn("Unknown automation instruction", data["minion_log"])
# ======================================================================
# END: GATING CHECKS, DIAGNOSTIC PAGE BLUEPRINT & API FORGE VALIDATION (PATCH 2 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/tests/test_api_commands.py (PATCH 3 OF 3)
# START: DESTRUCTION CLEANUP, STRUCTURAL LOCKS & BIND SUITE ASSERTIONS
# ======================================================================
    def test_destroy_command_wipes_unlocked_assets_completely(self):
        """Verify /destroy sweeps both page and api files along with DB footprints."""
        self.client.post(self.url, {"blueprint": f"/page {self.test_app} data_node public"})
        self.client.post(self.url, {"blueprint": f"/api {self.test_app} data_node public"})
        
        html_path = os.path.join(self.test_dir, 'templates', self.test_app, 'data_node.html')
        api_path = os.path.join(self.test_dir, 'api', 'data_node_api.py')
        
        self.assertTrue(os.path.exists(html_path))
        self.assertTrue(os.path.exists(api_path))

        destroy_cmd = f"/destroy {self.test_app} data_node"
        response = self.client.post(self.url, {"blueprint": destroy_cmd})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        
        self.assertIn("SURGICAL WIPE SUCCESS", data["minion_log"])
        self.assertFalse(os.path.exists(html_path))
        self.assertFalse(os.path.exists(api_path))
        self.assertFalse(ComponentRegistry.objects.filter(file_path=f"templates/{self.test_app}/data_node.html").exists())
        self.assertFalse(ComponentRegistry.objects.filter(file_path=f"{self.test_app}/api/data_node_api.py").exists())

    def test_destroy_command_is_blocked_by_active_component_locks(self):
        """Verify /destroy safely aborts if an asset is explicitly marked locked."""
        db_path = f"templates/{self.test_app}/secure_vault.html"
        asset = ComponentRegistry.objects.create(
            file_path=db_path,
            name="secure_vault",
            persona="COMPILER_MODULE",
            status="ACTIVE",
            visibility="PUBLIC",
            locked=True,
            created_by=self.user
        )
        
        html_path = os.path.join(self.test_dir, 'templates', self.test_app, 'secure_vault.html')
        os.makedirs(os.path.dirname(html_path), exist_ok=True)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write("<!-- Protected Vault Canvas -->")

        destroy_cmd = f"/destroy {self.test_app} secure_vault"
        response = self.client.post(self.url, {"blueprint": destroy_cmd})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        
        self.assertIn("PURGE DENIED: 'secure_vault' path infrastructure is LOCKED", data["minion_log"])
        self.assertTrue(os.path.exists(html_path))
        self.assertTrue(ComponentRegistry.objects.filter(file_path=db_path).exists())

    def test_bind_command_modifies_template_and_injects_jquery_callback(self):
        """Verify /bind command locates existing templates and embeds async ajax loaders."""
        html_dir = os.path.join(self.test_dir, 'templates', self.test_app)
        os.makedirs(html_dir, exist_ok=True)
        html_target_file = os.path.join(html_dir, 'dashboard_view.html')
        
        with open(html_target_file, 'w', encoding='utf-8') as f:
            f.write("<h1>Under Construction Placeholder</h1>")

        cmd = f"/bind {self.test_app} dashboard_view get_content"
        response = self.client.post(self.url, {"blueprint": cmd})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        
        self.assertTrue(data["validation"]["valid"])
        self.assertIn("SUCCESS: HTML view container bound", data["minion_log"])
        self.assertIn("[BIND_ENGINE] Commencing binding orchestration", data["telemetry_stream"])

        with open(html_target_file, 'r', encoding='utf-8') as f:
            updated_content = f.read()
            
        self.assertIn(f"fetch('/{self.test_app}/api/get_content/')", updated_content)
        self.assertIn("id='json_payload_render'", updated_content)
        self.assertNotIn("Under Construction Placeholder", updated_content)

    def test_bind_command_handles_missing_parameters_gracefully(self):
        """Verify /bind safely aborts and logs failures if short arguments are supplied."""
        cmd = f"/bind {self.test_app} incomplete_arguments"
        response = self.client.post(self.url, {"blueprint": cmd})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        
        self.assertFalse(data["validation"]["valid"])
        self.assertIn("Syntax: /bind <app_name> <function_name> <api_name>", data["minion_log"])
# ======================================================================
# END: DESTRUCTION CLEANUP, STRUCTURAL LOCKS & BIND SUITE ASSERTIONS (PATCH 3 OF 3)
# ======================================================================
