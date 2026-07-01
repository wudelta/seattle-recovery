# ======================================================================
# FILE: hopehub/tests/test_page_new_page_hopehub.py
# START: LIFECYCLE_TEST_SUITE_SETUP
# ======================================================================
import os
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from neomodel import db
from aurora.models import ComponentRegistry
from aurora.utils.forge_registry import register_new_component

class HopehubNewPageViewProductionTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username="test_dev", password="password")
        self.expected_path = "templates/hopehub/new_page.html"
        try:
            db.cypher_query("MATCH (n:ComponentNode) WHERE n.file_path = '" + self.expected_path + "' DETACH DELETE n")
        except Exception:
            pass
        register_new_component(self.expected_path, "new_page_layout", "private", self.test_user, "COMPILER_MODULE", "Verification baseline")
# ======================================================================
# END: LIFECYCLE_TEST_SUITE_SETUP
# ======================================================================

# ======================================================================
# START: LIFECYCLE_TEST_EXECUTION_FLOW
# ======================================================================
    def test_forged_component_integrity(self):
        disk_path = os.path.join(os.getcwd(), "hopehub", "templates", "hopehub", "new_page.html")
        self.assertTrue(os.path.exists(disk_path), f"Layout canvas missing from disk path: {disk_path}")

        url = reverse("hopehub:new_page")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.assertTrue(ComponentRegistry.objects.filter(file_path=self.expected_path).exists(), "Postgres component index mapping unresolved.")
# ======================================================================
# END: LIFECYCLE_TEST_EXECUTION_FLOW
# ======================================================================
