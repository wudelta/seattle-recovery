# hopehub/tests/test_my_account_hopehub.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class HopehubMyAccountViewRouteTest(TestCase):
    """Automated isolated page testing suite."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(username="hopehub_pilot", password="password123")
        self.url = reverse("hopehub:my_account")

    def test_unauthenticated_user_redirects_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_accesses_forged_view_successfully(self):
        self.client.login(username="hopehub_pilot", password="password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hopehub/my_account.html")
