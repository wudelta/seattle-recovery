# hopehub/tests/test_bed_locator_hopehub.py
from django.test import TestCase
from django.urls import reverse

class HopehubBedLocatorEndpointIsolationTest(TestCase):
    def test_visibility_api_rules(self):
        url = reverse("hopehub:bed_locator_endpoint")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
