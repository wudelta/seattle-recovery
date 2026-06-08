# ======================================================================
# FILE: aurora/tests/test_console_view.py (PATCH 1 OF 1)
# START: TERMINAL COCKPIT VIEW CORE AGENT TEST SUITE
# ======================================================================
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class ConsoleViewTests(TestCase):
    """Test suite ensuring strict security gating and context rendering for the console view."""

    def setUp(self):
        """Provision client connections and standard user accounts."""
        self.client = Client()
        self.username = "architect_agent"
        self.password = "secure_override_77"
        self.dev_user = User.objects.create_user(username=self.username, password=self.password)
        self.url = reverse("aurora:console")  # Targets your terminal dashboard view routing token

    def test_unauthenticated_request_is_safely_redirected_to_login(self):
        """Security Check: Requests lacking active sessions must trigger standard login redirects."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        # Ensure the destination path safely routes through your configured login page
        self.assertIn(reverse("aurora:login"), response.url)

    def test_authenticated_developer_session_renders_cockpit_with_context_payload(self):
        """Context Check: Valid accounts must bypass gates and load layout identity tokens."""
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.url)
        
        # Verify dashboard is successfully delivered using the new orchestrator template name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aurora/aurora_console.html')
        
        # Verify the dynamic rendering tokens exist inside the frontend context scope
        self.assertEqual(response.context['architect'], self.username)
        self.assertEqual(response.context['ai_lead'], "Wu")
# ======================================================================
# END: TERMINAL COCKPIT VIEW CORE AGENT TEST SUITE
# ======================================================================
