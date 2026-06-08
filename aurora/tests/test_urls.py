# ======================================================================
# FILE: aurora/tests/test_urls.py (PATCH 1 OF 1)
# START: NAMESPACED ROUTING REVERSE VALIDATION SUITE
# ======================================================================
from django.test import TestCase
from django.urls import reverse, resolve
from aurora.views import aurora_landing, ConsoleView
from aurora.api import execute_blueprint_api  # Updated import path to target the newly forged api package location

class AuroraUrlRoutingTests(TestCase):
    """Test suite ensuring all core namespaced routes resolve to their correct view targets."""

    def test_landing_url_resolves_to_aurora_landing_view(self):
        """Routing Check: Root namespace route must map directly to public landing engine."""
        url = reverse("aurora:landing")
        self.assertEqual(url, "/aurora/")
        self.assertEqual(resolve(url).func, aurora_landing)

    def test_console_url_resolves_to_console_class_view(self):
        """Routing Check: Terminal workspace namespace route must map directly to cockpit view."""
        url = reverse("aurora:console")
        self.assertEqual(url, "/aurora/console/")
        self.assertEqual(resolve(url).func.view_class, ConsoleView)

    def test_api_command_url_resolves_to_blueprint_executor_view(self):
        """Routing Check: AI orchestration interface route must map to stream router via app namespace."""
        # FIXED: Prepended with aurora: namespace context to match app_name declaration
        url = reverse("aurora:api_command")
        self.assertEqual(url, "/aurora/api/command/")
        self.assertEqual(resolve(url).func, execute_blueprint_api)
# ======================================================================
# END: NAMESPACED ROUTING REVERSE VALIDATION SUITE
# ======================================================================
