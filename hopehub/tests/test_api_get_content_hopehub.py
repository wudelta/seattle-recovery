# ======================================================================
# FILE: hopehub/tests/test_api_get_content_hopehub.py
# START: LIFECYCLE_TEST_SUITE_SETUP
# ======================================================================
import os
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from neomodel import db
from aurora.models import ComponentRegistry
from aurora.utils.forge_registry import register_new_component

class HopehubGetContentEndpointProductionTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username="test_dev", password="password")
        self.expected_path = "hopehub/api/get_content_api.py"
        # Enforce graph loopback isolation by clearing unique paths before validation
        try:
            db.cypher_query("MATCH (n:ComponentNode) WHERE n.file_path = '" + self.expected_path + "' DETACH DELETE n")
        except Exception:
            pass
        register_new_component(self.expected_path, "get_content_endpoint", "public", self.test_user, "ENTRY_POINT", "Verification baseline")
# ======================================================================
# END: LIFECYCLE_TEST_SUITE_SETUP
# ======================================================================

# ======================================================================
# START: LIFECYCLE_TEST_EXECUTION_FLOW
# ======================================================================
    def test_forged_endpoint_integrity(self):
        disk_path = os.path.join(os.getcwd(), "hopehub", "api", "get_content_api.py")
        self.assertTrue(os.path.exists(disk_path), f"API core module missing from disk path: {disk_path}")

        url = reverse("hopehub:get_content_endpoint")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(ComponentRegistry.objects.filter(file_path=self.expected_path).exists(), "Postgres API endpoint index mapping unresolved.")
# ======================================================================
# END: LIFECYCLE_TEST_EXECUTION_FLOW
# ======================================================================
