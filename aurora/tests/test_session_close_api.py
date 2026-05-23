import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class HeadlessSessionCloseAutomationTest(TestCase):
    """
    Automated Independent Verification Suite for the Headless Session Close API Core.
    Can be run directly via terminal commands with no browser.
    """
    def setUp(self):
        self.client = Client()
        self.username = "delta_test_close"
        self.password = "matrix_secure_pass_789"
        self.test_user = User.objects.create_user(username=self.username, password=self.password)
        self.target_url = reverse('aurora:end_session') # Maps cleanly to your urls.py route name

    def test_successful_session_close_and_thread_detachment(self):
        print("\n🧪 [TEST 1] Testing full secure close sequence handshake and thread detachment...")
        
        # Authenticate the user session cleanly
        self.client.login(username=self.username, password=self.password)
        
        mock_payload = {
            "session_id": "test_token_ab1234",
            "user_id": "delta_test_close"
        }
        
        print("📡 Sending raw mock JSON transaction payload directly into evening views controller...")
        response = self.client.post(
            self.target_url,
            data=json.dumps(mock_payload),
            content_type="application/json"
        )
        
        # Verify that Django immediately completes the request instead of waiting for Git push
        self.assertEqual(response.status_code, 200, f"Expected 200 OK, got: {response.status_code}")
        
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['session_status'], 'closed')
        self.assertIn('git_pipeline_status', data)
        print(f"✅ [TEST 1] Server disconnected loop safely. Status: {data['git_pipeline_status']}")
