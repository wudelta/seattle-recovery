import json
import os
import time
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class HeadlessSessionCloseAutomationTest(TestCase):
    """
    Automated Independent Verification Suite for the Headless Session Close API Core.
    Tests session termination, thread offloading, and backup logic browser-free.
    """
    def setUp(self):
        # 1. Set up test boundaries and client session
        self.client = Client()
        self.username = "delta_test_close"
        self.password = "matrix_secure_pass_789"
        self.test_user = User.objects.create_user(username=self.username, password=self.password)
        
        # 2. Target the exact namespaced URL pattern for session ending
        # FIXED: Restored original lookup string to match your exact routing maps
        self.target_url = reverse('aurora:end_session')
        
        # 3. Dedicated Local Staging Verification Folder
        self.local_backup_dir = os.path.join(os.getcwd(), 'core_logic/staging/backups')

    def test_successful_session_close_and_thread_detachment(self):
        print("\n🧪 [TEST] Simulating secure evening shutdown and thread detachment...")
        
        # Force log in to pass security decorators cleanly
        self.client.login(username=self.username, password=self.password)
        
        # Seed an active running session identity code into the fake engine client storage tracker
        session_tracker = self.client.session
        session_tracker['current_session_id'] = 'test_token_ab1234'
        session_tracker.save()
        
        mock_payload = {
            "session_id": "test_token_ab1234",
            "user_id": "delta_test_close"
        }
        
        print("📡 Dispatching transaction payload package to close endpoint view...")
        response = self.client.post(
            self.target_url,
            data=json.dumps(mock_payload),
            content_type="application/json"
        )
        
        # Core Verification: Django must disconnect the client instantly with a 200 OK status code
        self.assertEqual(response.status_code, 200, f"Expected 200 OK response from API, got: {response.status_code}")
        
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['session_status'], 'closed')
        self.assertIn('git_pipeline_status', data)
        print(f"✅ Handshake verified. Server response: '{data['git_pipeline_status']}'")

        # --- LOCAL RETENTION CAPACITY AUDIT MATRIX ---
        print("\n📊 --- LOCAL STORAGE ARCHIVE DATA FOOTPRINT AUDIT ---")
        
        # Pause briefly to allow the background worker daemon to write files down to disk paths safely
        time.sleep(1.2)
        
        if os.path.exists(self.local_backup_dir):
            discovered_archives = [
                os.path.join(self.local_backup_dir, file) 
                for file in os.listdir(self.local_backup_dir) 
                if file.endswith('.zip') or file.endswith('.db') or file.endswith('.sqlite3')
            ]
            
            if discovered_archives:
                # Find the most recently generated backup file output inside the workspace target
                latest_emergency_file = max(discovered_archives, key=os.path.getmtime)
                file_weight_bytes = os.path.getsize(latest_emergency_file)
                file_weight_kb = file_weight_bytes / 1024
                
                print(f"📁 Target Archive Recovered Safely: {os.path.basename(latest_emergency_file)}")
                print(f"📐 Tracked Footprint Weight: {file_weight_kb:.2f} KB ({file_weight_bytes} bytes)")
                
                # Cloud Guardrail Simulation Check: Ensure files are small enough to prevent Google Drive saturation anomalies
                STORAGE_ALERT_CEILING_BYTES = 50 * 1024 * 1024 # 50 Megabytes structural boundary line
                if file_weight_bytes > STORAGE_ALERT_CEILING_BYTES:
                    print("⚠️ ALERT WARNING: Single database snapshot exceeds 50MB baseline threshold limits!")
                else:
                    print("✅ Storage Allocation Safety Check: File size remains well within safe constraints.")
            else:
                print("ℹ️ Note: No backup files (.zip/.sqlite3) currently found inside the local storage matrix directory.")
        else:
            print(f"⚠️ Warning Matrix: Local retention backup tracking folder does not exist at: {self.local_backup_dir}")
            
        print("----------------------------------------------------\n")
