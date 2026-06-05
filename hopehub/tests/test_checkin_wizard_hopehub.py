# hopehub/tests/test_checkin_wizard_hopehub.py
from django.test import TestCase
from django.urls import reverse

class HopehubCheckinWizardViewIsolationTest(TestCase):
    """Automated testing suite for visibility safety mapping."""

    def test_visibility_access_rules(self):
        url = reverse("hopehub:checkin_wizard")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
