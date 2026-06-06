# ======================================================================
# FILE: aurora/tests/test_landing.py (PATCH 1 OF 1)
# START: PUBLIC ENTRYWAY PORTAL VIEW TEST SUITE
# ======================================================================
from django.test import TestCase, Client
from django.urls import reverse

class AuroraLandingViewTests(TestCase):
    """Test suite verifying public availability and template routing for the landing page."""

    def setUp(self):
        """Establish a standard testing web client network instance."""
        self.client = Client()
        self.url = reverse("aurora:landing")  # Matches your root public homepage view token

    def test_landing_page_is_publicly_accessible_without_authentication(self):
        """Availability Check: The landing entryway must respond with a pristine HTTP 200."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_landing_page_renders_with_correct_filesystem_template(self):
        """Template Check: Assert view maps accurately to its landing HTML file target."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'aurora/landing.html')
# ======================================================================
# END: PUBLIC ENTRYWAY PORTAL VIEW TEST SUITE
# ======================================================================
