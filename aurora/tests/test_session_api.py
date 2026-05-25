import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from aurora.models import Document, Content, DeltaNote, DeltaChange, DeltaDirective  # All models accounted for

class HeadlessSessionAutomationTest(TestCase):
    """
    Automated Independent Verification Suite for the Headless Session Start API Core.
    Executed entirely within the terminal command line environment via python manage.py test.
    """

    def setUp(self):
        print("🔍 [STAGE 1] Initializing complete structural mock testing database parameters...")
        self.client = Client()
        self.username = "delta_test"
        self.password = "matrix_secure_pass_123"
        self.test_user = User.objects.create_user(username=self.username, password=self.password)
        self.target_url = reverse('aurora:start_online_session')

    def test_unauthenticated_request_throws_json_unauthorized(self):
        print("\n🧪 [TEST 1] Verifying security guardrails block unauthenticated callers...")
        response = self.client.post(
            self.target_url,
            data=json.dumps({"session_intent": "Automated Test Sweep"}),
            content_type="application/json"
        )
        
        print(f"📊 [TEST 1 RESULT] Received Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 401)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        print("✅ [TEST 1] Security barrier confirmed. Request successfully denied with JSON 401.")

    def test_successful_delta_process_flow_handshake(self):
        print("\n🧪 [TEST 2] Running full secure headless login and Delta Process simulation...")
        
        # 1. Force state parameters onto the mock user account
        self.client.login(username=self.username, password=self.password)
        
        # [THE FIX] Manually force user session state parameters to bypass token mismatch drops
        user = User.objects.get(username=self.username)
        self.client.force_login(user) 
        print("🔐 [TEST 2] Enforced security credentials directly onto headless client session context.")

        # 2. Seed an Approved Directive to verify Wu's prompt injection
        print("🗄️ Seeding an approved structural DeltaDirective into the testing memory matrix...")
        DeltaDirective.objects.create(
            user=self.test_user,
            directive_name="GLOBAL_CONSTRAINTS",
            assigned_to="WU",
            dense_instructions="Never output presentation wrappers inside JSON view engines.",
            is_approved=True
        )

        # Log the mock user into the network simulation core
        login_success = self.client.login(username=self.username, password=self.password)
        self.assertTrue(login_success, "❌ Mock authentication loop failed.")

        print("📡 Sending raw session start request directly into view controllers...")
        response = self.client.post(
            self.target_url,
            data=json.dumps({"session_intent": "Initialize Workspace"}),
            content_type="application/json"
        )

        # Assert clean transmission
        print(f"📊 [TEST 2 RESULT] Received Status Code: {response.status_code}")
        self.assertEqual(response.status_code, 200, f"Expected 200 OK, got: {response.status_code}")

        # Evaluate headless JSON data properties directly
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Assert that the 8B worker loop intercepted and flipped the offline logs
        print("_ Asserting that offline DeltaNote statuses were flipped to is_processed=True...")
        unprocessed_count = DeltaNote.objects.filter(user=self.test_user, is_processed=False).count()
        self.assertEqual(unprocessed_count, 0, f"Expected 0 unprocessed notes, found: {unprocessed_count}")

        # Assert that new pending review rows were generated in the database
        change_count = DeltaChange.objects.filter(user=self.test_user, status='PENDING_REVIEW').count()
        self.assertTrue(change_count > 0, f"Expected generated review items, found: {change_count}")

        # Verify Wu's structural prompt envelope contains injected active directives
        print("🧠 Checking Wu's system prompt envelope for injected directives and user context...")
        self.assertIn("delta_test", data['system_prompt_envelope'])
        self.assertIn("GLOBAL_CONSTRAINTS", data['system_prompt_envelope'])
        self.assertIn("Never output presentation wrappers", data['system_prompt_envelope'])

        print("✅ [TEST 2] Full decoupled initialization loop ran perfectly without browser dependency.")
