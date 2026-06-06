# ======================================================================
# FILE: core_logic/tests/test_global_urls.py (PATCH 1 OF 1)
# START: GLOBAL ROUTING DISPATCH MATRIX REVERSE TEST SUITE
# ======================================================================
from django.test import TestCase
from django.urls import reverse, resolve

class GlobalUrlRoutingTests(TestCase):
    """Test suite ensuring all project-wide namespaces and admin targets map correctly."""

    def test_admin_url_resolves_to_admin_site(self):
        """Routing Check: Admin namespace path must resolve directly to standard Django admin site."""
        url = "/admin/"
        resolver_match = resolve(url)
        self.assertEqual(resolver_match.app_name, "admin")

    def test_hopehub_namespace_resolves_correctly(self):
        """Routing Check: HopeHub app namespace should register and point to its portal layout views."""
        # Tests reverse capability of namespaced url mapping rules
        url = reverse("hopehub:landing")
        self.assertTrue(url.startswith("/hopehub/"))

    def test_aurora_namespace_resolves_correctly(self):
        """Routing Check: Aurora infrastructure namespace should connect smoothly to terminal utilities."""
        url = reverse("aurora:landing")
        self.assertTrue(url.startswith("/aurora/"))
# ======================================================================
# END: GLOBAL ROUTING DISPATCH MATRIX REVERSE TEST SUITE
# ======================================================================
