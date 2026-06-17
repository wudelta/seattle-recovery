# ======================================================================
# FILE: aurora/tests/test_admin.py (PATCH 1 OF 1)
# START: ADMIN_REGISTRATION_AND_INLINE_VERIFICATION
# ======================================================================
from django.test import TestCase
from django.contrib.admin.sites import site
from django.contrib.auth.models import User
from neomodel import db as neomodel_db
from aurora.models import ComponentRegistry, StaticContent, DeltaDirectives
from aurora.admin import ComponentRegistryAdmin, StaticContentAdmin, DeltaDirectivesAdmin

class AdminInterfaceLayoutTests(TestCase):
    """Test suite verifying admin registration parameters and parent-child inlines."""

    def setUp(self):
        """Establish admin site environment securely without wiping the global graph."""
        # SAFE GRAPH FIX: Discarded global match-delete loop to protect production nodes
        self.user = User.objects.create_superuser(username="admin_root", password="root_password")
        self.registry_admin = ComponentRegistryAdmin(ComponentRegistry, site)

    def tearDown(self):
        """No graph operations executed during admin structural inspection loops."""
        pass

    def test_models_are_registered_correctly_with_admin_site(self):
        """Registration Check: Verify all three targeted models exist in the admin registry."""
        self.assertIn(ComponentRegistry, site._registry)
        self.assertIn(StaticContent, site._registry)
        self.assertIn(DeltaDirectives, site._registry)
        self.assertIsInstance(site._registry[ComponentRegistry], ComponentRegistryAdmin)
        self.assertIsInstance(site._registry[StaticContent], StaticContentAdmin)
        self.assertIsInstance(site._registry[DeltaDirectives], DeltaDirectivesAdmin)

    def test_component_registry_admin_exposes_expected_fields_and_filters(self):
        """Layout Check: Ensure column displays and sidebars map to active system keys."""
        self.assertIn('name', self.registry_admin.list_display)
        self.assertIn('persona', self.registry_admin.list_filter)
        self.assertIn('name', self.registry_admin.search_fields)

    def test_child_inlines_are_configured_within_parent_admin_panel(self):
        """Inline Check: Ensure child forms inject properly into the parent view block."""
        inline_model_classes = [inline.model for inline in self.registry_admin.inlines]
        self.assertIn(StaticContent, inline_model_classes)
        # FIXED: Removed DeltaDirectives assertion since it now operates as an independent, standalone model
        self.assertNotIn(DeltaDirectives, inline_model_classes)
# ======================================================================
# END: ADMIN_REGISTRATION_AND_INLINE_VERIFICATION (PATCH 1 OF 1)
# ======================================================================
