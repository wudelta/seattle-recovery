# ======================================================================
# FILE: aurora/tests/test_api_delta_notes_aurora.py (PATCH 1 OF 2)
# START: LIFECYCLE_TEST_SUITE_SETUP
# ======================================================================
import os
import tempfile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from neomodel import db
from aurora.models import ComponentRegistry, DeltaNotesEntry
from aurora.utils.forge_registry import register_new_component

class AuroraDeltaNotesEndpointProductionTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username="test_dev", password="password")
        self.expected_path = "aurora/api/delta_notes_api.py"
        
        # Build sandboxed temporary environment file system maps for blueprint compilation testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.mock_md_path = os.path.join(self.temp_dir.name, 'project.md')
        with open(self.mock_md_path, 'w', encoding='utf-8') as f:
            f.write("# Active Core Blueprint\n## Next Staging Steps")
        
        # Enforce graph loopback isolation by clearing unique paths before validation
        try:
            db.cypher_query("MATCH (n:ComponentNode) WHERE n.file_path = '" + self.expected_path + "' DETACH DELETE n")
        except Exception:
            pass
            
        register_new_component(
            self.expected_path, 
            "delta_notes_endpoint", 
            "private", 
            self.test_user, 
            "ENTRY_POINT", 
            "Verification baseline"
        )

    def tearDown(self):
        self.temp_dir.cleanup()
# ======================================================================
# END: LIFECYCLE_TEST_SUITE_SETUP
# ======================================================================

# ======================================================================
# FILE: aurora/tests/test_api_delta_notes_aurora.py (PATCH 2 OF 2)
# START: LIFECYCLE_TEST_EXECUTION_FLOW
# ======================================================================
    def test_forged_endpoint_integrity(self):
        # 1. Verify physical file asset existence
        disk_path = os.path.join(os.getcwd(), "aurora", "api", "delta_notes_api.py")
        self.assertTrue(os.path.exists(disk_path), f"API core module missing from disk path: {disk_path}")
        
        # 2. Assert strict security gate: Anonymous connection attempts hit a 302 redirect
        url = reverse("aurora:delta_notes_endpoint")
        anon_response = self.client.get(url)
        self.assertEqual(anon_response.status_code, 302)
        
        # 3. Verify standard Postgres baseline entry registration mapping
        self.assertTrue(ComponentRegistry.objects.filter(file_path=self.expected_path).exists(), "Postgres API endpoint index mapping unresolved.")

    def test_authenticated_api_actions_lifecycle(self):
        url = reverse("aurora:delta_notes_endpoint")
        self.client.login(username="test_dev", password="password")

        # Action A: Create Note payload integration test
        create_response = self.client.post(url, {
            'action': 'create_note',
            'text': 'Automated transaction boundary audit tracking.'
        })
        self.assertEqual(create_response.status_code, 200)
        note_id = create_response.json().get("note_id")
        self.assertIsNotNone(note_id)

        # Action B: Synchronize Timer active focus tracking loop test
        sync_response = self.client.post(url, {
            'action': 'sync_timer',
            'note_id': note_id,
            'current_duration': 360  # 6 minutes focus time allocation
        })
        self.assertEqual(sync_response.status_code, 200)
        self.assertEqual(DeltaNotesEntry.objects.get(id=note_id).total_seconds_logged, 360)

        # Action C: Markdown local file appending blueprint automation compilation test
        with override_settings(BASE_DIR=self.temp_dir.name):
            compile_response = self.client.post(url, {'action': 'compile_blueprint'})
            self.assertEqual(compile_response.status_code, 200)
            
            # Verify database states flipped cleanly to locked-out
            self.assertEqual(DeltaNotesEntry.objects.filter(processed=False).count(), 0)
            
            # Assert file mutations verified on isolated sandboxed path
            with open(self.mock_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn("* [ ] Automated transaction boundary audit tracking.", content)
# ======================================================================
# END: LIFECYCLE_TEST_EXECUTION_FLOW
# ======================================================================
