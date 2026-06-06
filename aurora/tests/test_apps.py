# ======================================================================
# FILE: aurora/tests/test_apps.py (PATCH 1 OF 1)
# START: APPLICATION FRAMEWORK CONFIGURATION TEST SUITE
# ======================================================================
import sys
from django.test import TestCase
from django.apps import apps
from aurora.apps import AuroraConfig

class AuroraConfigTests(TestCase):
    """Test suite ensuring app registration details and signal subsystems bootstrap correctly."""

    def test_app_config_metadata_is_correctly_defined(self):
        """Configuration Check: Assert app config paths match structural layout standards."""
        self.assertEqual(AuroraConfig.name, 'aurora')
        self.assertEqual(apps.get_app_config('aurora').name, 'aurora')

    def test_ready_lifecycle_loads_subsystems_successfully(self):
        """Lifecycle Check: Verify critical graph nodes and relational signal loops initialize without fault."""
        app_config = apps.get_app_config('aurora')
        
        # Ensure our critical targets exist in sys.modules after ready() has executed on startup
        self.assertIn('aurora.nodes', sys.modules)
        self.assertIn('aurora.signals', sys.modules)
# ======================================================================
# END: APPLICATION FRAMEWORK CONFIGURATION TEST SUITE
# ======================================================================
