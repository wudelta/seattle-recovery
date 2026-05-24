import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from ..models import Document, Content

class HeadlessSessionAutomationTest(TestCase):
    """
    Automated Independent Verification Suite for the Headless Session Start API Core.
    Can be run directly via terminal commands without a browser.
    """
    def setUp(self):
        # Initialize complete structural mock test environment parameters
        self.client = Client()
        self.username = "delta_test"
        self.password = "matrix_secure_pass_123"
        self.test_user = User.objects.create_user(username=self.username, password=self.password)
        # FIXED NAMESPACE: Added 'aurora:' prefix to map the routing lookup accurately
        self.target_url = reverse('aurora:start_online_session')

    def test_unauthenticated_request_throws_json_unauthorized(self):
        print("\n🧪 [TEST 1] Verifying security guardrails block unauthenticated callers...")
        response = self.client.post(
            self.target_url, 
            data=json.dumps({"brief_content": "Sample Test"}), 
            content_type="application/json"
        )
        
        # FIXED ASSERTION: Asserting a 401 Unauthorized status code and checking for a clean JSON error response payload
        print(f"📊 [TEST 1 RESULT] Received Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 401)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Unauthorized entry', data['error'])
        print("✅ [TEST 1] Security barrier confirmed. Request successfully denied with JSON 401 response.")

    def test_successful_json_payload_handshake_flow(self):
        print("\n🧪 [TEST 2] Running full secure headless login and payload simulation...")
        # Log the mock user into the network simulation core
        login_success = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login_success, "Mock authentication loop failed.")
        
        mock_payload = {
            "brief_content": "Test Objective: Connect automated unit testing strings to verification scripts.",
            "user_id": "delta_test"
        }
        
        print("📡 Sending raw mock JSON transaction payload directly into endpoint view controllers...")
        response = self.client.post(
            self.target_url,
            data=json.dumps(mock_payload),
            content_type="application/json"
        )
        
        # 1. Assert accurate HTTP transmission codes
        self.assertEqual(response.status_code, 200, f"Expected 200 OK, got: {response.status_code}")
        
        # 2. Evaluate parsed data properties directly
        data = json.loads(response.content)
        self.assertTrue(data['success'], "API returned a false operation status check result.")
        self.assertEqual(data['session_status'], 'active')
        self.assertIn('system_prompt_envelope', data)
        
        print("📝 Verifying that system runtime prompt accurately contains our security instruction arrays...")
        self.assertIn("delta_test", data['system_prompt_envelope'])
        self.assertIn("ACTIVE WORKSPACE ENVIRONMENT", data['system_prompt_envelope'])
        
        # 3. Verify that database entries were accurately committed to Postgres
        print("🗄️ Querying database tables to ensure metrics were written to EAV schema records...")
        doc_count = Document.objects.filter(title__contains="Daily Brief").count()
        self.assertEqual(doc_count, 1, f"Expected exactly 1 database document record row, found: {doc_count}")
        print("✅ [TEST 2] Full decoupled initialization loop ran perfectly without browser dependency.")
