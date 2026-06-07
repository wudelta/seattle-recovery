# ======================================================================
# FILE: aurora/tests/test_page_delta_notes_aurora.py (PATCH 1 OF 2)
# START: LIFECYCLE_TEST_SUITE_SETUP
# ======================================================================
import os
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from neomodel import db
from aurora.models import ComponentRegistry
from aurora.utils.forge_registry import register_new_component

class AuroraDeltaNotesViewProductionTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username="test_dev", password="password")
        self.expected_path = "templates/aurora/delta_notes.html"
        
        # Enforce graph loopback isolation by clearing unique paths before validation
        try:
            db.cypher_query("MATCH (n:ComponentNode) WHERE n.file_path = '" + self.expected_path + "' DETACH DELETE n")
        except Exception:
            pass
            
        register_new_component(
            self.expected_path, 
            "delta_notes_layout", 
            "private", 
            self.test_user, 
            "COMPILER_MODULE", 
            "Verification baseline"
        )
# ======================================================================
# END: LIFECYCLE_TEST_SUITE_SETUP
# ======================================================================

# ======================================================================
# FILE: aurora/tests/test_page_delta_notes_aurora.py (PATCH 2 OF 2)
# START: LIFECYCLE_TEST_EXECUTION_FLOW
# ======================================================================
    def test_forged_component_integrity(self):
        # 1. Verify physical layout asset exists locally on the disk
        disk_path = os.path.join(os.getcwd(), "aurora", "templates", "aurora", "delta_notes.html")
        self.assertTrue(os.path.exists(disk_path), f"Layout canvas missing from disk path: {disk_path}")
        
        # 2. Assert strict boundary security: Anonymous requests must be redirected (302) to login
        url = reverse("aurora:delta_notes")
        anonymous_response = self.client.get(url)
        self.assertEqual(anonymous_response.status_code, 302)
        
        # 3. Assert authorized entry: Logged-in developer must render console layout with a clean 200 OK
        self.client.login(username="test_dev", password="password")
        authorized_response = self.client.get(url)
        self.assertEqual(authorized_response.status_code, 200)
        self.assertContains(authorized_response, "DELTA_NOTES_CONSOLE")
        
        # 4. Confirm Postgres structural model index maps correctly
        self.assertTrue(
            ComponentRegistry.objects.filter(file_path=self.expected_path).exists(), 
            "Postgres component index mapping unresolved."
        )
# ======================================================================
# END: LIFECYCLE_TEST_EXECUTION_FLOW
# ======================================================================
