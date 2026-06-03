from django.test import TestCase
from django.urls import reverse, exceptions

class TestUnderConstructionView(TestCase):
    def test_page_resolves_and_renders_successfully(self):
        try:
            target_url = reverse('mission_statement')
        except exceptions.NoReverseMatch:
            self.fail("Routing namespace 'mission_statement' does not exist yet.")
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FEATURE UNDER CONSTRUCTION')
