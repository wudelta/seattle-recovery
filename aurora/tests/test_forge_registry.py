# ======================================================================
# FILE: aurora/tests/test_forge_registry.py (PATCH 1 OF 2)
# START: SYSTEM IMPORTS & GUARDRAIL ISOLATION SETUP
# ======================================================================
from django.test import TestCase
from django.contrib.auth.models import User
from neomodel import db
from aurora.models import ComponentRegistry
from aurora.utils.forge_registry import register_new_component

class ForgeRegistryTests(TestCase):
    """Test suite ensuring strict security verification for the forge registry engine."""

    def setUp(self):
        """Establish structural baseline users and isolate graph environment safely."""
        super().setUp()
        # SAFE GRAPH FIX: Confine destruction strictly to the sandboxed test path prefixes
        try:
            db.cypher_query(
                "MATCH (n) WHERE n.file_path STARTS WITH 'app/hopehub/pages/' "
                "OR n.file_path STARTS WITH 'app/hopehub/api/' DETACH DELETE n"
            )
        except Exception:
            pass
        self.dev_user = User.objects.create_user(
            username="forge_operator", password="test_password_123"
        )
        self.sample_path = "app/hopehub/pages/dashboard_view.py"

    def tearDown(self):
        """Clean local port structures and drop remaining runtime nodes safely."""
        # SAFE GRAPH FIX: Confine destruction strictly to the sandboxed test path prefixes
        try:
            db.cypher_query(
                "MATCH (n) WHERE n.file_path STARTS WITH 'app/hopehub/pages/' "
                "OR n.file_path STARTS WITH 'app/hopehub/api/' DETACH DELETE n"
            )
        except Exception:
            pass
        super().tearDown()

    def test_banned_directories_trigger_permission_guardrail_error(self):
        """Guardrail Check: Paths violating environment boundaries must raise PermissionError."""
        violation_paths = [
            "venv/lib/site-packages/malicious_mod.py",
            ".venv/config/settings.py",
            "app/modules/.git/HEAD"
        ]
        for bad_path in violation_paths:
            with self.assertRaises(PermissionError) as context:
                register_new_component(
                    file_path=bad_path,
                    name="breach_attempt",
                    visibility="public",
                    user_instance=self.dev_user
                )
            self.assertIn("FORGE GUARDRAIL VIOLATION", str(context.exception))
# ======================================================================
# END: SYSTEM IMPORTS & GUARDRAIL ISOLATION SETUP (PATCH 1 OF 2)
# ======================================================================

# ======================================================================
# FILE: aurora/tests/test_forge_registry.py (PATCH 2 OF 2)
# START: DATA INGESTION & USER OWNERSHIP ACCOUNTABILITY VERIFICATION
# ======================================================================
    def test_successful_component_registration_with_strict_ownership(self):
        """Verify entry composition, default unlock constraints, and user relationships."""
        asset = register_new_component(
            file_path=self.sample_path,
            name="system_dashboard",
            visibility=" public ",
            user_instance=self.dev_user,
            persona="COMPILER_MODULE",
            description="Testing standard registration sequences."
        )
        self.assertEqual(asset.name, "system_dashboard")
        self.assertEqual(asset.file_path, self.sample_path)
        self.assertEqual(asset.visibility.upper().strip(), "PUBLIC")
        self.assertEqual(asset.status, "ACTIVE")
        self.assertFalse(asset.locked)
        self.assertEqual(asset.created_by, self.dev_user)
        self.assertTrue(ComponentRegistry.objects.filter(id=asset.id).exists())

    def test_invalid_visibility_defaults_securely_to_private(self):
        """Sanitization Check: Erroneous strings must fall back to PRIVATE layout protection."""
        asset = register_new_component(
            file_path="app/hopehub/api/internal_stream.py",
            name="internal_stream",
            visibility="MALICIOUS_OR_CORRUPT_STRING",
            user_instance=self.dev_user
        )
        self.assertEqual(asset.visibility.upper().strip(), "PRIVATE")
# ======================================================================
# END: DATA INGESTION & USER OWNERSHIP ACCOUNTABILITY VERIFICATION (PATCH 2 OF 2)
# ======================================================================
