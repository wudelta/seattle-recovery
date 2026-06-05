# hopehub/tests/test_about_hopehub_hopehub.py
from django.test import TestCase
from django.urls import reverse

class HopehubAboutHopehubViewIsolationTest(TestCase):
    """Automated testing suite for visibility safety mapping."""

    def test_visibility_access_rules(self):
        url = reverse("hopehub:about_hopehub")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
