# ======================================================================
# FILE: aurora/tests/test_api_commands.py (PATCH 1 OF 4)
# START: SYSTEM IMPORTS, MOCK FIXTURES & TEST CLIENT INITIALIZATION
# ======================================================================
import json
import os
import shutil
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from aurora.models import ComponentRegistry

class ExecuteBlueprintApiTests(TestCase):
    """Integration tests verifying the Dual-Tier View Stream Router and commands."""

    def setUp(self):
        """Configure clean testing sandboxes, user authentication, and endpoints."""
        self.base_dir = os.getcwd()
        self.test_app = "hopehub_sandbox"
        self.client = Client()
        
        # Provision authenticated developer account footprint
        self.user = User.objects.create_user(username="dev_agent", password="secure_password_123")
        self.client.login(username="dev_agent", password="secure_password_123")
        
        # ABSOLUTE COMPLIANCE RESOLUTION: Build the top-level app folder right in os.getcwd()
        os.makedirs(os.path.join(self.base_dir, self.test_app), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, self.test_app, 'views'), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, self.test_app, 'api'), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, self.test_app, 'templates', self.test_app), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, self.test_app, 'tests'), exist_ok=True)
        
        # Initialize necessary project index modules cleanly
        for path in [
            os.path.join(self.base_dir, self.test_app, 'views', '__init__.py'),
            os.path.join(self.base_dir, self.test_app, 'api', '__init__.py')
        ]:
            with open(path, 'w') as f:
                f.write("__all__ = [\n]")
                
        with open(os.path.join(self.base_dir, self.test_app, 'urls.py'), 'w') as f:
            f.write("urlpatterns = [\n]")
            
        # FIXED NAMESPACE RESOLUTION: Matches aurora app_name declaration
        self.url = reverse("aurora:api_command")

    def tearDown(self):
        """Wipe out simulated codebase additions completely to ensure test isolation."""
        sandbox_path = os.path.join(self.base_dir, self.test_app)
        if os.path.exists(sandbox_path):
            shutil.rmtree(sandbox_path)
# ======================================================================
# END: SYSTEM IMPORTS, MOCK FIXTURES & TEST CLIENT INITIALIZATION
# ======================================================================

# ======================================================================
# FILE: aurora/tests/test_api_commands.py (PATCH 2 OF 4)
# START: GATING CHECKS & DIAGNOSTIC PAGE BLUEPRINT FORGE VALIDATION
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
        
        # Verify physical disk write operations inside sandbox folder
        html_path = os.path.join(self.base_dir, self.test_app, 'templates', self.test_app, 'terminal_core.html')
        self.assertTrue(os.path.exists(html_path))
        
        # Verify component database record registration matches path formatting
        db_path = f"templates/{self.test_app}/terminal_core.html"
        self.assertTrue(ComponentRegistry.objects.filter(file_path=db_path).exists())
# ======================================================================
# END: GATING CHECKS & DIAGNOSTIC PAGE BLUEPRINT FORGE VALIDATION
# ======================================================================

# ======================================================================
# FILE: aurora/tests/test_api_commands.py (PATCH 3 OF 4)
# START: API ENDPOINT FORGE SUBSYSTEM DIAGNOSTIC VALIDATION
# ======================================================================
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
        
        # Verify physical disk code placement inside sandbox folder
        api_path = os.path.join(self.base_dir, self.test_app, 'api', 'telemetry_stream_api.py')
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
# END: API ENDPOINT FORGE SUBSYSTEM DIAGNOSTIC VALIDATION
# ======================================================================

# ======================================================================
# FILE: aurora/tests/test_api_commands.py (PATCH 4 OF 4)
# START: DESTRUCTION CLEANUP & STRUCTURAL LOCK ASSERTIONS
# ======================================================================
    def test_destroy_command_wipes_unlocked_assets_completely(self):
        """Verify /destroy sweeps both page and api files along with DB footprints."""
        # 1. Seed assets inside the sandbox environment using dynamic test_app string tokens
        self.client.post(self.url, {"blueprint": f"/page {self.test_app} data_node public"})
        self.client.post(self.url, {"blueprint": f"/api {self.test_app} data_node public"})
        
        # Confirm structural entities exist on disk before teardown
        html_path = os.path.join(self.base_dir, self.test_app, 'templates', self.test_app, 'data_node.html')
        api_path = os.path.join(self.base_dir, self.test_app, 'api', 'data_node_api.py')
        self.assertTrue(os.path.exists(html_path))
        self.assertTrue(os.path.exists(api_path))
        
        # 2. Trigger the cascading universal wipe command
        destroy_cmd = f"/destroy {self.test_app} data_node"
        response = self.client.post(self.url, {"blueprint": destroy_cmd})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertIn("SURGICAL WIPE SUCCESS", data["minion_log"])
        
        # 3. Assert absolute filesystem erasure
        self.assertFalse(os.path.exists(html_path))
        self.assertFalse(os.path.exists(api_path))
        
        # 4. Assert full relational registry cleanup
        self.assertFalse(ComponentRegistry.objects.filter(file_path=f"templates/{self.test_app}/data_node.html").exists())
        self.assertFalse(ComponentRegistry.objects.filter(file_path=f"{self.test_app}/api/data_node_api.py").exists())

    def test_destroy_command_is_blocked_by_active_component_locks(self):
        """Verify /destroy safely aborts if an asset is explicitly marked locked."""
        db_path = f"templates/{self.test_app}/secure_vault.html"
        
        # 1. Direct Seeding Integration: Create the database row entry manually
        asset = ComponentRegistry.objects.create(
            file_path=db_path,
            name="secure_vault",
            persona="COMPILER_MODULE",
            status="ACTIVE",
            visibility="PUBLIC",
            locked=True,  # Engage safety constraint flag
            created_by=self.user
        )
        
        # 2. Mock out the physical filesystem canvas configuration file to pass disk checks
        html_path = os.path.join(self.base_dir, self.test_app, 'templates', self.test_app, 'secure_vault.html')
        os.makedirs(os.path.dirname(html_path), exist_ok=True)
        with open(html_path, 'w') as f:
            f.write("<!-- Protected Vault Canvas -->")
            
        # 3. Request destruction execution on the guarded component node
        destroy_cmd = f"/destroy {self.test_app} secure_vault"
        response = self.client.post(self.url, {"blueprint": destroy_cmd})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertIn("PURGE DENIED: 'secure_vault' path infrastructure is LOCKED", data["minion_log"])
        
        # 4. Confirm the physical file is untouched and remains securely on disk
        self.assertTrue(os.path.exists(html_path))
        self.assertTrue(ComponentRegistry.objects.filter(file_path=db_path).exists())
# ======================================================================
# END: DESTRUCTION CLEANUP & STRUCTURAL LOCK ASSERTIONS
# ======================================================================
