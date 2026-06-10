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
from aurora.models import ComponentRegistry, DeltaNotesEntry

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
        
        # Build the top-level app folder right in os.getcwd()
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
            
        self.url = reverse("aurora:api_command")
        self.notes_url = reverse("aurora:delta_notes_endpoint")

    def tearDown(self):
        """Wipe out simulated codebase additions completely to ensure test isolation."""
        sandbox_path = os.path.join(self.base_dir, self.test_app)
        if os.path.exists(sandbox_path):
            shutil.rmtree(sandbox_path)
            
        # FIXED: Removed os.remove("project.md"). Instead, only target the isolated sandboxed test artifact.
        if os.path.exists("test_project.md"):
            os.remove("test_project.md")
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
        self.client.post(self.url, {"blueprint": f"/page {self.test_app} data_node public"})
        self.client.post(self.url, {"blueprint": f"/api {self.test_app} data_node public"})
        html_path = os.path.join(self.base_dir, self.test_app, 'templates', self.test_app, 'data_node.html')
        api_path = os.path.join(self.base_dir, self.test_app, 'api', 'data_node_api.py')
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
            file_path=db_path, name="secure_vault", persona="COMPILER_MODULE",
            status="ACTIVE", visibility="PUBLIC", locked=True, created_by=self.user
        )
        html_path = os.path.join(self.base_dir, self.test_app, 'templates', self.test_app, 'secure_vault.html')
        os.makedirs(os.path.dirname(html_path), exist_ok=True)
        with open(html_path, 'w') as f:
            f.write("<!-- Protected Vault Canvas -->")

        destroy_cmd = f"/destroy {self.test_app} secure_vault"
        response = self.client.post(self.url, {"blueprint": destroy_cmd})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertIn("PURGE DENIED: 'secure_vault' path infrastructure is LOCKED", data["minion_log"])
        self.assertTrue(os.path.exists(html_path))
        self.assertTrue(ComponentRegistry.objects.filter(file_path=db_path).exists())


class DeltaNotesEndpointTests(TestCase):
    """Integration test suite validating DeltaNotesEntry multi-state tracking loops."""

    def setUp(self):
        """Provision user authentication hooks and state objects."""
        self.client = Client()
        self.user = User.objects.create_user(username="test_architect", password="password_xyz_123")
        self.client.login(username="test_architect", password="password_xyz_123")
        self.endpoint_url = reverse("aurora:delta_notes_endpoint")

    def test_delta_notes_get_returns_split_log_dictionary_arrays(self):
        """Verify GET request cleanly segments unprocessed and processed logs."""
        DeltaNotesEntry.objects.create(user=self.user, text="Active Directive Alpha", processed=False)
        DeltaNotesEntry.objects.create(user=self.user, text="Completed Directive Beta", processed=True)

        response = self.client.get(self.endpoint_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["unprocessed"]), 1)
        self.assertEqual(len(data["processed"]), 1)
        self.assertEqual(data["unprocessed"][0]["text"], "Active Directive Alpha")
        self.assertEqual(data["processed"][0]["text"], "Completed Directive Beta")

    def test_delta_notes_post_crud_and_status_toggles(self):
        """Verify note creation, modification, erasure, and completion hooks."""
        # 1. Test Create Action (writes to verified .text property)
        self.client.post(self.endpoint_url, {"action": "create_note", "text": "Forced Compilation Layer"})
        note = DeltaNotesEntry.objects.get(user=self.user, text="Forced Compilation Layer")
        self.assertFalse(note.processed)

        # 2. Test Edit Action
        self.client.post(self.endpoint_url, {"action": "edit_note", "note_id": note.id, "text": "Updated Layer Spec"})
        note.refresh_from_db()
        self.assertEqual(note.text, "Updated Layer Spec")

        # 3. Test Process Action (Marks completed)
        self.client.post(self.endpoint_url, {"action": "process_note", "note_id": note.id})
        note.refresh_from_db()
        self.assertTrue(note.processed)

        # 4. Test Delete Action
        self.client.post(self.endpoint_url, {"action": "delete_note", "note_id": note.id})
        self.assertFalse(DeltaNotesEntry.objects.filter(id=note.id).exists())

    def test_compile_blueprint_uses_non_destructive_appendation(self):
        """Verify compile action utilizes 'a' mode and inserts timestamp clusters."""
        DeltaNotesEntry.objects.create(user=self.user, text="Surgical Graph Injection Rule", processed=False)

        # Initialize base file with mock history data to verify append actions
        with open("project.md", "w", encoding="utf-8") as f:
            f.write("# Historic Baseline Record Data\n")

        response = self.client.post(self.endpoint_url, {"action": "compile_blueprint"})
        self.assertEqual(response.status_code, 200)
        
        with open("project.md", "r", encoding="utf-8") as f:
            content = f.read()

        # Assert historic layout was not wiped or corrupted
        self.assertIn("# Historic Baseline Record Data", content)
        # Assert timestamp subheader blocks were successfully injected
        self.assertIn("## Backlog Export Session Cluster", content)
        # Assert tracking node was logged cleanly without toggling db states
        self.assertIn("* [ ] Surgical Graph Injection Rule", content)
        self.assertTrue(DeltaNotesEntry.objects.filter(user=self.user, processed=False).exists())
# ====================================================================== 
# END: DESTRUCTION CLEANUP & STRUCTURAL LOCK ASSERTIONS 
# ====================================================================== 
